# M0.6 — Primary-Text Corrections to the Physical Arca Model

**Status:** current authority where this file corrects M0.1 / the first Historical Vertical Slice.  
**Source basis:** direct reading of the public-domain 1650 *Musurgia universalis* Tome II OCR derived from the UNC/Internet Archive 300-ppi scan, especially Book VIII pp. 184–186 (OCR around lines 80568–80718), cross-checked against the previously inspected Iconismus XIV and modern scholarship.  
**Purpose:** correct a consequential simplification in the earlier reconstruction: **the historical manipulable units stored in the Arca are musarithmic columns copied from the printed pinakes onto separate paper or wooden rods/strips. A whole printed pinax should not be treated as one indivisible physical slat.**

---

## 1. Kircher's own definition resolves the rod/pinax ambiguity

At the opening of *Musurgia Mechanica*, Kircher defines the Arca as the receptacle of **musarithmic columns**, then defines those columns as material copied separately from the musarithms of the pinakes onto wooden or paper rods (`ligneis aut chartaceis virgis`).

This establishes the historical information hierarchy more precisely:

```text
PRINTED PINAX / TABLE
    ↓ subdivided into its constituent columns
MUSARITHMIC COLUMN
    ↓ separately copied onto a physical carrier
WOODEN OR PAPER ROD / STRIP / COLUMN
    ↓ multiple copies stored in labelled cells
ARCA RECEPTACULUM
```

### Correction to earlier project language

The M0.1 dossier and Historical Vertical Slice often used **pinax** and **slat/rod** almost interchangeably. That was defensible from secondary descriptions, but it is too coarse after reading Kircher's construction instructions directly.

For the physical reconstruction:

- `pinax` = the source table / family of columns;
- `columna musarithmica` = a particular column extracted/copied from that table;
- `virga`, `bacillus`, `taxillus`, or paper column = the physical strip/rod that carries one such column;
- `receptaculum/cellula` = the labelled storage cell containing repeated copies of the appropriate column family.

The **rod/column is the principal physical control**.

---

## 2. Kircher specifies proportions for the ideal Arca

The first M0 pass correctly refused to invent dimensions. Book VIII now supplies a proportional construction prescription for the ideal printed Arca.

Kircher states that:

- length and height are equal;
- each is **one palm** (`palmum integrum`);
- width is **one half-palm**;
- the interior width/body is subdivided into **three equal principal spaces**.

This is H0-T evidence for the **ideal design described in 1650**, not a claim that every surviving implementation obeys it literally. The Wolfenbüttel exemplar's institutional measurements remain a separate H0-O witness and should not be forced to match a modern conversion of the Roman palm without further metrological study.

### Digital consequence

The first 3D/2.5D shell should begin from the **1 : 1 : 0.5 proportional envelope** rather than arbitrary treasure-chest proportions. The absolute on-screen scale may change responsively; the historical ratio should be the default reconstruction hypothesis.

---

## 3. The interior storage is explicitly partitioned by syntagma

Kircher's construction text gives a much more specific cabinet topology than the earlier visual reconstruction could establish.

The three principal interior spaces are divided as follows:

1. **First space / dodecamorium — 12 cells** for Syntagma I / simple counterpoint material.
2. **Second space / hexamorion — 6 cells** for Syntagma II / florid poetic counterpoint material.
3. **Third space — likewise six-partite** for Syntagma III material.

The text then describes placing the corresponding column families into those cells in order. For Syntagma I, the first cell receives columns from Pinax I, the second from Pinax II, the third from Pinax III, the fourth from Pinax IV, and so on.

This is strong H0-T evidence for a cabinet with **three banks and labelled subcells**, not one undifferentiated bed of decorative slats.

### Important historical incompleteness

The printed corpus and the ideal physical storage plan are not identical things. Kircher can prescribe cells for material that is absent, incomplete, withheld, or underspecified in the book. The UI should preserve empty/fragmentary capacity where appropriate instead of filling every historical slot with invented data.

