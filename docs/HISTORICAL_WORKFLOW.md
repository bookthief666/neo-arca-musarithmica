# HISTORICAL_WORKFLOW.md — How the Arca was actually operated

Reconstructed from scholarship, not from our own reading of Book VIII. Every step carries
its classification; see `HISTORICAL_RESEARCH.md` §0 for the limits of this pass.

The point of writing this down is negative as much as positive: it shows how much of what
our engine does is *not* what the Arca did.

---

## The operator's procedure

### 1. Begin with a text — H0
The user brings a **Latin text**, typically liturgical or devotional. The Arca sets words;
it does not invent absolute music. Nothing is generated without a text.

### 2. Scan it — H0
The user determines the **poetic metre** and the **syllable count** of each line, and
knows which syllables are long and which short. This is prosody, and the Arca does not do
it for you. It is the first place the machine assumes a competence its user must already
have.

### 3. Choose a syntagma — H0
- **Syntagma I** — simple, syllabic, homorhythmic writing; all four voices move together.
- **Syntagma II** — florid, melismatic writing, admitting imitation and *fugato*; the
  voices move independently.
- **Syntagma III** — rhetorical music. Intended to hold ten *pinakes* (H1).

The choice reflects the character wanted for the text.

### 4. Choose a pinax — H0
Within the syntagma, the **poetic metre selects the *pinax***. Different *pinakes* carry
phrases for different metres — Euripidean, Anacreontic, Archilochian, Sapphic and others.
Syntagma I holds eleven, although the cabinet was built with twelve *receptacula*, a
discrepancy Kircher leaves unexplained.

### 5. Choose a tonus — H1
The user selects one of the **twelve *toni*** (church tones) from the table on the case.
This fixes what the numbers will mean. Sources describe the *tonus* choice as guided by
the affect of the text; we did not find a rule that determines it, and we believe there
is none — it is a judgement.

### 6. Draw the musarithms — H1
From the chosen *pinax*, the user takes a **column of numbers** — the *musarithmi* — which
supplies, for each syllable, four values: one per voice. **This is the combinatorial
heart of the device.** Which column you take is free; that freedom is where the "millions
of pieces" come from.

### 7. Read numbers as pitches — H0
Each number, **1 to 8, is a scale degree** read against the chosen *tonus*. Degree plus
tone gives a pitch. The case's table of clefs and signatures tells the user how to place
those pitches on the staff for each voice.

### 8. Apply the rhythm separately — H0
The slat carries a **separate list of note values**. Pitch and rhythm are independently
combinable — the single most computational feature of the design, and the reason the
output space is so large.

### 9. Write it out, and use judgement — H1
The user copies the result into staff notation, in the appropriate clefs. Accidentals not
implied by the signature — *musica ficta*, above all the raised leading tone at cadences —
are supplied by **the singer's or scribe's own training**. The Arca does not encode them.

---

## What the machine decides, and what the human decides

| Decided by the Arca | Left to the human |
| --- | --- |
| Which pitches, as scale degrees | The text itself |
| Which rhythmic values | Scanning the metre |
| The four-voice disposition | Choosing syntagma, pinax, tonus |
| That the result is grammatical counterpoint | Which column to draw |
| | Clef and register placement |
| | *Musica ficta* |
| | Whether the result is any good |

Kircher's claim — that an untrained musician can compose properly with it — has to be read
against that right-hand column. The Arca guarantees **correctness**, not competence, and
it assumes a user who can scan Latin verse and read four staves.

---

## Where the counterpoint comes from — the crucial point

**The Arca does not compute counterpoint. It looks it up.**

The tables are *pre-composed*: Kircher wrote grammatical four-voice progressions and
tabulated them, so any column drawn is correct because it was correct when he wrote it.
The device guarantees correctness by construction, not by checking.

Our `kircher_engine.py` does the opposite. It *searches* for voicings and *tests* them
against an explicit rule engine, rejecting candidates that break the law. The output may
resemble the Arca's; the mechanism is the inverse of it.

Two consequences we hold ourselves to:

1. We may say the Neo-Arca is **inspired by** the Arca's combinatorial conception. We may
   not say it **reconstructs** the Arca's method.
2. A genuine ARCA HISTORICA engine would be a *table lookup and permutation* system, not a
   constraint solver — a different code path sharing only pitch primitives, the seeded
   stream, the event model and MIDI export. It is architecturally sketched in the roadmap
   and **not implemented**, because we do not have the tables (see `PROVENANCE.md` §4).

---

## What our engine does instead

| Arca | Neo-Arca |
| --- | --- |
| Latin text, scanned for metre | Free text in any language, mapped onto ten semantic axes (**N1**) |
| Metre selects a pinax | Semantics select mode, tempo, density, contour (**N1**) |
| One of twelve *toni* | One of seven modern diatonic modes (**N1**) |
| Numbers looked up in pre-composed tables | Pitches searched for under constraints (**N1**) |
| Correctness guaranteed by construction | Correctness verified by a rule engine and reported (**N1**) |
| Human supplies *musica ficta* | Engine raises the seventh at cadences that need it (H1 practice, **N1** trigger) |
| Human writes out the score | MIDI and event JSON (**N1**) |

Read down that right-hand column: almost all of it is N1. That is not a criticism of the
engine — it is the honest description of what it is.
