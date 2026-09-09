# DETERMINISM.md — What the engine actually guarantees

Determinism is a first-class requirement (project brief §XVIII / §8), but "deterministic"
is not one guarantee, it is several, of different strength and different scope. This
document states them precisely so the API and the tests can be held to something concrete
rather than the word alone.

## The four tiers, and where each one stops

Determinism is not one guarantee that either holds or doesn't; it is a ladder, and each
rung depends on something the rung below it does not. Naming them A–D so a claim can be
pinned to exactly one:

### A. Same process / same interpreter instance — GUARANTEED

For identical `(text, seed, mode, tonic, tempo, meter, measures, phrase_measures,
density, heretical)` and unchanged `ENGINE_VERSION`, two calls to `KircherEngine.compose`
*in the same running process* produce identical `NoteEvent` sequences for every voice —
same pitches, same offsets, same durations, same velocities, same roles.

This follows from two things the code enforces, not just intends:

- **No global randomness.** `random.seed` / `random.random` are never touched anywhere in
  the engine; every stochastic decision draws from an explicit, labelled
  `determinism.SeedStream`. `tests/test_determinism.py::test_composition_does_not_touch_the_global_random_state`
  asserts `random.getstate()` is bit-for-bit unchanged after a `compose()` call.
- **Canonical seed derivation.** `SeedStream.derive` is a pure function of
  `(root_seed, label_path)`. Sibling streams are independent regardless of the order they
  are created in, so adding a new decision point in one stage cannot perturb a seed
  already derived in another.

### B. Fresh process / same engine version + same Python runtime — GUARANTEED, and tested as such

A *new* interpreter process, started separately, on the **same Python version and
implementation** the engine was tested against, reproduces the identical `NoteEvent`
sequence for an identical request. This is the rung that actually matters for a real
deployment (a request served by worker process #7 today and worker process #12
tomorrow), and it is the rung this pass added a genuine test for:
`tests/test_cross_process.py` spawns independent `python` subprocesses — not repeated
calls inside one pytest run — and compares their output byte-for-byte.

Reaching tier B is not automatic; it depends on the seed and the config fingerprint being
derived the same way regardless of *how* the process was started, which used to fail on
`repr()`:

- `repr(SomeEnum.MEMBER)` embeds the class name and Python's own enum formatting, both of
  which have changed across interpreter versions (PEP 663, and earlier changes to
  `Enum.__repr__` and `Enum.__str__`).
- `repr({"a": 1, "b": 2})` differs from `repr({"b": 2, "a": 1})`, so two semantically equal
  configurations built via different code paths could fingerprint differently purely from
  dict insertion order.
- Float `repr` is stable in current CPython but is not a language-level guarantee.

`determinism.canonical()` replaces every `repr()`-based hash input with a **type-tagged**
serialisation (mappings sorted by canonicalised key, not `str(key)`; sets sorted and
distinguished from lists; floats, bytes and sequences each wrapped so they cannot collide
with an unrelated type that happens to format to the same digits — see the docstring on
`canonical()` for the concrete collisions this closes) and any type with no defined
canonical form raises `CanonicalisationError` rather than silently falling back to
`repr`. `stable_hash()` and `fingerprint()` both canonicalise their input, so the seed a
request resolves to, and the config fingerprint that names it, no longer depend on
interpreter version, dict construction order, or `Enum.__repr__`.

**Tier B covers "the same pitches, offsets, durations, roles" — the musical content
itself.** It does not cover the exact bytes of the serialized MIDI file (tier D), and it
does **not** extend to a different Python version or implementation (tier C).

### C. Different Python versions or implementations — NOT GUARANTEED, not tested

`SeedStream` wraps `random.Random`, seeded once from a `stable_hash()` output and driven
through `random()`, `randint()`, `randrange()` and friends from then on. Python's own
documentation is explicit that this is a *reproducibility-within-a-version* guarantee,
not a cross-version one: the `random` module promises that a given seed reproduces the
same sequence *for a given Python version*, but does not promise the algorithm or its
output are stable across CPython releases, let alone across CPython vs. PyPy vs. other
implementations. Nothing in this codebase tests or claims otherwise. A request served by
Python 3.11 and the same request served by Python 3.13 may therefore choose different
notes, and that would not be a bug in this engine — it would be exactly what tier C says
is unguaranteed.

**If long-term cross-version identity is ever required**, the fix is not a documentation
change: it means replacing `random.Random` with an engine-owned, explicitly specified PRNG
algorithm (e.g. a plain counter-based construction over the existing blake2b hashing,
which is already used for seed derivation and is not subject to this caveat). That is
future work, recorded here rather than spuriously implemented in this pass — the brief for
this correction explicitly asked not to build a new PRNG unless it turned out to be
necessary, and closing tiers A/B and being honest about C was sufficient.

### D. Byte-identical MIDI file — SCOPED FURTHER STILL, not universal

`models.ProvenanceModel` (returned as `provenance` in every `/compose` response) carries a
`runtime` block
(`{python, music21, implementation}`) precisely because this claim is the one that is
*not* unconditional. `music21`'s `score.write('midi', ...)` decides tick resolution,
event ordering within a simultaneity, and meta-event emission; a different `music21`
version is free to change any of that while still producing musically correct output.

