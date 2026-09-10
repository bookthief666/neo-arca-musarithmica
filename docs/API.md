# API.md — The Phase 1 Ghost's public contract

This documents the actual, current wire contract of the FastAPI service (`main.py` /
`models.py`), as of `ENGINE_VERSION` `1.3.0`. It is a contract document, not a tutorial:
every field, default, and error code below is what the code does today, not an aspiration.

**Scope note.** Everything here describes **NEO-ARCA** — the constraint-search engine
that is Phase 1's entire generative path. There is no historical **ARCA HISTORICA** table
lookup engine yet (see `docs/PHASE1_ACCEPTANCE.md`); nothing in this API references
transcribed primary-source data, and nothing here should be read as a historical claim.
Where the Orthodox/Heretical grammar extends beyond what the historical record
documents, that is marked N1 (Neo-Arca extension) elsewhere (`docs/PROVENANCE.md`).

## Endpoints

### `GET /health`

No parameters. Returns `HealthResponse`:

| Field | Meaning |
| --- | --- |
| `status` | Always `"ok"` if the process answers at all. |
| `engine` | `"neo-arca-musarithmica"`. |
| `version` | `ENGINE_VERSION` — see "Determinism and versioning" below. |
| `modes` | The seven supported modern modes (not the historical eight church tones). |
| `meters` | Every meter `POST /compose` accepts. |
| `law_profiles` | `["hereticus", "orthodox"]` (sorted). |
| `tonics` | The tonics the engine will choose **on its own** when a request omits `tonic` and lets the semantics decide — a curated, easily-notated subset (`theory.CANDIDATE_TONICS`). A request may still *ask* for any note name `normalize_note_name` accepts (below); this list is only the engine's own default choices. |
| `max_measures` | `64`, the same ceiling `ComposeRequest.measures` enforces. |

### `POST /compose`

Request body: `ComposeRequest` (below). Response body: `ComposeResponse` (below), on
success (`200`). See "Error taxonomy" for every non-200 outcome.

## Request fields (`ComposeRequest`)

Only `text` is required. Every other field either overrides what the Polygraphia
semantic stage would otherwise infer from `text`, or bounds the composition's shape.
Leave a field `null`/omitted to let the semantics decide it — see "Semantic derivation
vs explicit override" below for exactly which fields this applies to and how a consumer
can tell which happened.

| Field | Type | Bounds | Default when omitted |
| --- | --- | --- | --- |
| `text` | string | 1–600 characters, not all-whitespace | — (required) |
| `seed` | int \| string \| null | see "Seed grammar and replay semantics" | derived from the rest of the request |
| `mode` | string \| null | one of the seven modes, ≤32 chars, case-insensitive | from semantics |
| `tonic` | string \| null | a parseable note name (below), ≤16 chars | from semantics |
| `tempo` | int \| null | 30–240 (BPM) | from semantics |
| `measures` | int | 1–64 | `8` |
| `meter` | string \| null | one of the six supported meters, ≤16 chars | from semantics |
| `phrase_measures` | int \| null | 1–16 | from semantics |
| `density` | float \| null | 0.0–1.0, must be finite (NaN/Infinity rejected) | from semantics |
| `heretical` | bool \| null | — | from semantics |

Unknown top-level fields are rejected (`extra="forbid"`), not silently ignored.

**Note-name grammar** (`tonic`): a letter `A`–`G` (case-insensitive) followed by an
optional accidental — `#`, `##`/`x` (double sharp), `b`, `bb`/`--` (double flat), `-`
(single flat), or the literal word `natural`. `♯`/`♭` Unicode accidentals are accepted
and normalised. Anything else is a `422`.

**Pydantic coercion notes worth knowing, not defects:** `heretical` uses Pydantic v2's
lax boolean parsing, so `"yes"`, `"true"`, `"1"`, `"on"` (and their negations) are
accepted as well as a literal JSON boolean — a client should still only ever *send* a
real boolean. `seed: true`/`seed: false` is explicitly rejected (a custom validator runs
before Pydantic's own coercion, because a bare `int` field would otherwise silently widen
`True` to `1`).

## Seed grammar and replay semantics

`provenance.seed` (see below) is always a **decimal string**, not a JSON number — a
resolved seed is drawn from the full 64-bit space, and JavaScript's `Number` type only
represents integers exactly up to `2**53 - 1`. The request's `seed` field accepts:

