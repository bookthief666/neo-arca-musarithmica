# VISUAL_RECONSTRUCTION.md — What the Arca looked like

**Read this warning first.** This pass could **not fetch a single image**. The network
egress policy blocked `archive.org`, `en.wikipedia.org`, `arca1650.info`, museum sites and
every scan repository we tried. Everything below is *description of* the engraving and the
surviving cabinets, taken from scholarship — not observation of them.

The brief asked that this file be "detailed enough that the NEXT session can build the
actual digital Arca without inventing its anatomy". **It is not, and cannot be made so
from here.** What follows is an honest inventory of what is established, what is merely
described, and precisely which questions the next session must answer from primary
sources before modelling anything.

---

## 1. What is established about the object

| # | Claim | Class |
| --- | --- | --- |
| 1.1 | It is a **case or box** — *arca* — not a machine with moving parts | H0 |
| 1.2 | The **exterior/case carries two reference tables**: the *toni* (church tones) and the clefs-and-signatures table | H0 |
| 1.3 | The **interior holds slats**, each bearing tables of numbers and rhythmic values | H0 |
| 1.4 | Slats are grouped into **syntagmata**, and within those into **pinakes** | H0 |
| 1.5 | Syntagma I was built with **twelve *receptacula*** (compartments) though it holds **eleven *pinakes*** | H0 |
| 1.6 | Slats carry **inscriptions naming their poetic metre** — Euripidean, Anacreontic, Archilochian, Sapphic | H0 |
| 1.7 | One description gives **seventy-seven small sliding panels**, varying in size between roughly one and two and a half centimetres | **H1 — single secondary source (Digicult); unverified, and the units read oddly. Do not build to this figure.** |
| 1.8 | Surviving examples differ from one another and from the printed description; at least one holds only a partial set of tables | H0 |

## 2. What is NOT established — the questions for the next session

None of the following could be answered. Each must be resolved from a scan or a museum
record before it is modelled, and **must not be guessed**:

- Overall dimensions and proportions of the cabinet.
- Timber species; whether veneered, painted or plain.
- Whether the lid is hinged, sliding, or lifts free; whether the reference tables are on
  the lid's inner face or on the case's exterior.
- How compartments are partitioned — full-depth dividers, stacked trays, or slots.
- Slat dimensions, thickness, and whether they are read flat or stood upright.
- Whether inscriptions are **printed paper labels glued on**, **inked directly**, or
  **engraved** — this determines the entire material language of the interface.
- Any metal fittings: hinges, corner braces, clasps, handles.
- The layout and typography of a single *pinax*: how the number columns and the rhythm
  lists are arranged relative to one another on the slat.
- Whether slats are marked with an index, and how a user finds the right one.

## 3. Where to look, when egress allows

Listed with rights status, because it matters for what may be shipped:

| Source | What it should give | Rights |
| --- | --- | --- |
| *Musurgia universalis* (1650), vol. II, the plate facing p. 185 — the Arca engraving | The canonical image of the object | **Public domain** (1650) |
| Book VIII of the same volume | The primary text, the Latin terminology, the tables themselves | **Public domain** |
| Scans: Internet Archive, Google Books, e-rara.ch, Bayerische Staatsbibliothek (MDZ), HAB Wolfenbüttel digital | The above, as page images | PD content; check each host's own terms for the *scan* |
| Herzog August Bibliothek, Wolfenbüttel — catalogue record | Physical detail of a surviving cabinet | **Museum photography is typically all-rights-reserved** |
| Pepys Library, Magdalene College, Cambridge | Pepys's example | Likely all-rights-reserved |
| The Puebla example (Cashner 2024) | A partial, practically-selected cabinet | Per publication |

**Rule for this project:** modern museum photographs may be used as *private research
reference only*. They may not be shipped as application assets. The 1650 engraving is
public domain and may be, subject to the host's scan terms.

## 4. The consequence for the frontend, and why it is not a compromise

Because we cannot ship museum photography, and because the sandbox cannot download images
at all, **every visual asset in the eventual frontend must be generated procedurally** —
wood grain, parchment, brass, inked numerals authored in code as canvas, SVG or shader
work.

This is the right answer regardless of the constraint. It sidesteps the rights problem
entirely, it scales cleanly across viewport sizes, and it keeps inscriptions as real text
that can be read by a screen reader and resized without turning to mush. Research imagery
informs geometry and palette; it never becomes an asset.

## 5. Provisional anatomy for the interface — explicitly N1 where marked

A frontend needs *some* hierarchy to build against. This one is grounded where it can be:

```
ARCA (case)                                  H0 — it is a box
├── Lid / reference surface                  H1 — position of the tables unconfirmed
│   ├── Table of toni (twelve)               H0 that it exists; H1 that there are twelve
│   └── Table of clefs and signatures        H0
└── Interior
    └── SYNTAGMA  (I simple · II florid · III rhetorical)      H0
        └── RECEPTACULUM (compartment)                          H0 — twelve in syntagma I
            └── PINAX  (table, selected by poetic metre)        H0 — eleven in syntagma I
                └── SLAT / ROD / TABLET                         H0 that they exist
                    ├── metre inscription                       H0
                    ├── column of musarithmi (degrees 1–8)      H0
                    └── list of rhythmic values                 H0
```

**Terminology ruling.** Use *slat*, *rod* or *tablet* in English and *pinax* for a table.
Do **not** use *tariffa* as though it were Kircher's word: we could not confirm it in any
source (see `HISTORICAL_RESEARCH.md` §2.13). If the project wants it for flavour, it must
be labelled **N1** and presented as the Neo-Arca's own coinage.

**What is safe to design against now:** the nesting above, the fact of metre-labelled
slats bearing number columns and rhythm lists, and the two reference tables.

**What is not:** anything about how it physically looks. Proportion, material, fittings and
the layout of a slat's face are all open, and a reconstruction that invents them and
presents them as authentic would be exactly the overclaim this project has committed to
avoiding.