---

## 4. Multiple physical copies of columns are intentional

Kircher instructs the maker to copy individual pinax columns several times onto paper or wooden carriers — four, five, six, seven, eight, nine, ten times as needed — and store these repeated columns in their proper receptacles.

This is not redundant decoration. It enables a user to pull several compatible columns from one family and arrange them simultaneously for a multi-word or multi-line theme.

For the first syntagma he further advises that every physical column be divided into **ten equal cells/row positions**. Where an original printed column has fewer transverse rows, existing musarithms may be repeated to fill the vacant positions so that all physical columns share equal geometry.

The reason is mechanical-computational: when several strips are placed side-by-side, their row bands must align even while the strips are shifted vertically.

### Digital consequence

Do **not** implement the main historical operation as:

> tap one Pinax-IV card → choose a dropdown row.

Instead, the historically expressive interaction is:

> open a labelled cell → pull one or more narrow column-rods → lay them side-by-side on the working surface → slide each rod vertically → read a transverse combination across the aligned row bands.

That is the distinctive physical computation of the Arca.

---

## 5. The cabinet itself carries computational reference surfaces

Kircher explicitly instructs the maker to place/describe on the **face of the Arca**:

- the `systema phonotacticum`;
- the `mensa Tonographica`.

He also calls for additional compartments along side `DC` for tone-related musarithmic columns according to the order of the tone table.

This corrects the earlier tentative assumption that the tone table should necessarily live on the inside of the lid. The engraving may visually stage a broad raised reference surface, but the primary construction text's `in facie ... Arcae` is the stronger topological evidence.

### Reconstruction rule

Treat the exact geometric placement of the printed charts as an engraving/object-reconciliation problem, but treat **their integration into the body/face of the instrument** as historically established. They are not detachable modern HUD panels.

---

## 6. Receptacles are labelled, covered information architecture

Kircher instructs that individual receptacles receive their own covers and that the outer surface carry the title of the column family hidden within.

This gives us a historical solution to a modern UX problem: **discoverability can be built into the cabinet itself.**

Rather than floating labels or tooltips everywhere, the physical lids/tabs of storage cells can bear concise titles. Opening one reveals the repeated strips belonging to that family.

The box is therefore simultaneously:

- storage;
- index;
- data structure;
- user interface.

---

## 7. Primary operating procedure: arrange columns, then transpose them vertically

Kircher's Chapter III describes the use of the completed Arca with enough specificity to change the interaction model.

The operator:

1. prepares the phonotactic working surface and selects a musical/textual theme;
2. divides that theme according to the required syllabic/metre categories;
3. opens the receptacle covers bearing the needed labels;
4. removes the required physical columns;
5. places those columns next to one another in thematic order;
6. combines them by moving individual columns **upward or downward**;
7. reads a transverse row across the resulting alignment to obtain the intended musical material.

Kircher explicitly says that, provided equal row geometry is maintained, different vertical dispositions of the columns yield usable combinations.

### This is the central historical interaction

The Digital Arca should make the user feel that the music is produced by **physical metathesis/transposition of stored combinatorial strips**.

That is more specific, more historically grounded, and more unusual than our previous `retrieve one pinax and select a row` abstraction.

---

## 8. Revised historical scene topology

```text
ARCA
├── BODY / FACE
│   ├── MENSA TONOGRAPHICA
│   └── SYSTEMA / PALIMPSESTUS PHONOTACTICUS
│
├── BANK I — DODECAMORIUM / SYNTAGMA I
│   ├── CELL I   → repeated column-rods from Pinax I
│   ├── CELL II  → repeated column-rods from Pinax II
│   ├── CELL III → repeated column-rods from Pinax III
│   ├── CELL IV  → repeated column-rods from Pinax IV
│   └── ... twelve labelled cells in ideal construction
│
├── BANK II — HEXAMORIUM / SYNTAGMA II
│   └── six labelled column families
│
├── BANK III — SYNTAGMA III
│   └── six-partite ideal storage; surviving/published data incompleteness remains visible
│
├── SIDE TONE-COLUMN STORAGE
│
└── EXTERNAL / DEPLOYED WORK SURFACE
    ├── COLUMN ROD 1  ↕
    ├── COLUMN ROD 2  ↕
    ├── COLUMN ROD 3  ↕
    ├── COLUMN ROD 4  ↕
    └── ...
          ↓ aligned transverse row
       MUSICAL COMBINATION
```

