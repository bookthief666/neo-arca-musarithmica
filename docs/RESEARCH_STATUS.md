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
- `M0_6_PRIMARY_TEXT_CORRECTIONS.md` — current authority for the historical physical-control topology where it conflicts with earlier simplified “pinax-as-slat” language. Kircher's stored/manipulated units are separate musarithmic columns copied from pinakes onto paper/wood carriers and arranged/slid as a combinatorial instrument.
- `PRODUCT_DIRECTION_M0_2.md` — product authority: the first playable Neo-Arca is an instrument-first musical interface, not a semantic prompt-to-music product.
- `M0_3_INSTRUMENT_CONTROL_TOPOLOGY.md` — modern musical-control map, interpreted through the M0.6 physical correction.
- `HISTORICAL_DATA_TRANSCRIPTION_SPEC.md` — binding protocol for project-owned `ARCA HISTORICA` data.
- `historical_data/source_witnesses.json` — machine-readable primary-witness/navigation ledger.
- `PROVENANCE.md` — H0/H1/N1/HÆRETIC vocabulary and provenance rules.
- `PHASE1_ACCEPTANCE.md` — B10 release snapshot; do not rewrite it retroactively.

## M0.8 evidence checkpoint

The M0.7 follow-up research session directly inspected printed p.83 / Pinax IV and printed p.51 / Mensa Tonographica in two separate 1650 digitizations:

1. Bayerische Staatsbibliothek München, call number `2 Mus.th. 264-2`, Internet Archive identifier `bub_gb_97xCAAAAcAAJ`.
2. EPFL Library, Internet Archive identifier `chepfl-lipr-AXC19_02`, DOI `10.26035/epfl-plume-1455`.

Both Internet Archive records identify the 1650 volume and Public Domain Mark 1.0. The EPFL scan metadata reports 600 ppi. These witnesses are now recorded explicitly in `historical_data/source_witnesses.json`.

This repository update records the direct-inspection findings from that checkpoint. It does not falsely claim that the committing assistant independently re-read each glyph a third time.

## Verified historical data

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

The old Chierotti secondary reading `868733` for the Bassus row remains in `discrepancies.json` as permanent discrepancy history. It is not deleted merely because the independent primary witnesses resolve the printed value as `858733`.

### Mensa Tonographica / printed p.51 / Tone II Hypodorius — VERIFIED FOR THIS WITNESS

The two primary copies agree on the printed-p.51 Tone-II mapping:

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

This corrects an important limitation in the earlier staging file, which reduced the table to uninflected source letters plus a generic `mollis` interpretation. The staging file is retained unchanged as research history.

**Witness identity remains mandatory.** This record establishes the printed p.51 Mensa Tonographica, not the later Iconismus XIV tone-table witness. Do not silently collapse the two.

## Rhythm status — STILL NOT CANONICAL

The immediate blocker is Syntagma I / Pinax IV / Stropha I / `Notae Temporis` / duple Rperm 01.

The preferred research reading remains:

```text
semibreve_dotted, minim, minim, minim, semibreve, semibreve
relative units: 3, 1, 1, 1, 2, 2
```

Two primary p.83 copies were inspected during the M0.7 follow-up, but the first semibreve's small augmentation punctus was not unambiguous enough at the available rendering to satisfy the project's primary-source verification rule. A modern Cashner transcription supports the dotted reading, but secondary agreement cannot promote the row.

Explicit ambiguity record:

`historical_data/syntagma1_pinax04/rhythm_duple_rperm01_ambiguity.json`

Therefore the existing whole `Ave maris stella` symbolic preview remains **NONCANONICAL**.

## Canonical rendering gate

`scripts/historical_symbolic_preview.py` now treats provenance as data, not as a Boolean assertion.

Setting:

```json
{"canonical": true}
```

is no longer sufficient to enter the canonical path.

A canonical symbolic record must carry:

- a protocol version;
- at least two directly inspected primary witnesses;
- distinct witness IDs and independence keys;
- nonempty source locators;
- verified `pitch_permutation`, `tone_lookup`, and `rhythm` components;
- at least two primary witness readings for every active cell;
- stable cell paths;
- `active_value_origin: source_reading`;
- no silently applied editorial correction.

The first canonical policy intentionally rejects editorial substitution. A future critical-edition policy may support explicit repaired readings, but that must be a separate, declared policy rather than a hidden mutation of historical source data.

## What remains unresolved

- The augmentation dot on the first sign of Pinax-IV duple Rperm 01.
- Exact octave/register placement for the worked four-part example.
- Phrase-level musica-ficta beyond the verified printed-p.51 tone-table mapping.
- Direct comparison with the later Iconismus XIV tone table.
- Syntagma II Pinax II primary table grammar at useful resolution.
- Comparative physical details of additional surviving Arca objects where those details would materially affect reconstruction.

## Next gate

Do not bulk-transcribe the corpus and do not begin the large frontend yet.

The shortest path to the first genuine ARCA HISTORICA computation is now:

**verified p.83 Vperm01 + verified p.51 Tone-II lookup + verified p.83 duple Rperm01**

Only the rhythm glyph remains blocking.

Once a higher-resolution public-domain primary crop resolves the first augmentation punctus, create a versioned verified rhythm record, assemble a canonical symbolic phrase with complete component provenance, run the canonical provenance tests, and render the first auditable four-voice historical symbolic fragment.

Absolute MIDI pitch and modern BPM are not required for that threshold and must not be invented merely to make the phrase audible.
