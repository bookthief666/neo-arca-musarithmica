"""kircher_engine.py -- THE GHOST: the composition engine.

The pipeline, in order:

    request -> normalisation -> Polygraphia analysis -> GenesisConfig -> seed
            -> mode/final/tempo/meter -> harmonic skeleton (phrases + cadences)
            -> STRUCTURAL VOICING  (bounded backtracking search over SATB sonorities)
            -> DIMINUTION          (per-voice rhythmic surface: passing, neighbour,
                                    suspension, anticipation, chord-skip, and the
                                    Heretical transgressions)
            -> RENDER + REPAIR     (sample every attack point; revert any ornament that
                                    introduced a hard violation)
            -> FINAL VALIDATION    -> event JSON / music21 score / Base64 MIDI

Two design points are worth stating plainly.

**The four voices are solved together, not stacked.**  There is no melody that the other
three parts decorate.  Every slot of the harmonic skeleton is filled by searching over
complete four-note sonorities, scored by the constraint profile against the *previous*
sonority and each voice's own melodic history.  Parallel perfects, crossing, spacing,
doubling and leap recovery all prune the search before a note is committed.

**Rhythmic independence is a separate layer.**  Once the backbone is contrapuntally
sound, each voice independently decides whether to break its structural note into
smaller values, with a stagger term that damps the probability when other voices are
already moving.  Anything that layer introduces is re-checked on the rendered grid and
reverted if it breaks a hard law -- so the surface can never smuggle in a parallel fifth
the backbone forbade.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import constraints as law
from constraints import (
    ConstraintProfile, MomentContext, MusicalFrame, RuleViolation, Rules, Severity,
    Sonority, ValidationReport, get_profile, validate,
)
from determinism import Provenance, SeedStream, coerce_seed, fingerprint, stable_hash
from harmony import HarmonicPlan, HarmonicSlot, build_plan
from rhythm import MIN_EVENT_QL, diminution_probability, meter_spec
from semantics import ARTICULATIONS, INSTRUMENTS, SemanticAnalysis, SemanticAnalyzer
from theory import (
    ModeName, Speller, VOICE_ORDER, Voice, mode_spec, normalize_note_name,
    parse_note_name, pitches_in_range, shifted_range, voice_index,
)

ENGINE_NAME = "neo-arca-musarithmica"
ENGINE_VERSION = "1.0.0"


class GenerationError(RuntimeError):
    """A controlled, diagnosable failure of the generative process.

    Raised only when the search has genuinely exhausted its budget at every relaxation
    level.  Carries enough context for the API layer to explain what happened.
    """

    def __init__(self, message: str, diagnostics: Optional[Dict[str, object]] = None):
        super().__init__(message)
        self.diagnostics: Dict[str, object] = diagnostics or {}


# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SearchBudget:
    """Hard limits.  The engine never searches without one."""

    max_candidates_per_slot: int = 96
    max_nodes_per_slot: int = 5000
    max_backtracks: int = 600
    max_repair_passes: int = 8
    max_relaxation: int = law.MAX_RELAXATION

    def as_dict(self) -> Dict[str, int]:
        return {
            "max_candidates_per_slot": self.max_candidates_per_slot,
            "max_nodes_per_slot": self.max_nodes_per_slot,
            "max_backtracks": self.max_backtracks,
            "max_repair_passes": self.max_repair_passes,
            "max_relaxation": self.max_relaxation,
        }


@dataclass(frozen=True)
class GenesisConfig:
    """The fully normalised instruction set for one composition."""

    text: str
    mode: ModeName
    tonic: str
    tonic_pc: int
    tempo: int
    meter: str
    measures: int
    phrase_measures: int
    density: float
    register_shift: int
    contour_bias: float
    cadence_strength: float
    tension: float
    heresy: float
    heretical: bool
    articulation: str
    gate: float
    intensity: float
    mood: str
    ensemble: str
    instrumentation: Dict[str, str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "text": self.text,
            "mode": self.mode.value,
            "mood": self.mood,
            "tonic": self.tonic,
            "tonic_pitch_class": self.tonic_pc,
            "tempo": self.tempo,
            "meter": self.meter,
            "measures": self.measures,
            "phrase_measures": self.phrase_measures,
            "density": round(self.density, 4),
            "register_shift": self.register_shift,
            "contour_bias": round(self.contour_bias, 4),
            "cadence_strength": round(self.cadence_strength, 4),
            "tension": round(self.tension, 4),
            "heresy": round(self.heresy, 4),
            "heretical": self.heretical,
            "law_profile": "hereticus" if self.heretical else "orthodox",
            "articulation": self.articulation,
            "gate": round(self.gate, 3),
            "intensity": round(self.intensity, 4),
            "ensemble": self.ensemble,
            "instrumentation": dict(self.instrumentation),
        }

    def fingerprint(self) -> str:
        payload = self.as_dict()
        payload.pop("text", None)
        payload["instrumentation"] = tuple(sorted(self.instrumentation.items()))
        return fingerprint(payload)


# --------------------------------------------------------------------------------------
# Output structures
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class NoteEvent:
    """One sounding note, ready for Tone.js or for music21."""

    voice: Voice
    midi: int
    pitch: str
    offset: float
    duration: float           # notated quarter-lengths
    sounding_duration: float  # duration after the articulation gate
    velocity: int
    role: str
    slot_index: int
    measure: int

    def as_dict(self) -> Dict[str, object]:
        return {
            "pitch": self.pitch,
            "midi": self.midi,
            "offset": round(self.offset, 6),
            "duration": round(self.duration, 6),
            "sounding_duration": round(self.sounding_duration, 6),
            "velocity": self.velocity,
            "role": self.role,
            "slot": self.slot_index,
            "measure": self.measure,
        }


@dataclass
class SearchStats:
    slots: int = 0
    candidate_sets_built: int = 0
    candidates_considered: int = 0
    nodes_visited: int = 0
    backtracks: int = 0
    relaxation_level: int = 0
    solver_restarts: int = 0
    repair_passes: int = 0
    ornaments_reverted: int = 0
    ornaments_applied: int = 0
    elapsed_ms: float = 0.0
    budget_exhausted: bool = False

    def as_dict(self) -> Dict[str, object]:
        return {
            "slots": self.slots,
            "candidate_sets_built": self.candidate_sets_built,
            "candidates_considered": self.candidates_considered,
            "nodes_visited": self.nodes_visited,
            "backtracks": self.backtracks,
            "relaxation_level": self.relaxation_level,
            "solver_restarts": self.solver_restarts,
            "repair_passes": self.repair_passes,
            "ornaments_applied": self.ornaments_applied,
            "ornaments_reverted": self.ornaments_reverted,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "budget_exhausted": self.budget_exhausted,
        }


@dataclass
class Composition:
    """A finished composition and everything that explains it."""

    config: GenesisConfig
    analysis: SemanticAnalysis
    plan: HarmonicPlan
    frame: MusicalFrame
    profile: ConstraintProfile
    provenance: Provenance
    structural: List[Sonority]
    rendered: List[Sonority]
    events: Dict[Voice, List[NoteEvent]]
    validation: ValidationReport
    stats: SearchStats

    @property
    def total_ql(self) -> float:
        return self.plan.total_ql

    @property
    def duration_seconds(self) -> float:
        return self.total_ql * 60.0 / self.config.tempo

    def voice_payload(self) -> List[Dict[str, object]]:
        return [
            {
                "voice": voice.value,
                "instrument": self.config.instrumentation[voice.value],
                "instrument_name": INSTRUMENTS[
                    self.config.instrumentation[voice.value]
                ]["name"],
                "range": {
                    "low": self.frame.ranges[voice].low,
                    "high": self.frame.ranges[voice].high,
                },
                "event_count": len(self.events[voice]),
                "events": [event.as_dict() for event in self.events[voice]],
            }
            for voice in (Voice.SOPRANO, Voice.ALTO, Voice.TENOR, Voice.BASS)
        ]


# --------------------------------------------------------------------------------------
# The voicing solver
# --------------------------------------------------------------------------------------

#: Softmax temperature converting a candidate's penalty into a selection weight.  Low
#: values make the engine greedy; high values make it wander.  2.4 keeps every choice
#: musically defensible while letting different seeds genuinely diverge.
SELECTION_TEMPERATURE = 2.4


class VoicingSolver:
    """Fills the harmonic skeleton with complete SATB sonorities.

    Chronological backtracking over slots.  For each slot the solver enumerates complete
    four-note voicings with incremental pruning (range, crossing, spacing, melodic
    limits, and pairwise parallel checks the moment both members of a pair are
    assigned), scores the survivors with the active :class:`ConstraintProfile`, and
    visits them in a seeded weighted order.  Exhausting a slot's candidates backtracks
    into the previous slot's next-best voicing.  Every loop is bounded.
    """

    def __init__(
        self,
        plan: HarmonicPlan,
        frame: MusicalFrame,
        profile: ConstraintProfile,
        config: GenesisConfig,
        stream: SeedStream,
        budget: SearchBudget,
        stats: SearchStats,
    ) -> None:
        self.plan = plan
        self.frame = frame
        self.profile = profile
        self.config = config
        self.stream = stream
        self.budget = budget
        self.stats = stats
        self._pools: Dict[Tuple[int, Voice], Tuple[int, ...]] = {}
        self._enumeration_cache: Dict[Tuple[int, Optional[Tuple[int, ...]], int],
                                     List[Tuple[int, int, int, int]]] = {}

    # -- pitch pools -------------------------------------------------------------
    def _pool(self, slot: HarmonicSlot, voice: Voice) -> Tuple[int, ...]:
        key = (slot.index, voice)
        cached = self._pools.get(key)
        if cached is not None:
            return cached
        vr = self.frame.ranges[voice]
        pcs = slot.bass_pcs if voice is Voice.BASS else tuple(slot.triad.pcs)
        pool = tuple(pitches_in_range(pcs, vr.low, vr.high))
        self._pools[key] = pool
        return pool

    # -- enumeration -------------------------------------------------------------
    def _enumerate(
        self, slot: HarmonicSlot, previous: Optional[Sonority], relaxation: int
    ) -> List[Tuple[int, int, int, int]]:
        """Complete voicings for *slot*, pruned as early as possible."""
        cache_key = (
            slot.index, previous.pitches if previous is not None else None, relaxation
        )
        cached = self._enumeration_cache.get(cache_key)
        if cached is not None:
            return cached
        heretical = self.profile.allows_chromatic_harmony
        max_gap_upper = 12 if relaxation == 0 else 16
        crossing_slack = 7 if heretical else 0
        results: List[Tuple[int, int, int, int]] = []
        nodes = 0
        node_cap = self.budget.max_nodes_per_slot
        candidate_cap = self.budget.max_candidates_per_slot

        lenient = False

        def melodic_ok(voice: Voice, pitch: int) -> bool:
            if previous is None:
                return True
            move = pitch - previous.pitch(voice)
            size = abs(move)
            ceiling = law.MAX_LEAP[voice] + (5 if heretical else 0)
            if lenient:
                return size <= ceiling + 6
            if size > ceiling:
                return False
            if not heretical and relaxation == 0 and size in (6, 10, 11):
                return False
            return True

        def parallel_free(assigned: List[int], voice_i: int, pitch: int) -> bool:
            """Reject a partial assignment that already forms a parallel perfect."""
            if previous is None or heretical:
                return True
            for j, other in enumerate(assigned):
                pl, pu = previous.pitches[j], previous.pitches[voice_i]
                cl, cu = other, pitch
                iv_prev = (max(pl, pu) - min(pl, pu)) % 12
                iv_cur = (max(cl, cu) - min(cl, cu)) % 12
                if iv_prev != iv_cur or iv_cur not in (0, 7):
                    continue
                if cl == pl or cu == pu:
                    continue
                if ((cl - pl) > 0) == ((cu - pu) > 0):
                    return False
            return True

        pools = [self._pool(slot, voice) for voice in VOICE_ORDER]
        if any(not pool for pool in pools):
            return []

        def descend(level: int, assigned: List[int]) -> None:
            nonlocal nodes
            if len(results) >= candidate_cap or nodes >= node_cap:
                return
            if level == 4:
                if self._doubling_ok(slot, assigned, relaxation):
                    results.append((assigned[0], assigned[1], assigned[2], assigned[3]))
                return
            voice = VOICE_ORDER[level]
            floor = assigned[-1] - crossing_slack if assigned else None
            for pitch in pools[level]:
                nodes += 1
                if nodes >= node_cap:
                    return
                if floor is not None and pitch < floor:
                    continue
                if level >= 2 and pitch - assigned[-1] > max_gap_upper:
                    continue
                if level == 1 and pitch - assigned[0] > 26:
                    continue
                if not melodic_ok(voice, pitch):
                    continue
                if not parallel_free(assigned, level, pitch):
                    continue
                assigned.append(pitch)
                descend(level + 1, assigned)
                assigned.pop()
                if len(results) >= candidate_cap:
                    return

        descend(0, [])
        if not results and previous is not None:
            # The melodic filter, not the harmony, emptied this slot: a bass forced onto
            # a root a tritone away, for instance.  Re-enumerate without it rather than
            # dead-ending -- the offending interval then survives as a scored penalty the
            # search can weigh, which is what a bounded relaxation is for.
            lenient = True
            nodes = 0
            descend(0, [])
        self.stats.nodes_visited += nodes
        self.stats.candidate_sets_built += 1
        self._enumeration_cache[cache_key] = results
        return results

    def _doubling_ok(
        self, slot: HarmonicSlot, pitches: Sequence[int], relaxation: int
    ) -> bool:
        if self.profile.allows_chromatic_harmony:
            return True
        classes = [p % 12 for p in pitches]
        if relaxation == 0 and not slot.triad.pcs.issubset(set(classes)):
            return False
        lt = slot.leading_tone_pc
        if lt is not None and relaxation <= 1 and classes.count(lt) > 1:
            return False
        return True

    # -- scoring -----------------------------------------------------------------
    def _style_score(
        self, slot: HarmonicSlot, pitches: Tuple[int, ...], previous: Optional[Sonority]
    ) -> float:
        """Semantic shaping the constraint profile knows nothing about."""
        score = 0.0
        soprano = pitches[voice_index(Voice.SOPRANO)]
        bias = self.config.contour_bias
        if previous is not None and abs(bias) > 0.05:
            move = soprano - previous.pitch(Voice.SOPRANO)
            if move != 0:
                aligned = (move > 0) == (bias > 0)
                score -= 1.8 * abs(bias) * (1.0 if aligned else -1.0)
            if pitches == previous.pitches:
                score += 2.5  # a literal repetition of the whole sonority is inert
        if slot.is_final:
            if soprano % 12 == self.plan.tonic_pc:
                score -= 7.0 * self.config.cadence_strength
            elif soprano % 12 == slot.triad.third_pc:
                score -= 2.0 * self.config.cadence_strength
            score -= 1.2 * self.config.cadence_strength * (
                1.0 if pitches[0] % 12 == self.plan.tonic_pc else 0.0
            )
        if slot.is_cadential and previous is not None:
            score -= 1.0 * self.config.cadence_strength
        return score

    def _score(
        self,
        slot: HarmonicSlot,
        pitches: Tuple[int, int, int, int],
        previous: Optional[Sonority],
        before: Optional[Sonority],
        history: Dict[Voice, Tuple[int, ...]],
        relaxation: int,
    ) -> Tuple[float, Sonority, bool]:
        sonority = self._sonority(slot, pitches)
        ctx = MomentContext(
            current=sonority, previous=previous, before_previous=before,
            history=history, is_last=slot.is_final,
        )
        result = law.evaluate_moment(ctx, self.frame, self.profile, relaxation)
        total = result.penalty + self._style_score(slot, pitches, previous)
        return total, sonority, result.feasible

    def _sonority(
        self, slot: HarmonicSlot, pitches: Tuple[int, int, int, int]
    ) -> Sonority:
        return Sonority(
            offset=slot.offset,
            pitches=pitches,
            chord_pcs=slot.triad.pcs,
            root_pc=slot.triad.root_pc,
            third_pc=slot.triad.third_pc,
            leading_tone_pc=slot.leading_tone_pc,
            slot_index=slot.index,
            strong=slot.timing.strong,
            is_cadential=slot.is_cadential,
            is_final=slot.is_final,
        )

    def _ordered(
        self,
        slot: HarmonicSlot,
        previous: Optional[Sonority],
        before: Optional[Sonority],
        history: Dict[Voice, Tuple[int, ...]],
        relaxation: int,
    ) -> List[Sonority]:
        raw = self._enumerate(slot, previous, relaxation)
        self.stats.candidates_considered += len(raw)
        scored: List[Tuple[float, Sonority]] = []
        for pitches in raw:
            penalty, sonority, feasible = self._score(
                slot, pitches, previous, before, history, relaxation
            )
            if feasible:
                scored.append((penalty, sonority))
        if not scored:
            return []
        best = min(penalty for penalty, _ in scored)
        weights = [
            math.exp(-min(40.0, (penalty - best) / SELECTION_TEMPERATURE))
            for penalty, _ in scored
        ]
        picker = self.stream.derive("slot", slot.index, relaxation)
        return picker.weighted_order([s for _, s in scored], weights)

    # -- driver ------------------------------------------------------------------
    def solve(self, relaxation: int) -> Optional[List[Sonority]]:
        slots = self.plan.slots
        count = len(slots)
        orders: List[Optional[List[Sonority]]] = [None] * count
        cursor: List[int] = [0] * count
        chosen: List[Optional[Sonority]] = [None] * count
        history: List[Dict[Voice, Tuple[int, ...]]] = [
            {v: () for v in VOICE_ORDER} for _ in range(count)
        ]
        index = 0
        backtracks = 0

        while 0 <= index < count:
            if orders[index] is None:
                previous = chosen[index - 1] if index >= 1 else None
                before = chosen[index - 2] if index >= 2 else None
                if index == 0:
                    history[0] = {v: () for v in VOICE_ORDER}
                else:
                    history[index] = {
                        v: tuple(
                            son.pitch(v) for son in chosen[:index] if son is not None
                        )[-6:]
                        for v in VOICE_ORDER
                    }
                orders[index] = self._ordered(
                    slots[index], previous, before, history[index], relaxation
                )
                cursor[index] = 0
            options = orders[index]
            assert options is not None
            if cursor[index] >= len(options):
                orders[index] = None
                chosen[index] = None
                index -= 1
                backtracks += 1
                self.stats.backtracks = backtracks
                if backtracks > self.budget.max_backtracks:
                    self.stats.budget_exhausted = True
                    return None
                if index >= 0:
                    cursor[index] += 1
                continue
            chosen[index] = options[cursor[index]]
            index += 1

        self.stats.backtracks = backtracks
        if index < 0:
            # Backtracking walked off the front of the piece: the search space is
            # genuinely exhausted at this strictness.  Report failure rather than
            # handing back the partial assignment left in ``chosen``.
            self.stats.budget_exhausted = True
            return None
        solved = [son for son in chosen if son is not None]
        if len(solved) != count:  # pragma: no cover - defensive
            self.stats.budget_exhausted = True
            return None
        return solved


# --------------------------------------------------------------------------------------
# Diminution
# --------------------------------------------------------------------------------------

#: One fragment of a voice's surface: pitch, notated length, and the role it plays.
Figure = Tuple[int, float, str]


class DiminutionEngine:
    """Adds the rhythmic and melodic surface over the structural backbone."""

    def __init__(
        self,
        plan: HarmonicPlan,
        frame: MusicalFrame,
        profile: ConstraintProfile,
        config: GenesisConfig,
        stream: SeedStream,
        stats: SearchStats,
    ) -> None:
        self.plan = plan
        self.frame = frame
        self.profile = profile
        self.config = config
        self.stream = stream
        self.stats = stats
        self._scale_cache: Dict[Voice, Tuple[int, ...]] = {}

    def _scale(self, voice: Voice) -> Tuple[int, ...]:
        cached = self._scale_cache.get(voice)
        if cached is None:
            vr = self.frame.ranges[voice]
            pcs = set(self.frame.scale_pcs) | set(self.frame.ficta_pcs)
            cached = tuple(pitches_in_range(pcs, vr.low, vr.high))
            self._scale_cache[voice] = cached
        return cached

    def _step_from(self, voice: Voice, pitch: int, direction: int) -> Optional[int]:
        """The next scale pitch above (+1) or below (-1) *pitch*, if it exists."""
        scale = self._scale(voice)
        if direction > 0:
            for p in scale:
                if p > pitch:
                    return p
            return None
        for p in reversed(scale):
            if p < pitch:
                return p
        return None

    def _between(self, voice: Voice, low: int, high: int) -> Optional[int]:
        for p in self._scale(voice):
            if low < p < high:
                return p
        return None

    def build(
        self, structural: Sequence[Sonority]
    ) -> Dict[Tuple[Voice, int], List[Figure]]:
        """Choose a surface figure for every (voice, slot) pair."""
        slots = self.plan.slots
        figures: Dict[Tuple[Voice, int], List[Figure]] = {}
        for i, slot in enumerate(slots):
            active = 0
            for voice in VOICE_ORDER:
                pitch = structural[i].pitch(voice)
                plain: List[Figure] = [(pitch, slot.duration, law.ROLE_STRUCTURAL)]
                figures[(voice, slot.index)] = plain
                if slot.is_final:
                    continue
                if slot.is_cadential and (
                    slot.leading_tone_pc is not None
                    and pitch % 12 == slot.leading_tone_pc
                ):
                    # Never decorate the voice that must carry the leading tone into the
                    # close; the cadence has to arrive clean.
                    continue
                probability = diminution_probability(
                    voice, self.config.density, slot.timing, active_voices=active
                )
                picker = self.stream.derive("dim", voice.value, slot.index)
                if not picker.chance(probability):
                    continue
                previous = structural[i - 1] if i >= 1 else None
                following = structural[i + 1] if i + 1 < len(structural) else None
                figure = self._figure(
                    voice, slot, pitch, previous, following, picker
                )
                if figure is not None and len(figure) > 1:
                    figures[(voice, slot.index)] = figure
                    active += 1
                    self.stats.ornaments_applied += 1
        return figures

    def _figure(
        self,
        voice: Voice,
        slot: HarmonicSlot,
        pitch: int,
        previous: Optional[Sonority],
        following: Optional[Sonority],
        picker: SeedStream,
    ) -> Optional[List[Figure]]:
        half = slot.duration / 2.0
        if half < MIN_EVENT_QL:
            return None
        vr = self.frame.ranges[voice]
        options: List[Tuple[str, List[Figure], float]] = []

        # -- suspension: hold the previous pitch a step above across a strong beat ----
        if previous is not None and slot.timing.strong:
            held = previous.pitch(voice)
            if 1 <= held - pitch <= 2 and held % 12 in previous.chord_pcs:
                options.append((
                    "suspension",
                    [(held, half, law.ROLE_SUSPENSION), (pitch, half, law.ROLE_STRUCTURAL)],
                    2.4,
                ))

        # -- passing tone: fill a melodic third toward the next structural pitch ------
        if following is not None:
            target = following.pitch(voice)
            gap = target - pitch
            if 3 <= abs(gap) <= 4:
                mid = self._between(voice, min(pitch, target), max(pitch, target))
                if mid is not None:
                    options.append((
                        "passing",
                        [(pitch, half, law.ROLE_STRUCTURAL),
                         (mid, half, law.ROLE_PASSING)],
                        3.0,
                    ))
            elif gap == 0:
                direction = 1 if picker.chance(0.5) else -1
                neighbour = self._step_from(voice, pitch, direction)
                if neighbour is not None and vr.contains(neighbour):
                    options.append((
                        "neighbour",
                        [(pitch, half, law.ROLE_STRUCTURAL),
                         (neighbour, half, law.ROLE_NEIGHBOUR)],
                        2.2,
                    ))
            elif 1 <= abs(gap) <= 2 and slot.duration >= 4 * MIN_EVENT_QL:
                head = slot.duration * 0.75
                tail = slot.duration - head
                options.append((
                    "anticipation",
                    [(pitch, head, law.ROLE_STRUCTURAL),
                     (target, tail, law.ROLE_ANTICIPATION)],
                    1.3,
                ))

        # -- chord skip: a consonant arpeggiation, especially useful in the bass ------
        skips = [
            p for p in pitches_in_range(slot.triad.pcs, vr.low, vr.high)
            if p != pitch and abs(p - pitch) <= 9
        ]
        if skips:
            other = picker.derive("skip").choice(skips)
            options.append((
                "chord_skip",
                [(pitch, half, law.ROLE_STRUCTURAL), (other, half, law.ROLE_STRUCTURAL)],
                1.6 if voice is Voice.BASS else 1.0,
            ))

        # -- Modus Haereticus: figures the Orthodox grammar has no room for -----------
        if self.profile.transgressive_ornament_rate > 0.0:
            rate = self.profile.transgressive_ornament_rate
            chromatic = pitch + (1 if picker.derive("chrom").chance(0.5) else -1)
            if vr.contains(chromatic):
                options.append((
                    "chromatic",
                    [(pitch, half, law.ROLE_STRUCTURAL),
                     (chromatic, half, law.ROLE_CHROMATIC)],
                    4.0 * rate,
                ))
            stab = pitch + 6 if vr.contains(pitch + 6) else pitch - 6
            if vr.contains(stab):
                options.append((
                    "tritone_stab",
                    [(pitch, half, law.ROLE_STRUCTURAL),
                     (stab, half, law.ROLE_CHROMATIC)],
                    3.6 * rate,
                ))
            if following is not None:
                escape = self._step_from(voice, pitch, 1 if picker.chance(0.5) else -1)
                if escape is not None and vr.contains(escape):
                    options.append((
                        "escape",
                        [(pitch, half, law.ROLE_STRUCTURAL),
                         (escape, half, law.ROLE_ESCAPE)],
                        3.0 * rate,
                    ))
            displaced = pitch + 12 if vr.contains(pitch + 12) else pitch - 12
            if vr.contains(displaced):
                options.append((
                    "displacement",
                    [(pitch, half, law.ROLE_STRUCTURAL),
                     (displaced, half, law.ROLE_DISPLACED)],
                    2.2 * rate,
                ))

        if not options:
            return None
        chosen = picker.derive("shape").weighted_choice(
            [figure for _, figure, _ in options],
            [weight for _, _, weight in options],
        )
        return chosen


# --------------------------------------------------------------------------------------
# Rendering, repair and validation
# --------------------------------------------------------------------------------------


class Renderer:
    """Turns figures into events, samples the grid, and repairs hard violations."""

    def __init__(
        self,
        plan: HarmonicPlan,
        frame: MusicalFrame,
        profile: ConstraintProfile,
        config: GenesisConfig,
        stream: SeedStream,
        stats: SearchStats,
    ) -> None:
        self.plan = plan
        self.frame = frame
        self.profile = profile
        self.config = config
        self.stream = stream
        self.stats = stats
        self.speller = Speller(config.tonic, config.mode)
        self._events_cache: Dict[Voice, List[NoteEvent]] = {}

    # -- events ------------------------------------------------------------------
    def events(
        self,
        structural: Sequence[Sonority],
        figures: Dict[Tuple[Voice, int], List[Figure]],
    ) -> Dict[Voice, List[NoteEvent]]:
        out: Dict[Voice, List[NoteEvent]] = {v: [] for v in VOICE_ORDER}
        for voice in VOICE_ORDER:
            for i, slot in enumerate(self.plan.slots):
                offset = slot.offset
                for pitch, duration, role in figures[(voice, slot.index)]:
                    previous = out[voice][-1] if out[voice] else None
                    if (
                        role == law.ROLE_SUSPENSION
                        and previous is not None
                        and previous.midi == pitch
                        and abs(previous.offset + previous.duration - offset) < 1e-6
                    ):
                        # A true suspension is tied over, not re-attacked.
                        out[voice][-1] = self._extend(previous, duration)
                    else:
                        out[voice].append(self._event(
                            voice, pitch, offset, duration, role, slot, structural[i]
                        ))
                    offset += duration
        return out

    def _extend(self, event: NoteEvent, extra: float) -> NoteEvent:
        duration = event.duration + extra
        return NoteEvent(
            voice=event.voice, midi=event.midi, pitch=event.pitch, offset=event.offset,
            duration=duration, sounding_duration=round(duration * self.config.gate, 6),
            velocity=event.velocity, role=law.ROLE_SUSPENSION,
            slot_index=event.slot_index, measure=event.measure,
        )

    def _event(
        self,
        voice: Voice,
        pitch: int,
        offset: float,
        duration: float,
        role: str,
        slot: HarmonicSlot,
        sonority: Sonority,
    ) -> NoteEvent:
        return NoteEvent(
            voice=voice,
            midi=pitch,
            pitch=self.speller.name(pitch),
            offset=round(offset, 6),
            duration=round(duration, 6),
            sounding_duration=round(duration * self.config.gate, 6),
            velocity=self._velocity(voice, offset, slot, role),
            role=role,
            slot_index=slot.index,
            measure=slot.timing.measure,
        )

    #: Per-voice dynamic offset -- the outer voices carry the line, the inner ones fill.
    _VOICE_DYNAMIC: Dict[Voice, int] = {
        Voice.SOPRANO: 6, Voice.ALTO: -3, Voice.TENOR: -2, Voice.BASS: 3,
    }
    _ROLE_DYNAMIC: Dict[str, int] = {
        law.ROLE_PASSING: -7, law.ROLE_NEIGHBOUR: -6, law.ROLE_ANTICIPATION: -5,
        law.ROLE_SUSPENSION: 5, law.ROLE_ESCAPE: -3, law.ROLE_CHROMATIC: 2,
        law.ROLE_DISPLACED: 4,
    }

    def _velocity(
        self, voice: Voice, offset: float, slot: HarmonicSlot, role: str
    ) -> int:
        measure_position = (offset - slot.timing.offset) + slot.timing.beat_offset
        meter = self.plan.meter
        on_downbeat = abs(measure_position % meter.measure_ql) < 1e-6
        weight = 1.0 if on_downbeat else slot.timing.metrical_weight
        value = 58.0 + 24.0 * weight
        value += self._VOICE_DYNAMIC[voice]
        value += self._ROLE_DYNAMIC.get(role, 0)
        value += 20.0 * (self.config.intensity - 0.5)
        value += 8.0 * math.sin(math.pi * slot.position_in_phrase)
        if slot.is_final or slot.is_cadential:
            value += 4.0
        value += self.stream.derive("vel", voice.value, round(offset, 4)).jitter(3.0)
        return int(max(28, min(115, round(value))))

    # -- sampling ----------------------------------------------------------------
    def grid(
        self, events: Dict[Voice, List[NoteEvent]], structural: Sequence[Sonority]
    ) -> List[Sonority]:
        """Sample every attack point in the piece into a four-voice sonority."""
        points = sorted({
            round(event.offset, 6)
            for voice_events in events.values()
            for event in voice_events
        })
        slots = self.plan.slots
        by_slot = {slot.index: (slot, structural[i]) for i, slot in enumerate(slots)}
        cursors = {v: 0 for v in VOICE_ORDER}
        grid: List[Sonority] = []
        for point in points:
            pitches: List[int] = []
            roles: List[str] = []
            slot_index = 0
            for voice in VOICE_ORDER:
                seq = events[voice]
                idx = cursors[voice]
                while idx + 1 < len(seq) and seq[idx + 1].offset <= point + 1e-9:
                    idx += 1
                cursors[voice] = idx
                event = seq[idx]
                pitches.append(event.midi)
                roles.append(event.role)
                slot_index = max(slot_index, event.slot_index)
            slot, _ = by_slot[self._slot_at(point)]
            grid.append(Sonority(
                offset=point,
                pitches=(pitches[0], pitches[1], pitches[2], pitches[3]),
                roles=(roles[0], roles[1], roles[2], roles[3]),
                chord_pcs=slot.triad.pcs,
                root_pc=slot.triad.root_pc,
                third_pc=slot.triad.third_pc,
                leading_tone_pc=slot.leading_tone_pc,
                slot_index=slot.index,
                strong=abs(point - slot.offset) < 1e-9 and slot.timing.strong,
                is_cadential=slot.is_cadential and abs(point - slot.offset) < 1e-9,
                is_final=slot.is_final and abs(point - slot.offset) < 1e-9,
            ))
        return grid

    def _slot_at(self, offset: float) -> int:
        chosen = self.plan.slots[0].index
        for slot in self.plan.slots:
            if slot.offset <= offset + 1e-9:
                chosen = slot.index
            else:
                break
        return chosen

    # -- repair ------------------------------------------------------------------
    def repair(
        self,
        structural: Sequence[Sonority],
        figures: Dict[Tuple[Voice, int], List[Figure]],
        relaxation: int,
    ) -> Tuple[Dict[Voice, List[NoteEvent]], List[Sonority]]:
        """Revert any ornament that introduced a hard violation on the rendered grid.

        The structural backbone was proved sound during the search; only the diminution
        layer can add new hard violations, and only ornamental figures are reverted, so
        this loop strictly decreases the number of ornaments and terminates.
        """
        for attempt in range(self.stats.repair_passes, 100):
            events = self.events(structural, figures)
            grid = self.grid(events, structural)
            self._events_cache = events
            offenders = self._hard_offenders(grid, relaxation)
            self.stats.repair_passes = attempt + 1
            if not offenders:
                return events, grid
            reverted = False
            undone: set = set()
            for candidates in offenders:
                # One finding, one revert: undo the nearest ornament that could have
                # caused it and let the next pass re-judge, rather than stripping the
                # surface wholesale.
                for key in candidates:
                    if key in undone:
                        reverted = True
                        break
                    figure = figures.get(key)
                    if figure is None or len(figure) <= 1:
                        continue
                    voice, slot_index = key
                    position = self._structural_index(slot_index)
                    figures[key] = [(
                        structural[position].pitch(voice),
                        self.plan.slots[position].duration,
                        law.ROLE_STRUCTURAL,
                    )]
                    self.stats.ornaments_reverted += 1
                    undone.add(key)
                    reverted = True
                    break
            if not reverted:
                # Nothing ornamental left to undo; the remaining findings belong to the
                # backbone and are reported honestly by the validator.
                return events, grid
            if self.stats.repair_passes >= 100:  # pragma: no cover - guard
                break
        events = self.events(structural, figures)
        return events, self.grid(events, structural)

    def _structural_index(self, slot_index: int) -> int:
        for i, slot in enumerate(self.plan.slots):
            if slot.index == slot_index:
                return i
        raise KeyError(slot_index)  # pragma: no cover - slots are dense

    def _hard_offenders(
        self, grid: Sequence[Sonority], relaxation: int
    ) -> List[List[Tuple[Voice, int]]]:
        """Ornaments that could be responsible for each hard violation.

        Returns one candidate list per finding, nearest suspect first: the slot the
        violation sounds in, then the slot before it (an ornament's *approach* is as able
        to break a law as its arrival).
        """
        offenders: List[List[Tuple[Voice, int]]] = []
        seen: set = set()
        history: Dict[Voice, List[int]] = {v: [] for v in VOICE_ORDER}
        for i, sonority in enumerate(grid):
            ctx = MomentContext(
                current=sonority,
                previous=grid[i - 1] if i >= 1 else None,
                before_previous=grid[i - 2] if i >= 2 else None,
                following=grid[i + 1] if i + 1 < len(grid) else None,
                history={v: tuple(history[v]) for v in VOICE_ORDER},
                is_last=i == len(grid) - 1,
            )
            for finding in law.collect_findings(ctx, self.frame, law.GRID_RULES):
                if not self.profile.policy(finding.rule).is_hard(relaxation):
                    continue
                for name in finding.voices:
                    voice = Voice(name)
                    candidates = [
                        (voice, index)
                        for index in (sonority.slot_index, self._previous_slot(sonority))
                        if index is not None
                    ]
                    key = (voice, finding.rule, round(finding.position, 4))
                    if candidates and key not in seen:
                        seen.add(key)
                        offenders.append(candidates)
            for voice in VOICE_ORDER:
                history[voice].append(sonority.pitch(voice))

        for voice, notes in self._lines_from_events(self._events_cache).items():
            for finding in law.line_findings(voice, notes):
                if not self.profile.policy(finding.rule).is_hard(relaxation):
                    continue
                index = self._slot_at(finding.position)
                candidates = [
                    (voice, slot_index)
                    for slot_index in (index, self._previous_slot_index(index))
                    if slot_index is not None
                ]
                key = (voice, finding.rule, round(finding.position, 4))
                if candidates and key not in seen:
                    seen.add(key)
                    offenders.append(candidates)
        return offenders

    @staticmethod
    def _lines_from_events(
        events: Dict[Voice, List[NoteEvent]],
    ) -> Dict[Voice, List[Tuple[int, float, str]]]:
        """Each voice's own sequence of attacked notes, with the role of each."""
        return {
            voice: [(e.midi, e.offset, e.role) for e in voice_events]
            for voice, voice_events in events.items()
        }

    def _previous_slot(self, sonority: Sonority) -> Optional[int]:
        return self._previous_slot_index(sonority.slot_index)

    def _previous_slot_index(self, slot_index: int) -> Optional[int]:
        indices = [slot.index for slot in self.plan.slots]
        position = indices.index(slot_index)
        return indices[position - 1] if position > 0 else None


