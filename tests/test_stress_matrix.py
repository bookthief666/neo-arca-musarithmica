"""Lightweight tests for scripts/stress_matrix.py itself -- the harness, not the engine.

None of these run the full FULL profile (1,814 generations, several minutes); that is
release-verification tooling invoked directly, not part of routine `pytest`. What's
tested here is the harness's own guarantees: the matrix is a pure function of its
profile name, every declared dimension is actually represented, JSON round-trips, a
failing case preserves enough to replay it, exit-status semantics match the mission
brief, and the deterministic-subset selection is stable. One genuinely tiny smoke
invocation (two hand-picked cases, not the full 27-case smoke profile) proves the
whole pipeline -- build, run, report -- actually works end to end.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "stress_matrix", ROOT / "scripts" / "stress_matrix.py"
)
stress_matrix = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules.setdefault("stress_matrix", stress_matrix)
_SPEC.loader.exec_module(stress_matrix)


# --------------------------------------------------------------------------------------
# Matrix construction
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("profile", ["smoke", "full"])
def test_matrix_construction_is_deterministic(profile):
    a = stress_matrix.build_matrix(profile)
    b = stress_matrix.build_matrix(profile)
    assert [c.as_dict() for c in a] == [c.as_dict() for c in b]


@pytest.mark.parametrize("profile", ["smoke", "full"])
def test_case_ids_are_unique(profile):
    cases = stress_matrix.build_matrix(profile)
    ids = [c.case_id for c in cases]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("profile", ["smoke", "full"])
def test_all_seven_modes_are_represented(profile):
    cases = stress_matrix.build_matrix(profile)
    modes = {c.mode for c in cases if c.mode is not None}
    assert modes == set(stress_matrix.MODES)
    assert len(stress_matrix.MODES) == 7


@pytest.mark.parametrize("profile", ["smoke", "full"])
def test_all_supported_meters_are_represented(profile):
    cases = stress_matrix.build_matrix(profile)
    meters = {c.meter for c in cases if c.meter is not None}
    assert meters == set(stress_matrix.METERS)


@pytest.mark.parametrize("profile", ["smoke", "full"])
def test_both_law_profiles_are_represented(profile):
    cases = stress_matrix.build_matrix(profile)
    heretical_values = {c.heretical for c in cases if c.heretical is not None}
    assert heretical_values == {True, False}


@pytest.mark.parametrize("profile", ["smoke", "full"])
def test_both_configuration_paths_are_represented(profile):
    cases = stress_matrix.build_matrix(profile)
    paths = {c.config_path for c in cases}
    assert paths == {"explicit", "semantic"}


@pytest.mark.parametrize("profile", ["smoke", "full"])
def test_all_length_classes_are_represented(profile):
    cases = stress_matrix.build_matrix(profile)
    lengths = {c.length_class for c in cases}
    assert lengths == set(stress_matrix.LENGTH_CLASSES)


def test_full_matrix_reaches_the_earlier_claimed_scale():
    """The earlier, uncommitted report claimed ~1,764 generations; FULL must reach at
    least that scale, not quietly shrink below it."""
    cases = stress_matrix.build_matrix("full")
    assert len(cases) >= 1764


def test_smoke_matrix_is_small_enough_for_routine_development_use():
    cases = stress_matrix.build_matrix("smoke")
    assert len(cases) < 60


def test_an_unknown_profile_name_is_rejected():
    with pytest.raises(ValueError):
        stress_matrix.build_matrix("nonexistent-profile")


def test_expected_failure_cases_are_modeled_explicitly_not_left_to_fail_by_accident():
    """Section 4 of the B9 brief: a case that expects GenerationError must say so."""
    cases = stress_matrix.build_matrix("smoke")
    expected_failures = [c for c in cases if c.expect == "generation_error"]
    assert expected_failures
    for case in expected_failures:
        assert case.starved_budget, (
            "a case expecting GenerationError should do so by a documented mechanism "
            "(a deliberately starved budget), not an accident of the other parameters"
        )


# --------------------------------------------------------------------------------------
# Running cases and reporting
# --------------------------------------------------------------------------------------


def test_json_report_serialises_and_round_trips():
    import json

    report = stress_matrix.run_matrix("smoke", determinism_sample=2)
    payload = report.as_dict()
    text = json.dumps(payload, default=str)
    restored = json.loads(text)
    assert restored["run_name"] == "smoke"
    assert restored["total_configurations"] == len(stress_matrix.build_matrix("smoke"))
    assert isinstance(restored["worst_cases"], list)
    assert isinstance(restored["failures"], list)


def test_a_successful_smoke_run_exits_ok():
    report = stress_matrix.run_matrix("smoke", determinism_sample=2)
    assert report.unexpected_exceptions == 0
    assert report.exit_ok is True


def test_expect_generation_error_case_actually_raises_and_is_not_a_failure():
    cases = {c.case_id: c for c in stress_matrix.build_matrix("smoke")}
    starved_case = next(c for c in cases.values() if c.expect == "generation_error")
    outcome = stress_matrix.run_case(starved_case)
    assert outcome.ok is True
    assert outcome.error is not None
    assert outcome.composition is None
    assert outcome.failure_kind is None


def test_a_case_expecting_success_that_raises_is_reported_as_unexpected():
    """The inverse of the above: an ordinary case is not allowed to raise silently."""
    baseline = next(
        c for c in stress_matrix.build_matrix("smoke") if c.case_id == "smoke-baseline"
    )
    broken = stress_matrix.replace(
        baseline, starved_budget=True,  # forces GenerationError on a "success" case
    )
    outcome = stress_matrix.run_case(broken)
    assert outcome.ok is False
    assert outcome.error is not None
    assert "unexpected GenerationError" in outcome.problems[0]
    assert outcome.failure_kind == "unexpected_generation_error"


def test_a_success_case_reporting_generation_error_when_none_occurs_is_not_confused():
    """A case whose ``expect`` is 'generation_error' but that actually succeeds must be
    reported as a failure, not silently accepted -- and classified as its own kind, not
    lumped in with a genuinely unexpected exception (B10 section 7, finding A)."""
    cases = stress_matrix.build_matrix("smoke")
    starved = next(c for c in cases if c.expect == "generation_error")
    forced_success = stress_matrix.replace(starved, starved_budget=False)
    outcome = stress_matrix.run_case(forced_success)
    assert outcome.ok is False
    assert "expected GenerationError" in outcome.problems[0]
    assert outcome.failure_kind == "expectation_mismatch"


def test_an_unanticipated_exception_is_classified_distinctly_from_a_generation_error():
    """A non-GenerationError exception must be its own failure_kind, not folded into
    'unexpected_generation_error'."""
    baseline = next(
        c for c in stress_matrix.build_matrix("smoke") if c.case_id == "smoke-baseline"
    )

    class _Exploding:
        def compose(self, **kwargs):
            raise RuntimeError("something genuinely unanticipated")

    broken = stress_matrix.replace(baseline)
    import unittest.mock
    with unittest.mock.patch.object(stress_matrix.MatrixCase, "engine",
                                     return_value=_Exploding()):
        outcome = stress_matrix.run_case(broken)
    assert outcome.ok is False
    assert outcome.failure_kind == "unexpected_exception"


def test_an_invariant_failure_is_classified_distinctly_from_a_raised_exception():
    """A case that raises nothing but fails this harness's own independent check must
    be its own failure_kind -- not called an 'unexpected exception' (B10 finding A)."""
    baseline = next(
        c for c in stress_matrix.build_matrix("smoke") if c.case_id == "smoke-baseline"
    )
    composed = stress_matrix.run_case(baseline).composition
    assert composed is not None

    class _StubEngine:
        def compose(self, **kwargs):
            return composed

    broken = stress_matrix.replace(baseline)
    import unittest.mock
    with unittest.mock.patch.object(stress_matrix.MatrixCase, "engine",
                                     return_value=_StubEngine()), \
         unittest.mock.patch.object(
             stress_matrix, "_independent_invariants_hold",
             return_value=(False, ["stubbed structural problem"]),
         ):
        outcome = stress_matrix.run_case(broken)
    assert outcome.ok is False
    assert outcome.failure_kind == "invariant_failure"


def test_the_four_failure_kinds_and_success_partition_every_case():
    """No case can land outside success/expected-failure/exactly-one failure kind --
    the corrected schema's core invariant (B10 section 7, finding A)."""
    report = stress_matrix.run_matrix("smoke", determinism_sample=2)
    accounted = (
        report.successes + report.expected_generation_errors
        + report.unexpected_generation_errors + report.unexpected_exceptions
        + report.invariant_failures + report.expectation_mismatches
    )
    assert accounted == report.total_configurations


