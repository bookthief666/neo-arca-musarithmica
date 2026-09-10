# PHASE1_ACCEPTANCE.md — Release-candidate snapshot

**As of:** `ENGINE_VERSION` `1.3.0`, branch `feature/m0-history-phase1-hardening`, after
B1–B10.

This is a concise, honest grading of what Phase 1 ("THE GHOST" — the Python composition
backend) actually delivers against the original project brief, for whoever picks this up
next: a future session, a reviewer, or the frontend work that follows. Grades are
`COMPLETE`, `PARTIAL`, or `DEFERRED` — never inflated, and a `PARTIAL`/`DEFERRED` names
exactly what is missing rather than gesturing at it.

## Grading

| Area | Grade | Notes |
| --- | --- | --- |
| Four-part SATB generation | **COMPLETE** | `KircherEngine.compose` always returns four independently addressable voices (soprano/alto/tenor/bass) with complete event lists; regression-tested (`tests/test_api.py`, `tests/test_midi.py`) and independently re-verified at scale (B9/B10 stress evidence below: 906/906 and repeated Orthodox invariant checks, zero voice-count or range violations). |
| Orthodox law (LEX MUSICA) | **COMPLETE** | A genuine constraint-search solver (`kircher_engine.VoicingSolver`) with incremental pruning, bounded backtracking, three relaxation levels behind an explicit budget, and a public contract that a *returned* composition never contains a `defect`-classified violation (enforced by `GenerationError`, not merely documented). This is a species-counterpoint-**inspired** four-part grammar, explicitly **not** a complete implementation of Fux, Palestrina, or 18th-century harmony (`README.md`, "Scope") — a defensible modern subset, not a historical transcription. |
| Modus Haereticus (heretical grammar) | **COMPLETE** | The same rule set, re-judged: Orthodox-forbidden rule classes are licensed and weighted oppositely under the Heretical profile, every Heretical phrase is required to expose a sounding tritone (`RulePolicy.requires_phrase_tritone`), and every violation is classified `deliberate`/`emergent`/`defect`/`incidental` (`constraints.Intent`) so transgression is never confused with implementation fault. This classification, and the invariant itself, are **N1** — a Neo-Arca extension with no direct historical claim (see `docs/PROVENANCE.md`); nothing here asserts Kircher's Arca had an equivalent. |
| Polygraphia semantics | **COMPLETE** for the modern-language free-text mapping this project actually builds; **N1**, not a reconstruction of Kircher's own *Polygraphia* combinatorial-language system, which is a different (and, per `docs/UNCERTAINTIES.md`, largely un-researched from this environment) apparatus. Ten continuous axes, a weighted lexicon, deterministic mode/tonic/tempo/density/instrumentation suggestion, negation/intensifier handling, and a documented stable-hash fallback when nothing matches. |
| Seven modern modes | **COMPLETE** | `ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian` — explicitly the **modern diatonic modes**, not Kircher's eight historical church tones (an unresolved count itself — see `docs/UNCERTAINTIES.md` §2, "twelve *toni*... not counted in the primary text by us"). Labelled as such in `docs/API.md` so no consumer mistakes one for the other. |
| Determinism | **COMPLETE for tiers A/B** (same-process and fresh-process reproducibility, both genuinely tested — `tests/test_determinism.py`, `tests/test_cross_process.py` via real `subprocess` spawns) and for the wire/replay contract (a resolved seed read back from a response resubmits to the identical composition — `tests/test_seed_replay.py`). **Explicitly NOT GUARANTEED, and not tested**, across different Python versions/implementations (tier C) or across untested OS/architecture/dependency combinations for byte-identical MIDI (tier D beyond one locked environment) — see `docs/DETERMINISM.md` for the full tiered contract and exactly why each boundary is where it is. |
| Event JSON contract | **COMPLETE** | Ordered, gapless, finite, range-bounded events per voice; `sounding_duration` vs notated `duration` distinguished; no event extends past the composition's own duration; internally consistent with MIDI note-for-note (`tests/test_midi.py::test_the_midi_describes_the_same_composition_as_the_json`, `tests/test_api.py::test_every_event_is_finite_bounded_and_never_exceeds_the_composition`). |
| MIDI export | **COMPLETE** | Valid Standard MIDI File, four distinct named/instrumented tracks plus a conductor track, round-trips through `music21` note-for-note, ties held notes correctly over barlines, collision-proof temp-file handling verified under concurrency (`tests/test_concurrency.py`), no leftover temp files even on a failed write. |
| API (HTTP contract) | **COMPLETE** | Two endpoints, a single consistent `{error, message, diagnostics}` error envelope across every failure path (Pydantic validation, theory/meter errors, generation errors, MIDI export errors, and a catch-all for anything unanticipated), a defensible error taxonomy that distinguishes a retryable unrealizable request (`422`) from a genuine internal fault (`500`), and an adversarial-input sweep (oversized/malformed fields, NaN/Infinity, oversized seed strings) with zero unhandled exceptions as of B10. See `docs/API.md`. |
| Diagnostics (validation + search) | **COMPLETE** | `intent`/`licensed`/`defect` classification on every rule violation; full solver/repair telemetry (nodes visited, backtracks, relaxation level, repair passes/exhaustion) reported per composition, not just aggregated. |
| Voice ranges | **COMPLETE** | Fixed per-voice ranges (`theory.py`), shiftable by register bias, enforced both by the solver's own pruning and independently re-verified from the raw event JSON rather than trusting the production validator a second time (`scripts/stress_matrix.py`'s independent invariant checks; `tests/conftest.py`'s checkers). |
| Bounded search | **COMPLETE** | Every loop carries an explicit, configurable `SearchBudget`; budget exhaustion is itself a reported, tested condition (`tests/test_budgets.py`) rather than an unbounded hang. |
| Testing / stress evidence | **COMPLETE** | 524 pytest tests passing as of B10 (see the B10 final-verification numbers below); a checked-in, reproducible stress-matrix instrument (`scripts/stress_matrix.py`) with a versioned FULL-profile report as release evidence — not merely an uncommitted historical claim. |
| **ARCA HISTORICA (historical table-lookup engine)** | **DEFERRED — NOT STARTED, NOT SIMULATED** | See below. This is the one item on this list that is not a grading nuance; it does not exist in any form. |

