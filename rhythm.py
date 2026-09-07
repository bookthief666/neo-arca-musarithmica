"""rhythm.py -- Meter, harmonic rhythm and the appetite for diminution.

Two jobs:

1. Describe meters (:class:`MeterSpec`) precisely enough that the rest of the engine can
   reason about metrical weight -- which moments are strong, and therefore where
   suspensions may sound and where dissonance may not.
2. Lay out the *harmonic rhythm*: the sequence of :class:`SlotTiming` spans over which a
   single sonority is in force.  Rhythmic surface (passing tones, suspensions,
   anticipations) is a separate layer added later by the engine; this module only
   decides how fast the harmony itself moves, and how eager each voice should be to
   subdivide.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from determinism import SeedStream
from theory import Voice

# --------------------------------------------------------------------------------------
# Meters
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class MeterSpec:
    symbol: str
    numerator: int
    denominator: int
    measure_ql: float          # quarter-length of one measure
    beat_ql: float             # quarter-length of one felt beat
    strong_offsets: Tuple[float, ...]
    compound: bool
    #: Admissible partitions of one measure into harmonic slots, shortest list first.
    divisions: Tuple[Tuple[float, ...], ...]


METERS: Dict[str, MeterSpec] = {
    "4/4": MeterSpec("4/4", 4, 4, 4.0, 1.0, (0.0, 2.0), False,
                     ((4.0,), (2.0, 2.0), (3.0, 1.0), (2.0, 1.0, 1.0),
                      (1.0, 1.0, 1.0, 1.0))),
    "2/2": MeterSpec("2/2", 2, 2, 4.0, 2.0, (0.0, 2.0), False,
                     ((4.0,), (2.0, 2.0), (2.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0))),
    "3/4": MeterSpec("3/4", 3, 4, 3.0, 1.0, (0.0,), False,
                     ((3.0,), (1.5, 1.5), (2.0, 1.0), (1.0, 1.0, 1.0))),
    "2/4": MeterSpec("2/4", 2, 4, 2.0, 1.0, (0.0,), False,
                     ((2.0,), (1.0, 1.0))),
    "3/2": MeterSpec("3/2", 3, 2, 6.0, 2.0, (0.0,), False,
                     ((6.0,), (4.0, 2.0), (3.0, 3.0), (2.0, 2.0, 2.0))),
    "6/8": MeterSpec("6/8", 6, 8, 3.0, 1.5, (0.0, 1.5), True,
                     ((3.0,), (1.5, 1.5), (1.5, 0.75, 0.75))),
}

#: Meters the API accepts.
SUPPORTED_METERS: Tuple[str, ...] = tuple(METERS)


class MeterError(ValueError):
    """Raised for an unsupported meter symbol."""


def meter_spec(symbol: str) -> MeterSpec:
    try:
        return METERS[symbol.strip()]
    except KeyError as exc:
        raise MeterError(
            f"unsupported meter {symbol!r}; expected one of {', '.join(SUPPORTED_METERS)}"
        ) from exc


# --------------------------------------------------------------------------------------
# Harmonic rhythm
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SlotTiming:
    """One span of the harmonic grid."""

    index: int
    offset: float
    duration: float
    measure: int
    beat_offset: float          # position within its measure
    metrical_weight: float      # 0..1
    strong: bool


def _metrical_weight(meter: MeterSpec, beat_offset: float) -> float:
    if abs(beat_offset) < 1e-9:
        return 1.0
    if any(abs(beat_offset - s) < 1e-9 for s in meter.strong_offsets):
        return 0.75
    if abs(beat_offset % meter.beat_ql) < 1e-9:
        return 0.5
    return 0.25


def build_grid(
    meter: MeterSpec,
    measures: int,
    density: float,
    stream: SeedStream,
    *,
    cadence_measures: Sequence[int] = (),
) -> List[SlotTiming]:
    """Partition *measures* bars into harmonic slots.

    ``density`` in ``[0, 1]`` biases the choice of partition: near 0 the harmony changes
    once a bar, near 1 it changes on every beat.  Measures listed in *cadence_measures*
    are forced to carry at least two slots so a cadence formula has somewhere to live.
    """
    if measures < 1:
        raise ValueError("measures must be >= 1")
    cadential = set(cadence_measures)
    slots: List[SlotTiming] = []
    offset = 0.0
    index = 0
    for measure in range(measures):
        options = list(meter.divisions)
        if measure in cadential:
            multi = [d for d in options if len(d) >= 2]
            if multi:
                options = multi
        appetite = max(0.05, 2.6 * density)
        weights = [appetite ** (len(option) - 1) for option in options]
        chosen = stream.derive("bar", measure).weighted_choice(options, weights)
        beat = 0.0
        for duration in chosen:
            slots.append(SlotTiming(
                index=index,
                offset=round(offset, 6),
                duration=duration,
                measure=measure,
                beat_offset=round(beat, 6),
                metrical_weight=_metrical_weight(meter, beat),
                strong=_metrical_weight(meter, beat) >= 0.75,
            ))
            index += 1
            offset += duration
            beat += duration
    return slots


# --------------------------------------------------------------------------------------
# Diminution appetite
# --------------------------------------------------------------------------------------

#: How eager each voice is to break a structural note into smaller values.  The bass
#: moves most slowly (it carries the harmony); the soprano is the most florid.  These are
#: multipliers on the global density, not absolute probabilities.
VOICE_ACTIVITY: Dict[Voice, float] = {
    Voice.BASS: 0.45,
    Voice.TENOR: 0.75,
    Voice.ALTO: 0.85,
    Voice.SOPRANO: 1.15,
}

#: Shortest note value the diminution layer will produce, in quarter-lengths.
MIN_EVENT_QL = 0.25


def diminution_probability(
    voice: Voice, density: float, slot: SlotTiming, *, active_voices: int
) -> float:
    """Probability that *voice* subdivides its note in *slot*.

    Two forces shape it: the voice's own activity profile, and a stagger term that damps
    the probability once other voices are already moving.  Without the stagger the four
    parts tend to break into semiquavers together, which destroys rhythmic independence
    and collapses the texture back into homophony.
    """
    if slot.duration < 2 * MIN_EVENT_QL:
        return 0.0
    base = density * VOICE_ACTIVITY[voice]
    stagger = 1.0 / (1.0 + 0.85 * active_voices)
    span = min(1.6, slot.duration / 2.0)
    return max(0.0, min(0.92, base * stagger * span))


__all__ = [
    "MeterSpec", "METERS", "SUPPORTED_METERS", "MeterError", "meter_spec",
    "SlotTiming", "build_grid", "VOICE_ACTIVITY", "MIN_EVENT_QL",
    "diminution_probability",
]
