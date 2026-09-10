# HISTORICAL_VERTICAL_SLICE.md — First Digital Arca Implementation Contract

**Status:** implementation specification derived from M0.1 archaeology.  
**Authority:** `docs/M0_1_PRIMARY_ARCA_RECONSTRUCTION.md` + `docs/RESEARCH_STATUS.md`.  
**Backend authority:** Phase-1 Ghost frozen at B10 (`8869e2738d2b31f2682a5b1d30913baa6a8a12e2`, engine 1.3.0).  
**Purpose:** define the smallest frontend slice that proves the Arca itself can function as the interface without falsely presenting the existing Neo-Arca solver as Kircher's historical table engine.

---

## 1. Product test

The slice succeeds only if a first-time user can perceive all of the following without being shown a conventional dashboard:

1. **This is a small, openable seventeenth-century scholarly box.**
2. **Its stored slats/tables are the program.**
3. **A slat can be physically retrieved and worked with.**
4. **The lid and front reference surfaces participate in the computation.**
5. **Four voices are produced by operating the object.**
6. **The object has acquired impossible modern computational behavior without ceasing to be recognisably Kircher's Arca.**
7. **Historical evidence and Neo-Arca invention remain visibly distinguishable.**

If the same experience could be reproduced by replacing the box with cards, tabs, dropdowns and a `Generate` button, the slice has failed.

---

## 2. Scope — exactly one complete interaction path

The first slice does **not** build the full cabinet corpus.

It builds one coherent path around a single Syntagma I / Pinax-IV-shaped working slat:

```text
CLOSED / RESTING ARCA
    ↓ OPEN
OPEN ARCA
    ↓ INSCRIBE TEXT
TEXT PREPARED
    ↓ SELECT / REVEAL SYNTAGMA I
SYNTAGMA I BANK ACTIVE
    ↓ RETRIEVE ONE PINAX
PINAX IN HAND
    ↓ PLACE ON WORK SURFACE
PINAX WORKING
    ↓ CHOOSE STROPHA / COLUMN
COLUMN FOCUSED
    ↓ CHOOSE MUSARITHM / FOUR-VOICE NUMBER ROW
VPERM CHOSEN
    ↓ CHOOSE NOTAE TEMPORIS / RHYTHM
RPERM CHOSEN
    ↓ CONSULT LID TONAL SURFACE
TONAL RESOLUTION
    ↓ CONSULT FRONT STAFF / RANGE SURFACE
VOICE REGISTER RESOLUTION
    ↓ COMMIT
NEO-ARCA COMPOSE REQUEST
    ↓ RESPONSE
FOUR VOICES MANIFEST THROUGH THE SAME PHYSICAL SURFACES
    ↓ PLAY / STOP / REPLAY / EXPORT MIDI
```

The interaction path is historically structured, while the actual live composition remains N1 until project-owned historical table data exists.

---

## 3. Reconstruction mode and provenance mode

The slice must distinguish two kinds of pinax content.

### `FACSIMILE_REFERENCE`

A public-domain historical table can be inspected as a historical document. It is **not** connected to the current Neo-Arca generation call unless its data has been independently transcribed and implemented.

Visual marking may be subtle, but metadata must identify:

- source work;
- volume/book/page or folio;
- image/source institution;
- H0-V/H0-T status;
- whether the table is computationally active.

### `NEO_WORKING_PINAX`

Uses the **historical anatomy** of a pinax — title, strophe divisions, four-voice rows, lower rhythm field — but its live numbers/marks represent the Neo-Arca engine's current state rather than Kircher's 1650 dataset.

It must carry an explicit N1 provenance state internally and in an inspectable UI surface.

**Hard rule:** never render a real Kircher numeric row and then send unrelated Neo-Arca parameters while implying that row caused the result.

---

## 4. Physical scene hierarchy

The slice may use R3F/Three.js if it materially improves physical manipulation; DOM/SVG/text layers should be used where they preserve inscription precision and accessibility better.

Recommended conceptual scene tree:

```text
ArcaScene
├── Environment / WorkTable
├── ArcaCase
│   ├── LowerBody
│   ├── Lid
│   │   └── ToneTableSurface
│   ├── InternalBank
│   │   ├── SyntagmaLabel I
│   │   ├── SyntagmaLabel II  [present but inactive/limited in slice]
│   │   ├── SyntagmaLabel III [fragmentary / sealed]
│   │   └── PinaxSlots
│   │       └── WorkingPinax
│   └── FrontReferenceSurface
│       └── ScalaMusica / RangeSurface
├── WorkSurface
│   ├── ManuscriptLeaf
│   └── PinaxPlacementZone
├── VoiceManifestation
└── Accessibility / ReducedSpatialMode
```

### Physical proportions

Use the Wolfenbüttel 23 × 14.5 cm dimensions only as a **relative scale cue for that exemplar**, not as universal Kircher dimensions. The slice should feel hand-scale / desktop-scale. Do not make it read like a standing cabinet or altar.

Exact depth, hinge geometry, wood species and joinery remain H1 reconstruction variables. Parameterise them so later object evidence can correct the model without architectural rewrite.

---

## 5. Material hierarchy

Historical body first:

- restrained aged wood;
- paper-faced / paper-like pinax surfaces;
- black/brown ink;
- ruled tables;
- staff notation;
- Latin labels where directly supported;
- minimal metal only where structurally plausible.

Neo computation emerges through:

- subtle internal illumination along active ruled cells;
- four distinct voice trajectories derived from real SATB events;
- localized phosphorescence under selected numeric/rhythm cells;
- faint impossible depth/parallax inside otherwise flat ink marks;
- controlled temporal traces during playback.

Avoid as baseline styling:

- generic black/gold occult UI;
- floating glass panels;
- neon cyberpunk frames;
- full-screen glitch;
- decorative sigils unrelated to source evidence;
- DAW piano-roll grammar.

---

## 6. The pinax interaction

The working pinax is the central interaction object.

### Resting

- visible in a bank/slot inside the Arca;
- title/identifier legible enough to distinguish it from neighboring slats;
- expanded hit region may exceed physical geometry invisibly.

### Retrieval

On pointer/touch/controller selection:

1. pinax rises slightly from its receptacle;
2. user pulls/drags it toward the work surface;
3. camera may assist but must not teleport it into a generic modal;
4. original slot remains perceptible so the object retains spatial memory.

### Inspection

When brought near:

- inscription becomes fully legible;
- reading mode suppresses accidental camera orbit;
- semantic zoom exposes table hierarchy rather than raster zoom alone;
- a provenance affordance can reveal `historical reference` vs `Neo working pinax` without becoming permanent dashboard chrome.

### Strophe/column selection

Selecting a vertical region should feel like aligning/reading a column, not choosing a radio button.

Possible treatment:

- neighboring columns dim slightly;
- selected ruled column gains shallow dimensional separation;
- title / line index remains visible;
- no floating card is necessary.

### Musarithm selection

A numeric row represents four-voice structural material.

When chosen in `NEO_WORKING_PINAX` mode:

- four row strands activate independently;
- the response should foreshadow soprano / alto / tenor / bass without inventing historical absolute pitches;
- selected state should be physically local to that row.

### Rhythm selection

For the Syntagma-I-shaped slice, the lower `Notae Temporis` region is a distinct field. Selecting rhythm should visibly bind a shared temporal pattern to the active four-voice structure.

Do not design this as a separate modern `Rhythm` dropdown.

---

## 7. Manuscript / Polygraphia surface

The accepted backend accepts arbitrary free text; historical Kircher begins from a prepared poetic text. The slice should bridge these honestly.

The user writes/enters text on a **manuscript leaf placed beside the Arca**.

This is N1 in behavior but occupies the historical operator's real input position.

Suggested flow:

- blank/partly written leaf at rest;
- user taps/approaches it;
- accessible text editor becomes active without visually replacing the leaf;
- after submission, backend `semantics` output may annotate the manuscript margins subtly;
- inferred mode/metre/profile should not instantly become generic labels; instead the corresponding physical regions of the Arca become eligible/active.

The manuscript remains visible while operating the pinax so text and computation coexist spatially.

---

## 8. Lid tone table as an active computational surface

The lid is not scenic backdrop.

For the first slice:

- reconstruct the **density and ruled-table character** of the tone-reference surface;
- allow a tonal/final focus to illuminate the relevant path through the table;
- when the Neo backend resolves `tonic` / `mode`, reflect that state on the lid;
- if no historical data cell has been transcribed, label the mapping internally as N1 rather than pretending the exact 1650 lookup occurred.