**The contract:** byte-identical MIDI is guaranteed only within one locked dependency set,
on the operating system, CPU architecture and Python build actually tested — see
`requirements.lock.txt` for exactly what that is. Pinning package *versions* is
necessary but not sufficient: a wheel built for a different OS/arch can legitimately
differ in floating-point behaviour or binary layout even at an identical version number.
It is explicitly **not** promised "across arbitrary Python/music21 versions" (the
original brief's own wording), nor across untested platforms, because neither has been
tested and nothing here can make that promise responsibly without testing it.

`runtime_versions()` is deliberately **not** hashed into the seed. The same request
choosing different notes depending on which machine served it would be a genuine defect
(a tier B failure); the same request producing a MIDI file with a different tick count on
`music21==9.1` vs. `music21==10.5` is not — it is exactly what tier D's scoping predicts,
and is why the runtime is reported *alongside* the seed rather than folded into it.

## Practical guidance for a consumer

| You want to know | Compare |
| --- | --- |
| "Will this request always produce the same music?" | `seed`, `config_fingerprint`, `engine_version` — if all three match on the same Python version/implementation, yes (tier A/B) |
| "Will this request always produce the same MIDI bytes?" | The above, **plus** `provenance.runtime` matching **and** the same OS/arch/Python build as `requirements.lock.txt` — only guaranteed if all of it matches (tier D) |
| "Did the semantic mapping resolve to a different seed than I expected?" | `provenance.requested_seed` (what you sent) vs. `provenance.seed` (what was resolved) — both wire-safe decimal strings, see "Seed wire format" below |

## Seed wire format — why it is a string, not a number

`provenance.seed` and `provenance.requested_seed` are drawn from a full 64-bit range
internally, and are serialised as **decimal strings**, not JSON numbers. JavaScript's
`Number` type represents integers exactly only up to `2**53 - 1`; a seed above that,
returned as a bare JSON number, would silently lose precision the instant a browser or
Node parses the response — the classic "large ID rounds itself off" bug. A Tone.js/React
consumer should treat these fields as opaque strings for storage, comparison and
resubmission, and use `BigInt(seed)` rather than `Number(seed)` if the actual numeric
value is ever needed. `tests/test_seed_wire_contract.py` proves a seed above `2**53`
survives the full API round trip with no precision loss, and proves the raw JSON token is
a quoted string (not a bare number) for both an explicit large integer seed and an
auto-derived one.

## What is regression-tested

- `tests/test_determinism.py` — same-process reproducibility, global random state
  untouched, string vs. integer seeds, an omitted seed still reproducible, provenance
  fields.
- `tests/test_cross_process.py` — tier B specifically: independent `subprocess`-spawned
  interpreters (not repeated in-process calls) produce an identical canonical signature
  of voice/midi/offset/duration/role for a fixed request, and an identical resolved
  auto-seed/fingerprint for an omitted seed. This is a genuinely different process, not a
  relabelled same-process test, and it is *not* a cross-machine or cross-Python-version
  test — see tier C above for why that distinction matters.
- `tests/test_canonical.py` — `canonical()` in isolation: every collision named in this
  document (float/string, bytes/string, mapping-key, set/list) reproduced and closed,
  plus the documented equivalences (list/tuple, `-0.0`/`0.0`) and the documented
  non-equivalences (bool/int).
- `tests/test_seed_wire_contract.py` — the JS-safety property above, end to end through
  the real API.
- `tests/test_budgets.py`, `tests/test_ficta.py`, `tests/test_intent.py`,
  `tests/test_heretical_grammar.py`, `tests/test_relaxation.py`,
  `tests/test_key_signatures.py`, `tests/test_cadence_provenance.py` — each exercises
  determinism incidentally by relying on repeatable output for their own assertions;
  a canonicalisation regression would surface as flakiness across this whole suite, not
  just in `test_determinism.py`.
- **Not tested:** tier D across two different installed `music21` versions, or across two
  different operating systems/architectures. Either would require provisioning multiple
  full environments and is out of scope for this pass; if it becomes a requirement, the
  test belongs alongside `requirements.lock.txt` and should pin every environment
  explicitly rather than relying on whatever happens to be installed.
- **Not implemented:** an engine-owned PRNG that would extend tier B into tier C (see
  tier C above). Recorded as future work, not attempted here.

## `ENGINE_VERSION` as a determinism boundary

`ENGINE_VERSION` (`kircher_engine.py`) is bumped whenever a change alters the notes
produced for an unchanged request — including changes to *how* a seed is derived, not
just changes to musical logic. This has already happened twice for exactly that reason,
not for any musical one: `1.0.0` → `1.1.0` introduced `canonical()` in place of `repr()`;
`1.1.0` → `1.2.0` then fixed type collisions *within* `canonical()` itself (a float and
the string of its own digits used to hash identically), which moved every derived seed a
second time. Neither bump changed a single rule, mode, or cadence. A client that wants
long-term reproducibility across engine upgrades should pin `engine_version` in its own
records alongside `seed` and `config_fingerprint`.
