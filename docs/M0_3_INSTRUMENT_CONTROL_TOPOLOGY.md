# M0.3 — Instrument Control Topology

**Status:** product/research specification after M0.1 primary-source archaeology and M0.2 instrument-first direction.  
**Branch:** `feature/m0.1-primary-arca-archaeology`.  
**Purpose:** map the Arca's historically documented operator choices and variation procedures into the first playable Neo-Arca without falling back into either a generic synthesizer dashboard or a natural-language prompt interface.

---

## 1. Governing principle

The first playable Neo-Arca is a **direct-manipulation composition instrument**.

The player should be able to obtain compelling melodies, harmonies, counterpoint and loops by selecting and transforming musical structures. The Arca itself remains the control surface.

The project therefore distinguishes three layers:

1. **HISTORICAL CONTROL LOGIC** — operator choices documented for Kircher's Arca.
2. **NEO-ARCA EVOLUTION** — modern musical controls that extend that logic in a visibly later technological layer.
3. **HÆRETIC LAW** — explicit transgressive behavior, never confused with historical practice.

Free-text semantic mood interpretation is not part of this primary instrument.

---

## 2. Historical computational flow — the control graph we inherit

Cashner's reconstruction of Book VIII gives an unusually clear dependency graph for a single note/phrase:

```text
STYLE                  -> SYNTAGMA
TEXT METRE             -> PINAX
LINE POSITION          -> COLUMN / STROPHA
FREE CHOICE / CHANCE   -> VPERM / MUSARITHM
MUSICAL METRE          -> RPERM / NOTAE TEMPORIS   [Syntagma I]
VPERM                  -> PAIRED RPERM             [Syntagma II]
MOOD / CHARACTER       -> TONUS
TONUS + SCALE DEGREE   -> PITCH NAME + ACCIDENTAL
VOICE RANGE / CLEF     -> OCTAVE / REGISTER
RPERM                  -> DURATION
```

For the purely instrumental Neo-Arca, the text-dependent arrows are not needed in the main performance path. Their **musical equivalents** become player choices instead of inferred linguistic properties.

The resulting instrumental graph is:

```text
AFFECTUS / CHARACTER (optional direct choice)
            ↓
TONUS / ROOT + SCALE
            ↓
SYNTAGMA / TEXTURE
            ↓
PINAX / PATTERN FAMILY
            ↓
VPERM / PITCH-PERMUTATION ROW
            +
RPERM / RHYTHM-PERMUTATION ROW
            ↓
AMBitus / REGISTER + CADENCE / LOOP BOUNDARY
            ↓
FOUR-VOICE MATERIAL
            ↓
HISTORICAL MUTATION + NEO PERFORMANCE TRANSFORMATIONS
            ↓
PLAY / LOOP / LOCK / MUTATE / EXPORT
```

This retains the Arca's symbolic-computational identity even when there is no lyric text.

---

## 3. The primary physical controls

### 3.1 `AFFECTUS` — character selector

**Historical basis:** H0/H1. Kircher expects the operator to choose a mood/character suited to the setting; this helps determine a `tonus`. Modern scholarship notes that the `Mensa Tonographica` includes brief affective characterizations for the tones.

**Digital behavior:** optional direct selection, never NLP. It may:

- filter/recommend historically compatible `toni` in HISTORICA mode;
- bias a modern scale family, register and cadence profile in NEO mode only when the user explicitly asks it to;
- be bypassed completely when the player wants direct tonal control.

**UI form:** ideally part of the lid's tonal apparatus, not a mood dropdown floating over the scene.

### 3.2 `TONUS / RADIX / MODUS` — tonal field

Two distinct provenance states:

- **HISTORICA:** Kircher's tone system as independently transcribed from the public-domain source.
- **NEO:** root + modern scale/mode.

NEO scale families may eventually include:

- Ionian / major
- Dorian
- Phrygian
- Lydian
- Mixolydian
- Aeolian / natural minor
- Locrian
- harmonic minor
- melodic minor
- pentatonic families
- whole-tone / octatonic or other explicitly N1 collections where musically productive

Do not label the latter as Kircher's `toni`.

### 3.3 `SYNTAGMA` — texture engine

Historical core:

- **I — simplex:** syllabic / note-against-note / homorhythmic four-part material.
- **II — floridum:** melismatic/florid counterpoint with independent voice rhythms.
- **III — fragmentary / secret / incomplete:** do not fabricate a complete historical corpus.

Neo evolution can treat the same physical banks as increasing degrees of independence and generative freedom.

### 3.4 `PINAX` — pattern family

Historically a pinax is selected largely by poetic metre. In the first instrumental Neo-Arca, a **NEO_WORKING_PINAX** instead represents a coherent family of musical structures.

Possible N1 pattern-family identities:

- sustained harmonic field
- stepwise cantus
- cadential figure
- ascending sequence
- descending sequence
- contrary-motion lattice
- imitation seed
- ostinato / ground
- arpeggiated field
- suspended / open cadence

