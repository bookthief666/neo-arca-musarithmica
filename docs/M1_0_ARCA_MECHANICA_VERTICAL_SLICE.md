# M1.0 — Arca Mechanica vertical slice

Status: implementation candidate for physical owner QA. This is not an M1 baseline.

## Scope

M1.0 implements one direct-instrument path: resting Arca → open cabinet → Bank I / Cell IV → three individual column-rod instances → transverse band alignment → printed-page-51 Tone II → the M0.9 symbolic historical kernel → four provenance-bearing voices.

The frontend is a React/TypeScript/Vite application in `frontend/`. Its cabinet, paper, inscriptions, rods, and alignment surface are built with semantic DOM and CSS in restrained 2.5D. R3F/Three.js is deliberately deferred: at this stage it would not improve the source typography, focus order, or Fold-scale rod manipulation enough to justify a second interaction surface. The reducer and action contract are renderer-neutral so a later spatial renderer or XR controller can invoke the same authority-bearing actions.

## Historical execution boundary

The browser does not reproduce historical composition rules. It requests a manifest from `scripts/arca_mechanica_bridge.py`, which reads the canonical project records and presents only their authorised visible material. On execution, the bridge validates the submitted physical arrangement and then calls `build_default_fragment()` from `scripts/arca_historica_kernel.py`.

The required physical arrangement is:

- `pinax04-vperm-copy-1`, source `S1.P4.STROPHA1.VPERM01`, band 01;
- `pinax04-vperm-copy-2`, the second physical instance of that same immutable source, band 01;
- `pinax04-rperm03-copy-1`, source `S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03`, band 01;
- canonical side-by-side order on the working rule; and
- printed-page-51 Tone II physically engaged.

Offsets 1–9 expose bands 02–10. Those bands are labelled untranscribed, carry no historical-looking values, disable the read action, and are rejected by the Python bridge. Moving a visible rod therefore changes the physical request and its execution eligibility; the visible alignment is not decorative.

The Vite development and preview servers expose only two local endpoints:

- `GET /api/historica/manifest`
- `POST /api/historica/execute`

Each request starts the Python bridge as a child process using the repository virtual environment when present. No Ghost endpoint is called, and no historical musical logic is duplicated in TypeScript.

## Data authority

H0 / ARCA HISTORICA material comes directly from:

- `historical_data/syntagma1_pinax04/vperm01_printed_p83_verified.json`
- `historical_data/syntagma1_pinax04/rhythm_duple_rperm03_printed_p83_verified.json`
- `historical_data/mensa_tonographica/tone02_hypodorius_printed_p51_verified.json`
- `historical_data/source_witnesses.json`

The generated symbolic events retain the exact cell and witness provenance emitted by M0.9. `rhythm_duple_rperm01_ambiguity.json` is not loaded or presented as an executable choice.

H1 covers the carrier-face layout, physical copy embodiment, cabinet joinery, timber treatment, and screen-scale geometry. These choices make the primary-text physical model operable without claiming that a surviving cabinet fixes their exact appearance.

No N1 musical data is active in M1.0. Modern browser rendering, illumination, responsive semantic zoom, and interaction feedback are presentation technology only. The slice invents no register, octave, MIDI pitch, BPM, audio, SATB repair, or ficta.

## State and accessibility

`frontend/src/instrument/model.ts` owns the canonical state transitions. Historical source columns remain immutable; `ColumnRodInstance` records copy identity, location, order, and vertical offset separately. Mouse, touch/pointer, step controls, and keyboard slider actions all dispatch the same `MOVE_ROD` action. The rod sliders support Arrow Up/Down, Home, and End.

The cabinet and receptacles are native buttons; Tone II exposes pressed/disabled state; the read lever is a native button; the output is a semantic four-voice table with a live region; visible focus, reduced-motion handling, non-colour status text, and a provenance drawer provide semantic parity.

## Local operation

From the repository root, install the locked Python environment as described by the existing project documentation. Then:

```bash
cd frontend
npm ci
npm run dev
```

The Vite bridge expects the frontend directory to remain inside this repository so it can resolve the canonical Python kernel and historical records one directory above.

## Deliberate limits

M1.0 does not add the broader corpus, Syntagma II/III implementations, historical text setting, the Phase-1 Ghost, semantic prompting, audio, MIDI, Tone.js, WebXR, a second spatial renderer, save/account systems, or deployment infrastructure. A static production bundle alone cannot execute Python; this milestone's honest integration is the local Vite-to-kernel bridge pending a later production service boundary.