Future ARCA HISTORICA can replace the N1 adapter with source-located historical lookup data without changing the physical interaction.

---

## 9. Front Scala Musica / range surface

The front reference surface should become the physical home for the backend's SATB register/range state.

For each voice:

- map event/register state onto the appropriate staff region;
- respect `cantus/soprano`, `alto`, `tenor`, `bass` identity;
- show voice trajectories/range pressure through staff-local behavior;
- use actual backend pitches and validation information;
- never expose a detached `range slider` as the primary interaction.

During playback, the four voice traces may animate across this surface before extending into the work area.

---

## 10. Backend adapter — one-way truth boundary

The frontend may not reimplement composition rules.

Create one typed client boundary around B10's `POST /compose` contract.

Conceptually:

```ts
type ArcaComposeIntent = {
  text: string;
  seed?: string;
  mode?: Mode;
  tonic?: string;
  tempo?: number;
  meter?: Meter;
  measures?: number;
  phrase_measures?: number;
  density?: number;
  heretical?: boolean;
};
```

The response is canonical for:

- resolved configuration;
- semantic analysis;
- SATB events;
- validation diagnostics;
- search telemetry;
- provenance;
- MIDI.

The R3F/DOM scene derives visual state from that response. It must never invent parallel music state that can drift from the backend.

### Seed handling

Keep `provenance.seed` as an opaque string in JavaScript. Never cast it through `Number`. Resubmitting the exact string must reproduce the same composition, per B8.2/B10.

---

## 11. Playback contract

Tone.js is presentation only.

For the slice:

- one Tone.js voice/instrument per SATB line;
- schedule from `score.voices[].events[]`;
- use `offset` for onset and `sounding_duration` for heard duration;
- preserve deterministic replay from the same response;
- stop must release/silence all voices reliably;
- playback cursor/light should be driven from the same event schedule as the sound.

Initial timbre can be restrained and synthetic. Do not spend this milestone building a sample-library system.

---

## 12. Diagnostics become physical behavior

Use the existing accepted validation model as the source of visual transgression/strain.

Examples:

- `parallel_fifth` → two voice traces temporarily run as doubled rails;
- `voice_crossing` → traces physically intersect;
- `tritone_sonority` → six-semitone geometry opens between implicated voices;
- `leading_tone_unresolved` → trajectory remains visually unclosed;
- `defect` must never appear in a successful returned composition; if API returns a generation defect, the instrument should fail visibly but coherently.

`deliberate`, `emergent`, `incidental` and `defect` remain distinct. Heretical visual behavior should arise from real diagnostics, not a red filter or generic distortion mode.

---

## 13. Syntagma III treatment

Syntagma III should be present as **incomplete historical promise**, not as fake finished content.

For the slice:

- show a third bank/receptacle region;
- mark it as incomplete through absence, sealed positions, fragmentary labels, or missing slats;
- do not populate historically missing pinakes with invented H0 content;
- reserve future N1/HÆRETIC material behind an explicit provenance boundary.

Its incompleteness is part of the story and should feel intentional, not like unfinished UI.

---

## 14. Responsive / Fold acceptance

Primary physical QA target: Samsung Galaxy Z Fold class.

### Fold open (~884 px)

Must support:

- whole open Arca readable as an object;
- bank labels legible;
- retrieve and place pinax without losing context;
- manuscript leaf accessible;
- no horizontal page overflow;
- playback controls diegetic and reachable.

### Narrow phone (~344–400 px)

Do **not** shrink the full Arca until its tables are illegible.

Use semantic zoom:

```text
ARCA → BANK → PINAX → COLUMN → ROW → VOICE/RHYTHM CELL
```

A selected pinax may move toward the camera and occupy most of the viewport while the Arca remains visible behind it.

### Touch rules

- one-finger object manipulation should not fight camera orbit;
- reading state suppresses accidental orbit;
- hit targets >= practical touch size via invisible padding;
- drag has clear capture/release behavior;
- no action depends on hover.

---

## 15. Accessibility acceptance

Every physical operation needs a semantically equivalent non-spatial path without becoming the visual source of truth.

Required:

- keyboard navigation;
- screen-reader names for Arca, banks, pinax, columns, rows and controls;
- text equivalent for selected numeric/rhythm material;
- reduced-motion mode;
- focus visibility;
- no information encoded only by color/light;
- an accessible manuscript editor;
- playback controls with explicit state.

