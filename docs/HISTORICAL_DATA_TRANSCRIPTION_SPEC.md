# M0.4 — Historical Data Transcription Specification

**Status:** binding research/data protocol for any future `ARCA HISTORICA` dataset.  
**Branch:** `feature/m0.1-primary-arca-archaeology`.  
**Purpose:** make it possible to encode Kircher's actual 1650 tables without silently copying a modern transcription, correcting the source to taste, or turning uncertain digits into false historical facts.

---

## 1. Governing rule

No numerical or rhythmic table becomes canonical historical data in this repository unless it has been transcribed **independently from a public-domain facsimile of the 1650 source** and carries enough provenance to let another researcher inspect the same mark on the same page.

Andrew A. Cashner's software and transcription are invaluable scholarship and may be used to understand the system and to **cross-check after our own reading**, but his repository is not an open data source for redistribution. Carlo Mario Chierotti's published transcriptions are likewise secondary witnesses, not the canonical source of our dataset.

The public-domain facsimile is the authority. Secondary transcriptions are witnesses to discrepancies.

---

## 2. Current primary-source corpus

### Preferred book witnesses

1. **Internet Archive / UNC Music Library**  
   Identifier: `athanasiikircherkirc`  
   Work: Athanasius Kircher, *Musurgia universalis* (Rome, 1650), vols. I–II in one scan.  
   Scan: 300 ppi, 1262 leaves/pages in the digital object.  
   Item: `https://archive.org/details/athanasiikircherkirc`  
   Full-text OCR and original/processed JP2 files are exposed by the item.  
   Use original or high-resolution processed page images for transcription; OCR is navigation aid only.

2. **Universidad de Valladolid**  
   Volume II, 1650.  
   Handle: `https://uvadoc.uva.es/handle/10324/9140`  
   Repository marks the item Public Domain Mark 1.0.  
   Use as an independent facsimile witness whenever a mark in the UNC scan is ambiguous.

3. **Cornell University Library — Arca engraving**  
   Record: `https://digital.library.cornell.edu/catalog/ss:550167`  
   Bibliographic locator: vol. II, pp. 184/185, the Arca engraving / Iconismus XIV.  
   Cornell states the 1650 engraving is presumed public domain because of creation date.

### Secondary witnesses — interpretive/cross-check only

- Andrew A. Cashner, *Athanasius Kircher's Arca musarithmica (1650) as a Computational System* (2024).
- `arca1650.info` explanatory documentation.
- Carlo Mario Chierotti, *Comporre senza conoscere la musica* / associated Kircher study site.
- Caspar Schott where historically useful as a seventeenth-century correction/exposition, but never silently substituted for Kircher's printed reading.

---

## 3. First bounded transcription target

Do **not** begin by transcribing the whole Arca.

The pilot corpus is deliberately small:

### A. Syntagma I — Pinax IV

Printed locator: *Musurgia universalis*, vol. II, Book VIII, p./fol. 83.  
Title visible in the table: `PINAX IV. Iambica Euripedaea penultima longa.`

Target components:

- table title and marginal labels;
- four `Stropha`/line regions;
- all musarithm/Vperm rows only after the page image is readable enough for double entry;
- tone-compatibility marks;
- the `Notae Temporis` / rhythmic field;
- any typography or structural separators needed to reconstruct the pinax faithfully.

### B. Mensa Tonographica

Pilot only needs the tone information required to turn the selected Pinax-IV scale degrees into letter names/accidentals.

Important source problem: modern scholarship notes that the tone table printed around Book VIII p. 51 and the later engraved table on the Arca plate do **not** fully agree. Cashner reports using the engraving-facing-p.185 version because it appears to correct errors in the earlier table. Our data model must therefore preserve the witness identity rather than pretending there is one self-evident table.

### C. Syntagma II — Pinax II, inspection before transcription

Printed locator: vol. II, Book VIII, fol. 106.  
This is not yet part of the pilot executable corpus. First obtain and inspect a sufficiently legible primary page to establish the florid pinax's visual/data grammar.

Scholarship establishes that Syntagma II pairs four-voice pitch permutations with four-voice rhythm permutations and may give different note counts to different voices. That statement guides inspection; it is not a substitute for direct transcription.

