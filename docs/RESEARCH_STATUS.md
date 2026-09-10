# RESEARCH_STATUS.md — Current historical authority

**Current archaeology branch:** `feature/m0.1-primary-arca-archaeology`  
**Ghost/backend freeze point:** `8869e2738d2b31f2682a5b1d30913baa6a8a12e2` (B10)  
**M0.1 dossier baseline:** `1577d46ad2b2ca109072c2cb66a11d33eac0bdca`  
**Current physical-topology correction:** `docs/M0_6_PRIMARY_TEXT_CORRECTIONS.md`

This file exists to prevent a future implementation session from treating an earlier research pass as the latest authority.

## Which research document governs what?

- `HISTORICAL_RESEARCH.md` — **historical first-pass record.** It preserves what the project knew when the research environment could not inspect primary scans or object photographs. Its repeated statements that no image had been inspected are true **for that pass**, but are no longer the current project state.
- `VISUAL_RECONSTRUCTION.md` — **historical first-pass visual uncertainty record.** Keep it because it documents which details were previously unsupported; do not use its opening `could not fetch a single image` warning as the current frontend gate.
- `M0_1_PRIMARY_ARCA_RECONSTRUCTION.md` — primary visual/object archaeology dossier. It inspected the 1650 engraving, Syntagma I Pinax IV, the Wolfenbüttel institutional record, and a published photograph of the Wolfenbüttel cabinet.
- `M0_6_PRIMARY_TEXT_CORRECTIONS.md` — **current authority for the historical physical-control topology wherever it conflicts with M0.1 or the first Historical Vertical Slice.** Direct reading of Kircher's Book VIII construction/use instructions establishes that the stored/manipulated units are separate musarithmic **columns copied from pinakes onto paper or wooden rods**, often in multiple copies; users arrange these rods side-by-side and move them vertically to form transverse combinations.
- `PRODUCT_DIRECTION_M0_2.md` — current product decision: primary Neo-Arca is an instrument-first musical interface; no free-text semantic mood prompt is required.
- `M0_3_INSTRUMENT_CONTROL_TOPOLOGY.md` — direct musical-control map; interpret its historical rod behavior through the M0.6 correction above.
- `HISTORICAL_DATA_TRANSCRIPTION_SPEC.md` — binding protocol for any project-owned `ARCA HISTORICA` numerical/rhythmic data.
- `historical_data/source_witnesses.json` — machine-readable public-domain witness/navigation ledger.
- `UNCERTAINTIES.md` — still authoritative where later M0.x work does not explicitly close or narrow an uncertainty.
- `PROVENANCE.md` — still authoritative for H0/H1/N1/HÆRETIC distinctions; later archaeology adds H0-V/H0-T/H0-O sublabels.
- `PHASE1_ACCEPTANCE.md` — **B10 release snapshot.** Do not rewrite it retroactively. Its statement that primary visual archaeology remained to be done accurately records the state at B10.

## Current gate

### Cleared

- Phase-1 Neo-Arca Ghost backend: release-candidate foundation accepted.
- A permanent non-destructive B10 baseline exists at `baseline/phase1-ghost-b10`.
- Original 1650 Arca engraving: inspected.
- One original Syntagma I pinax layout: inspected (Pinax IV).
- Wolfenbüttel physical implementation: institutionally identified; published object photograph inspected; 23 × 14.5 cm dimensions recorded for that exemplar only.
- Kircher's own 1650 construction/use prose has now been read directly from the public-domain UNC scan OCR.
- Ideal Arca proportions from Kircher: length = height = one palm; width = half a palm (H0-T).
- Historical storage topology: three principal banks; first 12 cells, second 6, third likewise six-partite in the ideal construction instructions (H0-T).
- Historical physical control topology: individual pinax columns copied onto paper/wood rods, repeated as needed, arranged side-by-side, and shifted vertically to select transverse combinations (H0-T).
- Tone VI / Hypolydius lookup has a primary-text staging record with multiple internal 1650 cross-checks; visual witness verification remains pending before canonical promotion.
- Pinax IV has a real project-owned Pass-A staging record for its first musarithm block plus a separate same-witness verification reading and an explicit discrepancy ledger.
- Rights strategy: public-domain 1650 source material may underpin direct reconstruction/transcription; modern museum/scholarly photography is reference-only absent a reusable licence.

### Still open before a historically strong first playable release

1. **Complete strict independent Pass B for Pinax IV VPERM01.** The preferred witness is ETH/e-rara Tomus II printed p.83 = scan `[92]`, or Universidad de Valladolid `SC_05725.pdf`. Current project readings agree on `858733` for the disputed Bassus row, while a secondary transcription reads `868733`; no historical active value is allowed until the second public-domain facsimile is checked.
2. **Visually verify the Tone VI mapping against an independent facsimile and the corrected Iconismus XIV tone table.** Primary OCR and Kircher's worked examples strongly establish F–G–A–Bb–C–D–E–F for Tone VI/Hypolydius, but the final dataset must identify which tone-table witness it follows because p.51 and Iconismus XIV are known to disagree in places.
3. **Transcribe one complete Notae Temporis/Rperm from Pinax IV from a public-domain image at useful resolution.** Rhythm glyphs require image-level reading; do not infer them from a modern transcription and call that historical data.
4. **Directly inspect Syntagma II Pinax II at useful resolution.** ETH/e-rara maps printed p.106 to scan `[115]`. Scholarship establishes a different pitch/rhythm pairing grammar, but the primary table should govern the frontend's florid-bank geometry.
5. **Obtain stronger institutional documentation for the Cambridge/Pepys and Florence survivals** where useful to physical reconstruction. These are no longer blockers for the first column-rod interaction, but remain valuable comparative-object evidence.
6. **Resolve exact cabinet-detail uncertainties only where the first vertical slice needs them.** Timber species, hinge/clasp form, divider joinery, and slat thickness remain reconstruction choices unless further object evidence is found.

## Implementation rule

A frontend may now begin **reconstruction architecture** and a bounded physical-shell/column-manipulation prototype, but it must not visually imply that the existing Neo-Arca SATB solver is literally reading Kircher's historical number tables.

Until `ARCA HISTORICA` has a verified project-owned source corpus:

- real Kircher tables may appear as inspectable facsimile/reference material; or
- live generative column-rods may use historically faithful physical anatomy with clearly Neo-Arca/N1 data.

Do not silently combine those provenance modes.

The physical interaction model is now more precise than in the first vertical-slice document:

`open Arca → open labelled bank/cell → retrieve several column-rods copied from the relevant pinax family → arrange rods side-by-side → slide rods vertically → choose/read transverse row → resolve scale degrees through the tone table → place voices through the phonotactic/range surface → historical or Neo realization → playback/export`

## Recommended next gate

Do not create another broad design document before solving the smallest executable historical chain.

The next research target is:

**one verified Pinax-IV Vperm + one verified Pinax-IV Rperm + one verified Tone-VI mapping → a four-voice historical phrase whose every data element points back to a public-domain 1650 witness.**

Only after that chain works should transcription scale outward to the rest of Pinax IV.
