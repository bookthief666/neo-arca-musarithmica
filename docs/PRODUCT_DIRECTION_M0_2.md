# M0.2 — Product Direction: Instrument-First, No Semantic Text-to-Music UX

**Status:** product decision superseding the text-entry portions of `HISTORICAL_VERTICAL_SLICE.md` for the first playable Digital Arca.

## Decision

The first playable Neo-Arca will **not** expose a free-text prompt such as "melancholy", "radiant", or descriptive prose and then interpret that language into music.

The existing Phase-1 `semantics.py` / Polygraphia-inspired natural-language mapper remains valid backend research and may be retained as an optional experimental subsystem, but it is **not part of the primary instrument UX**.

The product should behave first as a musical instrument and combinatorial composition device: the user manipulates musical structure directly through the Arca itself.

## Historical clarification — text and affect were inputs, but not a modern semantic prompt

Kircher's historical Arca did use **text**, but principally as material to be **set to music**: prepared Latin or another language, divided into phrases, words and syllables, with poetic metre/prosodic structure helping determine which pinax/table was appropriate.

The operator also made **direct musical choices**. Modern scholarship reconstructing Book VIII makes the sequence explicit: the user selects style/texture, intended mood or character, and musical metre; style determines the syntagma, poetic metre determines the pinax, and the chosen mood helps determine the `tonus` used with the `mensa tonographica`. Kircher did not require the machine to infer a mood from arbitrary prose by semantic analysis. The human selected the affective character.

That distinction is important for the product:

- `natural-language idea -> machine infers mood -> generated soundtrack` is **N1** and is removed from the primary UX;
- **direct Affectus / Qualitas selection** is historically grounded enough to preserve as an optional first-class control: the user chooses the desired character, and that can filter or suggest a tone/mode;
- historical text-setting remains a legitimate future **ARCA HISTORICA / scholarly mode**;
- the first playable Neo-Arca may be fully instrumental and contain no text-entry field at all.

Sources informing this correction include Andrew A. Cashner, *Athanasius Kircher's Arca musarithmica (1650) as a Computational System* (2024), especially the reconstructed operator flow in §2, and Carlo Mario Chierotti's study of the *Mensa Tonographica* and Syntagma I.

## First-class musical controls

The Digital Arca should expose controls that produce strong musical results directly while preserving the historical computational metaphor.

### Historically grounded or historically adjacent controls

- **Affectus / Qualitas** — a direct character choice made by the operator; historically used to help select a suitable tone. It is never inferred from prose in the primary UX.
- **Tonus / Mode** — historical tones where historical data exists; modern scale/mode selection in Neo mode.
- **Syntagma / Texture** — simple homorhythmic versus florid/polyphonic behavior.
- **Mensura** — rhythmic/meter family.
- **Pinax / Permutation bank** — choose the family of stored compositional material.
- **Musarithm / Vperm** — choose or cycle a four-voice pitch permutation.
- **Rperm / Notae temporis** — choose rhythmic material.
- **Ambitus / Register** — voice-range/register behavior.
- **Cadentia** — cadence/final behavior.

### Historically documented variation operations worth turning into performance controls

The first Syntagma does not merely provide fixed lookup rows. Kircher also describes ways to vary the material. Chierotti's close reading of *Musurgia universalis* Book VIII identifies four especially useful procedures around pp. 57–59:

1. **Transpositio musarithmorum** — exchange/reassign the upper voices of a musarithm while retaining the bass foundation. This is an excellent historical ancestor of a modern `VOICE PERMUTE` control.
2. **Mutatio tonorum** — re-render the same musarithmic material under a different tone. This is a direct ancestor of a `REHARMONIZE / TONUS SHIFT` operation.
3. **Mutatio rationis valorum notarum** — vary the rhythmic-value pattern applied to the same numerical material. This maps naturally to a `RHYTHM MUTATE` operation.
4. **Processus per distincta membra** — assemble smaller musical/metrical fragments rather than treating a whole verse as one indivisible unit. This is particularly promising as the historical seed of the Neo-Arca's looping, pattern chaining, phrase mosaic and generative-sequencer behavior.

These should be treated as design gold: they let the instrument become exploratory and loop-oriented **without abandoning the historical computational logic**.

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
- **Voice locks / part locks** so selected voices survive a mutation while others regenerate
- **Pattern chaining / phrase order** for loop and sequence construction

The product may use period or Neo-Latin labels diegetically, but every control must remain understandable and playable.

## Revised primary interaction

The first playable vertical slice should now follow approximately:

```text
CLOSED / RESTING ARCA
    ↓ OPEN
OPEN ARCA
    ↓ SELECT AFFECTUS (optional) + TONUS / SCALE
TONAL FIELD ACTIVE
    ↓ SELECT SYNTAGMA / TEXTURE
COMPOSITIONAL FAMILY ACTIVE
    ↓ RETRIEVE / FOCUS A PINAX
PINAX WORKING
    ↓ SELECT OR CYCLE MUSARITHM / VPERM
PITCH MATERIAL CHOSEN
    ↓ SELECT OR CYCLE RPERM / MENSURA
RHYTHMIC MATERIAL CHOSEN
    ↓ APPLY HISTORICAL VARIATION OPERATIONS IF DESIRED
VOICE PERMUTE · TONUS MUTATION · RHYTHM MUTATION · DISTINCTA MEMBRA
    ↓ ADJUST N1 PERFORMANCE CONTROLS AS DESIRED
REGISTER · LOOP · ARPEGGIATION · DENSITY · VARIATION · CADENCE · VOICE LOCKS
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
4. directly choose the intended affect/character and a historically compatible tone;
5. use the metre to select the historically appropriate pinax;
6. apply genuine transcribed Kircher tables;
7. generate SATB text-setting from the historical data.

That is historical text-to-music in the correct sense. It must not be conflated with semantic mood interpretation.

## Product principle

> The Neo-Arca should reward musical decisions, not prompt-writing.

The central fantasy is not "describe a feeling and AI makes a song." It is "operate an impossible surviving combinatorial music machine and discover extraordinary melodies, harmonies, counterpoint, patterns and loops by manipulating its musical laws."

Affect can still matter, because it mattered to Kircher — but the player chooses it as part of the musical act.

That principle now governs the first playable frontend.