# --------------------------------------------------------------------------------------
# The engine
# --------------------------------------------------------------------------------------


class KircherEngine:
    """The public entry point.  Stateless; safe to share across requests."""

    def __init__(
        self,
        analyzer: Optional[SemanticAnalyzer] = None,
        budget: Optional[SearchBudget] = None,
    ) -> None:
        self.analyzer = analyzer or SemanticAnalyzer()
        self.budget = budget or SearchBudget()

    # -- configuration -----------------------------------------------------------
    def configure(
        self,
        *,
        text: str,
        mode: Optional[str] = None,
        tonic: Optional[str] = None,
        tempo: Optional[int] = None,
        meter: Optional[str] = None,
        measures: int = 8,
        phrase_measures: Optional[int] = None,
        density: Optional[float] = None,
        heretical: Optional[bool] = None,
    ) -> Tuple[GenesisConfig, SemanticAnalysis]:
        """Merge the semantic suggestion with explicit user overrides."""
        analysis = self.analyzer.analyze(text, default_measures=measures)
        suggestion = analysis.suggestion

        chosen_mode = ModeName(mode) if mode else suggestion.mode
        chosen_tonic = normalize_note_name(tonic) if tonic else suggestion.tonic
        chosen_meter = meter or suggestion.meter
        spec = meter_spec(chosen_meter)  # validates, raises MeterError otherwise
        chosen_heretical = (
            suggestion.heretical if heretical is None else bool(heretical)
        )
        chosen_density = suggestion.density if density is None else float(density)
        chosen_phrase = phrase_measures or suggestion.phrase_measures
        articulation = suggestion.articulation
        config = GenesisConfig(
            text=text,
            mode=chosen_mode,
            tonic=chosen_tonic,
            tonic_pc=parse_note_name(chosen_tonic),
            tempo=int(tempo) if tempo else suggestion.tempo,
            meter=spec.symbol,
            measures=int(measures),
            phrase_measures=max(1, min(int(chosen_phrase), int(measures))),
            density=max(0.0, min(1.0, chosen_density)),
            register_shift=suggestion.register_shift,
            contour_bias=suggestion.contour_bias,
            cadence_strength=suggestion.cadence_strength,
            tension=suggestion.tension,
            heresy=suggestion.heresy,
            heretical=chosen_heretical,
            articulation=articulation,
            gate=ARTICULATIONS[articulation],
            intensity=max(0.0, min(1.0, 0.5 + 0.5 * analysis.axes.energy)),
            mood=mode_spec(chosen_mode).mood,
            ensemble=suggestion.ensemble,
            instrumentation=dict(suggestion.instrumentation),
        )
        return config, analysis

    # -- generation --------------------------------------------------------------
    def compose(
        self,
        *,
        text: str,
        seed: "int | str | None" = None,
        mode: Optional[str] = None,
        tonic: Optional[str] = None,
        tempo: Optional[int] = None,
        meter: Optional[str] = None,
        measures: int = 8,
        phrase_measures: Optional[int] = None,
        density: Optional[float] = None,
        heretical: Optional[bool] = None,
    ) -> Composition:
        started = time.perf_counter()
        config, analysis = self.configure(
            text=text, mode=mode, tonic=tonic, tempo=tempo, meter=meter,
            measures=measures, phrase_measures=phrase_measures, density=density,
            heretical=heretical,
        )
        profile = get_profile(config.heretical)
        config_fp = config.fingerprint()
        resolved_seed = coerce_seed(
            seed, fallback=(ENGINE_VERSION, profile.name, config_fp,
                            analysis.normalized_text)
        )
        root = SeedStream(resolved_seed, path=(ENGINE_VERSION, profile.name))

        plan = build_plan(
            tonic_pc=config.tonic_pc,
            mode=config.mode,
            meter=meter_spec(config.meter),
            measures=config.measures,
            density=config.density,
            cadence_strength=config.cadence_strength,
            phrase_measures=config.phrase_measures,
            heretical=config.heretical,
            stream=root.derive("harmony"),
        )
        ranges = {v: shifted_range(v, config.register_shift) for v in VOICE_ORDER}
        frame = MusicalFrame.build(
            config.tonic_pc, config.mode, ranges, ficta_pcs=plan.ficta_pcs
        )

        stats = SearchStats(slots=len(plan.slots))
        solver = VoicingSolver(
            plan, frame, profile, config, root.derive("voicing"), self.budget, stats
        )
        structural: Optional[List[Sonority]] = None
        for relaxation in range(self.budget.max_relaxation + 1):
            stats.relaxation_level = relaxation
            if relaxation:
                stats.solver_restarts += 1
            structural = solver.solve(relaxation)
            if structural is not None:
                stats.budget_exhausted = False
                break
        if structural is None:
            stats.elapsed_ms = (time.perf_counter() - started) * 1000.0
            raise GenerationError(
                "the voicing search exhausted its budget at every relaxation level",
                {
                    "config": config.as_dict(),
                    "progression": plan.progression(),
                    "search": stats.as_dict(),
                    "budget": self.budget.as_dict(),
                },
            )

        diminution = DiminutionEngine(
            plan, frame, profile, config, root.derive("diminution"), stats
        )
        figures = diminution.build(structural)
        renderer = Renderer(
            plan, frame, profile, config, root.derive("render"), stats
        )
        events, grid = renderer.repair(structural, figures, stats.relaxation_level)

        lines = {
            voice: [(event.midi, event.offset, event.role) for event in voice_events]
            for voice, voice_events in events.items()
        }
        report = validate(grid, frame, profile, lines=lines)
        self._append_phrase_findings(report, plan, grid, profile)
        stats.elapsed_ms = (time.perf_counter() - started) * 1000.0

        return Composition(
            config=config,
            analysis=analysis,
            plan=plan,
            frame=frame,
            profile=profile,
            provenance=Provenance(
                engine_version=ENGINE_VERSION,
                seed=resolved_seed,
                requested_seed=seed,
                law_profile=profile.name,
                config_fingerprint=config_fp,
            ),
            structural=structural,
            rendered=grid,
            events=events,
            validation=report,
            stats=stats,
        )

    @staticmethod
    def _append_phrase_findings(
        report: ValidationReport,
        plan: HarmonicPlan,
        grid: Sequence[Sonority],
        profile: ConstraintProfile,
    ) -> None:
        """Phrase-scope checks that no single moment can see.

        Currently one: Modus Haereticus expects every phrase to expose at least one
        tritone.  A phrase that does not is a failure *of the Heretical grammar*, and is
        reported as such -- the inverse of an Orthodox parallel fifth.
        """
        if profile.policy(Rules.PHRASE_LACKS_TRITONE).weight <= 0.0:
            return
        for phrase in plan.phrases:
            found = False
            for sonority in grid:
                if not (phrase.first_slot <= sonority.slot_index <= phrase.last_slot):
                    continue
                pitches = sonority.pitches
                for i in range(4):
                    for j in range(i + 1, 4):
                        if (max(pitches[i], pitches[j])
                                - min(pitches[i], pitches[j])) % 12 == 6:
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            if not found:
                report.violations.append(RuleViolation(
                    rule=Rules.PHRASE_LACKS_TRITONE,
                    severity=Severity.WARNING,
                    voices=tuple(v.value for v in VOICE_ORDER),
                    position=float(plan.slots[phrase.first_slot].offset),
                    detail=f"phrase {phrase.index} exposes no tritone",
                    penalty=profile.policy(Rules.PHRASE_LACKS_TRITONE).weight,
                    intended=False,
                ))


#: Shared engine instance for the API layer.
ENGINE = KircherEngine()


__all__ = [
    "ENGINE_NAME", "ENGINE_VERSION", "GenerationError", "SearchBudget",
    "GenesisConfig", "NoteEvent", "SearchStats", "Composition", "VoicingSolver",
    "DiminutionEngine", "Renderer", "KircherEngine", "ENGINE",
]