## ARCA HISTORICA: explicitly not complete

**No historical primary tables have been transcribed.** `docs/UNCERTAINTIES.md` §2 is
explicit: *"The tables themselves. We hold none of the actual numbers. This is the
blocking gap for ARCA HISTORICA."* Every composition this codebase can currently produce
comes from **NEO-ARCA** — a constraint-search engine (`kircher_engine.py`) that shares
only a name and a spirit with Kircher's combinatorial procedure, not his actual pinax/rod
data. There is no `historical_engine.py`, no `arca_data.py`, no table-driven generation
path, and none is simulated or faked to look like one. Building ARCA HISTORICA without
genuine transcribed source data would mean inventing Kircher's numbers, which this
project has deliberately refused to do at every prior stage (`docs/UNCERTAINTIES.md`,
`docs/HISTORICAL_RESEARCH.md`) and refuses here too.

## Historical/visual research status

`docs/VISUAL_RECONSTRUCTION.md` and `docs/UNCERTAINTIES.md` both open with the same
governing limitation and it still holds: **this project's research sessions ran from an
environment that blocked image and page fetches** from archive.org, Wikipedia,
arca1650.info, andrewcashner.com, Zenodo, and every museum/scan repository attempted.
Nothing about the object's actual physical appearance, dimensions, materials, or
construction — and nothing about the actual content of Kircher's tables — has been
**observed**; what exists is secondary-source *description*, honestly labelled H0/H1/N1
throughout, with every open question recorded rather than invented shut.

Consequently: **primary-source visual archaeology — actually inspecting the 1650
engraving and surviving physical cabinets — is required before any digital
reconstruction of the Arca's appearance is built**, and has not yet happened in this
project's history.

## Final verification numbers (B10)

* **pytest:** 524 passed, 0 failed.
* **SMOKE stress profile:** see the B10 commit's reported numbers (a fast, representative
  coverage sweep across every mode/meter/profile/length/seed/density/tension/config-path
  dimension).
* **FULL stress profile:** see the B10 commit's reported numbers and
  `artifacts/stress/stress-engine-1.3.0-b10.json` — the corrected-schema report
  (B9's original `artifacts/stress/stress-engine-1.3.0.json` is kept as historical
  evidence of the pre-B10 schema, not overwritten).
* **Concurrency:** verified under genuine multi-threaded load (`tests/test_concurrency.py`)
  after an explicit shared-mutable-state audit found none requiring a lock.
* **Adversarial input sweep:** oversized/malformed fields, NaN/Infinity, and the specific
  >4300-digit seed-string defect B9 found are all now clean `422`s, never an unhandled
  `500` — `tests/test_seed_boundary.py`, `tests/test_api_hardening.py`.

## GO / NO-GO

See the B10 commit message / final report for the explicit GO/NO-GO matrix
(`PHASE-1 GHOST BACKEND`, `API CONTRACT`, `DETERMINISM`, `SATB/ORTHODOX`,
`MODUS HAERETICUS`, `STRESS EVIDENCE`, and the two readiness questions about
primary-source visual archaeology and frontend sequencing). The backend being
release-ready does **not** imply the frontend may begin before that archaeology —
those are independent questions, and the second one is answered `NO` regardless of how
the first six are graded.
