"""harmony.py -- The harmonic skeleton.

Before a single note is chosen the engine decides *what harmony sounds when*.  That
skeleton is the global structure the voice-leading solver is measured against, and it is
what stops the generator from being a Markov chain with delusions of counterpoint: local
transition weights choose the next root, but phrase boundaries, cadence formulas and the
final close are imposed from above.

Two things deserve comment.

**Musica ficta.**  Dorian, Mixolydian and Aeolian have a whole tone below the final, so
their degree-V triad is minor and cannot form a leading tone.  Sixteenth- and
seventeenth-century practice raised that third at cadences without writing it in the
signature.  The engine does the same, records the raised pitch class in
``HarmonicPlan.ficta_pcs``, and exempts it from the "chromatic alteration" rule.

**Modes without a usable dominant.**  Phrygian closes with the flat-second triad falling
a semitone in the bass.  Locrian has no perfect fifth above its final at all, and our
answer -- IV -> i(diminished) -- is a **Neo-Arca invention with no historical warrant**:
Locrian was not a practical mode in this repertoire and nothing in the period cadences
onto a diminished final.  It exists so that a mode our own system offers has some way to
stop, and it is reported with a reduced cadence ceiling rather than faked into stability.

**Cadences here are chord pairs, not clausulae.**  Historically a cadence in this
repertoire is a dyadic, contrapuntal event; we select pairs of scale degrees and let the
voicing solver find the voices.  :data:`CADENCE_PROVENANCE` records, per formula, exactly
how much each is entitled to claim, and ``docs/PROVENANCE.md`` section 3 explains the
difference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Tuple

from determinism import SeedStream
from rhythm import MeterSpec, SlotTiming, build_grid
from theory import CadenceFamily, ModeName, mode_spec

# --------------------------------------------------------------------------------------
# Triads
# --------------------------------------------------------------------------------------

ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII")


class Quality(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"


@dataclass(frozen=True)
class Triad:
    """A three-note chord expressed as pitch classes, with its analytic label."""

    root_pc: int
    third_pc: int
    fifth_pc: int
    quality: Quality
    label: str
    #: Diatonic degree 0-6, or ``None`` for a chromatic (Heretical) triad.
    degree: Optional[int] = None
    #: True when the third has been raised by *musica ficta*.
    ficta: bool = False

    @property
    def pcs(self) -> FrozenSet[int]:
        return frozenset({self.root_pc, self.third_pc, self.fifth_pc})

    @property
    def is_diatonic(self) -> bool:
        return self.degree is not None and not self.ficta


def _quality_of(root: int, third: int, fifth: int) -> Quality:
    t = (third - root) % 12
    f = (fifth - root) % 12
    if t == 4 and f == 7:
        return Quality.MAJOR
    if t == 3 and f == 7:
        return Quality.MINOR
    if t == 3 and f == 6:
        return Quality.DIMINISHED
    if t == 4 and f == 8:
        return Quality.AUGMENTED
    return Quality.MAJOR if t == 4 else Quality.MINOR


def _label_for(degree: int, quality: Quality, ficta: bool) -> str:
    numeral = ROMAN[degree]
    if quality in (Quality.MINOR, Quality.DIMINISHED):
        numeral = numeral.lower()
    if quality is Quality.DIMINISHED:
        numeral += "°"
    elif quality is Quality.AUGMENTED:
        numeral += "+"
    return ("#" if ficta else "") + numeral


def diatonic_triad(degree: int, tonic_pc: int, mode: ModeName) -> Triad:
    """The triad built in thirds on *degree* of the mode."""
    spec = mode_spec(mode)
    intervals = spec.intervals
    root = (tonic_pc + intervals[degree]) % 12
    third = (tonic_pc + intervals[(degree + 2) % 7]) % 12
    fifth = (tonic_pc + intervals[(degree + 4) % 7]) % 12
    quality = _quality_of(root, third, fifth)
    return Triad(root, third, fifth, quality, _label_for(degree, quality, False), degree)


def apply_ficta(triad: Triad, tonic_pc: int) -> Triad:
    """Raise a cadential triad's third to form a leading tone to *tonic_pc*."""
    leading = (tonic_pc - 1) % 12
    if triad.third_pc == leading:
        return triad
    if (triad.third_pc + 1) % 12 != leading:
        return triad
    quality = _quality_of(triad.root_pc, leading, triad.fifth_pc)
    degree = triad.degree if triad.degree is not None else 4
    return Triad(
        root_pc=triad.root_pc, third_pc=leading, fifth_pc=triad.fifth_pc,
        quality=quality, label=_label_for(degree, quality, True),
        degree=triad.degree, ficta=True,
    )


