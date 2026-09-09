# HISTORICAL_RESEARCH.md — Source ledger for the Neo-Arca Musarithmica

**Status:** M0 archaeology, first pass. Compiled 2026-09-09.

This document records what we have actually established about Athanasius Kircher's *Arca
musarithmica*, what we have inferred, and what we have invented. Its purpose is to keep
the software honest: nothing in the engine may claim historical authority that this
ledger does not support.

---

## 0. Method, and an important limitation

Research for this pass was carried out from a sandboxed environment whose network egress
policy permits `raw.githubusercontent.com`, the npm and PyPI registries, and a web-search
service, but **blocks direct page and image fetches** from `archive.org`, `zenodo.org`,
`en.wikipedia.org`, `www.arca1650.info`, `www.andrewcashner.com` and comparable hosts.

The practical consequence, stated plainly:

> **We have not inspected the 1650 engraving, any page of *Musurgia universalis*, or any
> photograph of a surviving cabinet.** Every claim below rests on scholarly and
> encyclopaedic *description* of those artefacts, not on our own examination of them.

This is a real gap, not a formality. Section 6 of this file and the research gate in
`UNCERTAINTIES.md` record it as such. Any future session with unrestricted egress should
redo sections 4 and 5 against primary scans before the visual reconstruction is treated
as settled.

## Classification taxonomy

Every substantive claim in this repository carries one of these marks:

| Mark | Meaning |
| --- | --- |
| **H0** | Directly documented by a primary source or a surviving object |
| **H1** | Strongly inferred — well supported by scholarship, not directly evidenced in the detail we need |
| **N1** | A Neo-Arca modern extension, historically sympathetic but our own |
| **HÆRETIC** | A deliberate, declared transgression belonging to Modus Hæreticus |

Because of the limitation above, claims marked **H0** in this pass mean "documented in the
primary source *according to the scholarship we consulted*", not "we read it ourselves".
That distinction is preserved in the ledger's `Evidence` column.

---

## 1. The device and its purpose

| # | Claim | Class | Evidence |
| --- | --- | --- | --- |
| 1.1 | Kircher describes the *Arca musarithmica* in Book VIII of *Musurgia universalis* (Rome, 1650) | H0 | Cashner 2024 (JCMS); multiple secondary |
| 1.2 | The name means, literally, a "box of music-numbers"; *musarithmi* / *musarithmos* is Kircher's own term for the numerical tables | H0 | arca1650.info (Cashner), via search summary |
| 1.3 | Its stated purpose is that "even an untrained musician can achieve perfect composition in a short time", and it demonstrates music's foundation in mathematical combinatorics | H0 | Kircher, quoted in secondary sources |
| 1.4 | It produces four-voice vocal settings of a given Latin text | H0 | Cashner; Wikipedia; Digicult |
| 1.5 | Its combinatorial reach is very large — commonly described as "millions" of possible pieces | H1 | Secondary; the figure depends on counting assumptions no source we saw states |
| 1.6 | It is **not** an automatic machine. No surviving implementation mechanises anything; the human does the work | H0 | Cashner 2024, on the surviving examples |

## 2. Internal structure

| # | Claim | Class | Evidence |
| --- | --- | --- | --- |
| 2.1 | The case exterior carries a table of *toni* (church tones) and a table of clefs and signatures | H0 | Cashner, via arca1650.info summary |
| 2.2 | Inside are slats/tablets, each carrying tables of numbers together with rhythmic values | H0 | Same |
| 2.3 | The numbers are scale degrees 1–8, to be read against the chosen *tonus* | H0 | Same; "lists of integers one through eight" |
| 2.4 | Rhythmic values are held as a **separate** list from the pitch numbers, so pitch and rhythm are independently combinable | H0 | Same |
| 2.5 | There are **twelve** *toni* | H1 | Digicult ("12 in total"); consistent with the period's twelve-mode systems but we have not counted them in the source |
| 2.6 | The material is divided into **three syntagmata**: I simple/syllabic/homorhythmic; II florid/melismatic, admitting imitation and *fugato*; III rhetorical | H0 | Cashner 2024 |
| 2.7 | Kircher himself likens syntagma I to note-against-note (first-species) writing and syntagma II to florid (fifth-species) writing | H1 | Secondary paraphrase; the species analogy may be the commentators' rather than Kircher's |
| 2.8 | Syntagma I contains **eleven** *pinakes*, although the cabinet was designed with **twelve** *receptacula* — a discrepancy Kircher does not explain | H0 | Cashner 2024 |
| 2.9 | Syntagma III was intended to contain **ten** *pinakes* | H1 | Cashner 2024, phrased as intent ("should have been ten") |
| 2.10 | Within a syntagma, **which** *pinax* you use is a function of the poetic metre of the text | H0 | Cashner; Digicult |
| 2.11 | Named metres include Euripidean, Anacreontic, Archilochian and Sapphic | H0 | Digicult, quoting the slat inscriptions |
| 2.12 | Each slat relates to a strophe of a given syllable count | H1 | Digicult |

