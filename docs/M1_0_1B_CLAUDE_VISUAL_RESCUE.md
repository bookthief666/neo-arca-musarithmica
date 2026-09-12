# M1.0.1B — Claude Visual Rescue Acceptance Brief

**Branch:** `feature/m1.0.1b-claude-visual-rescue`  
**Base authority:** `f755d0300afafed08de1b74a88ed1747ad7a0ef9` (`M1.0.1A: establish mechanical comprehension foundation`)  
**Purpose:** browser-driven physicality, choreography, Fold composition, and visual comprehension rescue. This is **not M1.1** and must not widen musical scope.

## Why this branch exists

A GPT Work session began this visual pass but hit its usage limit after validating the current frontend and starting private, uncommitted layout/CSS experiments. Those private changes are not on GitHub and are intentionally not assumed here. This branch is a clean parallel implementation line so Claude can work without racing or overwriting the suspended Work workspace.

Do not modify `feature/m1-arca-mechanica-vertical-slice` directly. Do not merge anything from the suspended Work workspace unless it later becomes available and is reviewed explicitly.

## Verified owner feedback

The first Samsung Galaxy Z Fold 6 physical view of M1.0 was structurally correct but not yet owner-testable. The dominant problems were:

- the composition read as stacked antique-themed web panels rather than one coherent machine;
- the cabinet was too flat;
- banks/cells read too much like buttons/tabs;
- Cell IV did not make rod removal self-evident;
- the working rule felt like a separate page panel;
- the mechanics required too much explanatory text;
- Tone II was compressed on the Fold;
- meaningful text was often too small;
- provenance competed with the instrument;
- the four-voice result was semantically correct but visually underpowered.

The historical direction itself was **not rejected**. The physical expression was.

## Preserve from M1.0.1A

Do not casually rewrite the canonical interaction architecture. Preserve these invariants unless a concrete runtime defect requires a narrow correction:

- React + TypeScript + Vite foundation;
- canonical reducer/action model;
- immutable historical source columns distinct from physical `ColumnRodInstance`s;
- `DEPLOY_ROD` as the primary simple deployment action;
- older retrieve/held/place path retained as a fallback or choreography state;
- semantic presentation focus derived from canonical phase rather than becoming a second musical authority;
- `getNextAffordance()` as a derived diegetic cue, not a stepper;
- moving any rod off the verified band invalidates Tone II and prior revelation;
- M0.9 Python kernel remains the historical computation authority;
- no Ghost path;
- no invented octave, MIDI, BPM, register, ficta, or fake historical rows;
- untranscribed bands remain sealed;
- provenance remains complete even when visually quiet.

## Historical interaction truth

The principal physical unit is the **individual musarithmic column-rod**, not a whole Pinax card.

The intended physical logic is:

`printed Pinax → individual copied rods → receptacle storage → remove rods → arrange side-by-side → slide rods vertically → read transverse alignment`

Visible historical material must correspond to verified project-owned records. If a visible manipulation appears to change the historical computation, it must really change canonical eligibility or kernel input.

## Visual thesis

The app should feel like Kircher's Arca Musarithmica survived and evolved into an impossible computational music instrument.

The material progression should read:

`WOOD → PAPER → RULED TABLE → RODS → ALIGNMENT → CALCULATION → LIVING MUSIC`

Avoid generic occult UI, glassmorphism, cyberpunk neon, giant glowing sigils, conventional dashboard cards, DAW grammar, and decorative spectacle disconnected from mechanics.

## Required visual/mechanical rescue

### 1. One machine, not stacked panels

At Fold/narrow widths, the dominant impression must be one physical Arca whose relevant subsystem comes forward. Do not simultaneously present masthead, Mensa, cabinet, giant work panel, provenance, and result as equal vertical siblings.

Use semantic focus: cabinet context remains visible, but the active subsystem gets useful scale.

### 2. Cabinet physicality

Improve frame thickness, recessed storage, slot depth, inner darkness, lids/tabs/lips, layered shadows, overlaps, paper/wood hierarchy, and restrained material response. Do not turn it into a fantasy treasure chest.

### 3. Bank architecture

Banks I/II/III should read as physical divisions of the machine, not navigation tabs. Bank I may come forward; Banks II/III remain clearly present but sealed/deferred.

### 4. Cell IV comprehension

Cell IV must visually communicate: **this opens; narrow physical things are stored inside; those things can be removed.** Use spatial continuity such as a sliding/lifting cover, drawer/recess movement, carrier heads rising, or another restrained H1 reconstruction.

### 5. Rod transfer choreography