def chromatic_triad(root_pc: int, tonic_pc: int, major: bool = True) -> Triad:
    """A triad outside the mode -- Modus Haereticus only."""
    third = (root_pc + (4 if major else 3)) % 12
    fifth = (root_pc + 7) % 12
    quality = Quality.MAJOR if major else Quality.MINOR
    distance = (root_pc - tonic_pc) % 12
    return Triad(root_pc, third, fifth, quality, f"†{distance}", None, False)


# --------------------------------------------------------------------------------------
# Cadences
# --------------------------------------------------------------------------------------


class CadenceKind(str, Enum):
    AUTHENTIC = "authentic"
    PHRYGIAN = "phrygian"
    PLAGAL = "plagal"
    PLAGAL_DIMINISHED = "plagal_diminished"
    HALF = "half"
    DECEPTIVE = "deceptive"
    TRITONE_FALL = "tritone_fall"      # Heretical
    SUSPENDED = "suspended"            # Heretical: closes on an alien triad


@dataclass(frozen=True)
class CadenceProvenance:
    """How much historical authority a cadence formula actually carries.

    Recorded in code rather than only in prose, because the code's own vocabulary is what
    overstates things: naming a chord pair "phrygian" invites the reading that we have
    implemented the historical cadence, and we have not.

    In this repertoire a cadence is a **clausula** -- a dyadic, intervallic event, not a
    chordal one.  Two voices approach an octave or unison by step: the *cantizans* rises
    by semitone, the *tenorizans* falls by step, and the *bassizans*, a third below the
    tenorizans, leaps down a fourth or up a fifth.  The identity of the cadence lives in
    that voice-leading.

    We select cadences as **pairs of scale degrees** and let the voicing solver find the
    voices, constrained only by the leading-tone rule.  That reproduces the harmonic
    gesture and, at the Phrygian close, the characteristic descending semitone in the
    bass -- but it does not implement the clausulae, and nothing here should claim it
    does.  See ``docs/PROVENANCE.md`` section 3.
    """

    #: H1 = period practice, implemented approximately.  N1 = our own construction.
    classification: str
    note: str


#: (penultimate degree, final degree) for the diatonic cadence kinds.  ``None`` in the
#: final slot means "the phrase simply stops here", used by the half cadence.
_CADENCE_DEGREES: Dict[CadenceKind, Tuple[Optional[int], Optional[int]]] = {
    CadenceKind.AUTHENTIC: (4, 0),
    CadenceKind.PHRYGIAN: (1, 0),
    CadenceKind.PLAGAL: (3, 0),
    CadenceKind.PLAGAL_DIMINISHED: (3, 0),
    CadenceKind.HALF: (0, 4),
    CadenceKind.DECEPTIVE: (4, 5),
}


