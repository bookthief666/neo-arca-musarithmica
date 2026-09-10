# M0.1 — Primary Arca Reconstruction Dossier

**Status:** primary-source / object-evidence archaeology pass, 2026-09-09.  
**Repository state when begun:** Phase-1 Ghost accepted at `8869e2738d2b31f2682a5b1d30913baa6a8a12e2`.  
**Purpose:** establish the physical and informational anatomy of Athanasius Kircher's *Arca musarithmica* strongly enough that a frontend can reconstruct the **instrument itself**, rather than invent a modern dashboard and apply a Baroque skin.

This document supersedes the visual-research limitation recorded in the first M0 pass. That pass could not inspect any page or image directly. This pass **did inspect visual and textual evidence**, including the 1650 Arca engraving, a 1650 *pinax* table reproduced from *Musurgia universalis*, the Herzog August Bibliothek catalogue entry for the Wolfenbüttel object, and a published photograph of that surviving cabinet. The earlier uncertainty register remains useful, but several questions can now be closed or narrowed.

---

## 0. Evidence classes used in this dossier

The repository's existing H0/H1/N1/HÆRETIC vocabulary is retained, with one useful refinement for this pass:

- **H0-V** — directly observed in a 1650 visual source or surviving-object record.
- **H0-T** — directly stated in Kircher's text as quoted/reproduced by a scholarly source, or directly legible in a 1650 table.
- **H0-O** — directly documented by the holding institution for a surviving object.
- **H1** — strong scholarly interpretation or reconstruction, not directly observed in the required detail.
- **N1** — Neo-Arca extension: our digital continuation, not Kircher's historical mechanism.
- **HÆRETIC** — deliberate transgression belonging to Modus Hæreticus.

A visual reconstruction may use H0-V/H0-O geometry as its bones, H1 only where declared, and N1 only where the interface visibly crosses from reconstruction into the imagined 376-year continuation.

---

## 1. Primary / near-primary records actually inspected

### 1.1 Kircher's canonical Arca engraving — 1650

**Source:** Athanasius Kircher, *Musurgia universalis*, vol. II, engraving facing p. 185.  
**Cornell record:** https://digital.library.cornell.edu/catalog/ss:550167  
**Cornell ID:** RMC2007_1212.  
**Bibliographic locator:** Vol. II pp. 184/185.  
**Rights:** Cornell states the engraving is presumed public domain because of creation date.  
**Cross-check:** Andrew A. Cashner, 2024, Fig. 1, identifies the same image as *Musurgia universalis* II, facing p. 185.

**What is visible:**

1. The Arca is represented as a **rectangular portable box/cabinet shown open**, not as a keyboard instrument or clockwork machine. **H0-V**.
2. A broad, raised/sloping upper surface is covered by a dense ruled reference table. Cashner identifies the lid table as the **mensa tonographica / table of toni** used to translate musarithmic numbers into pitch names and potential accidentals. **H0-V + H1 identification**.
3. The open body contains a dense bank of **long, narrow labelled elements**, presented as the stored working material of the machine. These correspond to the *pinakes* / slats described in Book VIII. **H0-V/H0-T**.
4. The lower front-facing informational region contains the **Scala Musica / palimpsest phonotacticum** material associated with the four vocal parts and their clefs/ranges. Cashner explicitly identifies the front chart as the device used to place pitch classes into octaves and acceptable vocal ranges. **H0-V/H0-T**.
5. The engraving is an **instructional idealisation**, not a construction drawing. It communicates the relationship between lid reference data, stored slats, and front notation/range aid more clearly than it specifies joinery, depth, exact hardware, or scale. **H1**.
6. The lower field of the plate also includes drawings/labels of musical instruments. They are part of the printed explanatory composition of the engraving; this pass found no evidence that such instrument pictures were physical ornament applied to surviving Arca cabinets. **Do not model them as cabinet hardware.**

### 1.2 Syntagma I, Pinax IV — 1650 table image

