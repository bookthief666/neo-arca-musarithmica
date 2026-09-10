# Historical data

This directory is reserved for **project-owned primary-source transcriptions** of
Athanasius Kircher's *Musurgia universalis* (Rome, 1650) and closely related witnesses.

It is intentionally separate from the Neo-Arca generative engine. Nothing under this
directory becomes executable `ARCA HISTORICA` authority merely because a file exists.

## Governing protocol

Read `docs/HISTORICAL_DATA_TRANSCRIPTION_SPEC.md` before adding or changing any musical
cell.

Canonical rule:

> Transcribe independently from a public-domain facsimile first. Consult modern
> transcriptions only afterward as secondary witnesses.

Do not copy the numerical/rhythmic datasets from Andrew A. Cashner's implementation or
other modern transcriptions into this repository.

## States

- `scaffold` — source/provenance/structure only; not executable.
- `in_transcription` — one or more primary-source readings exist, but verification is
  incomplete.
- `verified` — the record satisfies the M0.4 two-pass protocol for the material marked
  verified.
- `disputed` — a primary reading or witness conflict remains unresolved.
- `blocked` — source quality/access is insufficient.

A strict historical engine must consume only values whose individual readings are
`verified`, unless it is explicitly running a named critical/editorial policy.

## Layout

```text
data/historical/
├── README.md
├── schema/
│   └── arca-historica-transcription-v1.schema.json
└── pilot/
    └── MU1650-B8-S1-P4.json
```

The Pinax-IV pilot is deliberately a **blank musical-data scaffold** until a legible
public-domain page has been inspected twice. Its empty Vperm/Rperm arrays are a feature,
not missing implementation.

## Provenance modes in the eventual application

Keep these visibly distinct:

- `FACSIMILE_REFERENCE` — authentic source image/table shown for inspection; may be
  non-executable.
- `HISTORICA_DATA` — project-owned verified transcription driving historical computation.
- `NEO_WORKING_PINAX` — historically informed anatomy carrying Neo-Arca data/controls.

Never display a real Kircher row and let unrelated Neo-Arca generation masquerade as the
result of that row.

## Primary witnesses currently targeted

- Universitätsbibliothek Heidelberg, *Musurgia universalis* vol. II,
  DOI `10.11588/diglit.27669`, Public Domain Mark.
- Universidad de Valladolid, vol. II, handle `10324/9140`, Public Domain Mark 1.0.
- Cornell University Library, 1650 Arca engraving, record `ss:550167`.

Internet Archive/UNC (`athanasiikircherkirc`) remains a useful independent scan and OCR
navigation witness, but OCR must never be used to establish table digits or notation.