The visual anatomy must still resemble the historical long table/slat: strophic/section columns above, dense four-voice numerical material, rhythm field below or paired beside it according to syntagma.

### 3.5 `MUSARITHM / VPERM` — pitch permutation

This is one of the Arca's most important controls.

The player should be able to:

- select a row directly;
- step previous/next;
- roll a deterministic chance selection;
- lock the row while changing rhythm;
- compare adjacent rows;
- mutate the row according to allowed historical/Neo operations.

A selected row should manifest audibly immediately or on the next quantized boundary, depending on performance mode.

### 3.6 `NOTAE TEMPORIS / RPERM` — rhythm permutation

For Syntagma I, pitch and rhythm remain separately selectable. For Syntagma II, the historical pairing between pitch and four-voice rhythm should be respected in HISTORICA mode.

Neo mode may expose:

- rhythm row selection;
- subdivision family;
- density;
- gate/articulation;
- swing/humanization where desired;
- polymetric or phase behavior only when clearly N1.

### 3.7 `AMBITUS` — register / spread

Historically the front `Palimpsestus Phonotacticus` / Scala Musica helps place pitch classes into acceptable ranges for Cantus, Altus, Tenor and Bassus.

Neo evolution:

- register center;
- range spread;
- octave displacement;
- compact ↔ open voicing;
- per-voice octave locks.

This should be manipulated through the front face / voice staves, not a generic set of four knobs if avoidable.

---

## 4. Historical variation procedures should become the instrument's mutation language

A major product opportunity emerges from Book VIII's own variation procedures. Instead of inventing a modern `randomize` button, the Neo-Arca can evolve controls Kircher already described.

### 4.1 `TRANSPOSITIO MUSARITHMORUM` → VOICE PERMUTE

Historically: exchange the three upper voice assignments of a musarithm while retaining the bass foundation.

Neo performance operation:

- rotate or permute Cantus/Altus/Tenor identities;
- optionally preserve one or more locked voices;
- animate the numerical rows physically crossing/reseating in the pinax;
- preserve provenance as a transformation of an existing pattern, not a newly generated pattern.

### 4.2 `MUTATIO TONORUM` → TONAL RECAST

Historically: apply the same musarithmic structure under a different tone.

Neo performance operation:

- keep permutation topology fixed;
- choose a new root/scale/tonus;
- remap all voices coherently;
- quantize the change at a phrase/loop boundary when playing live.

This is more historically meaningful than a generic DAW `transpose` knob because the identity of the pattern survives while its tonal field changes.

### 4.3 `MUTATIO RATIONIS VALORUM NOTARUM` → RHYTHM RECAST

Historically: vary the rhythmic-value scheme while retaining underlying musarithmic material.

Neo performance operation:

- hold pitch material;
- switch/cycle rhythm permutation;
- allow density/subdivision transforms downstream;
- preserve deterministic replay.

### 4.4 `PROCESSUS PER DISTINCTA MEMBRA` → FRAGMENT / MOSAIC ENGINE

Historically: use smaller constituent segments rather than complete verse-length structures, then assemble them in different orders. This is one of the most powerful bridges between Kircher's design and a modern loop instrument.

Neo evolution:

- split a selected pinax pattern into deterministic musical members/fragments;
- reorder or chain them;
- loop one member;
- create A/B/C/D phrase cells;
- mutate one cell while locking the others;
- create Euclidean-like or probability-like scheduling only as an N1 extension layered on top of the historical fragment model.

This should become the **core loop-building metaphor** rather than importing a conventional clip launcher wholesale.

---

## 5. Neo-Arca controls that are worth adding

The project should add innovations when they increase musical agency, but every innovation must attach to an existing physical/computational idea in the Arca.

| Neo control | Function | Best diegetic ancestor |
| --- | --- | --- |
| Root | tonal center | Mensa tonographica |
| Scale | pitch collection | Tonus |
| Arpeggio mode | break/sequence sonorities | Vperm row traversal |
| Arpeggio direction | up/down/pendulum/random/order | reading direction / row traversal, N1 |
| Chord field | constrain harmony | musarithmic sonority field |
| Loop length | temporal window | distincta membra / selected phrase span |
| Subdivision | pulse granularity | notae temporis |
| Density | note-event occupancy | rhythm permutation density |
| Mutation | distance from current state | historical mutatio operations |
| Voice lock | preserve selected parts | physical row/voice locking, N1 |
| Pattern lock | preserve Vperm while changing Rperm | historical pitch/rhythm separation |
| Rhythm lock | preserve Rperm while changing Vperm | historical pitch/rhythm separation |
| Register spread | compact/open voicing | Palimpsest / ambitus |
| Cadence openness | closed ↔ suspended loop | cadence/final behavior |
| Tension | consonant ↔ transgressive | law profile / direct interval policy |
| Orthodox/Heretical | active law | Neo-Arca law switch |

### Arpeggiation specifically