**Source:** *Musurgia universalis*, Book VIII, Syntagma I, Pinax IV, fol./p. 83; reproduced as Fig. 2 in Cashner 2024.  
**Visible title:** `PINAX IV. Iambica Euripedaea penultima longa.`  
**Cross-reference:** https://www.arca1650.info/doc/Arca_musarithmica-Syntagma1-Pinax04.html

This is the most important single visual source for how a working *pinax* should look.

Observed anatomy:

- It is a **tall, narrow, densely ruled table**, appropriate to mounting on or reproducing as a long slat. **H0-V**.
- The table is divided into **four major vertical columns**, labelled for successive `Stropha` positions. Scholarship clarifies that Kircher's `stropha` in this context functions as successive **poetic lines**, not whole modern stanzas. **H0-V/H1**.
- Each major column contains repeated blocks of **four numeric rows**. These four rows encode the four vocal parts; the digits are scale-degree lookup values rather than literal pitches. **H0-V/H0-T**.
- The upper numeric field is followed by a clearly separated lower field labelled **`Notae Temporis`**, containing rhythmic note/rest symbols rather than pitch-number strings. **H0-V**.
- The pinax therefore visually embodies the historical separation between **pitch permutation** and **rhythm permutation**. In Syntagma I the four voices share one rhythm pattern; the numerical four-part sonority/melodic data and the rhythmic list are selected separately. **H0-T**.
- Tone applicability is indicated in or around the table. For Pinax IV, modern scholarly documentation gives I, II, III, IV, IX, X as accepted tones. **H1 until re-transcribed directly from the plate at full resolution**.

This layout must strongly influence the digital rod/slat. A Neo-Arca pinax that becomes a generic card with a title and a few buttons would throw away the most distinctive information design in the original machine.

### 1.3 Wolfenbüttel surviving object — institutional record

**Holding institution:** Herzog August Bibliothek, Wolfenbüttel.  
**Catalogue:** Cod. Guelf. 90 Aug. 8°; Heinemann-Nr. 3876.  
**Institutional record:** https://diglib.hab.de/?db=mss&id=90-aug-8f&lang=en&list=ms

The HAB catalogue describes the object as:

- a seventeenth-century **wooden box designed to fold/open** (`ein zum Aufklappen eingerichteter Holzkasten`); **H0-O**;
- **23 × 14.5 cm** in the two dimensions recorded by the catalogue; **H0-O**;
- associated with Athanasius Kircher's *Musurgia*; **H0-O**.

The documentation page notes that the manuscript/object Kircher dedicated to Duke August in **1660** has a parallel in Vienna (Cod. Vindob. 9536). The exact relationship of that Vienna manuscript to a physical Arca is not established here; do not infer another surviving cabinet from that remark alone.

**Critical consequence:** the Wolfenbüttel object is not a large furniture cabinet. It is a compact, portable scholarly instrument. A 23 cm dimension is comparable to a small book or desktop case. The digital reconstruction should therefore read first as an **intimate hand-operated box**, even if the camera and spatial presentation make it monumental on screen.

### 1.4 Wolfenbüttel surviving object — published photograph

A scholarly publication hosted by the Library of Congress reproduces a photograph captioned as Kircher's Arca presented to Augustus the Younger, Duke of Brunswick-Lüneburg, with permission from the Herzog August Bibliothek and the same shelfmark, Cod. Guelf. 90 Aug. 8°.

**LOC-hosted PDF:** https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/16/01/57/14/2016015714/2016015714.pdf  
**Figure:** 36 (p. 128 in the indexed text).

The photograph shows:

- a **tall rectangular wooden box**, open upward; **H0-V**;
- a visibly aged, relatively plain wood exterior rather than an ornate black-and-gold reliquary; **H0-V**;
- numerous **small labelled slips/slats** arranged in ordered rows inside; **H0-V**;
- a substantial closed lower/front wooden portion beneath the exposed slat bank; **H0-V**.

Cashner's 2024 study independently states that the **Wolfenbüttel and Cambridge implementations are wooden boxes with paper slats inside holding Kircher's tables of numbers and notes**. This resolves an important material question left open in the first M0 pass: at least these surviving implementations used **paper-bearing slats inside wooden cases**, not engraved brass plates or luminous exotic materials. **H1 supported by object photograph**.

