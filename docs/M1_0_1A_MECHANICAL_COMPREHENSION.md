# M1.0.1A — Mechanical Comprehension Foundation

**Status:** implementation checkpoint for the owner-rejected M1.0 physical-comprehension state.  
**Branch:** `feature/m1-arca-mechanica-vertical-slice`.  
**Parent authority:** M1.0 at `494d73526a52fddd00a6be6def13e181996e0fd0`.  
**Purpose:** improve the interaction/state foundation before the next browser-heavy visual choreography pass. This is not M1.1 and does not widen the musical scope.

## Owner signal

The first physical Samsung Galaxy Z Fold 6 view proved that the M1.0 architecture worked, but the instrument still read too much like stacked antique-themed application panels and was too difficult to understand without an operator script. M1.0 therefore remains **not owner-accepted**.

This checkpoint addresses the parts that can be corrected safely at the canonical state and composition level without inventing new historical data or making unverified visual claims.

## Changes

### Direct deployment path

The primary touch/click path no longer requires a conceptual two-step `retrieve -> lay beside rule` sequence. `DEPLOY_ROD` creates a physical `ColumnRodInstance` directly in the working rail while preserving immutable source-column data. The older `RETRIEVE_ROD -> PLACE_HELD_ROD` transition remains as a compatibility/fallback path and possible future drag choreography state.

### Derived semantic focus

`InstrumentView` is derived from the canonical instrument phase rather than stored as a second source of truth:

```text
arca -> cabinet -> cell -> working -> tone -> working -> revelation
```

This permits the UI to withhold unrelated surfaces until they matter:

- the working rule is absent before a rod is deployed;
- after all required rods reach the verified read band, the working surface yields focus to the Mensa Tonographica;
- engaging Tone II returns focus to the transverse rule for execution;
- a successful execution replaces the active working surface with the symbolic four-voice revelation;
- `Return to the rods` restores the aligned mechanism without another kernel call.

Presentation focus remains derived state. It does not become musical authority.

### Canonical affordance selector

`getNextAffordance()` derives the single next meaningful physical opportunity from canonical state:

```text
open_arca
focus_bank_i
open_cell_iv
deploy_rods
place_held_rod
align_rods
engage_tone_ii
read_transverse
await_execution
inspect_revelation
recover
```

The UI uses this only for restrained diegetic emphasis and accessibility status. It is not a wizard, step counter, or hidden workflow engine.

### Historical truth preservation

The accepted M1.0 invariants remain unchanged:

- historical source-column data is immutable;
- rod instances carry their own position and offset;
- untranscribed bands remain sealed;
- only the manifest-declared canonical read band can become H0-ready;
- moving any deployed rod invalidates Tone II and any previous execution result;
- the Python M0.9 bridge remains the computation authority;
- no octave, MIDI, BPM, register, ficta, or Ghost/SATB repair is introduced.

### Fold composition foundation

A late CSS layer (`frontend/src/mechanica-focus.css`) now reshapes the existing M1.0 presentation without discarding its accepted historical palette. It:

- removes the three-rem gap that made the working rule look like a second application panel;
- visually joins the working rail to the Arca body;
- enlarges practical rod step targets;
- makes Tone II an intentional semantic-focus state on narrow screens;
- turns the provenance apparatus into a fixed compact source seal with an expandable inspector;
- suppresses the long footer after the resting state;
- makes the Mensa horizontally scroll inside its own surface rather than overflowing the page;
- enlarges meaningful Fold typography and Cell-IV carrier targets;
- compresses the cabinet behind the revelation rather than appending another long section;
- preserves reduced-motion equivalence.

This layer is intentionally conservative. The subsequent Work pass should still perform real browser/physicality iteration and may replace specific CSS treatments if visual QA shows a better solution.

## Explicitly deferred to M1.0.1B / Work

- direct drag from Cell IV into the working rail with visible continuous transfer;
- high-quality cabinet/receptacle depth and material refinement;
- hinge/cover/rail choreography;
- final Fold spatial composition;
- four-voice visual revelation beyond the existing exact symbolic table;
- R3F, unless later browser evidence shows a surgical need;
- audio, MIDI, Tone.js, Ghost integration, Neo controls, XR, corpus expansion, deployment.

## Local validation performed in this checkpoint

Because this chat environment does not contain the Work checkout or its installed frontend `node_modules`, it does **not** claim the real Vitest/ESLint/Vite suite.

The following checks were run against the exact drafted files before repository write:

- TypeScript strict compilation of `instrument/types.ts` + `instrument/model.ts`: PASS.
- Direct Node acceptance exercise of the compiled reducer/selectors: PASS.
- TypeScript parser/transpiler syntax checks for all changed TS/TSX files: PASS.
- PostCSS parse of `mechanica-focus.css`: PASS.

The next GPT Work pass must run the full Python and frontend gates and visually inspect the result before M1.0.1 can be owner-tested.

## Acceptance boundary

M1.0.1A is successful if the next visual pass can treat the reducer/state/composition structure as stable and spend its effort on making the object physically self-explanatory rather than discovering that the page architecture itself fights the intended instrument.
