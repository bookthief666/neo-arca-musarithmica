# NEO-ARCA MUSARITHMICA — Phase 1: THE GHOST

> «A seventeenth-century combinatorial music engine excavated from an impossible
> technological timeline.»

In 1650 Athanasius Kircher published *Musurgia Universalis*, describing the **Arca
Musarithmica** — a cabinet of inscribed rods whose numbers and note-values let a user
assemble contrapuntal music by structured combination. Its significance was never that
it resembled a computer; it was that it treated composition as something that could be
**encoded, categorised, permuted, constrained, recombined and executed** through a formal
symbolic system.

This repository replaces the wooden cabinet with a deterministic generative engine.
Phase 1 builds only **THE GHOST**: the Python composition backend. THE SKIN & EYE
(React / Three.js) and THE VOICE (Tone.js) are later phases, and the API is shaped for
them.

---

## What it does

A sentence enters through a *Polygraphia*-inspired semantic mapper and leaves as a
deterministic four-voice composition:

```
POST /compose  {"text": "I dreamed of a cathedral sinking slowly into a black sea"}
  -> Phrygian on E-flat, 47 bpm, descending contour, low register, sostenuto
  -> genuine SATB counterpoint, validated against explicit rules
  -> event JSON for Tone.js + Base64 Standard MIDI, one track per voice
```

## Running it

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd)
.venv\Scripts\activate.bat

pip install -r requirements.txt
pytest -q
uvicorn main:app --reload
```

For a reproducible install — the exact versions this was developed and tested against,
including transitive dependencies — use `requirements.lock.txt` instead:
`pip install -r requirements.lock.txt`. See `docs/DETERMINISM.md` for what that does and
does not guarantee about byte-identical output across environments.

Interactive documentation is at <http://127.0.0.1:8000/docs>.

For a broader correctness/performance sweep than the unit suite exercises, see
`scripts/stress_matrix.py --profile smoke` (development, seconds) or `--profile full`
(release verification, several minutes; ~1,800 generations against a checked-in,
inspectable, machine-readable matrix). It writes a structured JSON report and a concise
terminal summary; see the module docstring for the full contract.

```bash
curl -s -X POST http://127.0.0.1:8000/compose \
  -H 'Content-Type: application/json' \
  -d '{
        "text": "Sorrowful lament beneath a dying winter sun",
        "seed": 418,
        "measures": 8,
        "meter": "4/4",
        "heretical": false
      }' | python -m json.tool | head -60
```

To hear it:

```bash
curl -s -X POST http://127.0.0.1:8000/compose \
  -H 'Content-Type: application/json' \
  -d '{"text":"Sorrowful lament beneath a dying winter sun","seed":418}' \
  | python -c "import base64,json,sys; open('arca.mid','wb').write(base64.b64decode(json.load(sys.stdin)['midi_base64']))"
```

## Architecture

| Module | Responsibility |
| --- | --- |
| `theory.py` | Voices, ranges, the seven diatonic modes, pitch spelling, interval classification |
| `determinism.py` | Stable hashing, labelled seed streams, provenance. No global randomness anywhere |
| `semantics.py` | POLYGRAPHIA — lexicon → ten semantic axes → musical configuration |
| `rhythm.py` | Meters, harmonic rhythm, per-voice appetite for diminution |
| `harmony.py` | Phrases, cadence formulas, *musica ficta*, the harmonic skeleton |
| `constraints.py` | LEX MUSICA — the rule engine and the two law profiles |
| `kircher_engine.py` | The voicing solver, the diminution layer, repair, validation |
| `midi_export.py` | music21 score construction and Base64 MIDI serialisation |
| `models.py` | Pydantic request/response contract |
| `main.py` | FastAPI application |

### The generative core

Composition happens in two layers.

**The backbone** is solved, not stacked. Every slot of the harmonic skeleton is filled by
searching over *complete four-note sonorities*, scored against the previous sonority and
each voice's own melodic history. Parallel perfects, crossing, spacing, doubling, range
and leap recovery prune candidates before a note is committed. Chronological
backtracking with an explicit budget recovers from dead ends; three relaxation levels sit
behind that, and a controlled `GenerationError` behind those.

**The surface** is added independently per voice: passing tones, neighbours, suspensions
tied over the bar, anticipations and arpeggiations, with a stagger term that damps a
voice's activity when its neighbours are already moving. Anything the surface introduces
is re-checked on the rendered grid and reverted if it breaks a hard law.

### The two law profiles

Rules **detect**; profiles **judge**. A rule reports "these two voices moved in parallel
fifths" and has no opinion about it. `ORTHODOX` weights that finding at +14 and treats it
as fatal. `HERETICAL` weights it at −4.5 and marks it *intended*. MODUS HAERETICUS is not
a disabled checker — it is the same body of law, inverted, so a Heretical composition can
still be validated against Orthodox law and every transgression in it can be told apart
from an implementation defect.

### Determinism

Identical text, configuration, seed, law profile and engine version produce an identical
composition, down to the MIDI bytes. The engine never touches `random.seed`; every
stochastic decision draws from an explicit, labelled seed stream.

## Scope

Phase 1 deliberately excludes authentication, databases, user accounts and deployment
infrastructure. The Orthodox profile is an explicit, extensible subset of species
counterpoint adapted into a four-part generative grammar — not a complete implementation
of Fux, Palestrina or eighteenth-century harmony.