Modern museum/object photography is **reference evidence only** unless a specific reuse licence is obtained. It should not be bundled into the application.

### 1.5 Full 1650 volume scan

**Universidad de Valladolid:** *Athanasii Kircheri... Musurgia universalis... tomus II* (Rome, 1650).  
https://uvadoc.uva.es/handle/10324/9140  
The repository describes a 462-page folio volume with engraved plates and marks the item **Public Domain Mark 1.0**.

This is the preferred legal source for our own future transcription of the original tables. Cashner's modern transcription/code is not open data for redistribution; if ARCA HISTORICA is built, its Kircher tables should be independently transcribed from a public-domain scan such as this one.

---

## 2. The Arca's physical anatomy — what may now be reconstructed

The evidence supports the following physical hierarchy without invention:

```text
ARCA — portable wooden case
│
├── OPENABLE / FOLDING LID OR UPPER REFERENCE SURFACE
│   └── MENSA TONOGRAPHICA / TONI REFERENCE
│       ├── tone / church-key information
│       ├── pitch-letter lookup
│       └── possible accidentals
│
├── INTERNAL STORAGE BODY
│   ├── SYNTAGMA I — simple, syllabic, homorhythmic
│   │   └── PINAKES selected by poetic metre
│   ├── SYNTAGMA II — florid, melismatic, rhythmically independent
│   │   └── PINAKES selected by poetic metre
│   └── SYNTAGMA III — mixed/rhetorical material, incompletely published
│       └── fragmentary / withheld in the historical specification
│
└── FRONT REFERENCE SURFACE
    └── PALIMPSEST PHONOTACTICUM / SCALA MUSICA
        ├── cantus
        ├── altus
        ├── tenor
        ├── bassus
        ├── clefs / signatures
        └── staff positions used to choose octave/range
```

### What remains uncertain physically

- The 23 × 14.5 cm HAB dimensions are for the Wolfenbüttel exemplar and **must not be universalised** to every historical Arca.
- A third overall dimension/depth has not been established.
- Timber species is not established for the Wolfenbüttel Arca.
- Exact hinge type, clasp, lock, handle, joinery, slat thickness and divider geometry remain unverified.
- The engraving's perspective should not be converted naively into millimetres.
- The exact physical organisation of syntagmata inside each surviving case may differ from Kircher's ideal printed arrangement.

For frontend geometry, these remaining details are **H1 reconstruction decisions** and should be parameterised rather than baked into supposedly historical truth.

---

## 3. The pinax is not a menu item — it is stored musical computation

Cashner's analysis of Book VIII makes the historical interaction unusually explicit. A pinax is not merely a label that chooses a style. It is a **portable data structure** the user physically retrieves from the box.

The operator:

1. prepares a text by dividing it into sections, phrases, words and syllables;
2. chooses style and mood;
3. selects the appropriate **syntagma** from style;
4. matches the poetic metre to the title/label of a **pinax**;
5. **removes the needed pinax/slat from the box and lays it on the work surface**;
6. in most pinakes selects a column according to the line's position in the poem;
7. chooses a **vperm / musarithm row** from the numeric material;
8. in Syntagma I separately chooses a rhythm permutation from the appropriate metrical subtable;
9. in Syntagma II uses paired four-voice pitch and rhythm permutations, allowing each voice its own rhythm;
10. carries the selected numeric scale degrees to the **mensa tonographica** on the lid to recover pitch names / accidentals for the chosen tone;
11. uses the **palimpsest phonotacticum** on the front to choose octave/register for each voice;
12. copies the resulting notes and rhythmic symbols onto music paper.

Cashner describes the historical user as removing pinakes, **laying them out in order and moving them up and down** while selecting the needed data. That is unusually strong evidence for an interface based on physical manipulation rather than menus.

### Important computation distinction

The numerical material does **not** directly store absolute pitch. Its digits are lookup keys. The user must combine:

```text
PINAX NUMBER
    + CHOSEN TONUS
    -> MENSA TONOGRAPHICA
    -> PITCH CLASS / ACCIDENTAL
    + FRONT STAFF / RANGE AID
    -> OCTAVE
    + NOTA TEMPORIS
    -> NOTATED NOTE
```

