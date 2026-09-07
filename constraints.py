"""constraints.py -- LEX MUSICA: the rule engine.

The engine is built on one idea: **rules detect, profiles judge.**

A *rule* is a pure function that looks at one moment of the composition (the sonority
now, the sonority before, the melodic history of each voice) and reports what it finds
-- "these two voices moved in parallel fifths", "this voice leapt a tritone", "the outer
voices moved in contrary motion".  Rules have no opinion about whether a finding is good.

A :class:`ConstraintProfile` supplies that opinion.  For each rule id it holds a
:class:`RulePolicy` giving a severity, a signed weight (negative weights are *rewards*)
and whether a finding is hard -- a hard finding prunes a candidate outright.  Two
profiles ship:

* :data:`ORTHODOX` -- Kircherian / species-counterpoint-inspired SATB constraints
  adapted into a computational four-part generative grammar.  It is *not* a claim to
  implement the whole of Fux or Palestrina; it is an explicit, extensible subset.
* :data:`HERETICAL` -- MODUS HAERETICUS.  The same rules, re-judged.  Parallel fifths
  become rewards, exposed tritones become goals, stepwise resolution becomes a penalty.
  It is an alternate grammar, not a disabled checker.

Because both profiles score the *same* findings, a Heretical composition can always be
validated against Orthodox law, and every violation it contains can be marked as
`intended` rather than mistaken (see :func:`validate`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Callable, Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Tuple,
)

from theory import (
    ADJACENT_PAIRS, ALL_PAIRS, OUTER_PAIR, UPPER_ADJACENT_PAIRS, VOICE_ORDER,
    ModeName, TRITONE, Voice, VoiceRange, harmonic_interval, is_consonant,
    melodic_interval_ok, motion_type, scale_pcs, voice_index,
)

# --------------------------------------------------------------------------------------
# Findings and violations
# --------------------------------------------------------------------------------------


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class RuleFinding:
    """A neutral observation.  Severity and weight are supplied by the profile."""

    rule: str
    voices: Tuple[str, ...]
    position: float
    detail: str = ""
    magnitude: float = 1.0


@dataclass(frozen=True)
class RuleViolation:
    """A finding judged by a profile."""

    rule: str
    severity: Severity
    voices: Tuple[str, ...]
    position: float
    detail: str
    penalty: float
    intended: bool

    def as_dict(self) -> Dict[str, object]:
        return {
            "rule": self.rule,
            "severity": self.severity.value,
            "voices": list(self.voices),
            "position": round(self.position, 4),
            "detail": self.detail,
            "penalty": round(self.penalty, 3),
            "intended": self.intended,
        }


# --------------------------------------------------------------------------------------
# Rule identifiers
# --------------------------------------------------------------------------------------


class Rules:
    """Canonical rule ids.  Strings, so they survive JSON round-trips unchanged."""

    PARALLEL_FIFTH = "parallel_fifth"
    PARALLEL_OCTAVE = "parallel_octave"
    CONTRARY_PERFECT = "contrary_perfect"
    HIDDEN_PERFECT = "hidden_perfect"
    VOICE_CROSSING = "voice_crossing"
    CROSSING_EXCESSIVE = "crossing_excessive"
    VOICE_OVERLAP = "voice_overlap"
    SPACING_UPPER = "spacing_upper"
    SPACING_LOWER = "spacing_lower"
    RANGE_VIOLATION = "range_violation"
    INCOMPLETE_TRIAD = "incomplete_triad"
    DOUBLED_LEADING_TONE = "doubled_leading_tone"
    DOUBLED_THIRD = "doubled_third"
    TRITONE_SONORITY = "tritone_sonority"
    SEMITONE_CLUSTER = "semitone_cluster"
    DISSONANT_SONORITY = "dissonant_sonority"
    HARMONIC_DISSONANCE = "harmonic_dissonance"
    DISSONANT_STRONG_BEAT = "dissonant_strong_beat"
    NONCHORD_TONE_UNSTEPWISE = "nonchord_tone_unstepwise"
    SUSPENSION_UNRESOLVED = "suspension_unresolved"
    MELODIC_FORBIDDEN_INTERVAL = "melodic_forbidden_interval"
    MELODIC_LEAP_EXCESSIVE = "melodic_leap_excessive"
    LEAP_NOT_RECOVERED = "leap_not_recovered"
    REPEATED_NOTE_EXCESS = "repeated_note_excess"
    STATIC_VOICE = "static_voice"
    CONTRARY_MOTION_OUTER = "contrary_motion_outer"
    SIMILAR_MOTION_OUTER = "similar_motion_outer"
    OBLIQUE_MOTION_OUTER = "oblique_motion_outer"
    LEADING_TONE_UNRESOLVED = "leading_tone_unresolved"
    LEADING_TONE_UNRESOLVED_INNER = "leading_tone_unresolved_inner"
    FINAL_SONORITY_NOT_TONIC = "final_sonority_not_tonic"
    CADENCE_SOPRANO_NOT_FINAL = "cadence_soprano_not_final"
    CHROMATIC_ALTERATION = "chromatic_alteration"
    DISSONANCE_RESOLVED_BY_STEP = "dissonance_resolved_by_step"
    REGISTRAL_DISPLACEMENT = "registral_displacement"
    PHRASE_LACKS_TRITONE = "phrase_lacks_tritone"


#: Melodic roles a note may play.  Anything other than ``structural`` is an ornament and
#: is allowed to be dissonant in the contexts the rules describe.
ROLE_STRUCTURAL = "structural"
ROLE_PASSING = "passing"
ROLE_NEIGHBOUR = "neighbour"
ROLE_SUSPENSION = "suspension"
ROLE_ANTICIPATION = "anticipation"
ROLE_ESCAPE = "escape"
ROLE_CHROMATIC = "chromatic"
ROLE_DISPLACED = "displaced"

ORNAMENT_ROLES: FrozenSet[str] = frozenset({
    ROLE_PASSING, ROLE_NEIGHBOUR, ROLE_SUSPENSION, ROLE_ANTICIPATION,
    ROLE_ESCAPE, ROLE_CHROMATIC, ROLE_DISPLACED,
})
#: Ornaments whose dissonance is admissible on a metrically strong moment.
STRONG_BEAT_ROLES: FrozenSet[str] = frozenset({ROLE_SUSPENSION, ROLE_CHROMATIC})
#: Ornaments the Orthodox grammar requires to be approached and left by step.
STEPWISE_ROLES: FrozenSet[str] = frozenset({ROLE_PASSING, ROLE_NEIGHBOUR})


# --------------------------------------------------------------------------------------
# The material a rule sees
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Sonority:
    """Four sounding pitches at one point in time, plus their harmonic context."""

    offset: float
    pitches: Tuple[int, int, int, int]          # ordered by VOICE_ORDER (bass..soprano)
    roles: Tuple[str, str, str, str] = (
        ROLE_STRUCTURAL, ROLE_STRUCTURAL, ROLE_STRUCTURAL, ROLE_STRUCTURAL
    )
    chord_pcs: FrozenSet[int] = frozenset()
    root_pc: int = 0
    third_pc: Optional[int] = None
    leading_tone_pc: Optional[int] = None
    slot_index: int = 0
    strong: bool = True
    is_cadential: bool = False
    is_final: bool = False

    def pitch(self, voice: Voice) -> int:
        return self.pitches[voice_index(voice)]

    def role(self, voice: Voice) -> str:
        return self.roles[voice_index(voice)]

    def with_pitches(self, pitches: Tuple[int, int, int, int]) -> "Sonority":
        return Sonority(
            offset=self.offset, pitches=pitches, roles=self.roles,
            chord_pcs=self.chord_pcs, root_pc=self.root_pc, third_pc=self.third_pc,
            leading_tone_pc=self.leading_tone_pc, slot_index=self.slot_index,
            strong=self.strong, is_cadential=self.is_cadential, is_final=self.is_final,
        )


@dataclass(frozen=True)
class MusicalFrame:
    """Context constant for a whole composition."""

    tonic_pc: int
    mode: ModeName
    ranges: Mapping[Voice, VoiceRange]
    scale_pcs: FrozenSet[int]
    ficta_pcs: FrozenSet[int] = frozenset()

    @classmethod
    def build(
        cls,
        tonic_pc: int,
        mode: ModeName,
        ranges: Mapping[Voice, VoiceRange],
        ficta_pcs: Iterable[int] = (),
    ) -> "MusicalFrame":
        return cls(
            tonic_pc=tonic_pc,
            mode=mode,
            ranges=ranges,
            scale_pcs=frozenset(scale_pcs(tonic_pc, mode)),
            ficta_pcs=frozenset(ficta_pcs),
        )


@dataclass(frozen=True)
class MomentContext:
    """One evaluation point: the sonority now, plus as much history as is known."""

    current: Sonority
    previous: Optional[Sonority] = None
    before_previous: Optional[Sonority] = None
    following: Optional[Sonority] = None
    #: Realised pitch history per voice, oldest first, *excluding* ``current``.
    history: Mapping[Voice, Sequence[int]] = field(default_factory=dict)
    is_last: bool = False

    def tail(self, voice: Voice, count: int) -> Tuple[int, ...]:
        seq = self.history.get(voice, ())
        return tuple(seq[-count:]) if count else ()


#: A rule takes a moment and the frame and reports findings.
Rule = Callable[[MomentContext, MusicalFrame], Iterable[RuleFinding]]


# --------------------------------------------------------------------------------------
# Vertical rules (single sonority)
# --------------------------------------------------------------------------------------


def _ornamented(son: Sonority) -> bool:
    """True when any voice is sounding an ornament at this moment.

    Several rules describe the harmonic *framework* -- complete triads, doubling,
    spacing, overlap -- and are properly judged on the structural sonority.  While a
    passing tone is sounding, a voice is legitimately off the chord and the spacing is
    legitimately in transit; enforcing framework rules there would forbid diminution
    altogether.  Vertical laws that govern the sounding surface (range, crossing,
    parallel perfects, dissonance treatment) are *not* suspended.
    """
    return any(role in ORNAMENT_ROLES for role in son.roles)


def rule_range(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    for voice in VOICE_ORDER:
        pitch = ctx.current.pitch(voice)
        vr = frame.ranges[voice]
        if not vr.contains(pitch):
            distance = vr.low - pitch if pitch < vr.low else pitch - vr.high
            yield RuleFinding(
                Rules.RANGE_VIOLATION, (voice.value,), ctx.current.offset,
                f"{voice.value} at MIDI {pitch} lies {distance} semitone(s) outside "
                f"[{vr.low}, {vr.high}]",
                magnitude=float(distance),
            )


def rule_crossing(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    pitches = ctx.current.pitches
    for lower, upper in ADJACENT_PAIRS:
        lo, hi = pitches[voice_index(lower)], pitches[voice_index(upper)]
        if lo > hi:
            depth = lo - hi
            yield RuleFinding(
                Rules.VOICE_CROSSING, (lower.value, upper.value), ctx.current.offset,
                f"{lower.value} lies {depth} semitone(s) above {upper.value}",
                magnitude=float(depth),
            )
            if depth > 7:
                yield RuleFinding(
                    Rules.CROSSING_EXCESSIVE, (lower.value, upper.value),
                    ctx.current.offset,
                    f"{lower.value} crosses {upper.value} by {depth} semitones",
                    magnitude=float(depth),
                )


def rule_spacing(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    if _ornamented(ctx.current):
        return
    pitches = ctx.current.pitches
    for lower, upper in UPPER_ADJACENT_PAIRS:
        gap = pitches[voice_index(upper)] - pitches[voice_index(lower)]
        if gap > 12:
            yield RuleFinding(
                Rules.SPACING_UPPER, (lower.value, upper.value), ctx.current.offset,
                f"{gap} semitones between {lower.value} and {upper.value}",
                magnitude=float(gap - 12),
            )
    lower_gap = pitches[voice_index(Voice.TENOR)] - pitches[voice_index(Voice.BASS)]
    if lower_gap > 19:
        yield RuleFinding(
            Rules.SPACING_LOWER, (Voice.BASS.value, Voice.TENOR.value),
            ctx.current.offset,
            f"{lower_gap} semitones between bass and tenor",
            magnitude=float(lower_gap - 19),
        )


def rule_doubling(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    son = ctx.current
    if not son.chord_pcs or _ornamented(son):
        return
    present = [p % 12 for p in son.pitches]
    missing = sorted(pc for pc in son.chord_pcs if pc not in present)
    if missing and len(son.chord_pcs) >= 3:
        yield RuleFinding(
            Rules.INCOMPLETE_TRIAD, tuple(v.value for v in VOICE_ORDER), son.offset,
            f"chord tone(s) {missing} absent from the sonority",
            magnitude=float(len(missing)),
        )
    if son.leading_tone_pc is not None and son.leading_tone_pc in son.chord_pcs:
        count = present.count(son.leading_tone_pc)
        if count > 1:
            voices = tuple(
                v.value for v in VOICE_ORDER
                if son.pitch(v) % 12 == son.leading_tone_pc
            )
            yield RuleFinding(
                Rules.DOUBLED_LEADING_TONE, voices, son.offset,
                f"leading tone (pc {son.leading_tone_pc}) doubled {count} times",
                magnitude=float(count - 1),
            )
    if son.third_pc is not None:
        count = present.count(son.third_pc)
        if count > 1:
            voices = tuple(
                v.value for v in VOICE_ORDER if son.pitch(v) % 12 == son.third_pc
            )
            yield RuleFinding(
                Rules.DOUBLED_THIRD, voices, son.offset,
                f"chordal third (pc {son.third_pc}) doubled {count} times",
                magnitude=float(count - 1),
            )


def rule_vertical_intervals(
    ctx: MomentContext, frame: MusicalFrame
) -> Iterable[RuleFinding]:
    """Consonance, tritones, semitone clusters and unexplained dissonance."""
    son = ctx.current
    for lower, upper in ALL_PAIRS:
        lo = son.pitch(lower)
        hi = son.pitch(upper)
        iv = harmonic_interval(min(lo, hi), max(lo, hi))
        pair = (lower.value, upper.value)
        if iv == TRITONE:
            yield RuleFinding(
                Rules.TRITONE_SONORITY, pair, son.offset,
                f"tritone between {lower.value} and {upper.value}",
            )
        if iv in (1, 11):
            yield RuleFinding(
                Rules.SEMITONE_CLUSTER, pair, son.offset,
                f"sounding semitone between {lower.value} and {upper.value}",
            )
        if is_consonant(min(lo, hi), max(lo, hi), against_bass=(lower is Voice.BASS)):
            continue
        if son.chord_pcs and lo % 12 in son.chord_pcs and hi % 12 in son.chord_pcs:
            # Both notes belong to the sounding chord, so the dissonance is the
            # harmony's own -- the diminished fifth of a vii(dim)6, for instance.  It is
            # a colour to be weighted, not an unprepared clash to be forbidden.
            yield RuleFinding(
                Rules.HARMONIC_DISSONANCE, pair, son.offset,
                f"chordal dissonance ({iv} semitones) between "
                f"{lower.value} and {upper.value}",
            )
            continue
        roles = (son.role(lower), son.role(upper))
        ornaments = [r for r in roles if r in ORNAMENT_ROLES]
        if not ornaments:
            yield RuleFinding(
                Rules.DISSONANT_SONORITY, pair, son.offset,
                f"unprepared dissonance ({iv} semitones) between "
                f"{lower.value} and {upper.value}",
            )
        elif son.strong and not any(r in STRONG_BEAT_ROLES for r in ornaments):
            yield RuleFinding(
                Rules.DISSONANT_STRONG_BEAT, pair, son.offset,
                f"dissonance on a strong position explained only by {ornaments}",
            )


def rule_chromatic(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    for voice in VOICE_ORDER:
        pc = ctx.current.pitch(voice) % 12
        if pc in frame.scale_pcs or pc in frame.ficta_pcs:
            continue
        yield RuleFinding(
            Rules.CHROMATIC_ALTERATION, (voice.value,), ctx.current.offset,
            f"{voice.value} sounds pitch class {pc}, outside the mode",
        )


# --------------------------------------------------------------------------------------
# Vertical rules (pairs of sonorities)
# --------------------------------------------------------------------------------------


def rule_parallels(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    prev = ctx.previous
    if prev is None:
        return
    for lower, upper in ALL_PAIRS:
        pl, pu = prev.pitch(lower), prev.pitch(upper)
        cl, cu = ctx.current.pitch(lower), ctx.current.pitch(upper)
        if pl == cl and pu == cu:
            continue  # nothing moved: no motion to judge
        iv_prev = harmonic_interval(min(pl, pu), max(pl, pu))
        iv_cur = harmonic_interval(min(cl, cu), max(cl, cu))
        if iv_prev != iv_cur or iv_cur not in (0, 7):
            continue
        moved_lower = cl != pl
        moved_upper = cu != pu
        if not (moved_lower and moved_upper):
            continue  # oblique motion into a perfect interval is legal
        same_direction = ((cl - pl) > 0) == ((cu - pu) > 0)
        pair = (lower.value, upper.value)
        kind = "octave/unison" if iv_cur == 0 else "fifth"
        if same_direction:
            rule = Rules.PARALLEL_FIFTH if iv_cur == 7 else Rules.PARALLEL_OCTAVE
            yield RuleFinding(
                rule, pair, ctx.current.offset,
                f"consecutive perfect {kind}s, {lower.value}/{upper.value}",
            )
        else:
            yield RuleFinding(
                Rules.CONTRARY_PERFECT, pair, ctx.current.offset,
                f"perfect {kind} to perfect {kind} by contrary motion, "
                f"{lower.value}/{upper.value}",
            )


def rule_hidden_perfect(
    ctx: MomentContext, frame: MusicalFrame
) -> Iterable[RuleFinding]:
    """Direct fifths/octaves reached by similar motion in the outer voices."""
    prev = ctx.previous
    if prev is None:
        return
    lower, upper = OUTER_PAIR
    pl, pu = prev.pitch(lower), prev.pitch(upper)
    cl, cu = ctx.current.pitch(lower), ctx.current.pitch(upper)
    iv_cur = harmonic_interval(min(cl, cu), max(cl, cu))
    if iv_cur not in (0, 7):
        return
    if motion_type(pl, cl, pu, cu) != "similar":
        return
    if abs(cu - pu) <= 2:
        return  # the upper voice arrives by step: permitted
    iv_prev = harmonic_interval(min(pl, pu), max(pl, pu))
    if iv_prev == iv_cur:
        return  # already reported as a true parallel
    yield RuleFinding(
        Rules.HIDDEN_PERFECT, (lower.value, upper.value), ctx.current.offset,
        f"outer voices reach a perfect {'octave' if iv_cur == 0 else 'fifth'} "
        f"by similar motion with a leap in the {upper.value}",
    )


def rule_overlap(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    prev = ctx.previous
    if prev is None or _ornamented(prev) or _ornamented(ctx.current):
        return
    for lower, upper in ADJACENT_PAIRS:
        if ctx.current.pitch(lower) > prev.pitch(upper):
            yield RuleFinding(
                Rules.VOICE_OVERLAP, (lower.value, upper.value), ctx.current.offset,
                f"{lower.value} rises above the {upper.value}'s previous pitch",
            )
        if ctx.current.pitch(upper) < prev.pitch(lower):
            yield RuleFinding(
                Rules.VOICE_OVERLAP, (lower.value, upper.value), ctx.current.offset,
                f"{upper.value} falls below the {lower.value}'s previous pitch",
            )


def rule_outer_motion(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    prev = ctx.previous
    if prev is None:
        return
    lower, upper = OUTER_PAIR
    kind = motion_type(
        prev.pitch(lower), ctx.current.pitch(lower),
        prev.pitch(upper), ctx.current.pitch(upper),
    )
    pair = (lower.value, upper.value)
    if kind == "contrary":
        yield RuleFinding(Rules.CONTRARY_MOTION_OUTER, pair, ctx.current.offset,
                          "outer voices move in contrary motion")
    elif kind == "similar":
        yield RuleFinding(Rules.SIMILAR_MOTION_OUTER, pair, ctx.current.offset,
                          "outer voices move in similar motion")
    elif kind == "oblique":
        yield RuleFinding(Rules.OBLIQUE_MOTION_OUTER, pair, ctx.current.offset,
                          "outer voices move in oblique motion")


# --------------------------------------------------------------------------------------
# Melodic rules
# --------------------------------------------------------------------------------------

#: Largest leap tolerated per voice, in semitones.  Inner voices move more smoothly.
MAX_LEAP: Dict[Voice, int] = {
    Voice.BASS: 12, Voice.TENOR: 9, Voice.ALTO: 9, Voice.SOPRANO: 12,
}


def line_findings(
    voice: Voice,
    notes: Sequence[Tuple],
    *,
    start_index: int = 1,
) -> Iterable[RuleFinding]:
    """Rules along one voice's own line of *attacked* notes.

    ``notes`` is ``(midi, offset)`` or ``(midi, offset, role)`` in order.  This is the
    single implementation of the horizontal rules: the solver calls it through
    :func:`rule_melodic` with a three-note window over the structural grid, and the
    validator calls it over each finished voice part.

    Working on attacks rather than on grid samples is what makes ornament treatment
    checkable at all.  On a sampled grid a voice appears once per *neighbour's* attack,
    so its own passing tone looks as though it were repeated and then left by no
    interval; along its own line the approach and departure are exactly the two notes
    either side.
    """

    def role_at(index: int) -> str:
        entry = notes[index]
        return entry[2] if len(entry) > 2 else ROLE_STRUCTURAL

    for i in range(max(1, start_index), len(notes)):
        pitch, offset = notes[i][0], notes[i][1]
        before = notes[i - 1][0]
        step = pitch - before
        size = abs(step)
        if size:
            if not melodic_interval_ok(step):
                kind = ("tritone" if size == 6
                        else "seventh" if size in (10, 11) else "compound")
                yield RuleFinding(
                    Rules.MELODIC_FORBIDDEN_INTERVAL, (voice.value,), offset,
                    f"{voice.value} leaps {step:+d} semitones ({kind})",
                    magnitude=float(size),
                )
            if size > MAX_LEAP[voice]:
                yield RuleFinding(
                    Rules.MELODIC_LEAP_EXCESSIVE, (voice.value,), offset,
                    f"{voice.value} leaps {step:+d} semitones, beyond its limit of "
                    f"{MAX_LEAP[voice]}",
                    magnitude=float(size - MAX_LEAP[voice]),
                )
            if size >= 12:
                yield RuleFinding(
                    Rules.REGISTRAL_DISPLACEMENT, (voice.value,), offset,
                    f"{voice.value} is displaced by {step:+d} semitones",
                    magnitude=float(size),
                )
            if i >= 2:
                leap = before - notes[i - 2][0]
                if abs(leap) >= 5:
                    recovered = (1 <= size <= 2) and ((step > 0) != (leap > 0))
                    if not recovered:
                        yield RuleFinding(
                            Rules.LEAP_NOT_RECOVERED, (voice.value,), offset,
                            f"{voice.value} leapt {leap:+d} and did not recover by step "
                            f"in the opposite direction (moved {step:+d})",
                            magnitude=abs(leap) / 4.0,
                        )
        if i >= 2 and notes[i - 2][0] == before == pitch:
            yield RuleFinding(
                Rules.REPEATED_NOTE_EXCESS, (voice.value,), offset,
                f"{voice.value} sounds MIDI {pitch} three times in succession",
            )
        if i >= 4 and len({entry[0] for entry in notes[i - 4:i + 1]}) == 1:
            yield RuleFinding(
                Rules.STATIC_VOICE, (voice.value,), offset,
                f"{voice.value} has not moved for five attacks",
            )

        # -- ornament treatment -------------------------------------------------
        role = role_at(i)
        if role in STEPWISE_ROLES and i + 1 < len(notes):
            departure = notes[i + 1][0] - pitch
            if not (1 <= abs(step) <= 2) or not (1 <= abs(departure) <= 2):
                yield RuleFinding(
                    Rules.NONCHORD_TONE_UNSTEPWISE, (voice.value,), offset,
                    f"{voice.value} {role} tone approached {step:+d} and left "
                    f"{departure:+d}; both must be steps",
                )
        previous_role = role_at(i - 1)
        if previous_role in ORNAMENT_ROLES:
            if 1 <= abs(step) <= 2:
                yield RuleFinding(
                    Rules.DISSONANCE_RESOLVED_BY_STEP, (voice.value,), offset,
                    f"{voice.value} resolves its {previous_role} tone by step "
                    f"({step:+d})",
                )
            elif previous_role == ROLE_SUSPENSION:
                yield RuleFinding(
                    Rules.SUSPENSION_UNRESOLVED, (voice.value,), offset,
                    f"{voice.value} leaves a suspension by {step:+d} instead of a "
                    f"descending step",
                )
        if previous_role == ROLE_SUSPENSION and step > 0:
            yield RuleFinding(
                Rules.SUSPENSION_UNRESOLVED, (voice.value,), offset,
                f"{voice.value} resolves a suspension upward ({step:+d}); a suspension "
                f"falls",
            )


def rule_melodic(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    """Horizontal rules at one grid moment, delegated to :func:`line_findings`."""
    if ctx.previous is None:
        return
    for voice in VOICE_ORDER:
        window = [(ctx.previous.pitch(voice), ctx.previous.offset)]
        if ctx.before_previous is not None:
            window.insert(0, (ctx.before_previous.pitch(voice),
                              ctx.before_previous.offset))
        window.append((ctx.current.pitch(voice), ctx.current.offset))
        yield from line_findings(voice, window, start_index=len(window) - 1)


def rule_repetition(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    for voice in VOICE_ORDER:
        tail = ctx.tail(voice, 2)
        now = ctx.current.pitch(voice)
        if len(tail) == 2 and tail[0] == tail[1] == now:
            yield RuleFinding(
                Rules.REPEATED_NOTE_EXCESS, (voice.value,), ctx.current.offset,
                f"{voice.value} sounds MIDI {now} three times in succession",
            )


def rule_cadence(ctx: MomentContext, frame: MusicalFrame) -> Iterable[RuleFinding]:
    prev = ctx.previous
    # The resolution happens at the *next chord*, not at the next sampled attack: on a
    # rendered grid another voice's ornament can insert a moment inside the cadential
    # chord, where the leading tone is still legitimately being held.
    crossed_slot = prev is not None and prev.slot_index != ctx.current.slot_index
    if (prev is not None and crossed_slot and prev.is_cadential
            and prev.leading_tone_pc is not None):
        for voice in VOICE_ORDER:
            if prev.pitch(voice) % 12 != prev.leading_tone_pc:
                continue
            if ctx.current.pitch(voice) - prev.pitch(voice) == 1:
                continue
            rule = (
                Rules.LEADING_TONE_UNRESOLVED
                if voice in (Voice.SOPRANO, Voice.BASS)
                else Rules.LEADING_TONE_UNRESOLVED_INNER
            )
            yield RuleFinding(
                rule, (voice.value,), ctx.current.offset,
                f"{voice.value} holds the leading tone and does not rise a semitone "
                f"to the final",
            )
    if ctx.current.is_final:
        bass_pc = ctx.current.pitch(Voice.BASS) % 12
        if bass_pc != frame.tonic_pc:
            yield RuleFinding(
                Rules.FINAL_SONORITY_NOT_TONIC, (Voice.BASS.value,),
                ctx.current.offset,
                f"the composition closes on pitch class {bass_pc}, not the final "
                f"({frame.tonic_pc})",
            )
        if ctx.current.pitch(Voice.SOPRANO) % 12 != frame.tonic_pc:
            yield RuleFinding(
                Rules.CADENCE_SOPRANO_NOT_FINAL, (Voice.SOPRANO.value,),
                ctx.current.offset,
                "the soprano does not close on the final",
            )


#: Rules that judge a vertical moment.  Safe to run over any grid, sampled or not.
GRID_RULES: Tuple[Rule, ...] = (
    rule_range,
    rule_crossing,
    rule_spacing,
    rule_doubling,
    rule_vertical_intervals,
    rule_chromatic,
    rule_parallels,
    rule_hidden_perfect,
    rule_overlap,
    rule_outer_motion,
    rule_cadence,
)

#: Horizontal rules.  Meaningful only where every voice attacks at every moment, which
#: is true of the structural grid the solver searches over, and false of the rendered
#: grid -- see :func:`validate`.
LINE_RULES: Tuple[Rule, ...] = (rule_melodic, rule_repetition)

#: The full set, used by the solver.
RULES: Tuple[Rule, ...] = GRID_RULES + LINE_RULES


# --------------------------------------------------------------------------------------
# Profiles
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class RulePolicy:
    """How a profile judges one rule.

    ``weight`` is signed: positive penalises, negative *rewards*.  ``hard_until`` is the
    highest relaxation level at which a finding still prunes a candidate outright; -1
    means the rule is never hard, and a large value means it is always hard.
    """

    weight: float
    severity: Severity = Severity.WARNING
    hard_until: int = -1
    intended: bool = False

    def is_hard(self, relaxation: int) -> bool:
        return relaxation <= self.hard_until


#: Levels the solver may relax to before giving up.  Level 0 is full strictness.
MAX_RELAXATION = 2
_ALWAYS = 99


@dataclass(frozen=True)
class ConstraintProfile:
    """A complete body of law: policies plus the shaping preferences of a style."""

    name: str
    title: str
    policies: Mapping[str, RulePolicy]
    #: Cost per semitone of melodic motion beyond a step (positive = prefer smoothness).
    melodic_smoothness: float
    #: Cost per semitone a voice sits outside its comfortable tessitura.
    tessitura_cost: float
    #: Reward for melodic motion *by leap* (Heretical appetite for disjunction).
    leap_appetite: float
    #: Whether the harmonic planner may introduce chromatic (non-modal) triads.
    allows_chromatic_harmony: bool
    #: Probability weight for ornaments that break Orthodox treatment.
    transgressive_ornament_rate: float

    def policy(self, rule: str) -> RulePolicy:
        return self.policies.get(rule, _DEFAULT_POLICY)

    def judge(self, finding: RuleFinding) -> RuleViolation:
        policy = self.policy(finding.rule)
        return RuleViolation(
            rule=finding.rule,
            severity=policy.severity,
            voices=finding.voices,
            position=finding.position,
            detail=finding.detail,
            penalty=policy.weight * max(1.0, finding.magnitude),
            intended=policy.intended,
        )

    def shape_cost(self, ctx: MomentContext, frame: MusicalFrame) -> float:
        """Style preferences that are graded rather than binary."""
        cost = 0.0
        for voice in VOICE_ORDER:
            pitch = ctx.current.pitch(voice)
            cost += self.tessitura_cost * frame.ranges[voice].excursion(pitch)
            if ctx.previous is not None:
                move = abs(pitch - ctx.previous.pitch(voice))
                cost += self.melodic_smoothness * max(0, move - 2)
                cost -= self.leap_appetite * min(move, 7)
        return cost


_DEFAULT_POLICY = RulePolicy(weight=0.0, severity=Severity.INFO)


ORTHODOX = ConstraintProfile(
    name="orthodox",
    title="LEX MUSICA — Kircherian / species-counterpoint-inspired SATB constraints "
          "adapted into a computational four-part generative grammar",
    melodic_smoothness=0.45,
    tessitura_cost=0.55,
    leap_appetite=0.0,
    allows_chromatic_harmony=False,
    transgressive_ornament_rate=0.0,
    policies={
        Rules.RANGE_VIOLATION: RulePolicy(24.0, Severity.ERROR, _ALWAYS),
        Rules.PARALLEL_FIFTH: RulePolicy(14.0, Severity.ERROR, _ALWAYS),
        Rules.PARALLEL_OCTAVE: RulePolicy(14.0, Severity.ERROR, _ALWAYS),
        Rules.VOICE_CROSSING: RulePolicy(11.0, Severity.ERROR, _ALWAYS),
        Rules.CROSSING_EXCESSIVE: RulePolicy(15.0, Severity.ERROR, _ALWAYS),
        Rules.FINAL_SONORITY_NOT_TONIC: RulePolicy(18.0, Severity.ERROR, _ALWAYS),
        Rules.MELODIC_FORBIDDEN_INTERVAL: RulePolicy(10.0, Severity.ERROR, _ALWAYS),
        Rules.DISSONANT_SONORITY: RulePolicy(9.0, Severity.ERROR, 1),
        Rules.NONCHORD_TONE_UNSTEPWISE: RulePolicy(7.0, Severity.ERROR, 1),
        Rules.SUSPENSION_UNRESOLVED: RulePolicy(7.0, Severity.ERROR, 1),
        Rules.LEADING_TONE_UNRESOLVED: RulePolicy(8.0, Severity.ERROR, 1),
        Rules.DOUBLED_LEADING_TONE: RulePolicy(6.0, Severity.ERROR, 1),
        Rules.MELODIC_LEAP_EXCESSIVE: RulePolicy(5.0, Severity.WARNING, 1),
        Rules.DISSONANT_STRONG_BEAT: RulePolicy(4.5, Severity.WARNING, 0),
        Rules.INCOMPLETE_TRIAD: RulePolicy(3.2, Severity.WARNING, 0),
        Rules.SPACING_UPPER: RulePolicy(2.8, Severity.WARNING, 0),
        Rules.VOICE_OVERLAP: RulePolicy(2.2, Severity.WARNING, 0),
        Rules.CONTRARY_PERFECT: RulePolicy(2.5, Severity.WARNING),
        Rules.HIDDEN_PERFECT: RulePolicy(2.0, Severity.WARNING),
        Rules.SEMITONE_CLUSTER: RulePolicy(3.0, Severity.WARNING),
        Rules.LEAP_NOT_RECOVERED: RulePolicy(2.0, Severity.WARNING),
        # The diminished fifth of a vii(dim)6 is the harmony's own colour, not an
        # unprepared clash: weighted, never forbidden.
        Rules.HARMONIC_DISSONANCE: RulePolicy(1.1, Severity.INFO),
        Rules.SPACING_LOWER: RulePolicy(1.4, Severity.INFO),
        Rules.CHROMATIC_ALTERATION: RulePolicy(1.6, Severity.WARNING),
        Rules.LEADING_TONE_UNRESOLVED_INNER: RulePolicy(1.5, Severity.WARNING),
        Rules.REGISTRAL_DISPLACEMENT: RulePolicy(1.5, Severity.INFO),
        Rules.REPEATED_NOTE_EXCESS: RulePolicy(1.2, Severity.INFO),
        Rules.STATIC_VOICE: RulePolicy(1.2, Severity.INFO),
        Rules.CADENCE_SOPRANO_NOT_FINAL: RulePolicy(1.0, Severity.INFO),
        Rules.DOUBLED_THIRD: RulePolicy(0.8, Severity.INFO),
        Rules.TRITONE_SONORITY: RulePolicy(0.6, Severity.INFO),
        Rules.SIMILAR_MOTION_OUTER: RulePolicy(0.5, Severity.INFO),
        Rules.OBLIQUE_MOTION_OUTER: RulePolicy(-0.25, Severity.INFO),
        Rules.CONTRARY_MOTION_OUTER: RulePolicy(-0.7, Severity.INFO),
        Rules.DISSONANCE_RESOLVED_BY_STEP: RulePolicy(-1.2, Severity.INFO),
        Rules.PHRASE_LACKS_TRITONE: RulePolicy(0.0, Severity.INFO),
    },
)


HERETICAL = ConstraintProfile(
    name="hereticus",
    title="MODUS HAERETICUS — an inverted grammar: the same laws, deliberately "
          "transgressed and scored as virtues",
    melodic_smoothness=0.0,
    tessitura_cost=0.18,
    leap_appetite=0.22,
    allows_chromatic_harmony=True,
    transgressive_ornament_rate=0.55,
    policies={
        # The two inviolable constraints: a voice may not leave its body, and it may
        # not collapse through its neighbour.  Everything else is negotiable.
        Rules.RANGE_VIOLATION: RulePolicy(24.0, Severity.ERROR, _ALWAYS),
        Rules.CROSSING_EXCESSIVE: RulePolicy(15.0, Severity.ERROR, _ALWAYS),

        # Orthodox errors, deliberately sought.
        Rules.PARALLEL_FIFTH: RulePolicy(-4.5, Severity.INFO, intended=True),
        Rules.PARALLEL_OCTAVE: RulePolicy(-3.5, Severity.INFO, intended=True),
        Rules.CONTRARY_PERFECT: RulePolicy(-0.8, Severity.INFO, intended=True),
        Rules.HIDDEN_PERFECT: RulePolicy(-1.2, Severity.INFO, intended=True),
        Rules.TRITONE_SONORITY: RulePolicy(-3.5, Severity.INFO, intended=True),
        Rules.SEMITONE_CLUSTER: RulePolicy(-2.6, Severity.INFO, intended=True),
        Rules.DISSONANT_SONORITY: RulePolicy(-2.2, Severity.INFO, intended=True),
        Rules.HARMONIC_DISSONANCE: RulePolicy(-1.5, Severity.INFO, intended=True),
        Rules.DISSONANT_STRONG_BEAT: RulePolicy(-2.0, Severity.INFO, intended=True),
        Rules.NONCHORD_TONE_UNSTEPWISE: RulePolicy(-1.6, Severity.INFO, intended=True),
        Rules.SUSPENSION_UNRESOLVED: RulePolicy(-1.6, Severity.INFO, intended=True),
        Rules.MELODIC_FORBIDDEN_INTERVAL: RulePolicy(-3.0, Severity.INFO, intended=True),
        Rules.MELODIC_LEAP_EXCESSIVE: RulePolicy(-0.6, Severity.INFO, intended=True),
        Rules.LEAP_NOT_RECOVERED: RulePolicy(-1.4, Severity.INFO, intended=True),
        Rules.REGISTRAL_DISPLACEMENT: RulePolicy(-1.8, Severity.INFO, intended=True),
        Rules.CHROMATIC_ALTERATION: RulePolicy(-2.4, Severity.INFO, intended=True),
        Rules.VOICE_CROSSING: RulePolicy(-1.0, Severity.INFO, intended=True),
        Rules.VOICE_OVERLAP: RulePolicy(-0.6, Severity.INFO, intended=True),
        Rules.SPACING_UPPER: RulePolicy(-0.5, Severity.INFO, intended=True),
        Rules.DOUBLED_LEADING_TONE: RulePolicy(-1.5, Severity.INFO, intended=True),
        Rules.LEADING_TONE_UNRESOLVED: RulePolicy(-2.2, Severity.INFO, intended=True),
        Rules.LEADING_TONE_UNRESOLVED_INNER: RulePolicy(-0.6, Severity.INFO, intended=True),
        Rules.FINAL_SONORITY_NOT_TONIC: RulePolicy(-1.0, Severity.INFO, intended=True),
        Rules.CADENCE_SOPRANO_NOT_FINAL: RulePolicy(-0.6, Severity.INFO, intended=True),
        Rules.SIMILAR_MOTION_OUTER: RulePolicy(-0.9, Severity.INFO, intended=True),

        # Orthodox virtues, penalised.  "Dissonance must leap"; inertia is still a sin.
        Rules.DISSONANCE_RESOLVED_BY_STEP: RulePolicy(2.2, Severity.WARNING),
        Rules.CONTRARY_MOTION_OUTER: RulePolicy(0.9, Severity.INFO),
        Rules.OBLIQUE_MOTION_OUTER: RulePolicy(0.2, Severity.INFO),
        Rules.REPEATED_NOTE_EXCESS: RulePolicy(2.0, Severity.WARNING),
        Rules.STATIC_VOICE: RulePolicy(2.5, Severity.WARNING),
        Rules.PHRASE_LACKS_TRITONE: RulePolicy(4.0, Severity.WARNING),

        # Neutral in this grammar.
        Rules.INCOMPLETE_TRIAD: RulePolicy(0.0, Severity.INFO),
        Rules.DOUBLED_THIRD: RulePolicy(0.0, Severity.INFO),
        Rules.SPACING_LOWER: RulePolicy(0.0, Severity.INFO),
    },
)


PROFILES: Dict[str, ConstraintProfile] = {
    ORTHODOX.name: ORTHODOX,
    HERETICAL.name: HERETICAL,
}


def get_profile(heretical: bool) -> ConstraintProfile:
    return HERETICAL if heretical else ORTHODOX


# --------------------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class MomentResult:
    penalty: float
    violations: Tuple[RuleViolation, ...]
    hard_failures: Tuple[RuleViolation, ...]

    @property
    def feasible(self) -> bool:
        return not self.hard_failures


def collect_findings(
    ctx: MomentContext, frame: MusicalFrame, rules: Sequence[Rule] = RULES
) -> List[RuleFinding]:
    findings: List[RuleFinding] = []
    for rule in rules:
        findings.extend(rule(ctx, frame))
    return findings


def evaluate_moment(
    ctx: MomentContext,
    frame: MusicalFrame,
    profile: ConstraintProfile,
    relaxation: int = 0,
    rules: Sequence[Rule] = RULES,
) -> MomentResult:
    """Run every rule at one moment and judge the findings under *profile*."""
    penalty = profile.shape_cost(ctx, frame)
    violations: List[RuleViolation] = []
    hard: List[RuleViolation] = []
    for finding in collect_findings(ctx, frame, rules):
        policy = profile.policy(finding.rule)
        violation = profile.judge(finding)
        penalty += violation.penalty
        if policy.weight != 0.0 or policy.severity is not Severity.INFO:
            violations.append(violation)
        if policy.is_hard(relaxation):
            hard.append(violation)
    return MomentResult(
        penalty=penalty, violations=tuple(violations), hard_failures=tuple(hard)
    )


@dataclass
class ValidationReport:
    """The inspectable outcome of validating a finished composition."""

    profile: str
    violations: List[RuleViolation] = field(default_factory=list)

    @property
    def unintended_errors(self) -> List[RuleViolation]:
        return [
            v for v in self.violations
            if v.severity is Severity.ERROR and not v.intended
        ]

    @property
    def intended_violations(self) -> List[RuleViolation]:
        return [v for v in self.violations if v.intended]

    @property
    def passed(self) -> bool:
        return not self.unintended_errors

    def counts(self) -> Dict[str, int]:
        tally: Dict[str, int] = {}
        for v in self.violations:
            tally[v.rule] = tally.get(v.rule, 0) + 1
        return dict(sorted(tally.items()))

    def as_dict(self) -> Dict[str, object]:
        return {
            "profile": self.profile,
            "passed": self.passed,
            "counts_by_rule": self.counts(),
            "counts_by_severity": {
                severity.value: sum(
                    1 for v in self.violations if v.severity is severity
                )
                for severity in Severity
            },
            "unintended_error_count": len(self.unintended_errors),
            "intended_violation_count": len(self.intended_violations),
            "violations": [v.as_dict() for v in self.violations],
        }


def validate(
    grid: Sequence[Sonority],
    frame: MusicalFrame,
    profile: ConstraintProfile,
    *,
    lines: Optional[Mapping[Voice, Sequence[Tuple[int, float]]]] = None,
    reference: ConstraintProfile = ORTHODOX,
) -> ValidationReport:
    """Validate a rendered composition.

    Vertical rules run over the sampled *grid*; horizontal rules run over *lines*, each
    voice's own sequence of attacked ``(midi, offset)`` notes.  Separating them matters:
    on a sampled grid a sustaining voice appears once per neighbour's attack, which would
    otherwise be misread as repeated notes.  If *lines* is omitted the grid is used for
    both, which is correct only when every voice attacks at every moment.

    Findings are graded under *reference* (Orthodox by default) so severities are
    comparable across profiles, while a finding the *active* profile deliberately rewards
    is flagged ``intended``.  A Heretical composition therefore reports its parallel
    fifths as intended transgressions, and an accidental implementation error still shows
    up as an unintended ``error``.
    """
    report = ValidationReport(profile=profile.name)

    def record(finding: RuleFinding) -> None:
        reference_policy = reference.policy(finding.rule)
        if reference_policy.weight <= 0.0 and reference_policy.severity is Severity.INFO:
            return  # a reward or a neutral observation, not a violation
        report.violations.append(RuleViolation(
            rule=finding.rule,
            severity=reference_policy.severity,
            voices=finding.voices,
            position=finding.position,
            detail=finding.detail,
            penalty=reference_policy.weight * max(1.0, finding.magnitude),
            intended=profile.policy(finding.rule).intended,
        ))

    history: Dict[Voice, List[int]] = {v: [] for v in VOICE_ORDER}
    for index, sonority in enumerate(grid):
        ctx = MomentContext(
            current=sonority,
            previous=grid[index - 1] if index >= 1 else None,
            before_previous=grid[index - 2] if index >= 2 else None,
            following=grid[index + 1] if index + 1 < len(grid) else None,
            history={v: tuple(history[v]) for v in VOICE_ORDER},
            is_last=index == len(grid) - 1,
        )
        for finding in collect_findings(ctx, frame, GRID_RULES):
            record(finding)
        if lines is None:
            for finding in collect_findings(ctx, frame, LINE_RULES):
                record(finding)
        for voice in VOICE_ORDER:
            history[voice].append(sonority.pitch(voice))

    if lines is not None:
        for voice in VOICE_ORDER:
            for finding in line_findings(voice, list(lines.get(voice, ()))):
                record(finding)

    report.violations.sort(key=lambda v: (v.position, v.rule))
    return report


__all__ = [
    "Severity", "RuleFinding", "RuleViolation", "Rules", "Sonority", "MusicalFrame",
    "MomentContext", "Rule", "RULES", "GRID_RULES", "LINE_RULES",
    "line_findings", "MAX_LEAP", "RulePolicy", "ConstraintProfile",
    "ORTHODOX", "HERETICAL", "PROFILES", "get_profile", "MomentResult",
    "collect_findings", "evaluate_moment", "ValidationReport", "validate",
    "MAX_RELAXATION",
    "ROLE_STRUCTURAL", "ROLE_PASSING", "ROLE_NEIGHBOUR", "ROLE_SUSPENSION",
    "ROLE_ANTICIPATION", "ROLE_ESCAPE", "ROLE_CHROMATIC", "ROLE_DISPLACED",
    "ORNAMENT_ROLES", "STRONG_BEAT_ROLES", "STEPWISE_ROLES",
]