#: What each cadence formula is actually entitled to claim.
CADENCE_PROVENANCE: Dict[CadenceKind, CadenceProvenance] = {
    CadenceKind.AUTHENTIC: CadenceProvenance(
        "H1",
        "Degree V to the final, with musica ficta raising the third where the mode's "
        "seventh is flat. The practice is documented for the period; the chord-pair "
        "implementation is ours, and the cantizans is enforced only as a leading-tone "
        "resolution rule.",
    ),
    CadenceKind.PHRYGIAN: CadenceProvenance(
        "N1",
        "The flat-second triad falling to the final. The descending semitone in the bass "
        "is the characteristic gesture of the historical mi cadence and our output does "
        "produce it, but the cadence is realised as a chord pair, not as the contrapuntal "
        "clausulae that actually define it.",
    ),
    CadenceKind.PLAGAL: CadenceProvenance(
        "N1",
        "Degree IV to the final. Scholarship notes that many apparent plagal cadences in "
        "this repertoire lack the melodic clausulae defining the other types, so treating "
        "IV-I as a cadence formula is a modern reading.",
    ),
    CadenceKind.PLAGAL_DIMINISHED: CadenceProvenance(
        "N1",
        "Locrian IV to a diminished final. No historical warrant whatsoever: Locrian was "
        "not a practical mode, and nothing in the period cadences onto a diminished "
        "final. Invented so that a mode our own system offers has some way to stop.",
    ),
    CadenceKind.HALF: CadenceProvenance(
        "N1",
        "Stopping the phrase on degree V. The half cadence is a functional-tonal "
        "concept: it depends on hearing the dominant as an unresolved tension pointing "
        "back to a tonic, which is not how a modal repertoire organised around clausulae "
        "works. Used here as a phrase-level breathing mark.",
    ),
    CadenceKind.DECEPTIVE: CadenceProvenance(
        "N1",
        "Degree V moving to vi instead of the final. Like the half cadence this is a "
        "functional-tonal device -- it means something only if the listener already "
        "expects V to resolve to I. Used here to keep interior phrases from all closing "
        "the same way.",
    ),
    CadenceKind.TRITONE_FALL: CadenceProvenance(
        "HAERETIC", "A Modus Haereticus close. Invented, and declared as such.",
    ),
    CadenceKind.SUSPENDED: CadenceProvenance(
        "HAERETIC",
        "A Modus Haereticus close that refuses the final altogether. Invented.",
    ),
}


def cadence_provenance(cadence: CadenceKind) -> CadenceProvenance:
    return CADENCE_PROVENANCE[cadence]


def full_close_for(mode: ModeName) -> CadenceKind:
    family = mode_spec(mode).cadence_family
    if family is CadenceFamily.PHRYGIAN:
        return CadenceKind.PHRYGIAN
    if family is CadenceFamily.PLAGAL_DIM:
        return CadenceKind.PLAGAL_DIMINISHED
    return CadenceKind.AUTHENTIC


# --------------------------------------------------------------------------------------
# Root transition weights
# --------------------------------------------------------------------------------------

#: Modal-functional transition weights over scale degrees.  These are a *local*
#: preference model only; phrase and cadence structure is imposed separately.
ORTHODOX_TRANSITIONS: Dict[int, Dict[int, float]] = {
    0: {3: 3.0, 4: 3.0, 5: 2.0, 1: 2.0, 2: 1.2, 6: 0.6},
    1: {4: 4.0, 6: 1.2, 3: 1.0, 0: 0.6},
    2: {5: 3.0, 3: 2.0, 0: 1.2, 1: 0.8},
    3: {4: 4.0, 0: 2.0, 1: 2.0, 6: 1.0, 5: 0.8},
    4: {0: 5.0, 5: 2.0, 3: 1.0, 2: 0.6},
    5: {1: 3.0, 3: 3.0, 4: 2.0, 0: 1.0, 2: 0.8},
    6: {0: 4.0, 2: 1.2, 4: 0.8},
}

#: Heretical roots prefer tritone and chromatic-mediant relations.  Expressed as
#: weights over *semitone distance* from the current root, so the same table works for
#: chromatic triads that have no scale degree.
HERETICAL_ROOT_MOVES: Dict[int, float] = {
    6: 4.0,   # tritone
    1: 3.0,   # semitone
    11: 3.0,
    8: 2.5,   # chromatic mediants
    4: 2.5,
    3: 1.6,
    9: 1.6,
    2: 1.2,
    10: 1.2,
    5: 1.0,
    7: 1.0,
    0: 0.2,
}