The original system therefore has a naturally spatial, multi-surface pipeline. We should preserve that topology digitally.

---

## 4. Syntagma I and II require visibly different interaction grammars

### Syntagma I — simple counterpoint

Historically grounded behavior:

- syllabic / homorhythmic four-part writing;
- the four voices share one selected rhythm pattern;
- numeric four-voice permutations and rhythm permutations are stored as distinct fields;
- the operator may choose a pitch permutation and rhythm permutation independently within the allowed column/meter logic.

**Digital implication (N1 presentation, H0 process topology):** selecting a numerical musarithm should illuminate four synchronized voice rows, while the rhythm choice lives in the lower *Notae Temporis* region and applies as one shared temporal lattice.

### Syntagma II — florid counterpoint

Historically grounded behavior:

- florid/melismatic writing;
- pitch and rhythm permutations are paired;
- each of the four voices can carry a different rhythm and number of notes;
- the published system is duple in this syntagma according to Cashner's reconstruction.

**Digital implication:** the same pinax interaction should visibly fracture into four independent temporal streams rather than simply toggling a `florid=true` state.

### Syntagma III — rhetorical / mixed

Kircher advertises a much broader third division but publishes only a small portion and claims to reserve further material for princes and worthy friends. Modern reconstructions treat it as incomplete and difficult or impossible to automate faithfully from the published specification alone.

**Ruling:** do not populate Syntagma III with invented historical tables. In the reconstruction it should be **visibly fragmentary**. A sealed, occluded, incomplete, or partially legible third bank is historically more honest—and aesthetically stronger—than fabricating a complete library of data. Any new content placed there belongs to **N1** or **HÆRETIC** and must be identified as such.

This is one of the rare cases where historical incompleteness itself can become a central piece of interaction design.

---

## 5. The tone table and front staff are active controls, not decoration

The engraving divides essential computation across surfaces:

### Lid — mensa tonographica

The tone table maps the chosen *tonus* and numerical scale-degree key onto pitch names and potential accidentals. Cashner notes that Kircher gives conflicting versions of this table in the book and that the table reproduced with the Arca engraving is the usable one; the Puebla copyist independently chose that usable version. **This discrepancy must be preserved in research provenance when we transcribe it.**

A future historical implementation should therefore store a source locator per cell/table version, not one anonymous `TONES` constant.

### Front — palimpsest phonotacticum / Scala Musica

The front chart is a graphical range/octave calculator. Cashner describes the historical procedure: before placing a note, the operator marks a temporary dot on the appropriate staff line, finds the rhythmic duration, then replaces the dot with the note symbol. The chart presents staff lines, clefs, `cantus durus` / `mollis` signatures and pitch names, constraining the four voices to usable ranges.

This is exceptionally important for Neo-Arca's interface because the backend already has explicit SATB ranges and event-level diagnostics. The front staff can become the historical anchor for those modern computational states instead of creating a detached range slider or piano-roll panel.

---

## 6. Surviving implementations: what we can and cannot generalise

Cashner 2024 reports that three surviving physical implementations in Europe were known before his identification of a fourth, partial implementation in Puebla. His site names **Cambridge, Wolfenbüttel and Florence** as the three European survivals; the Puebla manuscript is a functional subset without a wooden box.

### Wolfenbüttel

**Institutionally verified here.** Wooden fold-open box, 23 × 14.5 cm; published photograph visually inspected; shelfmark established.

### Cambridge / Pepys

Cashner identifies the Cambridge survival as a wooden box with paper slats. The Magdalene College archive demonstrably holds research material concerning an `Arca Musarithmica`, but this pass has **not yet located an institutional catalogue record giving the physical object's dimensions/shelfmark**. Treat current-location and construction details beyond Cashner's statement as H1 until the Pepys Library supplies a direct object record.

### Florence

