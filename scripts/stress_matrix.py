#!/usr/bin/env python3
"""A reproducible, checked-in stress instrument for the generative engine.

A previous Phase-1 report claimed a sweep of ~1,764 generations with zero failures and
no unintended violations, but that evidence was never checked into the repository -- so
nobody could reproduce it, inspect exactly what was exercised, or replay a failure if one
had occurred. This script replaces that ad-hoc claim with something concrete:

* the matrix itself (:func:`build_matrix`) is a **pure function** of a profile name --
  same profile in, byte-identical list of cases out, every time, on any machine;
* every case is addressable by a stable ``case_id`` and can be replayed in isolation with
  ``--replay <case-id>``;
* the result is a structured report (see :class:`StressReport`) written as JSON, plus a
  concise terminal summary;
* exit status is 0 only when every correctness condition below actually held -- not
  merely when nothing raised.

Two profiles:

``smoke``
    A one-factor-at-a-time coverage design: a baseline case, then one dimension varied
    at a time (mode, meter, profile, length, seed, density, tension text), plus a small
    semantic-derived-path sample and one deliberately-failing case. This touches every
    dimension at least once without crossing all of them, so it stays fast enough for a
    normal development loop (tens of cases, single-digit seconds).

``full``
    The full cross product of all 7 modes x all 6 meters x both law profiles x 3 length
    classes x 7 seeds (1,764 cases -- deliberately the same scale as the earlier claim),
    plus an additive sample of the semantic-derived configuration path and two
    deliberately-failing cases. Intended for release verification, not routine CI.

Run it directly:

    python scripts/stress_matrix.py --profile smoke
    python scripts/stress_matrix.py --profile full --out artifacts/stress/latest.json
    python scripts/stress_matrix.py --profile full \\
        --out artifacts/stress/stress-engine-1.3.0.json
    python scripts/stress_matrix.py --profile full --replay full-000512-dorian-3-4-...
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import statistics
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from constraints import Intent  # noqa: E402
from determinism import coerce_seed  # noqa: E402
from kircher_engine import (  # noqa: E402
    ENGINE_VERSION, GenerationError, KircherEngine, SearchBudget,
)
from midi_export import composition_to_base64  # noqa: E402
from rhythm import SUPPORTED_METERS  # noqa: E402
from theory import ModeName  # noqa: E402


def _load_independent_helpers():
    """Import the *independent* event-level checkers from ``tests/conftest.py``.

    These are the same functions the test suite uses to verify voice-crossing and
    parallel-fifth/octave invariants from the public event JSON alone, deliberately
    without going through ``constraints.validate`` a second time (see B9 mission,
    section 7: "Do not simply call the same production validator twice"). Loaded by
    file path under a private module name -- ``tests/`` has no ``__init__.py``, so it is
    not import-able as a package, and the project root already has an unrelated
    top-level ``conftest.py`` that a plain ``import conftest`` would collide with.
    """
    path = ROOT / "tests" / "conftest.py"
    spec = importlib.util.spec_from_file_location("_stress_matrix_test_helpers", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_helpers = _load_independent_helpers()

MODES: Tuple[str, ...] = tuple(m.value for m in ModeName)
METERS: Tuple[str, ...] = tuple(SUPPORTED_METERS)
PROFILES: Tuple[bool, ...] = (False, True)  # heretical? orthodox first, then heretical
LENGTH_MEASURES: Dict[str, int] = {"short": 4, "medium": 8, "long": 16}
LENGTH_CLASSES: Tuple[str, ...] = tuple(LENGTH_MEASURES)

#: Seeds used by the full cartesian core. Fixed values, not random -- the matrix must be
#: reproducible byte-for-byte from the profile name alone.
CORE_SEEDS: Tuple[int, ...] = (101, 202, 303, 404, 505, 606, 707)
#: Representative densities, aligned index-for-index with CORE_SEEDS so density coverage
#: comes for free from the seed dimension rather than multiplying the matrix by a
#: separate density axis.
CORE_DENSITIES: Tuple[float, ...] = (0.15, 0.3, 0.45, 0.5, 0.6, 0.75, 0.9)

#: Three texts chosen to make the semantic analyzer report low / neutral / high tension
#: (see semantics.py's lexicon) -- exercised as an explicit ``text`` axis rather than a
#: multiplicative dimension.
TENSION_TEXTS: Dict[str, str] = {
    "low": "a clear crystalline dawn of pure radiant light",
    "neutral": "a solemn procession through the vaulted cloister at dusk",
    "high": "a forbidden heretical abyss of blasphemous chromatic anguish",
}

#: Curated texts for the semantic-derived configuration path: mode, tonic, tempo, meter
#: and density are all left for the semantic analyzer to choose, so these are picked for
#: genuine lexical variety rather than to hit any specific mode.
SEMANTIC_TEXTS: Tuple[str, ...] = (
    "a sorrowful lament beneath a dying winter sun",
    "a triumphant fanfare at the gates of the city",
    "a forbidden heretical rite in the abyss below the crypt",
    "a joyful dawn procession through the orchard",
    "a void of ash and widowed silence",
    "a soaring ascent into pure crystal light",
    "an anguished dirge for the ruined watchtower",
    "a plain and unremarkable afternoon walk",
)

EXPLICIT_TONIC = "C"
EXPLICIT_TEMPO = 96

#: A budget tight enough that the search is expected to exhaust every relaxation level.
#: Used only by the deliberately-failing cases (section 4/5 of the B9 brief): a matrix
#: entry that expects ``GenerationError`` must say so explicitly rather than being
#: misread as an accidental failure.
STARVED_BUDGET = SearchBudget(
    max_candidates_per_slot=1, max_nodes_per_slot=1, max_backtracks=0,
    max_repair_passes=0, max_relaxation=0,
)


# ------------------------------------------------------------------------------------
# The matrix
# ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class MatrixCase:
    """One fully-specified ``KircherEngine.compose`` call, plus its expectation."""

    case_id: str
    group: str
    config_path: str  # "explicit" | "semantic"
    length_class: str
    tension_label: str
    text: str
    seed: "int | str"
    mode: Optional[str] = None
    tonic: Optional[str] = None
    tempo: Optional[int] = None
    meter: Optional[str] = None
    measures: int = 8
    phrase_measures: Optional[int] = None
    density: Optional[float] = None
    heretical: Optional[bool] = None
    expect: str = "success"  # "success" | "generation_error"
    starved_budget: bool = False

    def compose_kwargs(self) -> Dict[str, object]:
        return {
            "text": self.text, "seed": self.seed, "mode": self.mode,
            "tonic": self.tonic, "tempo": self.tempo, "meter": self.meter,
            "measures": self.measures, "phrase_measures": self.phrase_measures,
            "density": self.density, "heretical": self.heretical,
        }

    def engine(self) -> KircherEngine:
        if self.starved_budget:
            return KircherEngine(budget=STARVED_BUDGET)
        return KircherEngine()

    def as_dict(self) -> Dict[str, object]:
        return {
            "case_id": self.case_id, "group": self.group,
            "config_path": self.config_path, "length_class": self.length_class,
            "tension_label": self.tension_label, "expect": self.expect,
            **self.compose_kwargs(),
        }

    def replay_args(self) -> List[str]:
        """A CLI invocation that reproduces exactly this one case."""
        return ["python", "scripts/stress_matrix.py", "--replay", self.case_id,
                "--profile", self.case_id.split("-", 1)[0]]


def _explicit_case(
    case_id: str, group: str, *, mode: str, meter: str, heretical: bool,
    length_class: str, seed: "int | str", density: Optional[float],
    tension_label: str = "neutral", expect: str = "success",
    starved_budget: bool = False,
) -> MatrixCase:
    return MatrixCase(
        case_id=case_id, group=group, config_path="explicit",
        length_class=length_class, tension_label=tension_label,
        text=TENSION_TEXTS[tension_label], seed=seed, mode=mode,
        tonic=EXPLICIT_TONIC, tempo=EXPLICIT_TEMPO, meter=meter,
        measures=LENGTH_MEASURES[length_class], density=density,
        heretical=heretical, expect=expect, starved_budget=starved_budget,
    )


def _semantic_case(
    case_id: str, group: str, *, text: str, heretical: bool, seed: "int | str",
    length_class: str = "medium",
) -> MatrixCase:
    return MatrixCase(
        case_id=case_id, group=group, config_path="semantic",
        length_class=length_class, tension_label="derived", text=text, seed=seed,
        mode=None, tonic=None, tempo=None, meter=None,
        measures=LENGTH_MEASURES[length_class], density=None, heretical=heretical,
        expect="success",
    )


def _build_full_matrix() -> List[MatrixCase]:
    cases: List[MatrixCase] = []
    index = 0
    for mode in MODES:
        for meter in METERS:
            for heretical in PROFILES:
                for length_class in LENGTH_CLASSES:
                    for seed_pos, seed in enumerate(CORE_SEEDS):
                        density = CORE_DENSITIES[seed_pos]
                        tension_label = ("low", "neutral", "high")[
                            (MODES.index(mode) + METERS.index(meter)) % 3
                        ]
                        profile_tag = "hereticus" if heretical else "orthodox"
                        case_id = (
                            f"full-{index:05d}-{mode}-{meter.replace('/', '_')}-"
                            f"{profile_tag}-{length_class}-s{seed}"
                        )
                        cases.append(_explicit_case(
                            case_id, "core", mode=mode, meter=meter,
                            heretical=heretical, length_class=length_class, seed=seed,
                            density=density, tension_label=tension_label,
                        ))
                        index += 1
    for text_pos, text in enumerate(SEMANTIC_TEXTS):
        for heretical in PROFILES:
            for seed in (1, 2, 3):
                case_id = (
                    f"full-sem-{text_pos:02d}-"
                    f"{'hereticus' if heretical else 'orthodox'}-s{seed}"
                )
                cases.append(_semantic_case(
                    case_id, "semantic", text=text, heretical=heretical, seed=seed,
                ))
    cases.append(_explicit_case(
        "full-expect-fail-orthodox", "expected_failure", mode="phrygian", meter="4/4",
        heretical=False, length_class="long", seed=999, density=0.9,
        tension_label="high", expect="generation_error", starved_budget=True,
    ))
    cases.append(_explicit_case(
        "full-expect-fail-hereticus", "expected_failure", mode="locrian", meter="6/8",
        heretical=True, length_class="long", seed=998, density=0.9,
        tension_label="high", expect="generation_error", starved_budget=True,
    ))
    return cases


def _build_smoke_matrix() -> List[MatrixCase]:
    """A one-factor-at-a-time coverage design: touch every dimension, cross none.

    A baseline case anchors every axis; each coverage block then varies exactly one
    dimension while holding the rest at the baseline value. This is deliberately not a
    cartesian product -- it is designed to notice a mode/meter/profile-specific defect
    without paying for the 1000+ combinations that would catch nothing new.
    """
    baseline_mode, baseline_meter = MODES[0], METERS[0]
    cases: List[MatrixCase] = []

    def add(case_id_suffix: str, group: str, **overrides) -> None:
        params = dict(
            mode=baseline_mode, meter=baseline_meter, heretical=False,
            length_class="medium", seed=1, density=0.5, tension_label="neutral",
        )
        params.update(overrides)
        cases.append(_explicit_case(f"smoke-{case_id_suffix}", group, **params))

    add("baseline", "baseline")
    for mode in MODES:
        if mode == baseline_mode:
            continue
        add(f"mode-{mode}", "mode_coverage", mode=mode)
    for meter in METERS:
        if meter == baseline_meter:
            continue
        add(f"meter-{meter.replace('/', '_')}", "meter_coverage", meter=meter)
    add("profile-hereticus", "profile_coverage", heretical=True)
    for length_class in LENGTH_CLASSES:
        if length_class == "medium":
            continue
        add(f"length-{length_class}", "length_coverage", length_class=length_class)
    for seed in (2, 3, 2**60 + 42):
        add(f"seed-{seed}", "seed_coverage", seed=seed)
    for density in (0.2, 0.8):
        add(f"density-{density}", "density_coverage", density=density)
    for tension_label in ("low", "high"):
        add(f"tension-{tension_label}", "tension_coverage", tension_label=tension_label)

    for text_pos, text in enumerate(SEMANTIC_TEXTS[:4]):
        cases.append(_semantic_case(
            f"smoke-sem-{text_pos:02d}", "semantic", text=text,
            heretical=bool(text_pos % 2), seed=1,
        ))

    cases.append(_explicit_case(
        "smoke-expect-fail", "expected_failure", mode="phrygian", meter="4/4",
        heretical=False, length_class="long", seed=999, density=0.9,
        tension_label="high", expect="generation_error", starved_budget=True,
    ))
    return cases


def build_matrix(profile: str) -> List[MatrixCase]:
    """Build the matrix for *profile* ("smoke" or "full"). Pure: no randomness, no I/O,
    no wall-clock -- the same profile name always produces the same list of cases, in
    the same order, on any machine."""
    if profile == "smoke":
        return _build_smoke_matrix()
    if profile == "full":
        return _build_full_matrix()
    raise ValueError(f"unknown stress profile {profile!r}; expected 'smoke' or 'full'")


# ------------------------------------------------------------------------------------
# Independent invariants (section 7: do not just trust composition.validation)
# ------------------------------------------------------------------------------------


def _independent_invariants_hold(composition) -> Tuple[bool, List[str]]:
    """Re-derive structural invariants from the raw event JSON, using the same
    independent helpers the test suite trusts -- not by asking the production validator
    a second time.

    Four voices existing and staying in range are universal invariants (the Heretical
    law profile never suspends them). Voice crossing and parallel fifths/octaves are
    *not* checked here: the Heretical profile deliberately licenses both (Modus
    Haereticus), so finding them there is not a defect -- see
    :func:`_orthodox_harmonic_invariants_hold`, which is only ever called for Orthodox
    results, for that check.
    """
    problems: List[str] = []
    voices = composition.voice_payload()
    present = {v["voice"] for v in voices}
    expected = {"soprano", "alto", "tenor", "bass"}
    if present != expected:
        problems.append(f"expected voices {sorted(expected)}, found {sorted(present)}")
    for v in voices:
        if not v["events"]:
            problems.append(f"{v['voice']} produced no events")
            continue
        low, high = v["range"]["low"], v["range"]["high"]
        for event in v["events"]:
            if not (low <= event["midi"] <= high):
                problems.append(
                    f"{v['voice']} pitch {event['midi']} outside range [{low}, {high}]"
                )
                break
    return (not problems), problems


def _orthodox_harmonic_invariants_hold(composition) -> Tuple[bool, List[str]]:
    """Re-derive voice-crossing and parallel-fifth/octave findings from the raw event
    JSON for an Orthodox result, where the active law forbids both. Only meaningful for
    Orthodox output -- see :func:`_independent_invariants_hold` for why Heretical output
    is checked separately."""
    problems: List[str] = []
    body = {"score": {"voices": composition.voice_payload()}}
    try:
        crossings = _helpers.crossings(body)
        parallels = _helpers.parallel_perfects(body)
    except AssertionError as exc:  # a voice silent at some sampled offset
        problems.append(f"independent sampling failed: {exc}")
        return (not problems), problems
    if crossings:
        problems.append(f"{len(crossings)} independent voice-crossing finding(s)")
    if parallels:
        problems.append(f"{len(parallels)} independent parallel fifth/octave finding(s)")
    return (not problems), problems


# ------------------------------------------------------------------------------------
# Running one case
# ------------------------------------------------------------------------------------


@dataclass
class CaseOutcome:
    case: MatrixCase
    ok: bool
    elapsed_ms: float
    composition: Optional[object] = None
    error: Optional[BaseException] = None
    problems: Tuple[str, ...] = ()


def run_case(case: MatrixCase) -> CaseOutcome:
    engine = case.engine()
    started = time.perf_counter()
    try:
        composition = engine.compose(**case.compose_kwargs())
    except GenerationError as error:
        elapsed = (time.perf_counter() - started) * 1000.0
        if case.expect == "generation_error":
            return CaseOutcome(case, True, elapsed, error=error)
        return CaseOutcome(
            case, False, elapsed, error=error,
            problems=(f"unexpected GenerationError: {error}",),
        )
    except Exception as error:  # pragma: no cover - genuinely unexpected
        elapsed = (time.perf_counter() - started) * 1000.0
        return CaseOutcome(
            case, False, elapsed, error=error,
            problems=(f"unexpected {type(error).__name__}: {error}",),
        )
    elapsed = (time.perf_counter() - started) * 1000.0
    if case.expect == "generation_error":
        return CaseOutcome(
            case, False, elapsed, composition=composition,
            problems=("expected GenerationError but generation succeeded",),
        )
    problems: List[str] = []
    if composition.validation.defects:
        problems.append(
            f"{len(composition.validation.defects)} validation defect(s) reported"
        )
    if not composition.validation.passed:
        problems.append("composition.validation.passed is False")
    _, structural_problems = _independent_invariants_hold(composition)
    problems.extend(structural_problems)
    if not composition.config.heretical:
        _, harmonic_problems = _orthodox_harmonic_invariants_hold(composition)
        problems.extend(harmonic_problems)
    return CaseOutcome(case, not problems, elapsed, composition=composition,
                        problems=tuple(problems))


# ------------------------------------------------------------------------------------
# Determinism spot checks (section 6)
# ------------------------------------------------------------------------------------


@dataclass
class DeterminismCheck:
    case_id: str
    matched_seed: bool
    matched_events: bool
    matched_validation: bool
    matched_midi: Optional[bool]

    @property
    def ok(self) -> bool:
        return (
            self.matched_seed and self.matched_events and self.matched_validation
            and (self.matched_midi is not False)
        )


def _select_determinism_subset(
    cases: Sequence[MatrixCase], target_count: int,
) -> List[MatrixCase]:
    """A deterministic stride through the successful-by-design cases -- not every case
    re-run (that would double the whole run's cost), but a fixed, reproducible sample."""
    eligible = [c for c in cases if c.expect == "success"]
    if not eligible:
        return []
    stride = max(1, len(eligible) // max(1, target_count))
    return eligible[::stride][:target_count]


def run_determinism_checks(
    cases: Sequence[MatrixCase], target_count: int, midi_every: int = 5,
) -> List[DeterminismCheck]:
    subset = _select_determinism_subset(cases, target_count)
    results: List[DeterminismCheck] = []
    for i, case in enumerate(subset):
        first = run_case(case)
        second = run_case(case)
        if first.composition is None or second.composition is None:
            results.append(DeterminismCheck(case.case_id, False, False, False, None))
            continue
        a, b = first.composition, second.composition
        matched_seed = a.provenance.seed == b.provenance.seed
        matched_events = a.voice_payload() == b.voice_payload()
        matched_validation = a.validation.as_dict() == b.validation.as_dict()
        matched_midi: Optional[bool] = None
        if i % midi_every == 0:
            matched_midi = (
                composition_to_base64(a) == composition_to_base64(b)
            )
        results.append(DeterminismCheck(
            case.case_id, matched_seed, matched_events, matched_validation,
            matched_midi,
        ))
    return results


# ------------------------------------------------------------------------------------
# Item 11: extremely long digit-only seed strings and Python's int() conversion limit
# ------------------------------------------------------------------------------------


def probe_long_seed_robustness() -> Dict[str, object]:
    """``determinism._parse_decimal_seed`` calls ``int(text)`` on any all-digit string,
    and ``ComposeRequest`` places no length limit on it. Python (3.11+) refuses to
    convert an integer literal above a configured digit count (4300 by default) at all,
    which raises a bare ``ValueError`` rather than a clean validation error. This does
    not touch the seed *semantics* B8.2 closed -- it is a request-validation gap on the
    string's length, independent of what the digits mean -- so B9 only records it here
    rather than redesigning coerce_seed(); see the B10 deferral this produces.
    """
    digits = "7" * 5000
    try:
        coerce_seed(digits)
    except ValueError as exc:
        return {
            "digit_length": len(digits), "outcome": "unhandled_value_error",
            "detail": str(exc),
            "defer_to": "B10",
            "note": (
                "coerce_seed()/_parse_decimal_seed() calls int(text) with no length "
                "cap; ComposeRequest.seed has no max length either, so this reaches the "
                "API as an unhandled 500 rather than a 422. Not fixed here -- see B9 "
                "section 11: fixing it cleanly needs a validated length limit on the "
                "seed field, which is request-validation hygiene, not a determinism "
                "change, and is out of B9's scope."
            ),
        }
    except Exception as exc:  # pragma: no cover - would itself be news
        return {
            "digit_length": len(digits), "outcome": "unexpected_error",
            "detail": f"{type(exc).__name__}: {exc}", "defer_to": "B10",
        }
    return {"digit_length": len(digits), "outcome": "parsed_without_error"}


# ------------------------------------------------------------------------------------
# The report
# ------------------------------------------------------------------------------------


def _percentile(sorted_values: Sequence[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * pct
    lo, hi = int(k), min(int(k) + 1, len(sorted_values) - 1)
    frac = k - lo
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac


@dataclass
class StressReport:
    run_name: str
    engine_version: str
    started_at: str
    finished_at: str
    environment: Dict[str, object]
    total_configurations: int
    successes: int
    generation_failures: int
    unexpected_exceptions: int
    orthodox_count: int
    heretical_count: int
    counts_by_mode: Dict[str, int]
    counts_by_meter: Dict[str, int]
    counts_by_length_class: Dict[str, int]
    counts_by_config_path: Dict[str, int]
    relaxed_count: int
    relaxation_level_histogram: Dict[str, int]
    solver_restart_total: int
    node_budget_hit_count: int
    repair_budget_exhausted_count: int
    nodes_visited_total: int
    nodes_visited_max: int
    backtracks_total: int
    backtracks_max: int
    repair_passes_total: int
    repair_passes_max: int
    returned_defect_count: int
    phrase_tritone_failure_count: int
    intent_counts: Dict[str, int]
    elapsed_ms_stats: Dict[str, float]
    determinism_checks: Dict[str, object]
    independent_invariant_checks: Dict[str, object]
    worst_cases: List[Dict[str, object]]
    failures: List[Dict[str, object]]
    long_seed_probe: Dict[str, object]
    exit_ok: bool

    def as_dict(self) -> Dict[str, object]:
        return {
            "run_name": self.run_name, "engine_version": self.engine_version,
            "started_at": self.started_at, "finished_at": self.finished_at,
            "environment": self.environment,
            "total_configurations": self.total_configurations,
            "successes": self.successes,
            "generation_failures": self.generation_failures,
            "unexpected_exceptions": self.unexpected_exceptions,
            "orthodox_count": self.orthodox_count,
            "heretical_count": self.heretical_count,
            "counts_by_mode": self.counts_by_mode,
            "counts_by_meter": self.counts_by_meter,
            "counts_by_length_class": self.counts_by_length_class,
            "counts_by_config_path": self.counts_by_config_path,
            "relaxed_count": self.relaxed_count,
            "relaxation_level_histogram": self.relaxation_level_histogram,
            "solver_restart_total": self.solver_restart_total,
            "node_budget_hit_count": self.node_budget_hit_count,
            "repair_budget_exhausted_count": self.repair_budget_exhausted_count,
            "nodes_visited_total": self.nodes_visited_total,
            "nodes_visited_max": self.nodes_visited_max,
            "backtracks_total": self.backtracks_total,
            "backtracks_max": self.backtracks_max,
            "repair_passes_total": self.repair_passes_total,
            "repair_passes_max": self.repair_passes_max,
            "returned_defect_count": self.returned_defect_count,
            "phrase_tritone_failure_count": self.phrase_tritone_failure_count,
            "intent_counts": self.intent_counts,
            "elapsed_ms_stats": self.elapsed_ms_stats,
            "determinism_checks": self.determinism_checks,
            "independent_invariant_checks": self.independent_invariant_checks,
            "worst_cases": self.worst_cases,
            "failures": self.failures,
            "long_seed_probe": self.long_seed_probe,
            "exit_ok": self.exit_ok,
        }


def _environment() -> Dict[str, object]:
    from determinism import runtime_versions
    info = dict(runtime_versions())
    info["platform"] = platform.platform()
    info["machine"] = platform.machine()
    return info


def run_matrix(profile: str, determinism_sample: int = 30) -> StressReport:
    started_at = datetime.now(timezone.utc)
    cases = build_matrix(profile)
    outcomes = [run_case(case) for case in cases]

    successes = sum(1 for o in outcomes if o.ok and o.case.expect == "success")
    generation_failures = sum(
        1 for o in outcomes if o.ok and o.case.expect == "generation_error"
    )
    unexpected = [o for o in outcomes if not o.ok]

    counts_by_mode: Dict[str, int] = {}
    counts_by_meter: Dict[str, int] = {}
    counts_by_length: Dict[str, int] = {}
    counts_by_path: Dict[str, int] = {}
    orthodox_count = heretical_count = 0
    relaxed_count = 0
    relaxation_hist: Dict[str, int] = {}
    solver_restarts = node_budget_hits = repair_exhausted_count = 0
    nodes_total = nodes_max = 0
    backtracks_total = backtracks_max = 0
    repair_total = repair_max = 0
    defect_total = 0
    phrase_tritone_failures = 0
    intent_counts: Dict[str, int] = {intent.value: 0 for intent in Intent}
    elapsed_by_case: List[Tuple[str, float, MatrixCase, Optional[object]]] = []

    for outcome in outcomes:
        case = outcome.case
        if case.mode:
            counts_by_mode[case.mode] = counts_by_mode.get(case.mode, 0) + 1
        if case.meter:
            counts_by_meter[case.meter] = counts_by_meter.get(case.meter, 0) + 1
        counts_by_length[case.length_class] = (
            counts_by_length.get(case.length_class, 0) + 1
        )
        counts_by_path[case.config_path] = counts_by_path.get(case.config_path, 0) + 1
        elapsed_by_case.append((case.case_id, outcome.elapsed_ms, case,
                                 outcome.composition))

        comp = outcome.composition
        if comp is None:
            continue
        if comp.config.heretical:
            heretical_count += 1
        else:
            orthodox_count += 1
        stats = comp.stats
        if stats.relaxation_level > 0:
            relaxed_count += 1
        relaxation_hist[str(stats.relaxation_level)] = (
            relaxation_hist.get(str(stats.relaxation_level), 0) + 1
        )
        solver_restarts += stats.solver_restarts
        node_budget_hits += stats.node_budget_hits
        if stats.repair_exhausted:
            repair_exhausted_count += 1
        nodes_total += stats.nodes_visited
        nodes_max = max(nodes_max, stats.nodes_visited)
        backtracks_total += stats.backtracks
        backtracks_max = max(backtracks_max, stats.backtracks)
        repair_total += stats.repair_passes
        repair_max = max(repair_max, stats.repair_passes)
        defect_total += len(comp.validation.defects)
        if stats.phrases_without_tritone > stats.tritone_injections:
            phrase_tritone_failures += 1
        for key, value in comp.validation.counts_by_intent().items():
            intent_counts[key] = intent_counts.get(key, 0) + value

    elapsed_values = sorted(ms for _, ms, _, _ in elapsed_by_case)
    elapsed_stats = {
        "min": round(elapsed_values[0], 2) if elapsed_values else 0.0,
        "median": round(statistics.median(elapsed_values), 2) if elapsed_values else 0.0,
        "p95": round(_percentile(elapsed_values, 0.95), 2) if elapsed_values else 0.0,
        "p99": round(_percentile(elapsed_values, 0.99), 2) if elapsed_values else 0.0,
        "max": round(elapsed_values[-1], 2) if elapsed_values else 0.0,
        "total": round(sum(elapsed_values), 2),
        "sample_size": len(elapsed_values),
    }

    worst = sorted(elapsed_by_case, key=lambda t: t[1], reverse=True)[:20]
    worst_cases = []
    for case_id, ms, case, comp in worst:
        entry = {
            "case_id": case_id, "mode": case.mode, "meter": case.meter,
            "config_path": case.config_path, "measures": case.measures,
            "seed": case.seed, "elapsed_ms": round(ms, 2),
        }
        if comp is not None:
            entry.update({
                "relaxation_level": comp.stats.relaxation_level,
                "nodes_visited": comp.stats.nodes_visited,
                "backtracks": comp.stats.backtracks,
                "repair_passes": comp.stats.repair_passes,
            })
        worst_cases.append(entry)

    failures = []
    for outcome in unexpected:
        case = outcome.case
        failures.append({
            "case_id": case.case_id,
            "config": case.as_dict(),
            "replay_command": case.replay_args(),
            "problems": list(outcome.problems),
            "error_type": type(outcome.error).__name__ if outcome.error else None,
            "error_message": str(outcome.error) if outcome.error else None,
        })

    determinism_target = (
        determinism_sample if profile == "full" else min(8, determinism_sample)
    )
    determinism_results = run_determinism_checks(cases, determinism_target)
    determinism_failed = [d for d in determinism_results if not d.ok]

    independent_checked = sum(
        1 for o in outcomes
        if o.composition is not None and not o.composition.config.heretical
        and o.case.expect == "success"
    )
    independent_failed = sum(
        1 for o in outcomes
        if o.composition is not None and not o.composition.config.heretical
        and o.case.expect == "success" and not o.ok
    )

    long_seed_probe = probe_long_seed_robustness()

    exit_ok = not unexpected and not determinism_failed

    finished_at = datetime.now(timezone.utc)
    return StressReport(
        run_name=profile, engine_version=ENGINE_VERSION,
        started_at=started_at.isoformat(), finished_at=finished_at.isoformat(),
        environment=_environment(),
        total_configurations=len(cases), successes=successes,
        generation_failures=generation_failures,
        unexpected_exceptions=len(unexpected),
        orthodox_count=orthodox_count, heretical_count=heretical_count,
        counts_by_mode=dict(sorted(counts_by_mode.items())),
        counts_by_meter=dict(sorted(counts_by_meter.items())),
        counts_by_length_class=dict(sorted(counts_by_length.items())),
        counts_by_config_path=dict(sorted(counts_by_path.items())),
        relaxed_count=relaxed_count,
        relaxation_level_histogram=dict(sorted(relaxation_hist.items())),
        solver_restart_total=solver_restarts,
        node_budget_hit_count=node_budget_hits,
        repair_budget_exhausted_count=repair_exhausted_count,
        nodes_visited_total=nodes_total, nodes_visited_max=nodes_max,
        backtracks_total=backtracks_total, backtracks_max=backtracks_max,
        repair_passes_total=repair_total, repair_passes_max=repair_max,
        returned_defect_count=defect_total,
        phrase_tritone_failure_count=phrase_tritone_failures,
        intent_counts=intent_counts,
        elapsed_ms_stats=elapsed_stats,
        determinism_checks={
            "performed": len(determinism_results),
            "passed": len(determinism_results) - len(determinism_failed),
            "failed": len(determinism_failed),
            "midi_compared": sum(
                1 for d in determinism_results if d.matched_midi is not None
            ),
            "failures": [d.case_id for d in determinism_failed],
        },
        independent_invariant_checks={
            "performed": independent_checked, "failed": independent_failed,
        },
        worst_cases=worst_cases,
        failures=failures,
        long_seed_probe=long_seed_probe,
        exit_ok=exit_ok,
    )


# ------------------------------------------------------------------------------------
# Terminal summary + CLI
# ------------------------------------------------------------------------------------


def print_summary(report: StressReport) -> None:
    r = report
    print(f"\n=== stress_matrix.py -- profile={r.run_name} engine={r.engine_version} ===")
    print(f"configurations: {r.total_configurations}  "
          f"successes: {r.successes}  expected-failures: {r.generation_failures}  "
          f"unexpected: {r.unexpected_exceptions}")
    print(f"orthodox: {r.orthodox_count}  heretical: {r.heretical_count}")
    print(f"modes: {r.counts_by_mode}")
    print(f"meters: {r.counts_by_meter}")
    print(f"length classes: {r.counts_by_length_class}")
    print(f"config paths: {r.counts_by_config_path}")
    print(f"relaxed: {r.relaxed_count}  relaxation histogram: "
          f"{r.relaxation_level_histogram}")
    print(f"solver restarts: {r.solver_restart_total}  "
          f"node-budget hits: {r.node_budget_hit_count}  "
          f"repair-budget exhausted: {r.repair_budget_exhausted_count}")
    print(f"nodes visited: total={r.nodes_visited_total} max={r.nodes_visited_max}  "
          f"backtracks: total={r.backtracks_total} max={r.backtracks_max}  "
          f"repair passes: total={r.repair_passes_total} max={r.repair_passes_max}")
    print(f"returned defects: {r.returned_defect_count}  "
          f"phrase-tritone failures: {r.phrase_tritone_failure_count}")
    print(f"intent counts: {r.intent_counts}")
    e = r.elapsed_ms_stats
    print(f"elapsed ms -- min={e['min']} median={e['median']} p95={e['p95']} "
          f"p99={e['p99']} max={e['max']} total={e['total']} "
          f"(n={e['sample_size']})")
    d = r.determinism_checks
    print(f"determinism spot-checks: performed={d['performed']} passed={d['passed']} "
          f"failed={d['failed']} midi-compared={d['midi_compared']}")
    ii = r.independent_invariant_checks
    print(f"independent invariant checks (orthodox): performed={ii['performed']} "
          f"failed={ii['failed']}")
    print(f"long-seed robustness probe: {r.long_seed_probe['outcome']}"
          + (f" (deferred to {r.long_seed_probe['defer_to']})"
             if "defer_to" in r.long_seed_probe else ""))
    if r.worst_cases:
        print("slowest case: " + json.dumps(r.worst_cases[0]))
    if r.failures:
        print(f"\n{len(r.failures)} FAILING CASE(S):")
        for f in r.failures[:10]:
            print(f"  - {f['case_id']}: {f['problems']}")
            print(f"    replay: {' '.join(f['replay_command'])}")
    print(f"\nEXIT: {'OK' if r.exit_ok else 'FAIL'}")


def _replay(profile: str, case_id: str) -> int:
    cases = {c.case_id: c for c in build_matrix(profile)}
    case = cases.get(case_id)
    if case is None:
        print(f"no case {case_id!r} in the {profile!r} matrix "
              f"({len(cases)} cases available)", file=sys.stderr)
        return 2
    print(f"replaying {case_id}:")
    print(json.dumps(case.as_dict(), indent=2, default=str))
    outcome = run_case(case)
    print(f"\nresult: {'OK' if outcome.ok else 'FAIL'} "
          f"({outcome.elapsed_ms:.1f} ms)")
    if outcome.problems:
        for p in outcome.problems:
            print(f"  problem: {p}")
    if outcome.composition is not None:
        print(f"  resolved seed: {outcome.composition.provenance.seed}")
        print(f"  relaxation level: {outcome.composition.stats.relaxation_level}")
        print(f"  defects: {len(outcome.composition.validation.defects)}")
    if outcome.error is not None:
        print(f"  error: {type(outcome.error).__name__}: {outcome.error}")
    return 0 if outcome.ok else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--out", type=Path, default=None,
                         help="write the JSON report to this path")
    parser.add_argument("--replay", metavar="CASE_ID", default=None,
                         help="run exactly one case by id and exit")
    parser.add_argument("--determinism-sample", type=int, default=30,
                         help="target number of cases to run twice for a "
                              "determinism spot check (full profile only)")
    args = parser.parse_args(argv)

    if args.replay:
        return _replay(args.profile, args.replay)

    report = run_matrix(args.profile, determinism_sample=args.determinism_sample)
    print_summary(report)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report.as_dict(), indent=2, default=str))
        print(f"\nwrote {args.out}")

    return 0 if report.exit_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
