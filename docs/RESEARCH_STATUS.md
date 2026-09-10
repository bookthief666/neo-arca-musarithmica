# RESEARCH_STATUS.md — Current historical authority

**Current archaeology branch:** `feature/m0.1-primary-arca-archaeology`  
**Ghost/backend freeze point:** `8869e2738d2b31f2682a5b1d30913baa6a8a12e2` (B10)  
**Permanent Ghost baseline:** `baseline/phase1-ghost-b10`  
**M0.9 executable-kernel commit:** `06c76a2cb857e49ec64d7b8049bb4ce18a9ca887`  
**M0.9 historical baseline:** `baseline/m0.9-arca-historica-first-fragment` → `06c76a2cb857e49ec64d7b8049bb4ce18a9ca887`  
**Physical-topology authority:** `docs/M0_6_PRIMARY_TEXT_CORRECTIONS.md`

This file identifies the latest authority for implementation. Earlier M0 documents remain part of the research record but must not override later primary-source findings or the M0.9 executable contract.

## Governing documents

- `HISTORICAL_RESEARCH.md` — historical first-pass record from the source-restricted environment.
- `VISUAL_RECONSTRUCTION.md` — first-pass visual uncertainty register.
- `M0_1_PRIMARY_ARCA_RECONSTRUCTION.md` — primary visual/object archaeology dossier.
- `M0_6_PRIMARY_TEXT_CORRECTIONS.md` — authority for historical physical-control topology where it conflicts with earlier simplified “pinax-as-slat” language. The stored/manipulated units are separate musarithmic columns copied from pinakes onto paper/wood carriers, arranged side-by-side and shifted vertically.
- `PRODUCT_DIRECTION_M0_2.md` — product authority: the first playable Neo-Arca is a direct musical instrument, not a semantic prompt-to-music product.
- `M0_3_INSTRUMENT_CONTROL_TOPOLOGY.md` — modern control topology, interpreted through M0.6.
- `HISTORICAL_DATA_TRANSCRIPTION_SPEC.md` — binding protocol for project-owned `ARCA HISTORICA` data.
- `historical_data/source_witnesses.json` — machine-readable primary-witness/navigation ledger.
- `M0_9_ARCA_HISTORICA_KERNEL.md` — executable historical-chain contract and current boundary between HISTORICA and the Ghost.
- `PROVENANCE.md` — H0/H1/N1/HÆRETIC vocabulary and provenance rules.
- `PHASE1_ACCEPTANCE.md` — B10 release snapshot; do not rewrite it retroactively.

## Verified historical data

### Syntagma I / Pinax IV / Stropha I / Vperm01

Canonical record:

`historical_data/syntagma1_pinax04/vperm01_printed_p83_verified.json`

Independent primary witnesses agree on:

```text
Cantus  553233
Altus   875777
Tenor   323455
Bassus  858733
```

The Chierotti secondary `868733` Bassus variant remains permanently preserved in `discrepancies.json`. It is not substituted into canonical data.

### Mensa Tonographica / printed p.51 / Tone II Hypodorius

Canonical witness-specific record:

`historical_data/mensa_tonographica/tone02_hypodorius_printed_p51_verified.json`

Verified mapping:

```text
1 G
2 A
3 Bb
4 C
5 D
6 Eb
7 F#
8 G
```

This establishes the printed-p.51 witness only. It must not be silently merged with the later Iconismus XIV tone-table witness.

### Pinax IV / Notae Temporis / duple Rperm03

Canonical record:

`historical_data/syntagma1_pinax04/rhythm_duple_rperm03_printed_p83_verified.json`

BSB, EPFL, and BnF/Gallica primary witnesses agree on:

```text
minim, minim, minim, minim, semibreve, semibreve
relative minim units: 1, 1, 1, 1, 2, 2
```

The original duple Rperm01 augmentation-punctus problem remains unresolved in `rhythm_duple_rperm01_ambiguity.json`. M0.8.1 deliberately used a different unambiguous row rather than resolving Rperm01 by secondary agreement or majority vote.

## M0.9 — first executable ARCA HISTORICA fragment

M0.9 is complete and preserved on `baseline/m0.9-arca-historica-first-fragment`.

Executable:

`scripts/arca_historica_kernel.py`

Focused acceptance tests:

`tests/test_arca_historica_kernel.py`

The kernel consumes only the three verified records above plus the witness ledger. It validates canonical/verified status, independent primary witnesses, direct-inspection/public-domain authority, complete cell provenance, source agreement, event-count compatibility, and absence of silent editorial repair.

It deterministically emits six symbolic four-voice events totaling eight **relative minim units**:

```text
pos  off  dur  glyph       cantus  altus  tenor  bassus
  1    0    1  minim       5:D     8:G    3:Bb   8:G
  2    1    1  minim       5:D     7:F#   2:A    5:D
  3    2    1  minim       3:Bb    5:D    3:Bb   8:G
  4    3    1  minim       2:A     7:F#   4:C    7:F#
  5    4    2  semibreve   3:Bb    7:F#   5:D    3:Bb
  6    6    2  semibreve   3:Bb    7:F#   5:D    3:Bb
```

This is the first auditable project-owned historical computation. It is described as a **Pinax-IV historical fragment**, not as Kircher's exact prose `Ave maris stella` worked example.

The kernel remains completely separate from the Neo-Arca Ghost and does **not** claim or infer octave/register placement, MIDI note numbers, BPM, modern beat semantics, hidden phrase-level ficta, or SATB repair.

Focused local verification for M0.9: `13/13 PASS` plus `py_compile` and direct CLI execution. The implementation environment could not clone GitHub directly, so no claim is made that the complete pre-existing repository suite was run at this checkpoint.

## What remains unresolved historically

- The augmentation punctus on Pinax-IV duple Rperm01.
- Exact octave/register realization for a historical four-voice output.
- Phrase-level musica ficta beyond the verified printed-p.51 tone lookup.
- Direct comparison with the later Iconismus XIV tone table.
- Syntagma II Pinax II primary-table grammar at useful resolution.
- Comparative construction details of additional surviving Arca objects where those details would materially change the reconstruction.

These questions remain valid research targets, but they no longer block the first physical instrument slice.

## Current implementation gate — ARCA MECHANICA

Do **not** bulk-transcribe the historical corpus and do **not** reopen the frozen Ghost simply to add frontend controls.

The next milestone is a bounded physical vertical slice that proves the historical interaction grammar:

`open cabinet → open labelled bank/cell → retrieve individual column-rods → arrange rods side-by-side → slide/align → choose verified Vperm/Rperm → resolve through Tonus → display the M0.9 symbolic result`

Requirements for that slice:

- the physical control is the individual musarithmic column-rod, not a whole Pinax card;
- `ARCA HISTORICA` must call the M0.9 historical path, never the Ghost;
- any Neo material must be visibly/provenance-distinct from historical rods;
- one real verified fragment is enough for the first slice; missing corpus breadth must not be disguised as historical data;
- preserve the cabinet/bank/rod logic established by Kircher's construction/use instructions;
- prioritize direct manipulation and musical consequence over menus or prompt boxes;
- defer a broad manual Ghost API until the physical interaction reveals the smallest useful explicit-control contract.

Once the Arca Mechanica slice proves that interaction on a real device, the next decision is whether to expand the historical corpus or open the narrow instrument-control bridge into the frozen Ghost for `NEO-ARCA` mode.