1. **An integer.** Used directly (masked into the uint64 seed space).
2. **An unsigned decimal-digit string** (`"418"`, and `provenance.seed` always is one).
   Parsed as that same integer and resolves *exactly as if the equivalent integer had
   been sent* — `seed: 418` and `seed: "418"` are deliberately equivalent inputs, which
   is what makes a returned `provenance.seed` string exactly replayable by resubmitting
   it unchanged. Leading zeros are permitted and insignificant (`"007"` == `"7"`).
3. **Any other string** (`"musurgia universalis"`, a signed form like `"-5"`/`"+5"`,
   `""`) — resolved through stable hashing as a textual seed, not parsed as a number.
4. **Omitted / `null`** — derived from the rest of the (normalised) request, so an
   omitted seed is still reproducible for an identical request.

A string `seed` is capped at 128 characters (`MAX_SEED_STRING_LENGTH` in `models.py`),
enforced before any parsing is attempted. A real replay seed is a decimal string for a
uint64 value — at most 20 digits — so 128 is deliberately generous headroom, not a tight
fit; a longer string is rejected with a `422` rather than reaching Python's own
integer-string conversion limit (`sys.get_int_max_str_digits()`, 4300 by default)
uncontrolled. See `docs/DETERMINISM.md`, "Seed wire format", for the full history of this
contract (B8.1 made the seed JS-safe; B8.2 made it actually replayable; B10 closed the
oversized-input gap B9's stress matrix found).

`provenance.requested_seed` echoes what the request sent, also as a decimal string when
numeric — so an integer `418` and the string `"418"` are indistinguishable there too,
by design, since they are defined as the same input. Only a genuinely textual seed
remains distinguishable in `requested_seed`; an omitted seed is reported as `null`.

## Semantic derivation vs explicit override

Every request runs through the Polygraphia semantic stage (`semantics.py`) regardless of
what it explicitly sets — `text` always gets analysed. The response exposes **both**
what the text suggested and what was actually used, in two different places:

* `semantics.suggestion.*` — what the lexicon/axis analysis of `text` alone recommends.
  Never touched by an explicit override.
* `configuration.*` — what the composition actually used: the override when the request
  gave one for that field (`mode`, `tonic`, `tempo`, `meter`, `phrase_measures`,
  `density`, `heretical`), otherwise the same value as `semantics.suggestion`.

When a request supplies no overrides at all, `configuration.*` and
`semantics.suggestion.*` agree field-for-field (this is itself regression-tested — see
`tests/test_api.py::test_unspecified_parameters_come_from_the_semantics`). When they
diverge, that divergence *is* the override taking effect, and is the mechanism a
consumer should use to show "here's what your words gave us" alongside "here's the
knob you turned instead."

Determinism: identical `text` always produces an identical `semantics` analysis (no
randomness anywhere in the semantic stage) — see `docs/DETERMINISM.md`, tier A/B.

## The seven modern modes, and the two law profiles

`ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian` — the modern
diatonic modes, **not** Kircher's historical eight church tones (a deliberate N1
extension; see `docs/PROVENANCE.md`). `GET /health` echoes this list rather than
duplicating it here so it can never silently drift out of sync with the code.

**ORTHODOX** (`law_profile: "orthodox"`) is species-counterpoint-inspired SATB law:
parallel fifths/octaves, voice crossing, tritone sonorities, unresolved leading tones and
similar are error-severity and refused. **MODUS HAERETICUS** (`law_profile: "hereticus"`)
is the *same* rule set, re-weighted: what Orthodox law forbids, Heretical law licenses
(and in some cases requires — every Heretical phrase must expose a sounding tritone
somewhere in it). Neither profile is a disabled checker; a Heretical composition can
still be validated against Orthodox law, and every transgression in it is classified
(see "Validation diagnostics" below) rather than merely absent from a weaker check.

Select the profile with `heretical: true/false`, or omit it to let the semantics decide
from the text (a lexicon match on words like "forbidden", "heresy", "abyss" nudges
toward Heretical).

## Meters

`4/4, 2/2, 3/4, 2/4, 3/2, 6/8` (`rhythm.SUPPORTED_METERS`). An unsupported meter is a
`422` (`invalid_meter`), naming the accepted set.

## Response structure (`ComposeResponse`)

| Top-level section | Contents |
| --- | --- |
| `engine` | Name, `ENGINE_VERSION`, active law profile and its human-readable title. |
| `provenance` | Everything needed to reconstruct or replay this exact composition — see below. |
| `configuration` | The fully-resolved `GenesisConfig` actually used (see "Semantic derivation vs explicit override"). |
| `semantics` | The full Polygraphia analysis of `text` — tokens, matched lexicon terms, the ten continuous axes, mode-affinity scores, and the raw suggestion. |
| `score` | Everything about the composed music: tonic/mode/tempo/meter, key signature, musica ficta pitch classes, the harmonic progression and phrase/cadence structure, and all four voice lines with their events. |
| `validation` | The rule-violation report — see "Validation diagnostics". |
| `search` | Solver/repair diagnostics — see "Search diagnostics". |
| `midi_base64` | The complete four-part composition as a Base64 Standard MIDI File, one track per voice. |

