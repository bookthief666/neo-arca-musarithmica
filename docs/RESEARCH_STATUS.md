# RESEARCH_STATUS.md — Current historical authority

**Current archaeology branch:** `feature/m0.1-primary-arca-archaeology`  
**Ghost/backend freeze point:** `8869e2738d2b31f2682a5b1d30913baa6a8a12e2` (B10)  
**Permanent Ghost baseline:** `baseline/phase1-ghost-b10`  
**M0.1 dossier baseline:** `1577d46ad2b2ca109072c2cb66a11d33eac0bdca`  
**Physical-topology correction:** `docs/M0_6_PRIMARY_TEXT_CORRECTIONS.md`

This file identifies the latest historical authority for implementation. Earlier M0 documents remain part of the research record but must not override later primary-source findings.

## Governing documents

- `HISTORICAL_RESEARCH.md` — historical first-pass record from the source-restricted environment.
- `VISUAL_RECONSTRUCTION.md` — first-pass visual uncertainty register.
- `M0_1_PRIMARY_ARCA_RECONSTRUCTION.md` — primary visual/object archaeology dossier.
- `M0_6_PRIMARY_TEXT_CORRECTIONS.md` — current authority for historical physical-control topology where it conflicts with earlier simplified “pinax-as-slat” language. Kircher's stored/manipulated units are separate musarithmic columns copied from pinakes onto paper/wood carriers and arranged/slid as a combinatorial instrument.
- `PRODUCT_DIRECTION_M0_2.md` — product authority: the first playable Neo-Arca is an instrument-first musical interface, not a semantic prompt-to-music product.
- `M0_3_INSTRUMENT_CONTROL_TOPOLOGY.md` — modern musical-control map, interpreted through the M0.6 physical correction.
- `HISTORICAL_DATA_TRANSCRIPTION_SPEC.md` — binding protocol for project-owned `ARCA HISTORICA` data.
- `historical_data/source_witnesses.json` — machine-readable primary-witness/navigation ledger.
- `PROVENANCE.md` — H0/H1/N1/HÆRETIC vocabulary and provenance rules.
- `PHASE1_ACCEPTANCE.md` — B10 release snapshot; do not rewrite it retroactively.

## M0.8 verified pitch/tone checkpoint

M0.8 recorded direct comparison of printed p.83 / Pinax IV and printed p.51 / Mensa Tonographica in two separate 1650 digitizations:

1. Bayerische Staatsbibliothek München, call number `2 Mus.th. 264-2`, Internet Archive identifier `bub_gb_97xCAAAAcAAJ`.
2. EPFL Library, Internet Archive identifier `chepfl-lipr-AXC19_02`, DOI `10.26035/epfl-plume-1455`.

Both are independent primary print witnesses. EPFL metadata reports a 600-ppi scan.

### Syntagma I / Pinax IV / Stropha I / Vperm 01 — VERIFIED

Two independent primary copies agree on:

```text
Cantus  553233
Altus   875777
Tenor   323455
Bassus  858733
```

Canonical project record:

`historical_data/syntagma1_pinax04/vperm01_printed_p83_verified.json`

The old Chierotti secondary reading `868733` for the Bassus row remains in `discrepancies.json` as permanent discrepancy history.

### Mensa Tonographica / printed p.51 / Tone II Hypodorius — VERIFIED FOR THIS WITNESS

The two primary copies agree on:

```text
1 G
2 A
3 B♭
4 C
5 D
6 E♭
7 F♯
8 G
```

Canonical witness-specific record:

`historical_data/mensa_tonographica/tone02_hypodorius_printed_p51_verified.json`

The prior staging file remains unchanged as research history. This record establishes the printed p.51 Mensa only; the later Iconismus XIV witness must remain independently identified and may disagree.

## M0.8.1 rhythm checkpoint — data-complete historical chain

A third independent 1650 primary witness was inspected:

3. Bibliothèque nationale de France, département Musique / Gallica, shelfmark `RES F-142`, ark `ark:/12148/bpt6k12802862`.

Printed p.83 / Pinax IV was directly inspected in the BnF, EPFL, and BSB copies.

### Rperm 01 — REMAINS AMBIGUOUS

The previously preferred first duple row remains:

```text
semibreve_dotted, minim, minim, minim, semibreve, semibreve
relative units: 3, 1, 1, 1, 2, 2
```

but the small augmentation punctus on its first semibreve is not directly legible enough across the available primary renderings to satisfy the strict promotion rule. The ambiguity record remains authoritative:

`historical_data/syntagma1_pinax04/rhythm_duple_rperm01_ambiguity.json`

No value was chosen by majority vote and no secondary transcription was allowed to close the issue.

### Rperm 03 — VERIFIED

Rather than manufacture certainty about Rperm01, the project selected another historical duple row whose glyphs are materially clearer in all three independently inspected primary copies.

The third duple series reads:

```text
minim, minim, minim, minim, semibreve, semibreve
relative minim units: 1, 1, 1, 1, 2, 2
```

Canonical project record:

`historical_data/syntagma1_pinax04/rhythm_duple_rperm03_printed_p83_verified.json`

The normalization encodes only relative mensural ratios (`minim=1`, `semibreve=2`). It does **not** claim BPM, a modern beat unit, or MIDI duration.

This means the smallest historical data chain is now complete:

```text
verified Pinax-IV Vperm01
        +
verified Pinax-IV duple Rperm03
        +
verified printed-p.51 Tone-II lookup
        ↓
four symbolic historical voices
```

## Canonical rendering gate

`scripts/historical_symbolic_preview.py` treats provenance as evidence, not as a Boolean assertion. A top-level `"canonical": true` flag is insufficient.

The current strict policy requires:

- an explicit transcription protocol;
- at least two directly inspected independent primary witnesses;
- distinct witness IDs and independence keys;
- nonempty locators;
- verified component/cell status;
- active values originating in source readings;
- no silent editorial correction;
- sufficient per-cell witness readings.

A future critical-edition mode may explicitly apply documented repairs, but that must be a separate named policy.

## What remains unresolved

- The augmentation punctus on Pinax-IV duple Rperm01.
- Exact octave/register placement for the four voices.
- Phrase-level musica-ficta beyond values explicitly carried by the selected tone-table witness.
- Direct comparison with the later Iconismus XIV tone table.
- Syntagma II Pinax II primary grammar at useful resolution.
- Comparative physical details of additional surviving Arca objects where they materially affect reconstruction.

These are no longer blockers for the first **symbolic** ARCA HISTORICA kernel.

## Next gate — M0.9

Do not bulk-transcribe the corpus and do not begin the large frontend yet.

Implement the smallest real `ARCA HISTORICA` executable kernel, entirely separate from the Neo-Arca Ghost:

```text
verified Vperm01
+ verified Rperm03
+ verified printed-p.51 Tone II
→ four deterministic symbolic voices
```

The kernel must:

- consume only verified project-owned records;
- reject staging/noncanonical components;
- resolve scale degrees through the selected historical tone witness;
- apply the shared Syntagma-I rhythm without converting it to modern BPM;
- emit source/witness provenance with the result;
- perform no SATB repair or substitution through the Ghost;
- invent no octave, MIDI pitch, modern tempo, or hidden ficta.

The first executable fragment should be described as a **Pinax-IV historical fragment**, not as Kircher's exact `Ave maris stella` worked example: the verified Vperm01 rows differ from the separate degrees reported in Kircher's prose worked example.

Once this kernel passes its focused tests, create a non-destructive historical baseline and begin the bounded Arca Mechanica physical vertical slice around real column-rods.
