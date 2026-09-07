"""semantics.py -- POLYGRAPHIA: deterministic natural language -> musical parameters.

Kircher's *Polygraphia Nova* pursued a machine for carrying meaning across linguistic
boundaries.  This module carries meaning across a different boundary: from a sentence
to a musical configuration.

The Phase 1 implementation is deliberately **transparent and dependency-free**.  There
is no model download, no paid API, no opaque embedding: a curated lexicon projects
tokens onto ten continuous semantic axes, the axes are saturated into ``[-1, 1]``, and a
small set of documented mapping functions turns the axes into mode, tonic, tempo,
register, density, contour, cadence strength and instrumentation.  Every intermediate is
returned to the caller so the process is inspectable.

The seam for later work is :class:`SemanticAnalyzer`: replace ``_axes_from_tokens`` with
an embedding or LLM call that produces the same :class:`SemanticAxes`, and every
downstream mapping keeps working unchanged.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from determinism import SeedStream, stable_hash
from theory import CANDIDATE_TONICS, ModeName, mode_spec

# --------------------------------------------------------------------------------------
# Axes
# --------------------------------------------------------------------------------------

#: The semantic space.  Every axis is signed and saturates into ``[-1, 1]``.
AXIS_NAMES: Tuple[str, ...] = (
    "valence",     # -1 sorrowful ......... +1 radiant
    "energy",      # -1 motionless ........ +1 violent
    "density",     # -1 sparse ............ +1 teeming
    "tension",     # -1 pure consonance ... +1 chromatic dissonance
    "register",    # -1 subterranean ...... +1 high and thin
    "contour",     # -1 falling ........... +1 rising
    "cadence",     # -1 unresolved ........ +1 firmly closed
    "heresy",      # -1 orthodox .......... +1 transgressive
    "weight",      # -1 weightless ........ +1 massive, grave
    "luminosity",  # -1 murky ............. +1 luminous
)


@dataclass(frozen=True)
class SemanticAxes:
    valence: float = 0.0
    energy: float = 0.0
    density: float = 0.0
    tension: float = 0.0
    register: float = 0.0
    contour: float = 0.0
    cadence: float = 0.0
    heresy: float = 0.0
    weight: float = 0.0
    luminosity: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {name: round(getattr(self, name), 4) for name in AXIS_NAMES}


def _saturate(value: float) -> float:
    """Squash an unbounded accumulation into ``[-1, 1]`` without a hard clip.

    A rational sigmoid (``x / (1 + |x|)``) scaled so that a single strong lexeme
    (~0.9) lands near 0.55 and a pile-up of five reinforcing lexemes approaches, but
    never reaches, 1.0.  This keeps long sentences from saturating instantly while
    still letting emphasis accumulate.
    """
    scaled = value * 0.85
    return scaled / (1.0 + abs(scaled))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


# --------------------------------------------------------------------------------------
# Lexicon
# --------------------------------------------------------------------------------------

# Each entry maps a *stem* to axis deltas.  Magnitudes are roughly:
#   0.3 = a tint, 0.6 = a clear colour, 0.9 = the dominant sense of the phrase.
LEXICON: Dict[str, Dict[str, float]] = {
    # -- grief, lament, mourning -------------------------------------------------
    "sorrow":   {"valence": -0.9, "energy": -0.4, "contour": -0.6, "weight": 0.3},
    "sorrowful": {"valence": -0.9, "energy": -0.4, "contour": -0.6, "weight": 0.3},
    "lament":   {"valence": -0.85, "energy": -0.4, "contour": -0.7, "register": -0.3},
    "grief":    {"valence": -0.9, "energy": -0.3, "contour": -0.6, "weight": 0.4},
    "mourn":    {"valence": -0.8, "energy": -0.5, "contour": -0.6, "weight": 0.3},
    "weep":     {"valence": -0.8, "energy": -0.2, "contour": -0.7, "density": 0.2},
    "tear":     {"valence": -0.5, "contour": -0.4},
    "elegy":    {"valence": -0.7, "energy": -0.4, "contour": -0.4, "cadence": 0.2},
    "requiem":  {"valence": -0.7, "energy": -0.5, "weight": 0.7, "cadence": 0.4},
    "dirge":    {"valence": -0.8, "energy": -0.6, "weight": 0.6, "register": -0.4},
    "sad":      {"valence": -0.7, "energy": -0.3, "contour": -0.4},
    "melanchol": {"valence": -0.6, "energy": -0.4, "contour": -0.3, "density": -0.2},
    "despair":  {"valence": -0.9, "tension": 0.4, "contour": -0.6, "cadence": -0.3},
    "anguish":  {"valence": -0.8, "energy": 0.3, "tension": 0.6},
    "wound":    {"valence": -0.6, "tension": 0.4},
    "farewell": {"valence": -0.4, "contour": -0.5, "cadence": 0.5},
    "loss":     {"valence": -0.7, "contour": -0.5, "density": -0.2},
    "ruin":     {"valence": -0.6, "tension": 0.3, "contour": -0.5, "weight": 0.4},
    "ash":      {"valence": -0.5, "energy": -0.4, "register": -0.2, "luminosity": -0.4},
    "widow":    {"valence": -0.6, "energy": -0.4, "contour": -0.4},

    # -- radiance, triumph, ascent ------------------------------------------------
    "radiant":  {"valence": 0.9, "luminosity": 0.9, "contour": 0.4, "register": 0.3},
    "triumph":  {"valence": 0.85, "energy": 0.7, "contour": 0.6, "cadence": 0.7},
    "glory":    {"valence": 0.8, "luminosity": 0.7, "weight": 0.4, "cadence": 0.5},
    "joy":      {"valence": 0.9, "energy": 0.6, "contour": 0.5, "density": 0.3},
    "exult":    {"valence": 0.85, "energy": 0.8, "contour": 0.7, "density": 0.4},
    "ascend":   {"contour": 0.9, "register": 0.5, "energy": 0.3},
    "ascent":   {"contour": 0.9, "register": 0.5, "energy": 0.3},
    "rise":     {"contour": 0.8, "register": 0.4},
    "rising":   {"contour": 0.8, "register": 0.4},
    "soar":     {"contour": 0.85, "register": 0.7, "energy": 0.4},
    "dawn":     {"valence": 0.6, "luminosity": 0.8, "contour": 0.5, "energy": 0.2},
    "sun":      {"valence": 0.6, "luminosity": 0.8, "register": 0.2},
    "gold":     {"valence": 0.6, "luminosity": 0.7, "weight": 0.2},
    "crown":    {"valence": 0.6, "weight": 0.4, "cadence": 0.5},
    "victory":  {"valence": 0.8, "energy": 0.7, "cadence": 0.7, "contour": 0.5},
    "praise":   {"valence": 0.7, "energy": 0.4, "contour": 0.4, "cadence": 0.4},
    "bright":   {"valence": 0.7, "luminosity": 0.8, "register": 0.3},
    "clear":    {"valence": 0.4, "luminosity": 0.5, "tension": -0.4, "density": -0.2},
    "pure":     {"valence": 0.5, "tension": -0.7, "luminosity": 0.5, "heresy": -0.5},
    "holy":     {"valence": 0.6, "luminosity": 0.6, "heresy": -0.6, "cadence": 0.4},
    "heaven":   {"valence": 0.7, "register": 0.7, "luminosity": 0.7, "contour": 0.5},
    "angel":    {"valence": 0.6, "register": 0.6, "luminosity": 0.6},
    "silver":   {"valence": 0.3, "luminosity": 0.6, "register": 0.4, "weight": -0.3},
    "crystal":  {"luminosity": 0.7, "register": 0.5, "tension": -0.3, "weight": -0.3},

    # -- transgression, abyss, the left-hand path ---------------------------------
    "forbidden": {"heresy": 0.9, "tension": 0.7, "valence": -0.4},
    "heretic":  {"heresy": 1.0, "tension": 0.6, "valence": -0.3},
    "heresy":   {"heresy": 1.0, "tension": 0.6, "valence": -0.3},
    "profane":  {"heresy": 0.85, "tension": 0.5, "valence": -0.3},
    "blasphem": {"heresy": 0.95, "tension": 0.7, "energy": 0.4},
    "abyss":    {"heresy": 0.7, "tension": 0.7, "register": -0.9, "weight": 0.6,
                 "valence": -0.6, "luminosity": -0.8},
    "void":     {"tension": 0.5, "register": -0.5, "density": -0.7, "valence": -0.4,
                 "luminosity": -0.7},
    "fracture": {"heresy": 0.6, "tension": 0.8, "energy": 0.5, "cadence": -0.5},
    "shatter":  {"heresy": 0.5, "tension": 0.8, "energy": 0.8, "density": 0.4},
    "curse":    {"heresy": 0.8, "tension": 0.7, "valence": -0.6},
    "demon":    {"heresy": 0.85, "tension": 0.7, "valence": -0.6, "register": -0.3},
    "devil":    {"heresy": 0.85, "tension": 0.8, "valence": -0.5},
    "hell":     {"heresy": 0.8, "tension": 0.7, "register": -0.7, "valence": -0.7},
    "infernal": {"heresy": 0.85, "tension": 0.7, "register": -0.6, "energy": 0.4},
    "corrupt":  {"heresy": 0.7, "tension": 0.6, "valence": -0.4},
    "unclean":  {"heresy": 0.6, "tension": 0.5, "valence": -0.4},
    "witch":    {"heresy": 0.7, "tension": 0.5, "energy": 0.3},
    "occult":   {"heresy": 0.6, "tension": 0.4, "luminosity": -0.5},
    "serpent":  {"heresy": 0.5, "tension": 0.4, "contour": -0.3, "register": -0.3},
    "poison":   {"heresy": 0.5, "tension": 0.6, "valence": -0.5},
    "madness":  {"heresy": 0.7, "tension": 0.8, "energy": 0.6, "cadence": -0.6},
    "chaos":    {"heresy": 0.6, "tension": 0.7, "energy": 0.7, "density": 0.5,
                 "cadence": -0.6},
    "wrong":    {"heresy": 0.5, "tension": 0.5, "valence": -0.3},
    "broken":   {"tension": 0.5, "cadence": -0.5, "valence": -0.4, "energy": -0.2},
    "unresolved": {"cadence": -0.9, "tension": 0.4},

    # -- stillness, sleep, silence -------------------------------------------------
    "still":    {"energy": -0.8, "density": -0.6},
    "silence":  {"energy": -0.8, "density": -0.8, "luminosity": -0.2},
    "sleep":    {"energy": -0.7, "density": -0.5, "contour": -0.3, "valence": 0.1},
    "dream":    {"energy": -0.4, "density": -0.3, "tension": 0.2, "luminosity": 0.2},
    "slow":     {"energy": -0.8, "density": -0.4},
    "quiet":    {"energy": -0.6, "density": -0.4},
    "calm":     {"energy": -0.6, "tension": -0.4, "valence": 0.3},
    "hush":     {"energy": -0.7, "density": -0.5},
    "drift":    {"energy": -0.4, "contour": -0.2, "cadence": -0.4, "density": -0.3},
    "linger":   {"energy": -0.5, "density": -0.4, "cadence": -0.2},
    "patient":  {"energy": -0.5, "weight": 0.2},
    "eternal":  {"energy": -0.4, "weight": 0.6, "cadence": 0.3},
    "empty":    {"density": -0.8, "valence": -0.3, "luminosity": -0.3},
    "hollow":   {"density": -0.6, "valence": -0.4, "tension": 0.2, "register": -0.3},

    # -- violence, storm, machinery ------------------------------------------------
    "storm":    {"energy": 0.8, "density": 0.7, "tension": 0.5, "valence": -0.3},
    "thunder":  {"energy": 0.8, "weight": 0.7, "register": -0.5, "density": 0.4},
    "rage":     {"energy": 0.9, "tension": 0.7, "valence": -0.5, "density": 0.5},
    "fury":     {"energy": 0.9, "tension": 0.7, "valence": -0.4, "density": 0.6},
    "war":      {"energy": 0.8, "tension": 0.6, "valence": -0.4, "weight": 0.4},
    "burn":     {"energy": 0.7, "tension": 0.4, "luminosity": 0.4},
    "fire":     {"energy": 0.7, "luminosity": 0.6, "contour": 0.3, "density": 0.3},
    "blade":    {"energy": 0.6, "tension": 0.5, "register": 0.3},
    "iron":     {"weight": 0.7, "register": -0.3, "tension": 0.2, "luminosity": -0.3},
    "engine":   {"energy": 0.5, "density": 0.6, "weight": 0.4},
    "machine":  {"energy": 0.4, "density": 0.6, "tension": 0.3, "weight": 0.3},
    "gear":     {"density": 0.6, "energy": 0.4, "weight": 0.3},
    "clock":    {"density": 0.4, "energy": 0.2, "cadence": 0.3},
    "brass":    {"weight": 0.5, "luminosity": 0.3, "energy": 0.3},
    "hammer":   {"energy": 0.7, "weight": 0.7, "density": 0.4},
    "swift":    {"energy": 0.8, "density": 0.5, "weight": -0.4},
    "dance":    {"energy": 0.6, "valence": 0.5, "density": 0.4, "contour": 0.2},
    "flight":   {"energy": 0.6, "register": 0.6, "contour": 0.6, "weight": -0.5},

    # -- sacred, ritual, architecture ---------------------------------------------
    "cathedral": {"weight": 0.8, "register": -0.2, "cadence": 0.4, "energy": -0.3,
                  "luminosity": 0.3, "density": -0.2},
    "chapel":   {"weight": 0.4, "energy": -0.3, "density": -0.3},
    "monast":   {"weight": 0.5, "energy": -0.5, "valence": -0.1, "density": -0.4},
    "choir":    {"weight": 0.3, "density": 0.2, "cadence": 0.3},
    "chant":    {"energy": -0.4, "density": -0.4, "weight": 0.4, "contour": -0.1},
    "psalm":    {"energy": -0.3, "weight": 0.4, "cadence": 0.4},
    "hymn":     {"valence": 0.4, "weight": 0.4, "cadence": 0.5},
    "prayer":   {"energy": -0.4, "valence": 0.2, "cadence": 0.3, "contour": 0.2},
    "ritual":   {"weight": 0.5, "density": 0.2, "cadence": 0.3, "energy": -0.1},
    "relic":    {"weight": 0.5, "energy": -0.4, "luminosity": -0.2},
    "bell":     {"register": 0.4, "weight": 0.3, "density": -0.2, "luminosity": 0.4},
    "organ":    {"weight": 0.7, "density": 0.3, "register": -0.3},
    "stone":    {"weight": 0.8, "energy": -0.4, "register": -0.4},
    "vault":    {"weight": 0.6, "register": -0.3, "density": -0.2},
    "tower":    {"register": 0.6, "contour": 0.5, "weight": 0.4},
    "labyrinth": {"tension": 0.5, "density": 0.5, "cadence": -0.4, "heresy": 0.3},

    # -- water, depth, cold ---------------------------------------------------------
    "sea":      {"register": -0.4, "weight": 0.5, "energy": -0.1, "density": 0.2},
    "ocean":    {"register": -0.5, "weight": 0.6, "density": 0.2},
    "deep":     {"register": -0.8, "weight": 0.6},
    "sink":     {"contour": -0.8, "register": -0.6, "energy": -0.3},
    "sinking":  {"contour": -0.8, "register": -0.6, "energy": -0.3},
    "drown":    {"contour": -0.8, "register": -0.7, "valence": -0.6, "tension": 0.3},
    "fall":     {"contour": -0.8, "register": -0.4},
    "descend":  {"contour": -0.9, "register": -0.5},
    "descent":  {"contour": -0.9, "register": -0.5},
    "below":    {"register": -0.6, "contour": -0.3},
    "beneath":  {"register": -0.6, "contour": -0.3},
    "under":    {"register": -0.5, "contour": -0.2},
    "buried":   {"register": -0.7, "weight": 0.5, "valence": -0.4, "energy": -0.5},
    "cold":     {"valence": -0.3, "energy": -0.3, "luminosity": -0.2, "tension": 0.2},
    "frost":    {"valence": -0.3, "energy": -0.4, "luminosity": 0.2, "register": 0.3},
    "ice":      {"valence": -0.2, "energy": -0.4, "luminosity": 0.3, "tension": 0.2},
    "winter":   {"valence": -0.5, "energy": -0.4, "luminosity": -0.2, "density": -0.3},
    "rain":     {"energy": -0.2, "density": 0.4, "valence": -0.2, "contour": -0.4},
    "mist":     {"density": -0.4, "luminosity": -0.3, "tension": 0.2, "cadence": -0.3},
    "fog":      {"density": -0.4, "luminosity": -0.4, "cadence": -0.3},

    # -- darkness, night, decay ------------------------------------------------------
    "dark":     {"valence": -0.5, "luminosity": -0.8, "register": -0.3},
    "black":    {"valence": -0.5, "luminosity": -0.9, "register": -0.3},
    "night":    {"valence": -0.3, "luminosity": -0.7, "energy": -0.4},
    "shadow":   {"valence": -0.4, "luminosity": -0.7, "tension": 0.3},
    "dusk":     {"valence": -0.3, "luminosity": -0.5, "energy": -0.4, "contour": -0.3},
    "eclipse":  {"luminosity": -0.8, "tension": 0.5, "valence": -0.4},
    "dying":    {"valence": -0.7, "energy": -0.5, "contour": -0.6, "cadence": 0.2},
    "die":      {"valence": -0.7, "energy": -0.5, "contour": -0.6},
    "death":    {"valence": -0.8, "energy": -0.4, "weight": 0.5, "contour": -0.5},
    "decay":    {"valence": -0.6, "energy": -0.4, "tension": 0.4, "contour": -0.4},
    "rot":      {"valence": -0.6, "tension": 0.5, "heresy": 0.3},
    "rust":     {"valence": -0.4, "tension": 0.3, "energy": -0.3, "luminosity": -0.3},
    "grave":    {"valence": -0.6, "weight": 0.7, "register": -0.6, "energy": -0.5},
    "tomb":     {"valence": -0.5, "weight": 0.6, "register": -0.6, "energy": -0.5},
    "bone":     {"valence": -0.4, "weight": 0.3, "tension": 0.2, "density": -0.2},
    "ghost":    {"valence": -0.3, "density": -0.5, "register": 0.3, "tension": 0.3},
    "memory":   {"valence": -0.2, "energy": -0.3, "cadence": -0.2},
    "forgotten": {"valence": -0.4, "energy": -0.4, "density": -0.4, "luminosity": -0.3},
    "ancient":  {"weight": 0.6, "energy": -0.4, "luminosity": -0.2},

    # -- scale and multitude ---------------------------------------------------------
    "vast":     {"weight": 0.6, "density": -0.2, "energy": -0.2},
    "immense":  {"weight": 0.8, "energy": -0.1},
    "great":    {"weight": 0.5},
    "small":    {"weight": -0.5, "density": -0.2, "register": 0.3},
    "fragile":  {"weight": -0.6, "density": -0.4, "register": 0.3, "energy": -0.3},
    "thin":     {"weight": -0.5, "density": -0.5, "register": 0.4},
    "thousand": {"density": 0.7, "energy": 0.3},
    "swarm":    {"density": 0.9, "energy": 0.6, "tension": 0.4},
    "teeming":  {"density": 0.8, "energy": 0.5},
    "multitude": {"density": 0.7, "weight": 0.3},
    "single":   {"density": -0.7, "weight": -0.2},
    "alone":    {"density": -0.6, "valence": -0.4},
    "endless":  {"cadence": -0.6, "energy": -0.2, "weight": 0.3},
}

#: Words that invert the sense of the lexeme that follows them.
NEGATORS = frozenset({"no", "not", "never", "without", "un", "nor", "less", "lacking"})

#: Words that scale the lexeme that follows them.
INTENSIFIERS: Dict[str, float] = {
    "very": 1.5, "utterly": 1.7, "profoundly": 1.6, "deeply": 1.5, "immensely": 1.6,
    "absolutely": 1.6, "wholly": 1.4, "terribly": 1.5, "impossibly": 1.6,
    "slightly": 0.55, "faintly": 0.6, "barely": 0.5, "somewhat": 0.6, "half": 0.65,
}

_STEM_SUFFIXES = ("ingly", "ously", "ness", "ing", "edly", "ies", "ied", "ed", "es",
                  "ly", "s")
_TOKEN_RE = re.compile(r"[a-z]+")


def normalize_text(text: str) -> str:
    """Fold accents, lowercase, and collapse whitespace."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(stripped.lower().split())


