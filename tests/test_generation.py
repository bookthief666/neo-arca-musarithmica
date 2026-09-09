"""Bounded generation: the search must terminate, stay inside its budget, and fail loudly.

Section XVI's requirement is architectural rather than musical: no unbounded brute force,
explicit attempt limits, and a controlled domain error carrying useful diagnostics when
the limits are genuinely exhausted.
"""

from __future__ import annotations

import time

import pytest

from kircher_engine import (
    ENGINE, GenerationError, KircherEngine, SearchBudget,
)
from theory import ModeName


def test_the_default_budget_is_finite():
    budget = SearchBudget()
    for name, value in budget.as_dict().items():
        assert isinstance(value, (int, float)) and value > 0, name
    assert 0.0 < budget.strict_node_share <= 1.0
    assert 1 <= budget.strict_node_cap() <= budget.max_nodes_per_slot


def test_normal_generation_stays_well_inside_the_budget():
    budget = SearchBudget()
    composition = ENGINE.compose(
        text="I dreamed of a cathedral sinking slowly into a black sea",
        seed=1650, measures=8,
    )
    stats = composition.stats
    assert stats.backtracks <= budget.max_backtracks
    assert stats.relaxation_level <= budget.max_relaxation
    assert stats.repair_passes <= 100
    assert stats.budget_exhausted is False
    assert stats.nodes_visited <= budget.max_nodes_per_slot * stats.slots


@pytest.mark.parametrize("mode", [m.value for m in ModeName])
@pytest.mark.parametrize("heretical", [False, True])
def test_every_mode_and_profile_resolves_at_full_strictness(mode, heretical):
    """No relaxation should be needed for an ordinary request."""
    composition = ENGINE.compose(
        text="A solemn procession through the vaults", seed=31,
        mode=mode, measures=8, heretical=heretical,
    )
    assert composition.stats.relaxation_level == 0, (
        f"{mode} ({'heretical' if heretical else 'orthodox'}) needed relaxation"
    )
    assert composition.validation.defects == []


def test_an_impossible_budget_fails_fast_instead_of_hanging():
    starved = KircherEngine(budget=SearchBudget(
        max_candidates_per_slot=1, max_nodes_per_slot=1,
        max_backtracks=0, max_relaxation=0,
    ))
    started = time.perf_counter()
    with pytest.raises(GenerationError) as caught:
        starved.compose(text="A solemn procession", seed=1, measures=8)
    assert time.perf_counter() - started < 5.0, "the starved search did not terminate"
    diagnostics = caught.value.diagnostics
    assert diagnostics["search"]["budget_exhausted"] is True
    assert diagnostics["budget"]["max_backtracks"] == 0
    assert diagnostics["progression"], "the failure should say what it was trying to do"
    assert diagnostics["config"]["mode"]


def test_a_tight_budget_still_terminates_across_many_requests():
    tight = KircherEngine(budget=SearchBudget(
        max_candidates_per_slot=4, max_nodes_per_slot=60, max_backtracks=6,
    ))
    started = time.perf_counter()
    outcomes = {"ok": 0, "failed": 0}
    for seed in range(12):
        try:
            tight.compose(text="A solemn procession", seed=seed, measures=6)
            outcomes["ok"] += 1
        except GenerationError:
            outcomes["failed"] += 1
    assert sum(outcomes.values()) == 12
    assert time.perf_counter() - started < 20.0


@pytest.mark.parametrize("measures", [1, 2, 8, 32])
def test_generation_time_scales_sanely_with_length(measures):
    started = time.perf_counter()
    composition = ENGINE.compose(
        text="A thousand iron gears turning in the frost", seed=9, measures=measures,
    )
    elapsed = time.perf_counter() - started
    assert elapsed < 8.0, f"{measures} measures took {elapsed:.1f}s"
    assert composition.stats.slots >= measures
    assert composition.validation.passed


def test_the_longest_permitted_request_completes():
    started = time.perf_counter()
    composition = ENGINE.compose(
        text="An endless procession of stone", seed=4, measures=64, density=0.95,
    )
    assert time.perf_counter() - started < 30.0
    assert composition.total_ql > 0
    assert composition.validation.defects == []


def test_a_single_measure_still_produces_a_complete_cadence():
    composition = ENGINE.compose(text="A short prayer", seed=3, measures=1)
    assert composition.plan.slots
    assert composition.plan.slots[-1].is_final
    for events in composition.events.values():
        assert events