---

## 4. Two-pass transcription rule

Every canonical cell is entered twice from the source image.

### Pass A — diplomatic reading

The transcriber reads the facsimile and records exactly what appears to be printed.

Rules:

- do not consult a modern transcription while entering;
- preserve apparent printer errors;
- preserve repeated digits exactly;
- do not normalize an implausible voice-leading result into a plausible one;
- for unreadable content, record `null` / `?` with uncertainty metadata rather than guessing;
- note damaged, blurred, cropped, obscured or malformed glyphs.

### Pass B — independent verification

A second pass must be performed without looking at Pass A's cell values if practical. It may be by another researcher/model or by the same researcher after context separation, but it must be operationally independent enough to catch visual expectation errors.

Only exact A/B agreement promotes a reading automatically to `verified`.

### Reconciliation

If A and B disagree:

1. inspect the primary page at higher resolution or another public-domain scan;
2. record both candidate readings;
3. inspect secondary scholarship only **after** the independent readings exist;
4. record the secondary witness separately;
5. mark a resolved value only when the evidence supports it;
6. never overwrite the source-reading history.

---

## 5. Source-reading versus editorial interpretation

The data model must distinguish:

- `source_reading`: what the 1650 witness appears to print;
- `normalized_reading`: machine-friendly representation of the same mark;
- `editorial_correction`: optional proposed correction;
- `correction_basis`: why a correction is proposed;
- `active_value`: which value the HISTORICA engine is instructed to use under a named edition policy.

Example conceptually:

```json
{
  "source_reading": "8",
  "normalized_reading": 8,
  "editorial_correction": null,
  "status": "verified"
}
```

or, for a disputed cell:

```json
{
  "source_reading": "8?",
  "normalized_reading": null,
  "editorial_correction": 6,
  "correction_basis": [
    "second public-domain facsimile reads 6",
    "secondary witness reads 6"
  ],
  "status": "disputed"
}
```

The UI should eventually be able to show the difference between **Kircher-as-printed** and a **critical/repaired** realization rather than erasing it.

---

## 6. Required provenance per transcribed unit

At minimum each pinax/table record must contain:

```text
work
edition
publication_place
publication_year
volume
book
printed_page_or_folio
source_repository
source_identifier
source_url
scan_leaf_or_image_locator      # once established
source_image_filename           # if known
source_image_checksum           # if we store an allowed local derivative
crop_locator                    # optional coordinates for a cell/row crop
transcription_passes[]
verification_status
transcription_date
transcription_protocol_version
notes
```

Each row/cell should carry a stable path such as:

```text
S1.P4.STROPHA1.VPERM01.CANTUS.N01
S1.P4.STROPHA1.VPERM01.ALTUS.N01
S1.P4.NOTAE_TEMPORIS.DUPLA.RPERM01.N01
```

The path must describe **structure**, not a page-coordinate accident.

---

## 7. Confidence vocabulary

Use a small controlled vocabulary rather than fake numeric precision:

- `verified` — independent primary-source readings agree.
- `probable` — primary source is readable but one feature remains uncertain.
- `ambiguous` — two or more readings are genuinely possible.
- `unreadable` — source quality is insufficient.
- `editorial` — value is a correction/normalization, not what the witness literally prints.

A canonical `ARCA HISTORICA` release should consume only `verified` source values unless a named edition policy explicitly allows editorial repairs.

---

## 8. The known Pinax-IV discrepancy — use it as the protocol's first test

There is already a useful warning case in the scholarship around the beginning of Pinax IV.

A secondary transcription on Chierotti's site presents a first set of six-digit voice rows beginning with values including:

```text
553233
875777
323455
868733
```

Cashner's discussion/code excerpt available in his publication appears to disagree in at least one position in the corresponding material, while the reproduced facsimile is visually difficult enough that a digit can plausibly be misread at small scale.

**Do not resolve this discrepancy from either secondary source.**

This is exactly why M0.4 exists. The first high-resolution public-domain Pinax-IV page should be read independently twice. Only then should the secondary readings be compared and the discrepancy recorded.