def tokenize(text: str) -> List[str]:
    """Alphabetic tokens of the normalised text, in order."""
    return _TOKEN_RE.findall(normalize_text(text))


def stem(token: str) -> str:
    """A crude, deterministic suffix stripper -- enough to unify lexicon lookups."""
    for suffix in _STEM_SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[: -len(suffix)]
    return token


def lookup(token: str) -> Optional[Tuple[str, Mapping[str, float]]]:
    """Resolve *token* to a ``(lexeme, axis deltas)`` pair, or ``None``.

    Resolution order: exact token, stemmed token, then a longest-prefix match against
    lexicon keys of at least four characters (so ``"cathedrals"`` finds ``"cathedral"``
    and ``"lamenting"`` finds ``"lament"`` even when stemming falls short).
    """
    if token in LEXICON:
        return token, LEXICON[token]
    stemmed = stem(token)
    if stemmed in LEXICON:
        return stemmed, LEXICON[stemmed]
    best: Optional[str] = None
    for key in LEXICON:
        if len(key) < 4:
            continue
        if token.startswith(key) or stemmed.startswith(key) or key.startswith(stemmed):
            if len(key) >= 4 and (best is None or len(key) > len(best)):
                if key.startswith(stemmed) and len(stemmed) < 4:
                    continue
                best = key
    if best is not None:
        return best, LEXICON[best]
    return None