# --------------------------------------------------------------------------------------
# The plan
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Phrase:
    index: int
    first_slot: int
    last_slot: int
    first_measure: int
    last_measure: int
    cadence: CadenceKind

    @property
    def slot_count(self) -> int:
        return self.last_slot - self.first_slot + 1


@dataclass(frozen=True)
class HarmonicSlot:
    """One sonority's worth of harmonic instruction."""

    timing: SlotTiming
    triad: Triad
    phrase_index: int
    position_in_phrase: float          # 0..1
    is_cadential: bool                 # the penultimate chord of a cadence formula
    is_phrase_final: bool
    is_final: bool
    #: Pitch classes the bass may take, best first.
    bass_pcs: Tuple[int, ...]
    leading_tone_pc: Optional[int]

    @property
    def index(self) -> int:
        return self.timing.index

    @property
    def offset(self) -> float:
        return self.timing.offset

    @property
    def duration(self) -> float:
        return self.timing.duration


@dataclass(frozen=True)
class HarmonicPlan:
    slots: Tuple[HarmonicSlot, ...]
    phrases: Tuple[Phrase, ...]
    tonic_pc: int
    mode: ModeName
    meter: MeterSpec
    measures: int
    ficta_pcs: FrozenSet[int]
    leading_tone_pc: Optional[int]

    @property
    def total_ql(self) -> float:
        return self.measures * self.meter.measure_ql

    def ficta_by_slot(self) -> Dict[int, FrozenSet[int]]:
        """Which slots license which raised pitch classes.

        *Musica ficta* is a cadential inflection, not a change of scale.  The raised
        seventh belongs to the cadence that needs a leading tone; the same pitch class
        sounding elsewhere in the piece is an ordinary chromatic alteration and must
        still be reported as one.  ``ficta_pcs`` (the union) remains available for
        reporting, but the engine and the rules work from this per-slot licence.
        """
        return {
            slot.index: frozenset({slot.triad.third_pc})
            for slot in self.slots
            if slot.triad.ficta
        }

    def progression(self) -> List[str]:
        return [slot.triad.label for slot in self.slots]


def _phrase_bounds(measures: int, phrase_measures: int) -> List[Tuple[int, int]]:
    """Split *measures* bars into phrases of ``phrase_measures``, absorbing any remainder."""
    size = max(1, min(phrase_measures, measures))
    bounds: List[Tuple[int, int]] = []
    start = 0
    while start < measures:
        end = min(measures - 1, start + size - 1)
        if measures - (end + 1) < size and end != measures - 1:
            end = measures - 1
        bounds.append((start, end))
        start = end + 1
    return bounds


def _choose_interior_cadence(
    stream: SeedStream, cadence_strength: float, heretical: bool, mode: ModeName
) -> CadenceKind:
    if heretical:
        options = [CadenceKind.TRITONE_FALL, CadenceKind.SUSPENDED,
                   CadenceKind.HALF, CadenceKind.DECEPTIVE]
        weights = [3.0, 2.5, 1.2, 1.5]
        return stream.weighted_choice(options, weights)
    options = [CadenceKind.HALF, CadenceKind.AUTHENTIC, CadenceKind.DECEPTIVE]
    weights = [
        1.6 + 1.4 * (1.0 - cadence_strength),
        1.0 + 2.0 * cadence_strength,
        0.9 + 0.8 * (1.0 - cadence_strength),
    ]
    if diatonic_triad(3, 0, mode).quality is not Quality.DIMINISHED:
        # Lydian's subdominant triad is diminished and cannot support a plagal close.
        options.append(CadenceKind.PLAGAL)
        weights.append(0.8 + 0.6 * cadence_strength)
    return stream.weighted_choice(options, weights)


def _bass_options(
    triad: Triad,
    *,
    allow_inversion: bool,
    force_root: bool,
    force_root_final: bool,
    heretical: bool,
) -> Tuple[int, ...]:
    """Which chord members the bass may take, best first."""
    if triad.quality is Quality.DIMINISHED and not heretical and not force_root_final:
        # A diminished triad in root position leaves its diminished fifth over the bass,
        # and its root lies a tritone from the final -- an unsingable bass step into the
        # cadence.  First inversion is the only orthodox placement, cadence or not.
        return (triad.third_pc,)
    if force_root:
        return (triad.root_pc,)
    if heretical:
        return (triad.root_pc, triad.third_pc, triad.fifth_pc)
    if allow_inversion:
        return (triad.root_pc, triad.third_pc)
    return (triad.root_pc,)