Prefer a robust physical transfer:

`touch/select rod → rod visibly lifts → destination rail awakens → rod travels/snaps into rail`

A tap-lift + tap-destination fallback is acceptable if direct dragging is unreliable on mobile. Preserve object identity throughout the movement.

### 6. Working rail belongs to the Arca

The rule/rail should deploy from or mechanically connect to the cabinet: pull-out tray, ruled carriage, folding lectern, front rail, etc. Treat the exact mechanism as H1 reconstruction. It must not look like a separate full-width web card.

### 7. Rods are hero controls

Improve rod thickness, side edge, caps, ruling, shadows, read-band intersection, grasp state, and copy identity. Rhythm and pitch rods should differ structurally/inscriptionally rather than by modern color coding.

### 8. Vertical detents

The user should immediately understand that a rod has ten registered positions. Movement should settle/snaps confidently to bands. The read line must respond continuously. Bands 02–10 remain sealed/untranscribed.

### 9. Transverse rule is the hero mechanic

As rods move, the horizontal read line should visibly intersect their active bands. Invalid rods break continuity. Verified alignment should become visually continuous/locked/resonant with restrained material-local illumination. Text such as `H0 VERIFIED` may support accessibility but cannot be the main explanation.

### 10. Tone II semantic focus

When alignment is ready, the Mensa should come forward enough that all eight degrees are readable on Fold:

`1 G · 2 A · 3 Bb · 4 C · 5 D · 6 Eb · 7 F# · 8 G`

It must remain part of the Arca, not a settings modal.

### 11. Four-voice revelation

Keep exact accessible tabular data, but make execution feel like the machine revealed four voices. A safe visual language is four horizontal inscription/voice lanes showing event order, symbolic pitch class/degree, and relative duration without implying absolute register.

### 12. Provenance is quiet by default

Use a compact H0/source seal, marginal tab, or scholarly folio affordance. Full records/witnesses/fingerprint remain inspectable on demand.

### 13. Typography

Operational text must be comfortably readable at real Fold size. Do not make historical style depend on ~0.65–0.72rem text for meaningful controls.

### 14. Motion explains causality

Prioritize spatial continuity for: cabinet opening, Cell IV opening, rod lift/transfer/snap, rod detents, alignment lock, Mensa focus, read action, revelation, return to rods. Keep motion short, responsive, and reduced-motion equivalent.

## R3F policy

Do **not** add R3F by default. Push DOM/CSS/SVG first. Add R3F only if a specific mechanical interaction materially benefits and typography/touch/accessibility/testability remain intact. XR remains deferred.

## Viewports to inspect

At minimum:

- narrow/Folded-class: about `390 × 844`;
- Fold-open-class: about `884 × 960`;
- desktop: about `1360 × 900`.

Inspect these rendered states at narrow width: closed Arca, open cabinet, Cell IV open, one rod transfer/deployed, three rods misaligned, verified alignment, Tone II focus, four-voice revelation, provenance inspector.

## Mechanical truth checks

Before acceptance, verify all are true:

- move a rod off verified band → Tone II/result invalidate;
- Tone II eligibility comes from canonical state;
- final four voices come from `scripts/arca_historica_kernel.py` through the existing bridge;
- no visible historical-looking unverified values are invented;
- repeated Vperm rods remain distinct physical instances of shared source data.

## Scope explicitly deferred

Do not add: audio, Tone.js, MIDI UX, absolute register, Ghost/manual bridge, semantic prompting, Neo controls, Hæretic mode, more corpus, Syntagma II/III, text-setting, save/accounts, WebXR, deployment.

## Acceptance bar

M1.0.1B is complete only if the rendered Fold composition is **substantially transformed** from the owner-rejected M1.0 screenshot and primarily reads as one coherent physical instrument.

The owner should be able to infer most of the first interaction from form and motion instead of reading a long operator manual.

## Commit / release rules

Work only on `feature/m1.0.1b-claude-visual-rescue`.

Do not merge, deploy, rebase, squash, reset legitimate history, force-push, modify permanent baselines, or create an M1 baseline. Commit meaningfully and push this parallel branch only.

## Verification

Run `bash scripts/verify_m1_0_1b.sh` after dependencies are installed. It is the canonical convenience gate for this branch; if a command fails, investigate rather than weakening the script.

Also browser-run the app and perform the complete interaction path. Passing automated tests alone is insufficient.

## Stop condition

Stop after the visual/mechanical rescue is implemented, browser-iterated, responsive-inspected, tested, built, committed, and pushed. Do not proceed into M1.1.