No numbers from the block above are canonical project data yet.

---

## 9. Rhythm transcription requirements

Rhythm is more difficult than digits because glyph identity, mensural context, dots, rests and ligatures matter.

Do not reduce a rhythm symbol immediately to a modern floating-point duration.

Record at least:

```text
source_glyph_class
source_modifiers
rest_or_note
mensuration_context
position_in_rperm
normalized_duration_ql        # derived layer, not diplomatic source
normalization_rule
confidence
```

When a glyph is ambiguous, preserve the ambiguity.

For Syntagma I, maintain the historical fact that one selected rhythm series applies to all four voices. For Syntagma II, preserve the per-voice paired rhythm structures rather than flattening them into one shared rhythm.

---

## 10. Tone-table transcription requirements

A tone entry must preserve more than a modern scale name.

Store:

```text
tone_number
historical_name
durus_or_mollis
final
numerus_to_pitch_mapping[1..8]
printed_accidental_marks
affect_description_source
witness              # p.51 table, Iconismus/engraving, etc.
source_status
editorial_notes
```

Do not collapse historical `tonus` into the project's seven modern modes. A Neo-Arca `mode` and an Arca-Historica `tonus` are different entities even when they can be compared analytically.

---

## 11. Machine-readable schema — target shape

The pilot JSON should eventually resemble:

```json
{
  "schema": "arca-historica-transcription/v1",
  "record_id": "MU1650-B8-S1-P4",
  "provenance": {},
  "title": {},
  "tones_allowed": {},
  "strophes": [
    {
      "index": 1,
      "vperms": [
        {
          "index": 1,
          "voices": {
            "cantus": {"cells": []},
            "altus": {"cells": []},
            "tenor": {"cells": []},
            "bassus": {"cells": []}
          }
        }
      ]
    }
  ],
  "rperms": [],
  "discrepancies": [],
  "verification": {}
}
```

Do not create populated Vperm/Rperm records until primary-page readings satisfy the protocol.

---

## 12. OCR policy

Internet Archive OCR is useful for locating Book VIII sections and printed page numbers. It is **not an acceptable source for table digits or music notation**.

This pass has already used the public-domain UNC scan's OCR to independently confirm several pieces of Book VIII's prose structure, including:

- the description of Syntagmata I–III and Pinax II of Syntagma II;
- Kircher's statement that Syntagma III material was omitted from the printed work;
- `Per distincta membra...` as an explicit procedure;
- the p. 63–65 demonstration of mutating the same assumed theme through different `toni`;
- the p. 65–66 discussion of changing `notae metrometrae` / rhythmic values.

Those prose confirmations strengthen M0.2/M0.3's control topology. They do **not** authorize OCR-derived musical table data.

---

## 13. Critical-edition policies for the future engine

`ARCA HISTORICA` should eventually expose an explicit edition policy rather than one hidden repaired dataset:

### `PRINT_1650`

Use the 1650 witness literally where verified, including apparent source errors. The UI flags suspect readings but does not repair them silently.

### `CRITICAL`

Use documented editorial corrections where the source is demonstrably erroneous or a stronger contemporary witness supports a correction. Every changed cell remains inspectable.

### `NEO_REPAIR`

Permit the modern solver to repair historically sourced material that violates the current Neo-Arca law. This is **N1**, never described as Kircher's output.

These policies let the project turn textual instability into a scholarly and musical feature instead of hiding it.

---

## 14. Acceptance gate for the pilot

The first historical dataset is accepted only when:

1. a high-resolution public-domain Pinax-IV page has been directly inspected;
2. its pilot cells have two independent primary-source readings;
3. every disagreement is recorded, not averaged away;
4. at least one independent public-domain tone-table witness has been inspected at useful resolution;
5. source locators are sufficient for another researcher to reproduce the reading;
6. no Cashner/Chierotti transcription has been copied wholesale;
7. tests validate schema integrity and reject unresolved cells from a strict HISTORICA execution path;
8. the UI can tell `FACSIMILE_REFERENCE`, `HISTORICA_DATA`, and `NEO_WORKING_PINAX` apart.

Until that gate is met, the historical table remains research material rather than executable authority.