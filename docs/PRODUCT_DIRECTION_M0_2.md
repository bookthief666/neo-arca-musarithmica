# M0.2 — Product Direction: Instrument-First, No Semantic Text-to-Music UX

**Status:** product decision superseding the text-entry portions of `HISTORICAL_VERTICAL_SLICE.md` for the first playable Digital Arca.

## Decision

The first playable Neo-Arca will **not** expose a free-text prompt such as "melancholy", "radiant", or descriptive prose and then interpret that language into music.

The existing Phase-1 `semantics.py` / Polygraphia-inspired natural-language mapper remains valid backend research and may be retained as an optional experimental subsystem, but it is **not part of the primary instrument UX**.

The product should behave first as a musical instrument and combinatorial composition device: the user manipulates musical structure directly through the Arca itself.

## Historical clarification

Kircher's historical Arca did use **text**, but not in the modern semantic-prompt sense.

Its text input was principally material to be **set to music**: prepared Latin or other text, divided into syllables and associated with poetic metre/prosodic quantity. Those properties helped determine which pinax/table was appropriate. The user separately chose musical style/texture, tone, and mensuration. The machine did not analyze arbitrary natural-language concepts such as "melancholy" and infer an affective soundtrack from semantic embeddings or a modern mood classifier.

Therefore:

- `natural-language idea -> inferred mood -> generated soundtrack` is **N1** and is removed from the primary UX;
- historical text-setting remains a legitimate future **ARCA HISTORICA / scholarly mode**;
- the first playable Neo-Arca may be fully instrumental and contain no text-entry field at all.

## First-class musical controls

The Digital Arca should expose controls that produce strong musical results directly while preserving the historical computational metaphor.

### Historically grounded or historically adjacent controls

- **Tonus / Mode** — historical tones where historical data exists; modern scale/mode selection in Neo mode.
- **Syntagma / Texture** — simple homorhythmic versus florid/polyphonic behavior.
- **Mensura** — rhythmic/meter family.
- **Pinax / Permutation bank** — choose the family of stored compositional material.
- **Musarithm / Vperm** — choose or cycle a four-voice pitch permutation.
- **Rperm / Notae temporis** — choose rhythmic material.
- **Ambitus / Register** — voice-range/register behavior.
- **Cadentia** — cadence/final behavior.

### Explicit Neo-Arca performance controls (N1)

These are modern additions and should be visibly treated as the Arca's later evolutionary layer rather than projected backward onto Kircher:

- **Scale / modern mode**
- **Root / tonic**
- **Arpeggiation / broken-chord behavior**
- **Chord / harmonic field**
- **Loop length**
- **Rhythmic density**
- **Pattern subdivision**
- **Melodic contour / directional bias**
- **Register spread**
- **Voice density / number of active layers**
- **Variation / mutation amount**
- **Cadence strength / loop openness**
- **Consonance ↔ tension** as a direct musical control, not inferred from prose
- **Orthodox ↔ Heretical law**
- **Humanization / articulation** where musically useful

The product may use period or Neo-Latin labels diegetically, but every control must remain understandable and playable.

## Revised primary interaction

The first playable vertical slice should now follow approximately:

```text
CLOSED / RESTING ARCA
    ↓ OPEN
OPEN ARCA
    ↓ SELECT TONUS / SCALE
TONAL FIELD ACTIVE
    ↓ SELECT SYNTAGMA / TEXTURE
COMPOSITIONAL FAMILY ACTIVE
    ↓ RETRIEVE / FOCUS A PINAX
PINAX WORKING
    ↓ SELECT OR CYCLE MUSARITHM / VPERM
PITCH MATERIAL CHOSEN
    ↓ SELECT OR CYCLE RPERM / MENSURA
RHYTHMIC MATERIAL CHOSEN
    ↓ ADJUST N1 PERFORMANCE CONTROLS AS DESIRED
REGISTER · LOOP · ARPEGGIATION · DENSITY · VARIATION · CADENCE
    ↓ COMMIT / STRIKE / TURN THE MACHINE
FOUR VOICES / MELODY / HARMONY / LOOP MANIFEST
    ↓ PLAY · MUTATE · RESEED · LOCK PARTS · REPLAY · EXPORT MIDI
```

No text box is required in this path.

## Backend consequence

The accepted Phase-1 Ghost currently requires `text` and always runs the semantic analyzer. The frontend must **not** fake an instrumental workflow by secretly submitting meaningless placeholder prose such as `"instrumental"` or `"neutral"`.

Before the first production frontend is wired to the backend, add a narrow backend extension that supports an explicit **manual/instrument configuration path** where:

- natural-language text is optional or absent;
- semantic interpretation is bypassed;
- all effective musical controls come from explicit parameters or deterministic musical defaults;
- determinism/provenance clearly record that the composition source was `manual` / `instrument`, not `semantic`;
- the existing semantic endpoint/path remains backward compatible if retained.

This should be a small contract extension, not a rewrite of the accepted Ghost.

## Historical text-setting mode

A historically faithful text workflow remains valuable later, but it should be conceptually separate from the instrumental performance surface.

Future `ARCA HISTORICA` text-setting mode may allow the user to:

1. enter or select text to be sung;
2. divide/inspect syllables;
3. choose or identify poetic metre/prosodic pattern;
4. use that structure to select the historically appropriate pinax;
5. apply genuine transcribed Kircher tables;
6. generate SATB text-setting from the historical data.

That is historical text-to-music in the correct sense. It must not be conflated with semantic mood interpretation.

## Product principle

> The Neo-Arca should reward musical decisions, not prompt-writing.

The central fantasy is not "describe a feeling and AI makes a song." It is "operate an impossible surviving combinatorial music machine and discover extraordinary melodies, harmonies, counterpoint, patterns and loops by manipulating its musical laws."

That principle now governs the first playable frontend.