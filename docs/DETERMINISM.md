# DETERMINISM.md — What the engine actually guarantees

Determinism is a first-class requirement (project brief §XVIII / §8), but "deterministic"
is not one guarantee, it is several, of different strength and different scope. This
document states them precisely so the API and the tests can be held to something concrete
rather than the word alone.

## The three claims, and where each one stops

### 1. Same composition, same process — GUARANTEED, always

For identical `(text, seed, mode, tonic, tempo, meter, measures, phrase_measures,
density, heretical)` and unchanged `ENGINE_VERSION`, two calls to `KircherEngine.compose`
in the same process produce identical `NoteEvent` sequences for every voice — same
pitches, same offsets, same durations, same velocities, same roles.

This follows from two things the code enforces, not just intends:

- **No global randomness.** `random.seed` / `random.random` are never touched anywhere in
  the engine; every stochastic decision draws from an explicit, labelled
  `determinism.SeedStream`. `tests/test_determinism.py::test_composition_does_not_touch_the_global_random_state`
  asserts `random.getstate()` is bit-for-bit unchanged after a `compose()` call.
- **Canonical seed derivation.** `SeedStream.derive` is a pure function of
  `(root_seed, label_path)`. Sibling streams are independent regardless of the order they
  are created in, so adding a new decision point in one stage cannot perturb a seed
  already derived in another.

### 2. Same composition, any process, any machine — GUARANTEED, given canonical hashing

The same request must choose the same notes on a different machine, a different day, a
freshly started interpreter. This is *not* automatic — it depends on how the seed and the
config fingerprint are derived from the request, and that derivation used to depend on
`repr()`:

- `repr(SomeEnum.MEMBER)` embeds the class name and Python's own enum formatting, both of
  which have changed across interpreter versions (PEP 663, and earlier changes to
  `Enum.__repr__` and `Enum.__str__`).
- `repr({"a": 1, "b": 2})` differs from `repr({"b": 2, "a": 1})`, so two semantically equal
  configurations built via different code paths could fingerprint differently purely from
  dict insertion order.
- Float `repr` in CPython is stable today but is not a language-level guarantee.

`determinism.canonical()` replaces every `repr()`-based hash input: mappings are emitted
with sorted keys, sets are sorted, enums reduce to their `.value` (the semantic content;
the class name is an implementation detail), floats are written at 17 significant digits
(enough to round-trip any IEEE double exactly, with `-0.0` normalised to `0.0`), and any
type with no defined canonical form raises `CanonicalisationError` rather than silently
falling back to `repr`. `stable_hash()` and `fingerprint()` both canonicalise their
input, so the seed a request resolves to, and the config fingerprint that names it, no
longer depend on interpreter version, dict construction order, or `Enum.__repr__`.

**This guarantee covers "the same pitches, offsets, durations, roles" — the musical
content.** It does not cover the exact bytes of the serialized MIDI file; that is claim 3.

### 3. Byte-identical MIDI file — SCOPED, not universal

`models.ProvenanceModel` (returned as `provenance` in every `/compose` response) carries a
`runtime` block
(`{python, music21, implementation}`) precisely because this claim is the one that is
*not* unconditional. `music21`'s `score.write('midi', ...)` decides tick resolution,
event ordering within a simultaneity, and meta-event emission; a different `music21`
version is free to change any of that while still producing musically correct output.

**The contract:** byte-identical MIDI is guaranteed only within one locked dependency set
— see `requirements.lock.txt`. It is explicitly **not** promised "across arbitrary
Python/music21 versions" (the brief's own wording), because that has not been tested and
nothing here can make that promise responsibly without testing it.

`runtime_versions()` is deliberately **not** hashed into the seed. The same request
choosing different notes depending on which machine served it would be a genuine defect;
the same request producing a MIDI file with a different tick count on `music21==9.1` vs.
`music21==10.5` is not — it is exactly what claim 3's scoping predicts, and is why the
runtime is reported *alongside* the seed rather than folded into it.

## Practical guidance for a consumer

| You want to know | Compare |
| --- | --- |
| "Will this request always produce the same music?" | `seed`, `config_fingerprint`, `engine_version` — if all three match, yes (claim 1/2) |
| "Will this request always produce the same MIDI bytes?" | The above, **plus** `provenance.runtime` — only guaranteed if all of it matches (claim 3) |
| "Did the semantic mapping resolve to a different seed than I expected?" | `provenance.requested_seed` (what you sent) vs. `provenance.seed` (what was resolved) |

## What is regression-tested

- `tests/test_determinism.py` — same-process and cross-process reproducibility, global
  random state untouched, string vs. integer seeds, an omitted seed still reproducible,
  provenance fields.
- `tests/test_budgets.py`, `tests/test_ficta.py`, `tests/test_intent.py`,
  `tests/test_heretical_grammar.py`, `tests/test_relaxation.py`,
  `tests/test_key_signatures.py`, `tests/test_cadence_provenance.py` — each exercises
  determinism incidentally by relying on repeatable output for their own assertions;
  a canonicalisation regression would surface as flakiness across this whole suite, not
  just in `test_determinism.py`.
- **Not tested:** claim 3 across two different installed `music21` versions. This would
  require provisioning two full environments and is out of scope for this pass; if it
  becomes a requirement, the test belongs alongside `requirements.lock.txt` and should
  pin both environments explicitly rather than relying on whatever happens to be
  installed.

## `ENGINE_VERSION` as a determinism boundary

`ENGINE_VERSION` (`kircher_engine.py`) is bumped whenever a change alters the notes
produced for an unchanged request — including changes to *how* a seed is derived, not
just changes to musical logic. The canonicalisation change in this file's own history
(`1.0.0` → `1.1.0`) is the reference example: no rule, mode, or cadence changed, but every
derived seed did, because the hash of the request itself changed. A client that wants
long-term reproducibility across engine upgrades should pin `engine_version` in its own
records alongside `seed` and `config_fingerprint`.