def test_failing_cases_preserve_enough_information_to_replay():
    baseline = next(
        c for c in stress_matrix.build_matrix("smoke") if c.case_id == "smoke-baseline"
    )
    broken = stress_matrix.replace(baseline, starved_budget=True)
    outcome = stress_matrix.run_case(broken)
    assert outcome.ok is False

    replay_args = broken.replay_args()
    assert "--replay" in replay_args
    assert broken.case_id in replay_args

    config = broken.as_dict()
    for key in ("mode", "meter", "seed", "measures", "heretical", "text"):
        assert key in config


def test_heretical_voice_crossing_is_not_treated_as_a_defect():
    """Modus Haereticus deliberately licenses voice crossing and parallel motion; the
    harness's independent invariant check must not flag it as a correctness failure."""
    cases = stress_matrix.build_matrix("smoke")
    heretical_cases = [
        c for c in cases if c.heretical is True and c.expect == "success"
    ]
    assert heretical_cases
    for case in heretical_cases:
        outcome = stress_matrix.run_case(case)
        assert outcome.ok, (
            f"{case.case_id} failed: {outcome.problems} -- Heretical output must not "
            f"be judged by Orthodox harmonic invariants"
        )


# --------------------------------------------------------------------------------------
# B10 section 7, finding B: resolved vs requested-explicit mode/meter counts
# --------------------------------------------------------------------------------------