Arpeggiation should not simply mean "take a chord and run up/down". The more distinctive Neo-Arca interpretation is to treat the **Vperm itself as a traversal surface**.

Possible modes:

- **Columnar:** voices sound together as written.
- **Ascending:** Bassus → Tenor → Altus → Cantus.
- **Descending:** Cantus → Altus → Tenor → Bassus.
- **Alternating:** outer/inner or pendulum traversal.
- **Voice-order permutation:** traversal follows a selected transpositio order.
- **Member traversal:** sequence through `distincta membra` fragments.
- **Fortuna:** seeded deterministic traversal order.

That makes arpeggiation feel like an evolution of the Arca's numerical arrays rather than a pasted-on synth feature.

---

## 6. Loop instrument architecture

The first Neo-Arca should be able to become musically compelling before a full song arrangement system exists.

### Minimal loop state

```text
LoopState
├── sourcePinax
├── vpermSelection
├── rpermSelection
├── tonusOrScale
├── root
├── syntagmaTexture
├── memberSequence[]
├── loopLength
├── subdivision
├── registerState
├── voiceLocks[4]
├── patternLock
├── rhythmLock
├── mutationDepth
├── cadenceBoundary
├── lawProfile
└── seed / provenance
```

### Musical operations

- `STRIKE` — generate/commit current pattern.
- `MUTARE` — mutate unlocked structure while preserving locks.
- `RECAST TONUS` — remap current pattern to another tonal field.
- `RECAST RHYTHM` — preserve pitch, change rhythm.
- `PERMUTE VOICES` — historical upper-voice reassignment generalized for performance.
- `DIVIDE` — expose distincta membra.
- `CHAIN` — reorder/loop members.
- `FORTUNA` — deterministic chance choice from the currently valid permutation set.
- `RESTITUE` — return to the last committed state.

These verbs are more appropriate to the machine than `Generate`, `Randomize`, and `Reset`.

---

## 7. Backend vs frontend authority

Do not force every live performance gesture through the Python Ghost.

### Backend should remain authoritative for

- compositional generation;
- four-part voice-leading law;
- seed/provenance;
- deterministic structural mutations that alter exported composition identity;
- validation/diagnostics;
- canonical MIDI export.

### Frontend/Tone.js may own ephemeral performance interpretation for

- play/stop;
- previewing a row;
- quantized audition;
- temporary voice mute/solo;
- visualization;
- reversible arpeggio playback modes before committing them;
- loop transport.

If a live transformation must survive reload, be reproducible, or appear in exported MIDI, it becomes part of the committed composition state and must have explicit provenance. Do not let an invisible frontend-only mutation become indistinguishable from backend-authored music.

---

## 8. Narrow backend extension required before frontend wiring

The B10 Ghost is accepted. Do not reopen it broadly.

A later implementation pass should add an explicit **instrument/manual source path** roughly equivalent to:

```text
source = "semantic" | "instrument"
```

For `instrument`:

- `text` is absent/optional;
- semantic interpretation is bypassed;
- deterministic explicit defaults fill any omitted musical fields;
- `provenance.source` records `instrument`;
- direct tone/root/mode/meter/density/law controls remain first-class;
- the existing semantic path remains backward compatible;
- tests prove the two paths cannot be confused.

Do not use placeholder prose to satisfy the old API contract.

The new arpeggio/loop/fragment controls should be added only as their musical semantics become concrete. Avoid creating a giant request model full of speculative knobs before the physical instrument prototype proves which controls matter.

---

## 9. Historical research consequences

The instrumental direction does **not** make primary-source transcription less important. It makes it more useful.

A small genuine historical dataset can act as:

- reference material;
- a playable contrast against Neo patterns;
- a source of authentic variation logic;
- a visual grammar for the pinax;
- proof that the instrument lineage is real rather than decorative.

The immediate historical-data pilot remains:

1. independently transcribe a bounded portion of **Syntagma I, Pinax IV** from a public-domain 1650 scan;
2. independently transcribe the usable engraved **Mensa Tonographica** needed to resolve that sample;
3. inspect **Syntagma II, Pinax II** at useful resolution before designing the florid pinax bank;
4. record every transcribed row/cell with source locator and confidence;
5. never copy Cashner's copyrighted modern transcription as the project dataset.

---

## 10. Acceptance test for the eventual first playable

A successful first playable should allow a user, without typing prose, to spend ten minutes doing something musically meaningful:

- choose a tonal field;
- choose simple or florid texture;
- pull a pinax;
- audition several pitch permutations;
- audition several rhythms;
- create a loop;
- recast its tone;
- change rhythm without losing pitch identity;
- permute or lock voices;
- divide the material into members and rearrange them;
- push it toward or away from dissonance;
- mutate the unlocked parts;
- hear/see all four voices react;
- save/replay/export a deterministic result.

If that experience is deep and satisfying, the Neo-Arca is an instrument.

If the player mostly presses one button and waits for a finished composition, it is not.