Cashner cites Erik Boni, “L’arca musurgica di Athanasius Kircher alla Biblioteca nazionale centrale di Firenze,” *Accademie & Biblioteche d’Italia* 15/1 (2020), pp. 7–13, as the modern study of the Florence survival. This pass confirmed the bibliographic reference but did not obtain an institutional object record or inspect that object's photographs. **Still H1 for physical modelling.**

### Puebla

Cashner's 2022 article identifies Biblioteca Palafoxiana manuscript vol. **31.765** as a partial but functional physical implementation, copied around 1690–1695. It contains a practical subset rather than the full system: the tone table, clef/range table, selected Syntagma I pinakes, and selected Syntagma II pinakes. It demonstrates that the **box is not logically necessary**: the computational system survives as an organised set of paper tables. This is crucial evidence that the information architecture—not ornamental cabinetry—is the essence of the Arca.

---

## 7. Materials and visual language: revised ruling

The first M0 pass correctly warned against defaulting to “black-and-gold occult UI,” but lacked object evidence. M0.1 strengthens that ruling.

The historically defensible baseline is:

- **wooden portable case**;
- **paper/slip/slat surfaces** bearing dense black textual/numeric notation;
- ruled tabular structure;
- functional labels in Latin;
- music notation and staff diagrams;
- restrained fittings and wear appropriate to a handled scholarly instrument.

Therefore the visual hierarchy for the application should be:

1. **wood / paper / ink / ruled table / staff notation** — historical body;
2. **subtle brass/metal only where physical fittings require it or where N1 marks the continued technological evolution**;
3. **light as computation** — numbers, ruled cells and voice paths activate from within the historical object;
4. **CRT/digital contamination as tertiary anomaly**, never the base design language.

No generic occult sigils should be added merely to make the device “mystical.” Kircher's real information density is stranger and more distinctive than an invented magical-dashboard vocabulary.

---

## 8. Canonical digital interaction model

This is the interface skeleton the frontend should build around. Historical operations are marked **H**; Neo-Arca transitions are marked **N1**.

```text
CLOSED ARCA / APPROACH                         H1 reconstruction
    ↓ open
LID + STORAGE BODY REVEALED                    H
    ↓
INSCRIBE / PREPARE TEXT                        H topology / N1 free-text UI
    ↓
CHOOSE STYLE → SYNTAGMA                        H
    ↓
PARSE / CHOOSE POETIC METRE                    H / N1 assistance
    ↓
REMOVE MATCHING PINAX                          H
    ↓
PLACE PINAX ON WORK SURFACE                    H
    ↓
CHOOSE LINE / STROPHA COLUMN                   H
    ↓
CHOOSE MUSARITHM / PITCH PERMUTATION           H
    ↓
CHOOSE OR ACCEPT RHYTHM PERMUTATION            H
    ↓
CONSULT TONUS TABLE ON LID                     H
    ↓
RESOLVE RANGE/OCTAVE ON FRONT STAFF            H
    ↓
WRITE / ACCUMULATE FOUR VOICES                 H
    ↓
PLAY / VISUALISE / EXPORT                      N1
```

### Rule: the Arca itself remains the navigation system

A user should not need a conventional sidebar to understand the major stages. The physical surfaces already provide them:

- **lid = tonal lookup / global reference**;
- **internal banks = program/data library**;
- **removable pinax = local generative choice**;
- **front staff = register / inscription logic**;
- **external work surface = temporary composition memory/output**.

The app may provide accessibility equivalents and compact mobile fallbacks, but those are alternate access paths—not the conceptual source of truth.

---

## 9. Mapping the accepted Phase-1 Ghost onto the historical body

The current backend is **NEO-ARCA**, not ARCA HISTORICA. The frontend must not hide this distinction.

A safe mapping is:

| Accepted Ghost concept | Historical body | Classification |
| --- | --- | --- |
| `text` / semantic analysis | manuscript/verse preparation surface | N1 using H process position |
| final `mode` / tonic | lid tonal reference | N1 value mapped through H surface |
| SATB event rows | four-row musarithmic logic / front staff | N1 computation, historically sympathetic |
| density / contour / tension | how pinakes activate / how voice traces behave | N1 |
| Orthodox law | “Lex Musica” operating discipline | N1, not Kircher's encoded table data |
| Modus Hæreticus | impossible/transgressive state of same instrument | HÆRETIC |
| validation diagnostics | physical cell/voice-path response | N1 |
| seed | hidden repeatability index / lot number | N1; do not pretend historical chance was seeded |
| MIDI/export | written music leaves the Arca | N1 continuation |