def build_plan(
    *,
    tonic_pc: int,
    mode: ModeName,
    meter: MeterSpec,
    measures: int,
    density: float,
    cadence_strength: float,
    phrase_measures: int,
    heretical: bool,
    stream: SeedStream,
) -> HarmonicPlan:
    """Compose the harmonic skeleton: phrases, cadences, and a triad for every slot."""
    spec = mode_spec(mode)
    bounds = _phrase_bounds(measures, phrase_measures)
    cadence_measures = [end for _, end in bounds]
    timings = build_grid(
        meter, measures, density, stream.derive("grid"),
        cadence_measures=cadence_measures,
    )

    # Assign phrase membership by measure.
    measure_to_phrase = {}
    for pi, (start, end) in enumerate(bounds):
        for m in range(start, end + 1):
            measure_to_phrase[m] = pi

    phrase_slots: Dict[int, List[SlotTiming]] = {pi: [] for pi in range(len(bounds))}
    for timing in timings:
        phrase_slots[measure_to_phrase[timing.measure]].append(timing)

    full_close = full_close_for(mode)
    cadences: List[CadenceKind] = []
    for pi in range(len(bounds)):
        if pi == len(bounds) - 1:
            cadences.append(
                CadenceKind.SUSPENDED if heretical and cadence_strength < 0.35
                else full_close
            )
        else:
            cadences.append(_choose_interior_cadence(
                stream.derive("cadence", pi), cadence_strength, heretical, mode
            ))

    leading_tone_pc = (tonic_pc - 1) % 12
    ficta: set[int] = set()
    slots: List[HarmonicSlot] = []
    phrases: List[Phrase] = []
    degree_cursor = 0

    for pi, (first_measure, last_measure) in enumerate(bounds):
        timings_here = phrase_slots[pi]
        if not timings_here:  # pragma: no cover - build_grid always yields >=1 per bar
            continue
        cadence = cadences[pi]
        count = len(timings_here)
        is_last_phrase = pi == len(bounds) - 1
        degrees = _phrase_degrees(
            count=count,
            cadence=cadence,
            mode=mode,
            tonic_pc=tonic_pc,
            start_degree=degree_cursor,
            heretical=heretical,
            stream=stream.derive("phrase", pi),
        )
        for position, (timing, entry) in enumerate(zip(timings_here, degrees)):
            degree, chromatic_root = entry
            is_phrase_final = position == count - 1
            is_cadential = position == count - 2
            is_final = is_last_phrase and is_phrase_final
            if chromatic_root is not None:
                triad = chromatic_triad(
                    chromatic_root, tonic_pc,
                    major=stream.derive("alien", pi, position).chance(0.7),
                )
            else:
                triad = diatonic_triad(degree, tonic_pc, mode)
                needs_lt = (
                    is_cadential
                    and cadence in (CadenceKind.AUTHENTIC, CadenceKind.DECEPTIVE)
                    and spec.needs_ficta
                )
                if needs_lt:
                    raised = apply_ficta(triad, tonic_pc)
                    if raised.ficta:
                        triad = raised
                        ficta.add(triad.third_pc)
            slot_lt = leading_tone_pc if leading_tone_pc in triad.pcs else None
            slots.append(HarmonicSlot(
                timing=timing,
                triad=triad,
                phrase_index=pi,
                position_in_phrase=position / max(1, count - 1),
                is_cadential=is_cadential,
                is_phrase_final=is_phrase_final,
                is_final=is_final,
                bass_pcs=_bass_options(
                    triad,
                    allow_inversion=not (is_cadential or is_phrase_final),
                    force_root=is_final or is_cadential or (pi == 0 and position == 0),
                    force_root_final=is_final,
                    heretical=heretical,
                ),
                leading_tone_pc=slot_lt,
            ))
        phrases.append(Phrase(
            index=pi,
            first_slot=timings_here[0].index,
            last_slot=timings_here[-1].index,
            first_measure=first_measure,
            last_measure=last_measure,
            cadence=cadence,
        ))
        last_degree = degrees[-1][0]
        degree_cursor = last_degree if last_degree is not None else 0

    return HarmonicPlan(
        slots=tuple(slots),
        phrases=tuple(phrases),
        tonic_pc=tonic_pc,
        mode=mode,
        meter=meter,
        measures=measures,
        ficta_pcs=frozenset(ficta),
        leading_tone_pc=leading_tone_pc,
    )