---

## 9. Product-direction reconciliation: instrument-first still stands

M0.2 remains binding: the primary playable Neo-Arca should not require a free-text mood prompt.

The historical text confirms that Kircher expected an operator to consider the **affective character** of a text and select an appropriate tone, but that is a direct musical/rhetorical choice, not a modern NLP inference engine. The user can therefore choose tone/mode/affect directly through the instrument.

For the instrument-first Neo-Arca, the column mechanism becomes even more valuable:

- choose tonal field directly;
- choose a compositional bank/texture;
- pull several rods;
- slide them into new alignments;
- lock promising rows/voices;
- mutate or reseed unlocked material;
- arpeggiate, loop, vary density/register/cadence through clearly N1 evolved controls;
- hear the resulting structure immediately.

The historical mechanism supplies the gestural grammar. Modern features evolve **from** that grammar instead of replacing it with knobs and forms.

---

## 10. Immediate implementation/transcription consequences

### Historical data

The first Pinax-IV transcription should be represented as at least:

```text
Pinax IV
└── source columns / stropha columns
    └── row index / cell 01..10
        ├── Cantus degree sequence
        ├── Altus degree sequence
        ├── Tenor degree sequence
        ├── Bassus degree sequence
        └── linked Notae Temporis material
```

But the **physical carrier model** should be separate:

```text
ColumnRodInstance
├── pinax_id
├── source_column_id
├── copy_index
├── vertical_row_offset
├── label
└── provenance
```

That separation lets the same historical column data instantiate several physical strips, exactly as Kircher prescribes.

### Frontend

Before a large frontend build, revise the Historical Vertical Slice from:

`retrieve one pinax → choose stropha/column → choose musarithm`

to:

`open labelled pinax-family cell → retrieve one or more column-rods → arrange side-by-side → slide rods vertically → select/read transverse row → resolve degrees through tone table → realize voices`.

This is now the preferred historical interaction topology.

---

## 11. Evidence status

| Claim | Status |
| --- | --- |
| Arca is receptacle of musarithmic columns | **H0-T** |
| Columns are separately copied from pinax data onto wooden or paper rods | **H0-T** |
| Ideal length = height = one palm | **H0-T** |
| Ideal width = half a palm | **H0-T** |
| Three principal internal spaces | **H0-T** |
| First bank has 12 cells | **H0-T** |
| Second bank has 6 cells | **H0-T** |
| Third bank is likewise six-partite in construction instructions | **H0-T** |
| Individual columns are copied multiple times | **H0-T** |
| Physical columns should share equal row geometry, with ten cells advised | **H0-T** |
| Receptacles/cells have labelled covers | **H0-T** |
| Operator arranges extracted columns and shifts them vertically | **H0-T** |
| Mensa Tonographica + phonotactic system belong on/in the face of the Arca | **H0-T**, exact visual placement still requires reconciliation |
| Modern lock/mutate/loop/arpeggiation behavior | **N1** |

---

## 12. Source locator

Primary text: Athanasius Kircher, *Musurgia universalis*, Tomus II, Book VIII, `Musurgiae Mirificae Pars V — De Musurgia Mechanica`, especially Chapters I–III around printed pp. 184–186. Public-domain UNC Music Library scan via Internet Archive, identifier `athanasiikircherkirc`; OCR region approximately lines 80568–80718.

The OCR is used here to read Kircher's prose and navigate the source. Geometry visible only in the engraving remains subject to image-level verification against the public-domain Cornell/e-rara witnesses.
