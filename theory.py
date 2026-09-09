"""theory.py -- Pitch, mode, and vocal-range primitives for the Neo-Arca Musarithmica.

This module is deliberately free of randomness, I/O and framework code.  It is the
shared vocabulary that every other layer of THE GHOST speaks:

* :class:`Voice`            -- the four SATB parts, ordered low to high.
* :class:`VoiceRange`       -- absolute limits plus a comfortable tessitura.
* :class:`ModeSpec`         -- the seven diatonic modes as *structure*, with their
                               Kircherian *mood* label kept as separate metadata.
* pitch-class / spelling helpers used by both the generator and the MIDI exporter.

Nothing here knows about counterpoint; see ``constraints.py`` for that.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Tuple

# --------------------------------------------------------------------------------------
# Voices
# --------------------------------------------------------------------------------------


class Voice(str, Enum):
    """The four independent contrapuntal lines."""

    BASS = "bass"
    TENOR = "tenor"
    ALTO = "alto"
    SOPRANO = "soprano"


#: Low to high.  Index in this tuple is the canonical slot in a :class:`Sonority`.
VOICE_ORDER: Tuple[Voice, ...] = (Voice.BASS, Voice.TENOR, Voice.ALTO, Voice.SOPRANO)

#: Vertically adjacent pairs, (lower, upper).
ADJACENT_PAIRS: Tuple[Tuple[Voice, Voice], ...] = (
    (Voice.BASS, Voice.TENOR),
    (Voice.TENOR, Voice.ALTO),
    (Voice.ALTO, Voice.SOPRANO),
)

#: Every unordered pair, expressed as (lower, upper) by VOICE_ORDER position.
ALL_PAIRS: Tuple[Tuple[Voice, Voice], ...] = tuple(combinations(VOICE_ORDER, 2))

#: The pairs whose spacing is governed by the "upper voices within an octave" rule.
UPPER_ADJACENT_PAIRS: Tuple[Tuple[Voice, Voice], ...] = (
    (Voice.TENOR, Voice.ALTO),
    (Voice.ALTO, Voice.SOPRANO),
)

OUTER_PAIR: Tuple[Voice, Voice] = (Voice.BASS, Voice.SOPRANO)


def voice_index(voice: Voice) -> int:
    """Position of *voice* in :data:`VOICE_ORDER` (0 = bass ... 3 = soprano)."""
    return VOICE_ORDER.index(voice)


# --------------------------------------------------------------------------------------
# Ranges
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class VoiceRange:
    """Absolute range plus the comfortable interior band.

    ``low``/``high`` are hard limits (a pitch outside them is a hard rule violation).
    ``tess_low``/``tess_high`` describe the band the generator is *scored* toward, so
    voices sit in a comfortable tessitura and only make controlled excursions to the
    extremes.
    """

    low: int
    high: int
    tess_low: int
    tess_high: int

    @property
    def center(self) -> float:
        return (self.tess_low + self.tess_high) / 2.0

    def contains(self, midi: int) -> bool:
        return self.low <= midi <= self.high

    def excursion(self, midi: int) -> int:
        """Semitones by which *midi* falls outside the comfortable tessitura."""
        if midi < self.tess_low:
            return self.tess_low - midi
        if midi > self.tess_high:
            return midi - self.tess_high
        return 0


#: Defensible working ranges (see spec section XV).  Values are MIDI note numbers.
#:   bass     E2 (40) - E4 (64),  tessitura G2 (43) - C4 (60)
#:   tenor    C3 (48) - G4 (67),  tessitura F3 (53) - D4 (62)
#:   alto     G3 (55) - D5 (74),  tessitura B3 (59) - A4 (69)
#:   soprano  C4 (60) - G5 (79),  tessitura E4 (64) - E5 (76)
VOICE_RANGES: Dict[Voice, VoiceRange] = {
    Voice.BASS: VoiceRange(low=40, high=64, tess_low=43, tess_high=60),
    Voice.TENOR: VoiceRange(low=48, high=67, tess_low=53, tess_high=62),
    Voice.ALTO: VoiceRange(low=55, high=74, tess_low=59, tess_high=69),
    Voice.SOPRANO: VoiceRange(low=60, high=79, tess_low=64, tess_high=76),
}


def shifted_range(voice: Voice, semitones: int) -> VoiceRange:
    """Return the range for *voice* with its *tessitura* shifted by ``semitones``.

    The absolute limits are never widened -- a global register request may move where
    the engine prefers to sit, but it can never push a voice out of its real range.
    """
    base = VOICE_RANGES[voice]
    lo = max(base.low, min(base.high - 4, base.tess_low + semitones))
    hi = min(base.high, max(lo + 4, base.tess_high + semitones))
    return VoiceRange(low=base.low, high=base.high, tess_low=lo, tess_high=hi)


# --------------------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------------------


class ModeName(str, Enum):
    IONIAN = "ionian"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    AEOLIAN = "aeolian"
    LOCRIAN = "locrian"


class CadenceFamily(str, Enum):
    """How a mode forms its strongest full close.

    ``AUTHENTIC``   -- degree V (major, by *musica ficta* where the mode's 7th is flat)
                       falling to the final.
    ``PHRYGIAN``    -- the flat-second triad descending by semitone in the bass.
    ``PLAGAL_DIM``  -- Locrian: no perfect fifth above the final, so the strongest
                       available close is IV -> i(dim).  Deliberately unstable.
    """

    AUTHENTIC = "authentic"
    PHRYGIAN = "phrygian"
    PLAGAL_DIM = "plagal_diminished"


@dataclass(frozen=True)
class ModeSpec:
    """A diatonic mode.

    ``intervals`` is the *structure*.  ``mood`` is semantic metadata inherited from the
    prototype's vocabulary and is never used to make musical decisions -- only to label
    them for the interface.
    """

    name: ModeName
    intervals: Tuple[int, ...]
    mood: str
    #: Sharps (positive) / flats (negative) of the mode built on C, i.e. the key
    #: signature offset relative to the Ionian of the same final.
    signature_offset: int
    cadence_family: CadenceFamily
    #: Scale degree (0-indexed) carrying the penultimate cadential triad.
    cadential_degree: int
    #: True when the mode's natural 7th degree lies a whole tone below the final and
    #: must be raised by *musica ficta* to obtain a leading tone at cadences.
    needs_ficta: bool
    #: Baseline strength of this mode's full close, 0..1.  Locrian cannot close firmly.
    cadence_ceiling: float


MODES: Dict[ModeName, ModeSpec] = {
    ModeName.IONIAN: ModeSpec(
        ModeName.IONIAN, (0, 2, 4, 5, 7, 9, 11), "Radiant", 0,
        CadenceFamily.AUTHENTIC, 4, False, 1.0,
    ),
    ModeName.DORIAN: ModeSpec(
        ModeName.DORIAN, (0, 2, 3, 5, 7, 9, 10), "Solemn", -2,
        CadenceFamily.AUTHENTIC, 4, True, 0.95,
    ),
    ModeName.PHRYGIAN: ModeSpec(
        ModeName.PHRYGIAN, (0, 1, 3, 5, 7, 8, 10), "Lamenting", -4,
        CadenceFamily.PHRYGIAN, 1, False, 0.8,
    ),
    ModeName.LYDIAN: ModeSpec(
        ModeName.LYDIAN, (0, 2, 4, 6, 7, 9, 11), "Luminous", 1,
        CadenceFamily.AUTHENTIC, 4, False, 0.9,
    ),
    ModeName.MIXOLYDIAN: ModeSpec(
        ModeName.MIXOLYDIAN, (0, 2, 4, 5, 7, 9, 10), "Ceremonial", -1,
        CadenceFamily.AUTHENTIC, 4, True, 0.92,
    ),
    ModeName.AEOLIAN: ModeSpec(
        ModeName.AEOLIAN, (0, 2, 3, 5, 7, 8, 10), "Elegiac", -3,
        CadenceFamily.AUTHENTIC, 4, True, 0.95,
    ),
    ModeName.LOCRIAN: ModeSpec(
        ModeName.LOCRIAN, (0, 1, 3, 5, 6, 8, 10), "Forbidden", -5,
        CadenceFamily.PLAGAL_DIM, 3, False, 0.45,
    ),
}


def mode_spec(mode: "ModeName | str") -> ModeSpec:
    """Look up a :class:`ModeSpec` from an enum member or its lowercase name."""
    if isinstance(mode, ModeSpec):  # pragma: no cover - defensive
        return mode
    key = ModeName(mode) if not isinstance(mode, ModeName) else mode
    return MODES[key]


# --------------------------------------------------------------------------------------
# Pitch classes, names, spelling
# --------------------------------------------------------------------------------------

LETTER_ORDER = "CDEFGAB"
LETTER_PC: Dict[str, int] = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ACCIDENTAL_ALTER: Dict[str, int] = {
    "": 0, "#": 1, "##": 2, "x": 2, "b": -1, "bb": -2, "-": -1, "--": -2,
    "natural": 0,
}
_ALTER_SUFFIX: Dict[int, str] = {-2: "bb", -1: "b", 0: "", 1: "#", 2: "##"}

#: Circle-of-fifths position of each natural letter.  Each sharp adds seven
#: positions, each flat subtracts seven, so the signature follows from how the
#: final is *spelled* rather than from which key it sounds.
_LETTER_FIFTHS: Dict[str, int] = {
    "F": -1, "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5,
}

#: Tonics the engine is willing to choose on its own -- readable key signatures only.
CANDIDATE_TONICS: Tuple[str, ...] = ("C", "D", "Eb", "E", "F", "G", "A", "Bb")


class TheoryError(ValueError):
    """Raised for malformed musical input (bad note name, unknown mode, ...)."""


def parse_note_name(name: str) -> int:
    """Return the pitch class 0-11 of a note name such as ``"C"``, ``"Bb"``, ``"F#"``."""
    if not name:
        raise TheoryError("empty note name")
    text = name.strip()
    letter = text[0].upper()
    if letter not in LETTER_PC:
        raise TheoryError(f"unknown note letter: {name!r}")
    accidental = text[1:].replace("♯", "#").replace("♭", "b")
    if accidental not in _ACCIDENTAL_ALTER:
        raise TheoryError(f"unknown accidental in note name: {name!r}")
    return (LETTER_PC[letter] + _ACCIDENTAL_ALTER[accidental]) % 12


def normalize_note_name(name: str) -> str:
    """Canonicalise a note name: ``"bb"`` -> ``"Bb"``, ``"f♯"`` -> ``"F#"``."""
    text = name.strip()
    letter = text[0].upper()
    accidental = text[1:].replace("♯", "#").replace("♭", "b")
    if letter not in LETTER_PC or accidental not in _ACCIDENTAL_ALTER:
        raise TheoryError(f"unparseable note name: {name!r}")
    if accidental == "-":
        accidental = "b"
    elif accidental == "--":
        accidental = "bb"
    elif accidental == "x":
        accidental = "##"
    return letter + accidental


@dataclass(frozen=True)
class SpelledPitch:
    """A pitch with an orthographically correct letter, alteration and octave."""

    step: str          # "C".."B"
    alter: int         # -2..2
    octave: int
    midi: int

    @property
    def name(self) -> str:
        return f"{self.step}{_ALTER_SUFFIX[self.alter]}{self.octave}"


class Speller:
    """Spells MIDI numbers as letters/accidentals appropriate to a mode on a final.

    Diatonic pitches take their letter from the mode's own scale, so D Dorian yields
    ``C``, not ``B#``, and Eb Aeolian yields ``Db``, not ``C#``.  Chromatic pitches --
    which only ever appear in Modus Haereticus or as *musica ficta* -- are spelled as an
    alteration of the nearest diatonic letter, following the key signature's sign.
    """

    def __init__(self, tonic: str, mode: ModeName) -> None:
        self.tonic = normalize_note_name(tonic)
        self.mode = mode_spec(mode)
        self.tonic_pc = parse_note_name(self.tonic)
        self._by_pc: Dict[int, Tuple[str, int]] = {}
        tonic_letter_index = LETTER_ORDER.index(self.tonic[0].upper())
        for degree, semitones in enumerate(self.mode.intervals):
            letter = LETTER_ORDER[(tonic_letter_index + degree) % 7]
            target_pc = (self.tonic_pc + semitones) % 12
            alter = ((target_pc - LETTER_PC[letter] + 6) % 12) - 6
            if -2 <= alter <= 2:
                self._by_pc[target_pc] = (letter, alter)
        self._prefer_sharps = self.signature_sharps() >= 0

    def signature_sharps(self) -> int:
        """Signed key-signature count: positive = sharps, negative = flats.

        Derived from the final's **spelling**, not its pitch class.  Keying this on the
        pitch class collapses every enharmonic pair -- C# with Db, F# with Gb, G# with
        Ab, D# with Eb, A# with Bb -- and worse, it picked one arbitrary member of each
        pair, so G# Ionian was reported as four flats when it is eight sharps.

        The value is the true circle-of-fifths position and may legitimately exceed the
        seven accidentals a conventional signature can write; see
        :meth:`notatable_signature` for the value notation and MIDI can carry.
        """
        letter = self.tonic[0].upper()
        alter = _ACCIDENTAL_ALTER[self.tonic[1:]]
        return _LETTER_FIFTHS[letter] + 7 * alter + self.mode.signature_offset

    def notatable_signature(self) -> int:
        """The signature wrapped into the +/-7 a staff and a MIDI file can express.

        Twelve steps around the circle of fifths is an enharmonic respelling, so wrapping
        by twelve keeps the sounding pitches while giving up the theoretically exact
        spelling.  Some mode-and-final combinations genuinely need more than seven
        accidentals -- Db Aeolian wants eight flats -- and no staff can write those.
        """
        total = self.signature_sharps()
        while total > 7:
            total -= 12
        while total < -7:
            total += 12
        return total

    def signature_is_notatable(self) -> bool:
        return abs(self.signature_sharps()) <= 7

    def spell(self, midi: int) -> SpelledPitch:
        pc = midi % 12
        entry = self._by_pc.get(pc)
        if entry is None:
            entry = self._spell_chromatic(pc)
        letter, alter = entry
        octave = (midi - alter - LETTER_PC[letter]) // 12 - 1
        return SpelledPitch(step=letter, alter=alter, octave=octave, midi=midi)

    def _spell_chromatic(self, pc: int) -> Tuple[str, int]:
        """Spell a pitch outside the mode as an inflection of a diatonic letter.

        Both neighbouring diatonic letters are considered; the one needing the smaller
        accidental wins, so heavily flattened modes yield ``C`` rather than ``Dbb``.
        Ties are broken in the direction of the key signature.
        """
        preferred = 1 if self._prefer_sharps else -1
        best: Optional[Tuple[Tuple[int, int], Tuple[str, int]]] = None
        for delta in (1, -1):
            # Spell as the diatonic neighbour inflected by *delta* semitones.
            neighbour = (pc - delta) % 12
            entry = self._by_pc.get(neighbour)
            if entry is None:
                continue
            letter, alter = entry
            alter += delta
            if not -2 <= alter <= 2:
                continue
            rank = (abs(alter), 0 if delta == preferred else 1)
            if best is None or rank < best[0]:
                best = (rank, (letter, alter))
        if best is not None:
            return best[1]
        # Last resort: plain spelling from the natural letters.
        for letter, natural in LETTER_PC.items():
            for alter in (0, 1, -1, 2, -2):
                if (natural + alter) % 12 == pc:
                    return letter, alter
        raise TheoryError(f"cannot spell pitch class {pc}")  # pragma: no cover

    def name(self, midi: int) -> str:
        return self.spell(midi).name


# --------------------------------------------------------------------------------------
# Scales and intervals
# --------------------------------------------------------------------------------------


def scale_pcs(tonic_pc: int, mode: ModeName) -> Tuple[int, ...]:
    """Pitch classes of the mode on *tonic_pc*, in ascending scale order."""
    spec = mode_spec(mode)
    return tuple((tonic_pc + i) % 12 for i in spec.intervals)


def pitches_in_range(pcs: Iterable[int], low: int, high: int) -> List[int]:
    """Every MIDI pitch in ``[low, high]`` whose pitch class is in *pcs*, ascending."""
    wanted = {p % 12 for p in pcs}
    return [m for m in range(low, high + 1) if m % 12 in wanted]


def degree_of_pc(pc: int, tonic_pc: int, mode: ModeName) -> Optional[int]:
    """Scale degree (0-indexed) of *pc*, or ``None`` if it is chromatic."""
    spec = mode_spec(mode)
    target = (pc - tonic_pc) % 12
    for degree, semitones in enumerate(spec.intervals):
        if semitones == target:
            return degree
    return None


def harmonic_interval(lower: int, upper: int) -> int:
    """Interval class 0-11 of the vertical interval, reduced to within an octave."""
    return (upper - lower) % 12


PERFECT_CONSONANCES = frozenset({0, 7})           # unison/octave, perfect fifth
IMPERFECT_CONSONANCES = frozenset({3, 4, 8, 9})   # thirds and sixths
TRITONE = 6


def is_consonant(lower: int, upper: int, *, against_bass: bool) -> bool:
    """Consonance test for a vertical interval.

    The perfect fourth is treated as a consonance between upper voices and as a
    dissonance against the bass -- the standard renaissance/species distinction, and the
    one Kircher's own tables assume.
    """
    iv = harmonic_interval(lower, upper)
    if iv in PERFECT_CONSONANCES or iv in IMPERFECT_CONSONANCES:
        return True
    if iv == 5:  # perfect fourth
        return not against_bass
    return False


#: Melodic intervals that a well-behaved line does not leap: sevenths, the tritone and
#: anything wider than an octave.  (Ascending minor sixths and octaves are permitted.)
FORBIDDEN_MELODIC_INTERVALS = frozenset({6, 10, 11})


def melodic_interval_ok(semitones: int) -> bool:
    """True when a melodic leap of *semitones* is admissible in the Orthodox grammar."""
    size = abs(semitones)
    if size > 12:
        return False
    if size == 12:
        return True
    return size not in FORBIDDEN_MELODIC_INTERVALS


def motion_type(prev_lower: int, cur_lower: int, prev_upper: int, cur_upper: int) -> str:
    """Classify the motion of a voice pair as contrary / oblique / similar / static."""
    dl = cur_lower - prev_lower
    du = cur_upper - prev_upper
    if dl == 0 and du == 0:
        return "static"
    if dl == 0 or du == 0:
        return "oblique"
    if (dl > 0) == (du > 0):
        return "similar"
    return "contrary"


__all__ = [
    "Voice", "VOICE_ORDER", "ADJACENT_PAIRS", "ALL_PAIRS", "UPPER_ADJACENT_PAIRS",
    "OUTER_PAIR", "voice_index", "VoiceRange", "VOICE_RANGES", "shifted_range",
    "ModeName", "ModeSpec", "MODES", "mode_spec", "CadenceFamily",
    "LETTER_ORDER", "LETTER_PC", "CANDIDATE_TONICS", "TheoryError",
    "parse_note_name", "normalize_note_name", "SpelledPitch", "Speller",
    "scale_pcs", "pitches_in_range", "degree_of_pc", "harmonic_interval",
    "PERFECT_CONSONANCES", "IMPERFECT_CONSONANCES", "TRITONE", "is_consonant",
    "FORBIDDEN_MELODIC_INTERVALS", "melodic_interval_ok", "motion_type",
]