def test_resolved_counts_account_for_semantic_derived_cases_requested_counts_do_not():
    """A semantic-derived case (config_path='semantic') sends mode=None/meter=None, so
    it must contribute to `resolved_counts_by_mode/meter` (what the engine actually
    produced) but not to `requested_explicit_counts_by_mode/meter` (what the request
    named) -- the schema issue an independent B10 audit found: the old single
    `counts_by_mode` silently missed every semantic-derived case."""
    report = stress_matrix.run_matrix("smoke", determinism_sample=2)
    semantic_cases = [
        c for c in stress_matrix.build_matrix("smoke") if c.config_path == "semantic"
    ]
    assert semantic_cases
    assert sum(report.requested_explicit_counts_by_mode.values()) < (
        report.successes + report.expected_generation_errors
    )
    assert sum(report.resolved_counts_by_mode.values()) >= sum(
        report.requested_explicit_counts_by_mode.values()
    )
    assert sum(report.resolved_counts_by_meter.values()) >= sum(
        report.requested_explicit_counts_by_meter.values()
    )


def test_resolved_mode_counts_cover_every_successful_composition():
    report = stress_matrix.run_matrix("smoke", determinism_sample=2)
    assert sum(report.resolved_counts_by_mode.values()) == report.successes
    assert sum(report.resolved_counts_by_meter.values()) == report.successes


# --------------------------------------------------------------------------------------
# B10 section 7, finding C: successful-only vs all-cases performance sample
# --------------------------------------------------------------------------------------


def test_successful_only_timing_excludes_expected_failure_cases():
    """The headline performance metric must not include the deliberately-starved
    expected-failure cases, whose near-instant budget exhaustion is not a genuine
    'fast composition' and would understate typical timing if mixed in."""
    report = stress_matrix.run_matrix("smoke", determinism_sample=2)
    assert (
        report.elapsed_ms_stats_successful["sample_size"]
        == report.successes
        < report.elapsed_ms_stats_all_cases["sample_size"]
        == report.total_configurations
    )


# --------------------------------------------------------------------------------------
# Determinism subset selection
# --------------------------------------------------------------------------------------


def test_deterministic_subset_selection_is_stable():
    cases = stress_matrix.build_matrix("full")
    first = stress_matrix._select_determinism_subset(cases, 30)
    second = stress_matrix._select_determinism_subset(cases, 30)
    assert [c.case_id for c in first] == [c.case_id for c in second]


def test_deterministic_subset_only_contains_cases_expected_to_succeed():
    cases = stress_matrix.build_matrix("full")
    subset = stress_matrix._select_determinism_subset(cases, 30)
    assert subset
    assert all(c.expect == "success" for c in subset)


def test_deterministic_subset_respects_the_requested_target_count():
    cases = stress_matrix.build_matrix("full")
    subset = stress_matrix._select_determinism_subset(cases, 10)
    assert 0 < len(subset) <= 10


# --------------------------------------------------------------------------------------
# Item 11: the long-digit-seed probe is recorded, not silently swallowed
# --------------------------------------------------------------------------------------


def test_long_seed_probe_confirms_the_b10_boundary_fix():
    """B9 found an unhandled 500 on an oversized digit-only seed string; B10 fixed it
    at the public API boundary (ComposeRequest.seed) while deliberately leaving the
    internal coerce_seed() function itself unbounded. This probe must show both."""
    result = stress_matrix.probe_long_seed_robustness()
    assert result["digit_length"] > 4300  # past Python's int-string conversion limit

    boundary = result["public_api_boundary"]
    assert boundary["fixed"] is True
    assert boundary["outcome"] == "rejected_cleanly"

    internal = result["internal_coerce_seed"]
    assert internal["outcome"] in ("unhandled_value_error", "unexpected_error",
                                    "parsed_without_error")