@dataclass(frozen=True)
class MatchedTerm:
    token: str
    lexeme: str
    weight: float

    def as_dict(self) -> Dict[str, object]:
        return {"token": self.token, "lexeme": self.lexeme, "weight": round(self.weight, 3)}


# --------------------------------------------------------------------------------------
# Mode affinities
# --------------------------------------------------------------------------------------

#: Dot-product weights: ``score(mode) = sum(affinity[axis] * axes[axis])``.
#: These encode the *character* each mode is asked to carry, not a claim about how
#: seventeenth-century theorists classified the modes.
MODE_AFFINITY: Dict[ModeName, Dict[str, float]] = {
    ModeName.IONIAN: {
        "valence": 1.0, "luminosity": 0.45, "tension": -0.65, "heresy": -0.6,
        "cadence": 0.3,
    },
    ModeName.LYDIAN: {
        "valence": 0.6, "luminosity": 1.0, "register": 0.35, "contour": 0.3,
        "tension": -0.1, "heresy": -0.1,
    },
    ModeName.MIXOLYDIAN: {
        "valence": 0.45, "energy": 0.65, "luminosity": 0.2, "tension": -0.15,
        "cadence": -0.1, "heresy": -0.2,
    },
    ModeName.DORIAN: {
        "valence": -0.2, "weight": 0.55, "energy": -0.15, "tension": 0.05,
        "cadence": 0.2, "heresy": -0.3,
    },
    ModeName.AEOLIAN: {
        "valence": -0.75, "weight": 0.3, "contour": -0.35, "luminosity": -0.3,
        "tension": 0.1, "heresy": -0.2,
    },
    ModeName.PHRYGIAN: {
        "valence": -0.85, "tension": 0.5, "contour": -0.6, "register": -0.25,
        "luminosity": -0.35, "heresy": 0.35,
    },
    ModeName.LOCRIAN: {
        "valence": -0.5, "tension": 1.0, "heresy": 1.0, "cadence": -0.6,
        "luminosity": -0.4,
    },
}

