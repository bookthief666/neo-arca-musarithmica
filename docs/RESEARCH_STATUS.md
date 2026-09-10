# RESEARCH_STATUS.md — Current historical authority

**Current archaeology branch:** `feature/m0.1-primary-arca-archaeology`  
**Ghost/backend freeze point:** `8869e2738d2b31f2682a5b1d30913baa6a8a12e2` (B10)  
**M0.1 dossier baseline:** `1577d46ad2b2ca109072c2cb66a11d33eac0bdca`

This file exists to prevent a future implementation session from treating the first M0 documents as the latest visual authority.

## Which research document governs what?

- `HISTORICAL_RESEARCH.md` — **historical first-pass record.** It preserves what the project knew when the research environment could not inspect primary scans or object photographs. Its repeated statements that no image had been inspected are true **for that pass**, but are no longer the current project state.
- `VISUAL_RECONSTRUCTION.md` — **historical first-pass visual uncertainty record.** Keep it because it documents which details were previously unsupported; do not use its opening `could not fetch a single image` warning as the current frontend gate.
- `M0_1_PRIMARY_ARCA_RECONSTRUCTION.md` — **current authority for frontend reconstruction anatomy and interaction topology.** This pass inspected the 1650 engraving, Syntagma I Pinax IV, the Wolfenbüttel institutional record, and a published photograph of the Wolfenbüttel cabinet.
- `UNCERTAINTIES.md` — still authoritative where M0.1 does not explicitly close or narrow an uncertainty.
- `PROVENANCE.md` — still authoritative for H0/H1/N1/HÆRETIC distinctions; M0.1 adds H0-V/H0-T/H0-O sublabels for visual/textual/object evidence.
- `PHASE1_ACCEPTANCE.md` — **B10 release snapshot.** Do not rewrite it retroactively. Its statement that primary visual archaeology remained to be done accurately records the state at B10.

## Current gate

### Cleared

- Phase-1 Neo-Arca Ghost backend: release-candidate foundation accepted.
- Original 1650 Arca engraving: inspected.
- One original Syntagma I pinax layout: inspected (Pinax IV).
- Wolfenbüttel physical implementation: institutionally identified; published object photograph inspected; 23 × 14.5 cm dimensions recorded for that exemplar only.
- Historical operator topology: sufficiently established to design an interaction architecture based on removable pinakes, lid lookup, front range/clef reference, and an external working surface.
- Rights strategy: public-domain 1650 source material may underpin direct reconstruction; modern museum/scholarly photography is reference-only absent a reusable licence.

### Still open before a historically strong first visual release

1. **Directly inspect a Syntagma II pinax at useful resolution.** Cashner identifies Fig. 3 / *Musurgia universalis* II, fol. 106 as Syntagma II Pinax II. Scholarship establishes that Syntagma II pairs four-voice pitch and rhythm permutations rather than using Syntagma I's separate shared-rhythm table, but its visual table grammar should still be inspected before modelling the florid bank.
2. **Obtain stronger institutional documentation for the Cambridge/Pepys and Florence survivals.** Cashner is good scholarly evidence that the Cambridge example is a wooden box with paper slats; a 1930s Cambridge loan-exhibition catalogue independently confirms Magdalene College loaned the `Musarithmica Mirifica` from the Pepys Library. Exact dimensions/shelfmark and a current institutional object record remain open. Florence is well-attested in Erik Boni's 2020 study but still lacks a direct BNCF object record in this project's evidence ledger.
3. **Independently transcribe a bounded public-domain historical dataset.** The best pilot is Syntagma I Pinax IV plus the usable tone table from the 1650 Arca engraving. This must be transcribed from a public-domain primary scan, with per-cell/page provenance, not copied from Cashner's modern implementation.
4. **Resolve exact cabinet-detail uncertainties only where the first vertical slice needs them.** Timber species, depth, hinge/clasp form, divider joinery and slat thickness remain reconstruction choices unless further object evidence is found.

## Implementation rule

A frontend may now begin **reconstruction architecture** and a bounded physical-shell prototype, but it must not visually imply that Neo-Arca's current SATB solver is literally reading Kircher's historical number tables.

Until `ARCA HISTORICA` has a project-owned primary-source transcription:

- real Kircher tables may appear as inspectable facsimile/reference material; or
- live generative slats may use historically faithful anatomy with clearly Neo-Arca/N1 data.

Do not silently combine those two provenance modes.

## Recommended next gate

Before a large-scale React/R3F build, finish one **Historical Vertical Slice specification** around a single removable Syntagma I pinax. It should define:

`open Arca → select syntagma → retrieve pinax → place on work surface → choose stropha/column → choose musarithm → choose rhythm → consult lid tone table → resolve register on front staff → accumulate four voices → Neo playback/export`

The historical actions supply the interface topology. The Neo-Arca backend supplies modern composition and diagnostics. Their boundary must remain visible and inspectable.
