# PROVENANCE.md — The historical/N1 boundary, feature by feature

Where the line falls between what Kircher did, what period practice supports, and what we
invented. This file is the one to check before writing any user-facing claim.

Classes: **H0** documented · **H1** strongly inferred · **N1** Neo-Arca extension ·
**HÆRETIC** declared transgression. See `HISTORICAL_RESEARCH.md` for the evidence.

---

## 1. The one-line honest description

> The Neo-Arca Musarithmica is a modern generative composition engine **inspired by** the
> combinatorial conception of Kircher's *Arca musarithmica* (1650). It does not
> reconstruct Kircher's method, does not use his tables, and does not implement his
> modal system.

Everything below elaborates that sentence.

## 2. The mode system — N1

| | Kircher | Neo-Arca |
| --- | --- | --- |
| System | **Twelve *toni*** (church tones), tabulated on the case (H1 on the count) | **Seven** modern diatonic modes: Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian |
| Basis | Period modal theory, with its own finals, ambitus and affective associations | The rotations of the modern major scale |
| Selection | Human judgement, guided by the affect of the text | Computed from a semantic axis vector |

**Class: N1.** The seven-mode construct in `theory.py` does not map cleanly onto Kircher's
theoretical world and must never be presented as his. Two specific traps:

- **Locrian was not a practical mode.** It has no perfect fifth above its final and was
  not used compositionally in this period. Its presence here is a modern convenience, and
  its behaviour in our engine is doubly invented (see §3).
- **Mode is structure, mood is metadata.** `ModeSpec.mood` ("Radiant", "Lamenting", …) is
  our own labelling for the interface. It is not Kircher's affective doctrine, and no
  musical decision is taken from it.

## 3. Cadences — mixed, and the chord labels are N1

This is the most important entry in this file, because the code's own vocabulary
overstates what it models.

**What the period actually did (H0).** A cadence in this repertoire is a **clausula** — a
*dyadic, intervallic* event, not a chordal one. Two voices approach an octave or unison by
step; the *clausula cantizans* rises by semitone, the *tenorizans* falls by step, and the
*bassizans*, a third below the tenorizans, leaps down a fourth or up a fifth. The
identity of the cadence lives in **that voice-leading**, not in a succession of chords.
The Phrygian cadence is one of these contrapuntal formulae (the "mi cadence"); scholarship
notes that many apparent plagal cadences in the late sixteenth and early seventeenth
century *lack* the melodic clausulae that define the other types.

**What we implement (N1).** `harmony.py` selects cadences as **pairs of Roman-numeral
chord degrees** — `(4, 0)` for authentic, `(1, 0)` for Phrygian, `(3, 0)` for plagal. The
voice leading is then whatever the constraint solver happens to choose subject to the
leading-tone rule. We do **not** implement the clausulae.

| Our label | What it is | Class |
| --- | --- | --- |
| `authentic` | Degree V → I, with *musica ficta* raising the third where the mode's seventh is flat | **H1** as practice; **N1** as a chord-pair implementation |
| `phrygian` | Flat-second triad → final, bass descending a semitone | **N1** — a chordal reduction of a contrapuntal formula. The semitone bass descent is the right *gesture*; the clausulae are absent |
| `plagal` | Degree IV → I | **N1** as implemented |
| `half` | Ends on degree V | **N1** — a later functional concept |
| `deceptive` | V → vi | **N1** — a later functional concept |
| `plagal_diminished` | Locrian IV → i(diminished) | **N1, with no historical warrant whatsoever.** Locrian was not a practical mode and nothing in the period cadences onto a diminished final. This is a Neo-Arca construction, invented so that a mode our own system offers has *some* way to stop |
| `tritone_fall`, `suspended` | Heretical closes | **HÆRETIC** |

**Ruling:** the engine may describe these as "cadence formulae of the Neo-Arca grammar".
It may **not** describe them as historical cadences, and the phrase "Phrygian cadence" in
our output means "our chordal approximation of the gesture", which is what
`docs/MUSICAL_ARCHITECTURE.md` and the API description now say.

## 4. Musica ficta — H1 practice, N1 trigger

Raising the seventh degree at cadences in modes whose seventh is a whole tone below the
final is **documented period practice** (H1 in our sourcing), and Kircher's own device
leaves it to the performer entirely — the tables do not encode it.

Our engine applies it **automatically**, by a rule of our own: at a cadential slot, when
the cadence is authentic or deceptive and the mode needs it. That trigger is **N1**. It is
now correctly scoped to the slot that licenses it (see B2), so a raised seventh is not
treated as diatonic elsewhere in the piece.

## 5. ARCA HISTORICA — not implemented, and why

The roadmap calls for an engine that reproduces Kircher's actual combinatorial procedure.
**It is not implemented and no part of this repository claims to be it.**

The reason is documented and legal, not a matter of effort:

- Cashner's digital transcription is **all rights reserved** (`HISTORICAL_RESEARCH.md`
  §5.5). We may compile it for our own use; we may not vendor or derive from it.
- The 1650 text is public domain, but this environment cannot fetch the scans, so we
  cannot transcribe the tables ourselves.

**Therefore we ship no tables.** Inventing plausible-looking numbers and labelling them
Kircher's would be the single worst thing this project could do, and it is explicitly
forbidden by the brief. When an ARCA HISTORICA engine is built it must be seeded from our
own transcription of the primary source, with the transcription itself version-stamped in
provenance.

## 6. Polygraphia — N1

*Polygraphia nova* (1663) is a work on universal language and cryptography. It has nothing
to do with the Arca, and Kircher never mapped natural-language description onto musical
parameters. Our `semantics.py` — lexicon, ten axes, mode and tempo selection — is
**entirely our own invention** (N1), named in homage to an ambition rather than a method.

## 7. Modus Hæreticus — HÆRETIC

Wholly invented, and declared as such. It is an inversion of our own Orthodox profile, not
of anything historical. Its one enforced invariant (every phrase exposes a tritone) and
its weighted preferences are documented in `constraints.py` and verified in
`tests/test_heretical_grammar.py`.

## 8. Engineering — N1 throughout

Constraint search, bounded backtracking, seeded determinism, the diminution layer, event
JSON, Base64 MIDI, the REST API. None of it has a historical analogue and none of it
pretends to.

## 9. Claims this project must never make

- ❌ "Faithfully reproduces Kircher's Arca"
- ❌ "Implements Fux's / Palestrina's counterpoint" — the Orthodox profile is an explicit,
  extensible subset, and says so in its own title
- ❌ "Uses Kircher's tables" — we have none
- ❌ "Kircher's twelve modes" while shipping seven modern ones
- ❌ "Historical Phrygian cadence" for a bII→i chord pair
- ❌ "*Tariffa*" presented as Kircher's Latin — unconfirmed (`HISTORICAL_RESEARCH.md` §2.13)

## 10. Claims this project may make

- ✅ "Inspired by the combinatorial conception of Kircher's Arca musarithmica (1650)"
- ✅ "Kircherian / species-counterpoint-inspired SATB constraints adapted into a
  computational four-part generative grammar" — the Orthodox profile's actual title
- ✅ "Applies *musica ficta* at cadences, following period practice"
- ✅ "A modern generative engine that treats composition as encodable, permutable and
  constrainable — the idea Kircher's device embodies"