#: Instrument vocabulary carried over from the prototype (Reference Artifact A),
#: extended with the General MIDI programs the exporter needs.
INSTRUMENTS: Dict[str, Dict[str, object]] = {
    "organ":       {"name": "Pipe Organ", "type": "mixed", "gm_program": 19},
    "harpsichord": {"name": "Harpsichord", "type": "sawtooth", "gm_program": 6},
    "viola":       {"name": "Viola da Gamba", "type": "sawtooth", "gm_program": 41},
    "choir":       {"name": "Choir", "type": "mixed", "gm_program": 52},
    "pulse50":     {"name": "NES Pulse (50%)", "type": "square", "gm_program": 80},
    "crusher":     {"name": "Bitcrushed Noise", "type": "sawtooth", "gm_program": 81},
}

ARTICULATIONS: Dict[str, float] = {
    "legato": 0.99,
    "sostenuto": 0.94,
    "ordinario": 0.88,
    "detached": 0.74,
    "martellato": 0.62,
}


# --------------------------------------------------------------------------------------
# Suggestions
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SemanticSuggestion:
    """The musical configuration the text asks for, before user overrides."""

    mode: ModeName
    tonic: str
    tempo: int
    meter: str
    measures: int
    density: float               # 0..1, drives harmonic rhythm and diminution
    register_shift: int          # semitones applied to every voice's tessitura
    contour_bias: float          # -1..1, preferred soprano direction
    cadence_strength: float      # 0..1
    tension: float               # 0..1, appetite for dissonance
    heresy: float                # 0..1
    heretical: bool
    phrase_measures: int
    articulation: str
    mood: str
    ensemble: str
    instrumentation: Dict[str, str]

    def as_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["mode"] = self.mode.value
        for key in ("density", "contour_bias", "cadence_strength", "tension", "heresy"):
            payload[key] = round(float(payload[key]), 4)
        return payload