### 2.13 On the word *tariffa* — flagged

The master brief for this project describes the rods as "often described as **tariffae**".
**We could not confirm that this is Kircher's Latin, or indeed anyone's.** The sources we
reached call them *slats*, *wooden staves*, *tablets*, *rods* and *sliding panels*; the
Latin terms we did confirm are *arca*, *syntagma*, *pinax*, *musarithmus* and
*receptaculum*.

**Class: UNCERTAIN.** Until someone reads Book VIII directly, the software and the
interface should prefer *rod*, *slat* or *tablet* in English and *pinax* where a table is
meant. See `UNCERTAINTIES.md` §1.

## 3. How a piece is actually made

See `HISTORICAL_WORKFLOW.md` for the reconstructed procedure. In summary:

| # | Claim | Class |
| --- | --- | --- |
| 3.1 | The operator begins with a Latin text whose syllable quantities are known | H0 |
| 3.2 | The metre and syllable count select a *pinax* | H0 |
| 3.3 | The desired affect and the text select a *tonus* | H1 |
| 3.4 | A column of *musarithmi* supplies four numbers per syllable, one per voice | H1 |
| 3.5 | The numbers are read as scale degrees against the chosen *tonus* to give pitches | H0 |
| 3.6 | A separate rhythmic list supplies note values | H0 |
| 3.7 | The operator writes the result out in staff notation, applying clefs and any *musica ficta* by their own judgement | H1 |

## 4. Surviving physical examples

| # | Claim | Class | Evidence |
| --- | --- | --- | --- |
| 4.1 | Three surviving implementations were known until a fourth was identified in Puebla, Mexico | H0 | Cashner 2024 |
| 4.2 | One is at the Herzog August Bibliothek, Wolfenbüttel | H1 | Search summary; not verified against the HAB catalogue |
| 4.3 | Samuel Pepys owned one; the Pepys Library at Magdalene College, Cambridge is the associated collection | H1 | Pepys Diary encyclopaedia; the *present* location was not confirmed |
| 4.4 | Ferdinand III of the Holy Roman Empire owned one | H1 | Secondary |
| 4.5 | The Puebla example contains only a **partial** selection of Kircher's tables, apparently chosen for practical usefulness | H0 | Cashner 2024 |
| 4.6 | No surviving example is identical to another, and none is complete in the sense the printed book describes | H1 | Follows from 4.5 and 1.6 |

**Not established:** dimensions, timber species, whether the lid is hinged, how the
compartments are partitioned, whether inscriptions are printed paper labels or inked
directly. See `VISUAL_RECONSTRUCTION.md`.

## 5. Modern scholarship and digital work

| # | Claim | Class | Evidence |
| --- | --- | --- | --- |
| 5.1 | Andrew A. Cashner (University of Rochester) has produced the principal modern study and a working digital implementation | H0 | github.com/andrewacashner/kircher; JCMS 2024 |
| 5.2 | That implementation is written in Haskell and emits MEI (with provision for Lilypond) | H0 | Repository README |
| 5.3 | It is served as a web application at arca1650.info | H0 | Repository README |
| 5.4 | Cashner's work documents the Arca's reception and practical use, particularly in the Spanish Empire | H0 | JCMS 2024 abstract |

### 5.5 Licence — decisive for this project

Fetched directly from the repository:

> "Everything in this repository is copyright © 2022 by Andrew A. Cashner. All rights are
> reserved, except you may download the repository and compile your own copy of the
> program."
>
> — `arca/README.md`, `andrewacashner/kircher` @ `master`
> (the root `README.md` carries the same statement dated 2021)

**This is not an open licence.** We may download and build it. We may **not** copy,
redistribute, or derive a dataset from his transcription of Kircher's tables.

**Consequence for the roadmap:** an ARCA HISTORICA engine cannot be seeded from Cashner's
data. Its tables must come from our own transcription of the public-domain 1650 text —
which this pass could not perform, because we cannot fetch the scans. Until then, the
honest position is to build the machinery and ship **no** tables at all, rather than
inventing numbers and calling them Kircher's. Recorded in `PROVENANCE.md` §4.

## 6. Research gate (brief §VI), answered honestly