### Voice events (`score.voices[].events[]`)

Each of the four voices (`soprano, alto, tenor, bass`) carries an ordered, gapless list
of `NoteEventModel` entries. All quarter-length-based time fields are in **quarter
notes** (`ql`), not seconds or ticks — multiply by `60 / tempo` to get seconds, or use
`score.duration_seconds` for the whole piece (already computed that way).

| Field | Meaning |
| --- | --- |
| `pitch` | Spelled pitch, e.g. `"Eb4"` — mode-aware spelling, not defaulted to sharps. |
| `midi` | `0`–`127`. |
| `offset` | Onset in quarter-lengths from the start of the piece. |
| `duration` | **Notated** length in quarter-lengths — this is what the exported MIDI carries. |
| `sounding_duration` | Length after the articulation gate (`0 < sounding_duration <= duration`) — a Tone.js consumer should schedule *this*, not `duration`, for how long a note actually sounds; the notated duration is what makes the notation (and the tie-over-the-barline for a suspension) correct. |
| `velocity` | `0`–`127`. |
| `role` | `structural \| passing \| neighbour \| suspension \| anticipation \| escape \| chromatic \| displaced`. Anything other than `structural` is a rhythmic-surface ornament and is allowed to be momentarily dissonant in the contexts the rules describe. |
| `slot` | Index into `score.slots` — the harmonic slot this note belongs to. |
| `measure` | 0-indexed measure number. |

Within one voice, events are strictly ordered and gapless: each event's `offset` equals
the running sum of every earlier event's `duration` in that voice, and the last event's
`offset + duration` equals `score.total_quarter_length` exactly — regression-tested in
`tests/test_api.py::test_events_are_ordered_gapless_and_cover_the_whole_piece` and
`test_every_event_is_finite_bounded_and_never_exceeds_the_composition`. `midi_base64`
describes the identical composition note-for-note (`tests/test_midi.py`).

### Validation diagnostics (`validation`)

