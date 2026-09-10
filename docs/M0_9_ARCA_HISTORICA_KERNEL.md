# M0.9 — ARCA HISTORICA executable kernel

**Status:** implemented on the archaeology line after M0.8.1.  
**Scope:** one verified Syntagma-I / Pinax-IV historical fragment only.  
**Separation rule:** this module does not import or call the Neo-Arca Ghost.

## Purpose

M0.9 crosses the project from historical-data staging into a real, auditable execution path. It combines only project-owned records already promoted under `docs/HISTORICAL_DATA_TRANSCRIPTION_SPEC.md`:

- `historical_data/syntagma1_pinax04/vperm01_printed_p83_verified.json`
- `historical_data/syntagma1_pinax04/rhythm_duple_rperm03_printed_p83_verified.json`
- `historical_data/mensa_tonographica/tone02_hypodorius_printed_p51_verified.json`
- `historical_data/source_witnesses.json`

The executable is `scripts/arca_historica_kernel.py`.

## Historical chain

The kernel evaluates the bounded historical chain directly:

```text
Syntagma I / Pinax IV / Stropha I / Vperm01
        +
Pinax IV / duple Rperm03
        +
Mensa Tonographica / printed p.51 / Tone II Hypodorius
        ↓
verified symbolic four-voice event stream
```

The verified Vperm is:

```text
Cantus  553233
Altus   875777
Tenor   323455
Bassus  858733
```

The verified rhythm is:

```text
minim, minim, minim, minim, semibreve, semibreve
relative minim units: 1, 1, 1, 1, 2, 2
```

The selected witness-specific tone lookup is:

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

Therefore the first kernel result is:

```text
pos  off  dur  glyph       cantus  altus  tenor  bassus
  1    0    1  minim       5:D     8:G    3:Bb   8:G
  2    1    1  minim       5:D     7:F#   2:A    5:D
  3    2    1  minim       3:Bb    5:D    3:Bb   8:G
  4    3    1  minim       2:A     7:F#   4:C    7:F#
  5    4    2  semibreve   3:Bb    7:F#   5:D    3:Bb
  6    6    2  semibreve   3:Bb    7:F#   5:D    3:Bb
```

Total duration is **8 relative minim units**. This is a symbolic mensural ratio, not a modern tempo declaration.

## Validation contract

Canonical execution is evidence-gated. Before producing an event, the kernel requires each component to be `canonical: true` and `verification_status: verified`, and then verifies rather than trusting those flags.

It checks:

- a declared transcription protocol;
- at least two independent primary witnesses per component;
- witness IDs and independence keys against the repository witness ledger;
- direct-inspection status for each active witness;
- a public-domain assertion in the ledger;
- `all_cells_verified: true`;
- no editorial correction in the selected `PRINT_1650` path;
- complete cell coverage and stable structural paths;
- agreement between active values, component arrays/maps, and witness readings;
- Vperm voice order and scale-degree range;
- witness-specific Tone-II identity;
- rhythm glyph/duration normalization and event count;
- Vperm/Rperm Syntagma-Pinax compatibility;
- a common transcription protocol across all three components.

M0.8 records use compact per-cell witness dictionaries for Vperm and tone data, while M0.8.1 rhythm cells use explicit `witness_readings` arrays with source locators. The kernel accepts both historical shapes without weakening the evidential gate.

## Provenance of output

Every emitted voice event carries both:

- its Vperm cell path; and
- the exact Tone-II cell path used to resolve its degree.

Every shared rhythm event carries its Rperm cell path. The top-level result also identifies the component records and all primary witnesses used by the three components.

The output format is:

`neo-arca-historica-symbolic/v1`

The initial edition policy is:

`PRINT_1650`

## Explicit non-claims

M0.9 does **not** invent or infer:

- absolute octave/register placement;
- MIDI note numbers;
- BPM or absolute tempo;
- a modern beat-unit interpretation;
- phrase-level musica ficta beyond accidentals already encoded by the selected printed-p.51 tone witness;
- SATB repairs from the Ghost;
- identity with Kircher's prose `Ave maris stella` worked example.

The last point is important: the verified Vperm01 used here is a real Pinax-IV permutation, but it is not the same degree sequence as the separate prose worked example. The first M0.9 result is therefore described only as a **Pinax-IV historical fragment**.

## Verification

Focused M0.9 acceptance suite:

```text
python -m py_compile scripts/arca_historica_kernel.py
pytest -q tests/test_arca_historica_kernel.py
python scripts/arca_historica_kernel.py
```

The focused suite covers deterministic exact output, event-level provenance, absence of modern realization fields, rejection of noncanonical or unverified components, unknown/duplicate witness authority, silent editorial correction, incompatible event counts, invalid degrees, tone-map disagreement, rhythm-witness disagreement, and input immutability.

The implementation environment used for this pass could not clone GitHub directly because DNS resolution to GitHub was unavailable. The module and focused tests were therefore executed in an isolated local mirror of the exact M0.8/M0.8.1 record shapes fetched through the authenticated GitHub connector. No claim is made that the full pre-existing repository test suite was executed in that environment.

## Next gate

Once this kernel is committed and preserved on a non-destructive historical baseline, the project should stop extending backend archaeology horizontally and begin the bounded **Arca Mechanica** vertical slice:

`open cabinet → retrieve real column-rods → arrange/slide → choose Vperm/Rperm → resolve through Tonus → show the M0.9 symbolic result`

The first physical slice must consume the historical kernel directly when in `ARCA HISTORICA`. It must not display authentic historical rods while secretly calling the Neo-Arca Ghost.