@dataclass(frozen=True)
class SemanticAnalysis:
    """Everything the semantic stage decided, and why."""

    source_text: str
    normalized_text: str
    tokens: List[str]
    matched_terms: List[MatchedTerm]
    unmatched_tokens: List[str]
    axes: SemanticAxes
    mode_scores: Dict[str, float]
    suggestion: SemanticSuggestion
    fallback_used: bool

    def as_dict(self) -> Dict[str, object]:
        return {
            "source_text": self.source_text,
            "normalized_text": self.normalized_text,
            "tokens": self.tokens,
            "matched_terms": [m.as_dict() for m in self.matched_terms],
            "unmatched_tokens": self.unmatched_tokens,
            "axes": self.axes.as_dict(),
            "mode_scores": {k: round(v, 4) for k, v in self.mode_scores.items()},
            "suggestion": self.suggestion.as_dict(),
            "fallback_used": self.fallback_used,
        }


class SemanticAnalyzer:
    """Deterministic text -> :class:`SemanticAnalysis`.

    The analyzer is stateless and side-effect free; the only randomness is the explicit
    :class:`SeedStream` derived from the normalised text, which is used solely for
    tie-breaking and for the no-match fallback.
    """

    #: Meters the engine is willing to choose, with the axis conditions that favour them.
    METER_CANDIDATES: Tuple[str, ...] = ("4/4", "3/4", "2/2", "3/2", "6/8")

    def analyze(self, text: str, *, default_measures: int = 8) -> SemanticAnalysis:
        normalized = normalize_text(text)
        tokens = tokenize(normalized)
        matched, unmatched, raw = self._accumulate(tokens)

        fallback_used = not matched
        stream = SeedStream(stable_hash("polygraphia", normalized))
        if fallback_used:
            raw = self._fallback_axes(stream)

        # A small deterministic tint keeps two different sentences with identical
        # lexical hits from producing literally the same configuration.
        tint = stream.derive("tint")
        axes = SemanticAxes(
            **{
                name: _saturate(raw.get(name, 0.0) + tint.jitter(0.07))
                for name in AXIS_NAMES
            }
        )

        mode_scores = self._mode_scores(axes, stream)
        mode = max(mode_scores, key=lambda name: mode_scores[name])
        mode_enum = ModeName(mode)
        suggestion = self._suggest(axes, mode_enum, stream, default_measures)

        return SemanticAnalysis(
            source_text=text,
            normalized_text=normalized,
            tokens=tokens,
            matched_terms=matched,
            unmatched_tokens=unmatched,
            axes=axes,
            mode_scores=mode_scores,
            suggestion=suggestion,
            fallback_used=fallback_used,
        )

    # -- stages ------------------------------------------------------------------
    def _accumulate(
        self, tokens: Sequence[str]
    ) -> Tuple[List[MatchedTerm], List[str], Dict[str, float]]:
        raw: Dict[str, float] = {name: 0.0 for name in AXIS_NAMES}
        matched: List[MatchedTerm] = []
        unmatched: List[str] = []
        polarity = 1.0
        scale = 1.0
        for token in tokens:
            if token in NEGATORS:
                polarity = -1.0
                continue
            if token in INTENSIFIERS:
                scale = INTENSIFIERS[token]
                continue
            found = lookup(token)
            if found is None:
                unmatched.append(token)
                # A modifier only reaches across one unmatched word.
                polarity, scale = 1.0, 1.0
                continue
            lexeme, deltas = found
            weight = polarity * scale
            for axis, value in deltas.items():
                raw[axis] += value * weight
            matched.append(MatchedTerm(token=token, lexeme=lexeme, weight=weight))
            polarity, scale = 1.0, 1.0
        return matched, unmatched, raw

    def _fallback_axes(self, stream: SeedStream) -> Dict[str, float]:
        """Stable pseudo-semantics for text the lexicon does not recognise.

        Unknown input must still yield a *reproducible* and *varied* composition rather
        than always collapsing to the same neutral default.
        """
        source = stream.derive("fallback")
        return {name: source.derive(name).uniform(-0.75, 0.75) for name in AXIS_NAMES}

    def _mode_scores(self, axes: SemanticAxes, stream: SeedStream) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        breaker = stream.derive("mode-tiebreak")
        for mode_name, affinity in MODE_AFFINITY.items():
            total = sum(weight * getattr(axes, axis) for axis, weight in affinity.items())
            total += breaker.derive(mode_name.value).jitter(0.04)
            scores[mode_name.value] = total
        return scores

    def _suggest(
        self,
        axes: SemanticAxes,
        mode: ModeName,
        stream: SeedStream,
        default_measures: int,
    ) -> SemanticSuggestion:
        spec = mode_spec(mode)

        tempo = int(round(_clamp(
            88.0 + 42.0 * axes.energy - 20.0 * axes.weight
            + 8.0 * axes.valence + 7.0 * axes.density,
            40.0, 168.0,
        )))
        density = _clamp(0.5 + 0.5 * axes.density + 0.15 * axes.energy, 0.05, 0.98)
        register_shift = int(round(_clamp(
            4.5 * axes.register - 1.5 * axes.weight, -5.0, 5.0
        )))
        cadence_strength = _clamp(
            (0.6 + 0.4 * axes.cadence + 0.12 * axes.valence) * spec.cadence_ceiling,
            0.05, 1.0,
        )
        tension = _clamp(0.5 + 0.5 * axes.tension, 0.0, 1.0)
        heresy = _clamp(0.5 + 0.45 * axes.heresy + 0.15 * max(0.0, axes.tension), 0.0, 1.0)
        phrase_measures = 2 if axes.energy > 0.3 or axes.density > 0.45 else 4

        return SemanticSuggestion(
            mode=mode,
            tonic=self._suggest_tonic(axes, stream),
            tempo=tempo,
            meter=self._suggest_meter(axes, stream),
            measures=default_measures,
            density=density,
            register_shift=register_shift,
            contour_bias=axes.contour,
            cadence_strength=cadence_strength,
            tension=tension,
            heresy=heresy,
            heretical=heresy >= 0.72,
            phrase_measures=phrase_measures,
            articulation=self._suggest_articulation(axes),
            mood=spec.mood,
            ensemble=self._suggest_ensemble(axes),
            instrumentation=self._suggest_instrumentation(axes),
        )

    def _suggest_tonic(self, axes: SemanticAxes, stream: SeedStream) -> str:
        """Pick a final, mildly biased toward flat keys for dark texts."""
        picker = stream.derive("tonic")
        flatness = {"C": 0.0, "D": 0.25, "Eb": -0.75, "E": 0.6,
                    "F": -0.3, "G": 0.4, "A": 0.5, "Bb": -0.6}
        weights = [
            1.0 + 0.8 * axes.valence * flatness[name] + 0.3 * axes.luminosity * flatness[name]
            for name in CANDIDATE_TONICS
        ]
        weights = [max(0.05, w) for w in weights]
        return picker.weighted_choice(CANDIDATE_TONICS, weights)

    def _suggest_meter(self, axes: SemanticAxes, stream: SeedStream) -> str:
        picker = stream.derive("meter")
        weights = {
            "4/4": 2.4 + 0.4 * axes.weight,
            "3/4": 1.0 + 0.9 * max(0.0, axes.valence) + 0.6 * max(0.0, axes.energy),
            "2/2": 0.8 + 0.9 * max(0.0, axes.weight) - 0.4 * axes.energy,
            "3/2": 0.5 + 1.1 * max(0.0, axes.weight) - 0.7 * axes.energy,
            "6/8": 0.6 + 0.9 * max(0.0, axes.energy) + 0.5 * max(0.0, axes.luminosity),
        }
        names = list(self.METER_CANDIDATES)
        return picker.weighted_choice(names, [max(0.05, weights[n]) for n in names])

    def _suggest_articulation(self, axes: SemanticAxes) -> str:
        if axes.heresy > 0.45 and axes.energy > 0.2:
            return "martellato"
        if axes.energy > 0.45:
            return "detached"
        if axes.energy < -0.4 and axes.weight > 0.1:
            return "sostenuto"
        if axes.energy < -0.15:
            return "legato"
        return "ordinario"

    def _suggest_ensemble(self, axes: SemanticAxes) -> str:
        if axes.heresy > 0.5:
            return "crusher"
        if axes.weight > 0.35:
            return "organ"
        if axes.energy > 0.4 and axes.luminosity > 0.1:
            return "harpsichord"
        if axes.valence < -0.25:
            return "viola"
        return "choir"

    def _suggest_instrumentation(self, axes: SemanticAxes) -> Dict[str, str]:
        """Per-voice timbre recommendations for THE VOICE (Tone.js) layer."""
        if axes.heresy > 0.55:
            return {"soprano": "pulse50", "alto": "crusher",
                    "tenor": "crusher", "bass": "crusher"}
        if axes.weight > 0.4:
            return {"soprano": "choir", "alto": "choir",
                    "tenor": "organ", "bass": "organ"}
        if axes.energy > 0.45:
            return {"soprano": "harpsichord", "alto": "harpsichord",
                    "tenor": "viola", "bass": "viola"}
        if axes.valence < -0.3:
            return {"soprano": "viola", "alto": "viola",
                    "tenor": "viola", "bass": "organ"}
        return {"soprano": "choir", "alto": "choir",
                "tenor": "viola", "bass": "organ"}


#: Module-level analyzer; stateless, safe to share.
ANALYZER = SemanticAnalyzer()


def analyze(text: str, *, default_measures: int = 8) -> SemanticAnalysis:
    """Convenience wrapper over the shared :data:`ANALYZER`."""
    return ANALYZER.analyze(text, default_measures=default_measures)


__all__ = [
    "AXIS_NAMES", "SemanticAxes", "LEXICON", "NEGATORS", "INTENSIFIERS",
    "MODE_AFFINITY", "INSTRUMENTS", "ARTICULATIONS", "normalize_text", "tokenize",
    "stem", "lookup", "MatchedTerm", "SemanticSuggestion", "SemanticAnalysis",
    "SemanticAnalyzer", "ANALYZER", "analyze",
]