| Question | Answer |
| --- | --- |
| Original engraving inspected | **NO** — image egress blocked |
| Primary textual description inspected | **NO** — only scholarly description of it |
| Surviving Arca examples researched | **PARTIAL** — existence and count established; physical detail not |
| Pinax structure understood | **PARTIAL** — role and selection understood; exact contents not transcribed |
| Pitch-permutation system understood | **PARTIAL** — degrees 1–8 against a *tonus*; the actual permutations not held |
| Rhythm-permutation system understood | **PARTIAL** — separate value lists confirmed; contents not held |
| Operator workflow understood | **YES (in outline)** — see `HISTORICAL_WORKFLOW.md`; step-level detail is H1 |
| Physical reconstruction evidence adequate | **NO** — insufficient to model the cabinet without invention |
| Rights/provenance reviewed | **YES** — Cashner all-rights-reserved; 1650 text is public domain |
| Uncertainties documented | **YES** — `UNCERTAINTIES.md` |

**Verdict:** adequate to proceed with a clearly-labelled Neo-Arca, and adequate to
constrain what the engine may claim. **Not** adequate to build ARCA HISTORICA or a
faithful visual reconstruction. Both need a session with primary-source access.

## 7. Polygraphia Nova — what it was, and what our feature is not

| # | Claim | Class |
| --- | --- | --- |
| 7.1 | Kircher published *Polygraphia nova et universalis* in 1663 | H0 |
| 7.2 | It concerns universal language and cryptography — encoding meaning so it can pass between languages, and concealing it | H0 |
| 7.3 | It is a **separate** work from the Arca and does not drive it | H0 |
| 7.4 | Kircher never connected a natural-language description to musical parameters | H1 — no source suggests he did |
| 7.5 | **Our `semantics.py` — text to mode, tempo, contour, register — is entirely our own** | **N1** |

The name "Polygraphia" is borrowed as an *homage to an ambition*: that meaning can be
mapped systematically across representations. The mapping itself is a modern invention and
must never be presented as Kircher's method.

## 8. Where the current engine stands relative to all of this

| Feature | Class | Note |
| --- | --- | --- |
| Combinatorial four-voice generation from a symbolic system | H1 | The *idea* is Kircher's; the mechanism is not |
| Seven modern diatonic modes (Ionian…Locrian) | **N1** | Kircher used twelve *toni*. See `PROVENANCE.md` §2 |
| Constraint-solved SATB voice leading | **N1** | A modern search; Kircher's tables were pre-composed |
| *Musica ficta* raised at cadences | H1 | Consistent with period practice; our trigger rule is ours |
| Roman-numeral cadence formulae | **N1** | Historically these were contrapuntal *clausulae*, not chord progressions. See `PROVENANCE.md` §3 |
| Locrian IV→i(dim) "plagal diminished" close | **N1** | No historical warrant; Locrian was not a practical mode |
| Modus Hæreticus | **HÆRETIC** | Wholly invented |
| Polygraphia semantic mapping | **N1** | See §7 |
| Base64 MIDI, event JSON, REST API | **N1** | Obviously |

## Sources consulted

- Andrew A. Cashner, *Athanasius Kircher's "Arca musarithmica" (1650) as a Computational System*, Journal of Cultural Analytics / JCMS, 2024 — <https://www.andrewcashner.com/docs/Cashner-2024-Kircher_Computation-JCMS.pdf> (metadata and summary only; PDF fetch blocked)
- Andrew A. Cashner, `andrewacashner/kircher` — <https://github.com/andrewacashner/kircher> (README fetched directly; **all rights reserved**)
- *Arca musarithmica* project site — <https://www.arca1650.info/> (fetch blocked; consulted via search summary)
- *The Arca Musarithmica of Athanasius Kircher…*, International Journal of Humanities and Arts Computing, 2025 — <https://www.euppublishing.com/doi/10.3366/ijhac.2025.0356>
- "Athanasius Kircher. Arca Musarithmica And Many Sound Devices", Digicult, issue 055 — <https://digicult.it/digimag/issue-055/athanasius-kircher-arca-musarithmica-and-many-sound-devices/>
- Wikipedia, "Arca Musarithmica" — <https://en.wikipedia.org/wiki/Arca_Musarithmica> (fetch blocked; via search summary)
- Megan Kaes Long, "Reassessing the Plagal Cadence in Byrd and Morley", *Music Theory Online* 28.3 (2022) — <https://mtosmt.org/issues/mto.22.28.3/mto.22.28.3.long.html>
- Wikipedia, "Clausula (music)" — <https://en.wikipedia.org/wiki/Clausula_(music)>
- *The Diary of Samuel Pepys* encyclopaedia, "Athanasius Kircher" — <https://www.pepysdiary.com/encyclopedia/12185/>