**Do not print Kircher's actual 1650 numeric tables on a live Neo-Arca slat if the backend is not actually using those numbers.** That would visually imply an algorithmic provenance the software does not have.

Until ARCA HISTORICA has transcribed data, choose one of two honest treatments:

1. **Historical facsimile mode:** real public-domain pinax tables are inspectable as documents, but clearly not driving Neo generation; or
2. **Neo pinax mode:** the slat anatomy is historically faithful, while its live numbers/marks are visibly generated and labelled N1 / Neo-Arca.

The strongest eventual product should support both.

---

## 10. Fold-first / responsive implications

The physical Arca is small, but its information is dense. On the Samsung Galaxy Z Fold class of device, the solution should be **semantic zoom**, not shrinking the entire engraving until unreadable.

Recommended spatial levels:

```text
ARCA
  → SYNTAGMA BANK
    → PINAX
      → STROPHA / COLUMN
        → MUSARITHM ROW
          → FOUR VOICE CELLS / RHYTHM SYMBOLS
```

- **Fold open (~884 px):** show the full open box with legible bank labels; one selected pinax can occupy a reading/work zone without leaving the object.
- **Narrow phone (~344–400 px):** the open Arca becomes a navigable close-up instrument. A pinax may slide toward the camera and fill most of the viewport while the cabinet remains perceptually present behind it.
- Touch targets may be larger than the historical slat geometry, but the enlargement should happen through invisible/transparent hit regions rather than visibly turning each row into a modern button.
- Reading a pinax must temporarily suppress accidental orbit/drag gestures.

---

## 11. Rights / asset policy

### Safe source material for direct reconstruction

- **Kircher 1650 engraving and tables:** public-domain historical content.
- **Universidad de Valladolid scan:** item marked Public Domain Mark 1.0; preserve source attribution and repository locator.
- **Cornell Arca engraving record:** Cornell states the 1650 engraving is presumed public domain because of creation date.
- **Wikimedia reproductions of the 1650 plate:** usable only according to the file's stated public-domain/Commons metadata; prefer the institutional source in provenance.

### Reference-only unless separately licensed

- modern photographs of Wolfenbüttel, Cambridge, Florence, Puebla holdings;
- Cashner's article figures as modern layout/reproduction artefacts;
- Cashner's code/transcribed tables: do not redistribute or vendor as our historical dataset unless the specific version's licence authorises it. The existing repository research already records the all-rights-reserved restriction on his code/data repository; the current arca1650.info site also displays a CC BY-NC-ND notice for site content.

### Preferred production strategy

Use public-domain 1650 sources for direct facsimile/reference assets, and reconstruct the cabinet procedurally from observed geometry. Use modern object photographs only to answer physical questions such as proportions, wear, material, slat storage and opening behavior.

---

## 12. Research gate after M0.1

| Question | M0 first pass | M0.1 result |
| --- | --- | --- |
| Original Arca engraving inspected | NO | **YES** |
| At least one actual pinax image inspected | NO | **YES — Syntagma I, Pinax IV** |
| Primary volume source located with reusable rights | PARTIAL | **YES — Valladolid PDM 1.0; Cornell plate PD** |
| Surviving physical object institutionally verified | PARTIAL | **YES — Wolfenbüttel HAB** |
| Surviving object dimensions known | NO | **PARTIAL — Wolfenbüttel 23 × 14.5 cm** |
| Surviving cabinet photograph inspected | NO | **YES — Wolfenbüttel published photograph** |
| Slat material evidence | NO | **YES/PARTIAL — paper-bearing slats in Wolfenbüttel/Cambridge per Cashner** |
| Exact joinery/hardware/timber | NO | **NO — still H1** |
| Pinax information layout understood | PARTIAL | **YES for Syntagma I exemplar; Syntagma II still needs direct visual inspection** |
| Operator workflow understood | outline only | **YES at interaction-architecture level** |
| Historical data tables transcribed by this project | NO | **NO** |
| ARCA HISTORICA can honestly run | NO | **NO** |
| Physical UI can begin without inventing its basic anatomy | NO | **YES, with the remaining H1 details declared** |

