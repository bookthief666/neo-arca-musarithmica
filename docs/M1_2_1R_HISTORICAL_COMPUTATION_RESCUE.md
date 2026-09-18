# M1.2.1R — Historical Computation Rescue

**Status:** implementation complete; automated verification green; physical Fold/TalkBack release acceptance deferred by owner decision.

**Canonical implementation branch:** `feature/m1.2.1r-historical-computation-rescue`

**Accepted M1.2 ancestor:** `7dc5e3c66e4602478d4f8a23f45f136db457f0e1`

**Tasks 1–4 checkpoint ancestor:** `7f9263d52845cdd8fb67ba34857cdd9a38fef2fa`

**Final implementation / Fold-reader rescue HEAD:** `63e8472084fdfa544dfb1f15c2f297a2f67a2a4c`

**Design authority:** `feature/m1.2.1r-historical-computation-rescue-design@e9fa058be127a7f48bb1800b14bf576398af4857`

## Outcome

M1.2.1R replaces the rejected scripted three-carrier/band ritual with one truthful critical-edition computation workbench:

- one persistent H1 critical-edition carrier;
- H0 Vperm01 source content;
- H0 Rperm03 mensural identities;
- derived relative-minim normalization `1 1 1 1 2 2`;
- printed-p.51 Tone II as H0 witness transcription and H1 fixed operating policy;
- six H1 event-inspection positions;
- fail-closed source/execution parity against the unchanged M0.9 kernel;
- one canonical reducer shared by spatial and semantic controls;
- explicit H0/H1/modern-representation provenance.

The M0.9 kernel and verified historical records were not modified.

## Verification

### Python

Most recent complete Python suite after Tasks 1–9 and before the presentation-only Fold-reader rescue:

- **572 passed**
- no functional failures;
- only dependency deprecation warnings were recorded.

The Fold-reader rescue changed only frontend spatial presentation/interaction code.

### Frontend exact Fold-reader-rescue HEAD

GitHub Actions verified `63e8472084fdfa544dfb1f15c2f297a2f67a2a4c`:

- **16 / 16 test files passed**
- **127 / 127 tests passed**
- `npm run typecheck` — passed
- `npm run lint` — passed
- `npm run build` — passed
- `git diff --check` — passed
- global `document.body.dataset.arcaGrab` scan — no matches
- legacy `MAX_VERTICAL_OFFSET` / `VIRGA_TRAVEL` band-control scan — no matches
- M0.9 kernel and historical data — unchanged

Build output at the final Fold-reader-rescue HEAD:

- `SpatialArca-nwI95iGe.js`: **908.17 kB raw**
- gzip: **246.19 kB**

The chunk remains within the design's +10% M1.2 growth ceiling.

The test environment continues to emit the known "Multiple instances of Three.js being imported" warning in two test paths. The installed production dependency graph was separately recorded as one deduplicated Three.js runtime; the warning remains test-environment debt.

## Browser / interaction evidence

Automated browser acceptance covered:

- `360×800`
- `768×1024`
- `884×1104`
- `1104×884`
- `1440×900`

The browser gates verified:

- no horizontal overflow at required viewports;
- complete legacy-renderer v2 flow;
- unknown v2 bridge fields rejected with HTTP 422;
- deliberate bridge rejection → retry → successful revelation;
- event-reader direct manipulation reaches Event 6;
- camera remains stationary while the reader owns the gesture;
- orbit resumes after off-target release and pointer cancel;
- semantic and spatial event values remain aligned.

A Fold-like native-touch emulation run used:

- viewport `884×1104`;
- `deviceScaleFactor: 2`;
- `isMobile: true`;
- `hasTouch: true`;
- Chromium CDP `touchStart` / `touchMove` / `touchEnd`.

Recorded evidence:

- resulting semantic state: **Event 6 of 6**
- Event 6: C 3 → B-flat; A 7 → F-sharp; T 5 → D; B 3 → B-flat; semibreve; 2 relative minim units
- camera delta during reader touch: **0**
- camera delta after release/orbit gesture: **0.3678215667**
- browser errors: **none**

## Physical Galaxy Z Fold 6 findings

The owner ran the application locally on a Galaxy Z Fold 6 through Termux and a Fold browser.

Confirmed on the real device:

- the spatial application loads and renders;
- cabinet/open/cell states render correctly;
- semantic Instrument Controls operate the canonical state;
- carrier retrieval/seating and event 1/event 6 values are visible;
- semantic source labels and provenance are readable after the contrast fix.

The first physical direct-reader attempt **did not pass**: the owner could not discover or reliably operate the event reader without Instrument Controls.

That physical finding produced the final rescue commit:

`63e8472084fdfa544dfb1f15c2f297a2f67a2a4c — fix(m1.2.1r): make Fold event reader directly grabbable`

The rescue:

- enlarges/raises the visible gold grip;
- makes the complete white event folio a generous direct drag surface;
- preserves the same canonical six-position state;
- does not change the reducer, bridge, kernel, or historical data.

Automated browser and native-touch gates pass after this change.

The owner explicitly elected to continue development without repeating every intermediate physical-device test. Therefore:

> **Physical Fold and TalkBack acceptance are deferred release smoke tests, not claimed as passed.**

This document does not convert automated success into a physical-device verdict.

## Authority / provenance contract preserved

Canonical source values remain:

### Vperm01

- Cantus: `553233`
- Altus: `875777`
- Tenor: `323455`
- Bassus: `858733`

The secondary `868733` Bassus variant remains discrepancy history only.

### Rperm03

Mensural identities:

`minim minim minim minim semibreve semibreve`

Derived project normalization:

`1 1 1 1 2 2`

The integer normalization is not represented as literal source notation.

### Tone II / printed p.51

`1 G · 2 A · 3 Bb · 4 C · 5 D · 6 Eb · 7 F# · 8 G`

This remains a witness-specific H0 transcription used through an explicitly H1 fixed operating policy. The broader tone-table conflict remains provenance, not silently reconciled data.

## Deferred limitations

Still deferred:

- real-device re-test of the post-`63e847` direct folio drag;
- TalkBack smoke test on the owner's Fold;
- broader historical corpus;
- unresolved Rperm01 augmentation punctus;
- octave/register realization;
- phrase-level ficta;
- audio/MIDI/playback;
- Neo/Haeretica controls;
- WebXR;
- repository default-branch governance.

## Owner continuation decision

The M1.2.1R design required a new owner decision before beginning the next corpus milestone.

After the physical Fold session exposed the direct-reader discoverability defect, the defect was repaired and automated mobile-touch verification passed. The owner then explicitly chose to continue development while deferring repeated physical Fold/TalkBack verification to a later release/freeze smoke test.

This is authorization to begin design of the **Minimum Agency Corpus**. It is not a retroactive claim that the M1.2.1R physical acceptance gate passed.