A DOM/SVG overlay may coexist with R3F for precise readable text. Avoid DOM bridges that simulate XR pointer actions indirectly; if XR comes later, controller rays should invoke canonical scene actions directly.

---

## 16. State machine

Keep the first implementation explicit rather than distributing interaction state across component-local booleans.

Suggested states:

```text
DORMANT
OPEN
INSCRIBING
BANK_FOCUS
PINAX_RETRIEVAL
PINAX_PLACED
COLUMN_FOCUS
VPERM_FOCUS
RPERM_FOCUS
TONAL_RESOLUTION
REGISTER_RESOLUTION
COMPOSING
REVEALED
PLAYING
ERROR
```

Canonical actions should work from touch, mouse, keyboard and later XR without separate behavioral implementations.

Important persistent state:

- text/manuscript;
- selected provenance mode;
- selected syntagma/pinax/column/row/rhythm representation;
- current compose request;
- current backend response;
- replay seed;
- playback state;
- camera/semantic-zoom state should be presentation state, not musical authority.

---

## 17. First vertical-slice test script

A successful physical test should read like this:

1. Open application on Fold.
2. See a compact closed/resting Arca on a work surface.
3. Open it.
4. Enter: `Ave maris stella` or another short text on the manuscript leaf.
5. Syntagma I bank becomes the relevant working region.
6. Pull the Pinax-IV-shaped slat out of its bank.
7. Lay it on the work surface.
8. Inspect its four-column / four-voice / lower-rhythm anatomy.
9. Select a column, a four-row structural choice, and a rhythm choice.
10. Consult/activate the lid tonal surface.
11. Observe four voice/register states on the front staff surface.
12. Commit the Neo composition request.
13. Receive four backend voices.
14. Watch those voices manifest through the same table/staff geometry.
15. Play and stop.
16. Replay with returned seed and obtain the identical music.
17. Download MIDI.
18. Toggle Heretical mode only if included in the slice and verify visual transgressions come from returned diagnostics.

At no point should the primary experience turn into a settings dashboard.

---

## 18. Milestone boundaries

### Must be complete in this slice

- project/frontend scaffold;
- typed API client;
- one evidence-based Arca shell;
- open/close state;
- manuscript input;
- Syntagma-I bank representation;
- one removable working pinax;
- semantic zoom/readability;
- column + structural row + rhythm interaction;
- lid/reference interaction;
- front staff/range manifestation;
- `/compose` integration;
- four-voice playback;
- deterministic seed replay;
- MIDI download;
- Fold-open + narrow-phone acceptance;
- provenance distinction between facsimile and N1 live data.

### Explicitly deferred

- full transcription of all historical pinakes;
- ARCA HISTORICA engine;
- full Syntagma II visual corpus;
- complete Syntagma III;
- elaborate sample libraries;
- XR parity;
- multiplayer/networking/accounts;
- cloud persistence;
- deployment;
- polishing every historical cabinet variant.

---

## 19. Research blockers that may pause only the affected surface

A missing historical detail should block **claiming that detail as H0**, not halt unrelated implementation.

Examples:

- unknown hinge style → use restrained H1 hinge geometry, parameterised and documented;
- unknown timber species → use neutral aged wood, do not label a species;
- Syntagma II visual not yet inspected → keep that bank noninteractive or schematic in this slice;
- no historical table transcription → use `NEO_WORKING_PINAX`, never counterfeit historical causation.

---

## 20. Implementation gate

The next coding session may begin **only the Historical Vertical Slice**, not the entire product.

It should start from the archaeology branch and preserve the Ghost backend as an accepted dependency rather than refactoring it opportunistically.

Before code, verify:

- current repo/branch/SHA;
- `docs/M0_1_PRIMARY_ARCA_RECONSTRUCTION.md` read in full;
- `docs/RESEARCH_STATUS.md` read in full;
- this file read in full;
- `docs/API.md` / `docs/DETERMINISM.md` read in full;
- no claim that current Neo generation is ARCA HISTORICA.

The first implementation decision should be **scene/interface architecture**, not color palette.

---

## Governing sentence

> **The user should compose by operating a reconstructed computational object, not by filling out a form that happens to be rendered inside one.**