### Gate verdict

**GO for frontend reconstruction architecture and a historically grounded physical shell.**

**NO-GO for claiming a complete historical Arca engine.**

Before a first “historical mode” can be functional, this project still needs its own transcription of at least the tone table and a bounded set of pinax data from the public-domain 1650 volume.

---

## 13. Recommended next implementation milestone

Do **not** jump directly to a polished 3D cabinet.

The best next milestone is a **Historical Vertical Slice** that proves the instrument's actual interaction grammar:

1. reconstruct the open box at evidence-based proportions;
2. implement lid tone-table surface and front palimpsest surface as real readable controls;
3. implement one removable **Syntagma I pinax** with faithful table anatomy;
4. allow pull → inspect → column → musarithm → rhythm selection;
5. place the pinax on a work surface;
6. connect that physical operation to the accepted Neo-Arca API without pretending the Neo solver is Kircher's table engine;
7. reserve an explicit provenance channel for a later historical dataset;
8. verify Fold-open and narrow-phone interaction before adding the rest of the cabinet.

Even stronger: before or alongside that slice, independently transcribe **Syntagma I, Pinax IV** plus the usable engraved tone table from the 1650 public-domain scan. That would let the first visual prototype contain at least one genuinely functioning historical path rather than a purely representational reconstruction.

---

## Sources / stable locators

1. Athanasius Kircher, *Musurgia universalis*, vol. II (Rome, 1650), Universidad de Valladolid scan, Public Domain Mark 1.0: https://uvadoc.uva.es/handle/10324/9140
2. Cornell University Library, “Musurgia Univeralis: Musurgical Ark,” RMC2007_1212, Vol. II pp. 184/185: https://digital.library.cornell.edu/catalog/ss:550167
3. Herzog August Bibliothek, Cod. Guelf. 90 Aug. 8° / Heinemann-Nr. 3876: https://diglib.hab.de/?db=mss&id=90-aug-8f&lang=en&list=ms
4. Andrew A. Cashner, “Athanasius Kircher's Arca musarithmica (1650) as a Computational System,” *Journal of Creative Music Systems* 8/1 (2024): https://www.andrewcashner.com/docs/Cashner-2024-Kircher_Computation-JCMS.pdf
5. Cashner, Arca project overview / operator model: https://www.arca1650.info/about.html
6. Cashner, `Aedifico` documentation for data structures: https://www.arca1650.info/doc/Aedifico.html
7. Cashner, Syntagma I Pinax IV documentation: https://www.arca1650.info/doc/Arca_musarithmica-Syntagma1-Pinax04.html
8. Andrew A. Cashner, “Kirchercianos y trisectores: el sistema automático de composición de Athanasius Kircher,” *Anuario Musical* 77 (2022), 51–75, DOI 10.3989/anuariomusical.2022.77.04: https://anuariomusical.revistas.csic.es/index.php/anuariomusical/article/view/390
9. Library of Congress-hosted publication containing Fig. 36, Wolfenbüttel Arca photograph: https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/16/01/57/14/2016015714/2016015714.pdf
10. Carlo Mario Chierotti research/transcription portal, pinax index (secondary reference; do not copy modern presentation assets without permission): https://kircher.chierotti.it/pinax/
11. Wikimedia Commons, public-domain reproduction record for the 1650 Arca illustration: https://commons.wikimedia.org/wiki/File:Kircher-ark.jpg

---

## Governing design sentence

> **Reconstruct the seventeenth-century computation first; let the impossible 2026 computation reveal itself through the same surfaces.**

The historical Arca supplies the body and the interaction topology. The accepted Phase-1 Ghost supplies a modern mind. The next frontend must make those two layers visibly legible rather than collapsing them into one false claim of historical fidelity.