`validation.passed` is `true` exactly when no violation is classified `defect` — see
`intent` below; a licensed transgression never fails a composition, and (see "Error
taxonomy") a composition that *would* fail is never returned at all; the request fails
with a structured error instead.

Each `violations[]` entry (`RuleViolationModel`) carries:

* `rule` — a stable string id (e.g. `parallel_fifth`, `voice_crossing`, `tritone_sonority`).
* `severity` — graded under **Orthodox** law always, so severities are comparable
  between profiles regardless of which one actually generated the music.
* `licensed` — true when the *active* profile permits this rule class (a parallel fifth
  is licensed under Heretical law, not under Orthodox).
* `intent` — how this occurrence arose, the axis that actually matters for telling
  transgression from defect:
  * `deliberate` — the generator recorded an explicit decision that produces this (a
    chromatic ornament, a tritone stab, an alien triad, a Heretical cadence).
  * `emergent` — licensed by the active law, but nothing specifically sought this
    occurrence; it emerged from the search.
  * `defect` — error-severity **and not licensed** by the active law: an implementation
    fault. This is the only category `validation.passed`/`defect_count` react to.
  * `incidental` — an ordinary stylistic observation, neither sought nor faulty.
* `reason` — the recorded decision that explains a `deliberate` violation (e.g.
  `"chromatic_ornament"`, `"heretical_cadence"`), `null` otherwise.

### Search diagnostics (`search`)

Everything the bounded voicing search did: `nodes_visited`, `backtracks`,
`candidate_sets_built`, `lenient_enumerations` (slots whose strict pass came back empty
and needed the lenient fallback — sharing that slot's own node budget, not a fresh one),
`node_budget_hits`, `relaxation_level` (`0` is full strictness; the returned music is
still guaranteed defect-free regardless — see "Error taxonomy"), `repair_passes`,
`repair_exhausted`, `ornaments_applied`/`reverted`, and `elapsed_ms`.

### Key-signature fields (`score.key_signature_*`)

* `key_signature_sharps` — signed circle-of-fifths position of the final **as spelled**
  (positive = sharps, negative = flats); C# and Db differ (7 sharps vs. 5 flats) because
  this is derived from spelling, not from the sounding pitch class. May exceed ±7.
* `key_signature_notatable` — the same signature wrapped into what a staff/MIDI file can
  actually express (±7); equal to `key_signature_sharps` unless that exceeds the range.
* `key_signature_is_notatable` — `false` exactly when wrapping happened.

### Cadence provenance fields (`score.phrases[].cadence_provenance`, `.cadence_note`)

How much historical authority a phrase's cadence formula carries: `H1` (period practice,
implemented approximately), `N1` (a Neo-Arca construction with no direct historical
claim), or `HAERETIC` (a declared transgression). These are chord-pair cadences, not the
contrapuntal *clausulae* that historically define a cadence — see `docs/PROVENANCE.md`
section 3 for the full caveat. `cadence_note` states what that specific formula does and
does not claim.

## Error taxonomy

Every failure path returns the same envelope — `ErrorResponse`:

```json
{"error": "<stable machine-readable code>", "message": "<human-readable>", "diagnostics": {}}
```

| HTTP | `error` | Raised for | Client can retry by |
| --- | --- | --- | --- |
| `422` | `invalid_request` | Any Pydantic request-validation failure (bad type, out of range, unknown field, NaN/Infinity, oversized string, ...). `diagnostics.errors` carries Pydantic's own error list. | Fixing the named field. |
| `422` | `invalid_musical_input` | A `TheoryError` — an unparseable note name. | Sending a valid note name. |
| `422` | `invalid_meter` | A `MeterError` — an unsupported meter symbol reached the engine. | Sending a supported meter. |
| `422` | `unrealizable_request` | `GenerationError` with `kind="search_exhausted"` — the bounded voicing search ran out of budget at every relaxation level for *this* combination of parameters. Not an engine fault. | Changing the seed, density, mode, meter, or measure count. |
| `500` | `generation_defect` | `GenerationError` with `kind="defect_found"` — a relaxed search returned a composition containing an error-severity violation the active law does not license. The engine's own contract (`validation.passed` implies no defect) failed internally. | Nothing the client can do; retrying the identical request will not help. |
| `500` | `midi_export_failed` | `MidiExportError` — MIDI serialisation itself failed after a valid composition was produced. | Nothing the client can do. |
| `500` | `internal_error` | Anything not one of the above — a genuinely unanticipated exception, logged server-side with a full traceback and never echoed to the client. | Nothing the client can do; this is a bug report. |

**Why `search_exhausted` is `422` and `defect_found` stays `500`:** the first is a
property of *this request* — a different seed/density/mode/measure count can succeed
where this one didn't, so the client can usefully act on it. The second is an
implementation fault in the engine's own repair/relaxation logic; retrying the identical
request cannot fix it. This distinction was made explicit in B10 after review found the
previous single `generation_failed` → `500` mapping conflated the two (see
`kircher_engine.GENERATION_ERROR_KINDS`).

No response body ever contains a raw Python traceback, an unserialised exception object,
or a non-finite float (`NaN`/`Infinity` are sanitised to their string form before any
diagnostics payload is rendered) — `main.py::_json_safe`.

## Determinism

See `docs/DETERMINISM.md` for the complete, tiered contract (same-process vs.
fresh-process vs. cross-Python-version vs. byte-identical-MIDI guarantees) and
`provenance.runtime` for the Python/music21 versions a given response was produced on.
In summary: identical `(text, seed, mode, tonic, tempo, meter, measures,
phrase_measures, density, heretical)` and unchanged `engine_version` reproduce an
identical composition within the same Python runtime (tiers A/B, both tested); cross
Python-version/implementation reproduction is explicitly **not** guaranteed or tested
(tier C); byte-identical MIDI is scoped further still to one locked dependency set and
OS/architecture (tier D, `requirements.lock.txt`).

`ENGINE_VERSION` is bumped whenever a change alters the notes produced for an unchanged
request, including changes to *how* a seed is derived — not only musical-rule changes.
See `docs/DETERMINISM.md`, "`ENGINE_VERSION` as a determinism boundary", for the full
history of what has moved it and why.

## Concurrency

`POST /compose` is a synchronous handler FastAPI runs on its worker threadpool, so
concurrent requests genuinely execute `KircherEngine.compose(...)` on different threads
of the same process. This is safe: the shared `ENGINE` instance holds no per-request
mutable state, all randomness goes through a per-request `determinism.SeedStream`
(never the global `random` module), and MIDI export writes through a collision-proof
unique temp file. See `tests/test_concurrency.py` for the executable verification and
its module docstring for the full audit trail.