def _phrase_degrees(
    *,
    count: int,
    cadence: CadenceKind,
    mode: ModeName,
    tonic_pc: int,
    start_degree: int,
    heretical: bool,
    stream: SeedStream,
) -> List[Tuple[Optional[int], Optional[int]]]:
    """Choose a root for every slot of one phrase.

    Returns ``(degree, chromatic_root_pc)`` pairs; exactly one member of each pair is
    non-``None``.  The last one or two entries are dictated by the cadence formula; the
    rest are drawn from the transition model.
    """
    spec = mode_spec(mode)
    tail = _cadence_tail(cadence, mode, tonic_pc)
    body_len = max(0, count - len(tail))
    body: List[Tuple[Optional[int], Optional[int]]] = []

    current = start_degree
    for step in range(body_len):
        picker = stream.derive("root", step)
        if step == 0 and start_degree == 0:
            body.append((0, None))
            current = 0
            continue
        if heretical and picker.chance(0.38):
            alien = picker.weighted_choice(
                (1, 6, 8, 3, 10), (3.0, 4.0, 2.0, 1.5, 1.5)
            )
            body.append((None, (tonic_pc + spec.intervals[current] + alien) % 12))
            continue
        weights = ORTHODOX_TRANSITIONS[current]
        degrees = tuple(weights.keys())
        if heretical:
            values = tuple(
                HERETICAL_ROOT_MOVES.get(
                    (spec.intervals[d] - spec.intervals[current]) % 12, 1.0
                )
                for d in degrees
            )
        else:
            values = tuple(weights.values())
        current = picker.weighted_choice(degrees, values)
        body.append((current, None))

    if body_len == 0:
        body = []
    return (body + tail)[:count] if count >= len(tail) else tail[-count:]


def _cadence_tail(
    cadence: CadenceKind, mode: ModeName, tonic_pc: int
) -> List[Tuple[Optional[int], Optional[int]]]:
    """The final one or two roots that realise *cadence*."""
    spec = mode_spec(mode)
    if cadence is CadenceKind.HALF:
        return [(0, None), (spec.cadential_degree, None)]
    if cadence is CadenceKind.DECEPTIVE:
        return [(spec.cadential_degree, None), (5, None)]
    if cadence is CadenceKind.PHRYGIAN:
        return [(1, None), (0, None)]
    if cadence in (CadenceKind.PLAGAL, CadenceKind.PLAGAL_DIMINISHED):
        return [(3, None), (0, None)]
    if cadence is CadenceKind.TRITONE_FALL:
        return [(None, (tonic_pc + 6) % 12), (0, None)]
    if cadence is CadenceKind.SUSPENDED:
        return [(spec.cadential_degree, None), (None, (tonic_pc + 1) % 12)]
    return [(spec.cadential_degree, None), (0, None)]


__all__ = [
    "Quality", "Triad", "diatonic_triad", "apply_ficta", "chromatic_triad",
    "CadenceKind", "CadenceProvenance", "CADENCE_PROVENANCE",
    "cadence_provenance", "full_close_for", "ORTHODOX_TRANSITIONS", "HERETICAL_ROOT_MOVES",
    "Phrase", "HarmonicSlot", "HarmonicPlan", "build_plan", "ROMAN",
]
