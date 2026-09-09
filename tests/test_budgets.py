"""Search budgets are authoritative, and the reported work matches the work done.

Two defects motivated this file:

* ``Renderer.repair`` looped to a private hardcoded ceiling of 100 and ignored
  ``SearchBudget.max_repair_passes`` entirely, so the configured budget was decorative.
* ``VoicingSolver._enumerate`` reset its node counter to zero before the lenient
  re-enumeration pass.  The strict pass's work was therefore dropped from
  ``nodes_visited`` (under-reporting), and the fallback received a *second* full
  ``max_nodes_per_slot`` allowance (a slot could silently cost twice its budget).

The tests below pin both: the configured ceilings bind, and one slot costs at most one
slot's allowance even when it needs two passes to find candidates.
"""

from __future__ import annotations

import pytest

import constraints as law
from constraints import MusicalFrame
from determinism import SeedStream
from harmony import build_plan
from kircher_engine import (
    ENGINE_VERSION, KircherEngine, SearchBudget, SearchStats, VoicingSolver,
)
from rhythm import meter_spec
from theory import VOICE_ORDER, shifted_range

#: Phrygian reliably forces the lenient fallback: its flat-second cadence and its
#: diminished degree-v pin the bass onto roots the melodic filter cannot always reach,
#: so at least one slot comes back empty on the strict pass.
LENIENT_CASE = dict(
    text="a solemn procession through the vaults",
    mode="phrygian", meter="4/4", measures=8, seed=1,
)


def build_solver(budget: SearchBudget, **overrides):
    """Assemble a solver exactly as ``KircherEngine.compose`` does, for unit-level work."""
    engine = KircherEngine(budget=budget)
    params = {**LENIENT_CASE, **overrides}
    seed = params.pop("seed")
    config, _ = engine.configure(**params)
    profile = law.get_profile(config.heretical)
    root = SeedStream(seed, path=(ENGINE_VERSION, profile.name))
    plan = build_plan(
        tonic_pc=config.tonic_pc, mode=config.mode, meter=meter_spec(config.meter),
        measures=config.measures, density=config.density,
        cadence_strength=config.cadence_strength,
        phrase_measures=config.phrase_measures, heretical=config.heretical,
        stream=root.derive("harmony"),
    )
    ranges = {v: shifted_range(v, config.register_shift) for v in VOICE_ORDER}
    frame = MusicalFrame.build(
        config.tonic_pc, config.mode, ranges, ficta_by_slot=plan.ficta_by_slot()
    )
    stats = SearchStats(slots=len(plan.slots))
    solver = VoicingSolver(
        plan, frame, profile, config, root.derive("voicing"), budget, stats
    )
    return solver, plan, stats


# --------------------------------------------------------------------------------------
# Repair budget
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("ceiling", [1, 2, 3, 5, 8])
def test_repair_never_exceeds_the_configured_budget(ceiling):
    engine = KircherEngine(budget=SearchBudget(max_repair_passes=ceiling))
    composition = engine.compose(
        text="a thousand swarming gears in the frost", seed=418, measures=8, density=0.7
    )
    assert composition.stats.repair_passes <= ceiling, (
        f"repair ran {composition.stats.repair_passes} passes under a budget of {ceiling}"
    )


def test_a_starved_repair_budget_reports_itself_rather_than_pretending():
    """One pass is not enough for this composition; that must be visible, not hidden."""
    starved = KircherEngine(budget=SearchBudget(max_repair_passes=1)).compose(
        text="a thousand swarming gears in the frost", seed=418, measures=8, density=0.7
    )
    generous = KircherEngine(budget=SearchBudget(max_repair_passes=8)).compose(
        text="a thousand swarming gears in the frost", seed=418, measures=8, density=0.7
    )
    assert starved.stats.repair_passes == 1
    assert starved.stats.repair_exhausted is True
    # The generous run converges on its own and must NOT claim exhaustion.
    assert generous.stats.repair_passes <= 8
    assert generous.stats.repair_exhausted is False


def test_repair_exhaustion_is_reported_through_the_api(client):
    response = client.post("/compose", json={
        "text": "a thousand swarming gears in the frost", "seed": 418, "measures": 8,
        "density": 0.7,
    })
    assert response.status_code == 200
    search = response.json()["search"]
    assert "repair_exhausted" in search
    assert search["repair_passes"] <= SearchBudget().max_repair_passes


# --------------------------------------------------------------------------------------
# Node accounting
# --------------------------------------------------------------------------------------


def test_the_lenient_fallback_is_actually_reachable():
    """Guards the rest of this file: if this case stops going lenient, the tests below
    would silently stop testing anything."""
    engine = KircherEngine()
    composition = engine.compose(**LENIENT_CASE)
    assert composition.stats.lenient_enumerations > 0, (
        "the chosen case no longer exercises the lenient re-enumeration path"
    )


class _CountingPool(list):
    """A pitch pool that tallies how many pitches the search actually pulls from it.

    ``_enumerate`` increments its node counter exactly once per pitch drawn from a pool,
    so counting yields here measures the real work *independently* of the counter under
    test -- which is the only way to catch the counter being silently reset.
    """

    def __init__(self, items, tally):
        super().__init__(items)
        self._tally = tally

    def __iter__(self):
        for item in super().__iter__():
            self._tally[0] += 1
            yield item


def test_one_slot_costs_at_most_one_slot_allowance_even_when_it_goes_lenient():
    """The defect: the fallback used to start a fresh ``max_nodes_per_slot`` budget."""
    budget = SearchBudget()
    solver, plan, stats = build_solver(budget)

    tally = [0]
    original_pool = solver._pool
    solver._pool = lambda slot, voice: _CountingPool(original_pool(slot, voice), tally)

    went_lenient = False
    previous = None
    for slot in plan.slots:
        before_reported = stats.nodes_visited
        before_lenient = stats.lenient_enumerations
        tally[0] = 0

        candidates = solver._enumerate(slot, previous, 0)

        reported = stats.nodes_visited - before_reported
        actually_done = tally[0]

        assert reported <= budget.max_nodes_per_slot, (
            f"slot {slot.index} spent {reported} nodes against a per-slot budget of "
            f"{budget.max_nodes_per_slot}"
        )
        assert reported == actually_done, (
            f"slot {slot.index} really visited {actually_done} nodes but reported "
            f"{reported} -- the accounting does not match the work"
        )
        if stats.lenient_enumerations > before_lenient:
            went_lenient = True
        if candidates:
            previous = solver._sonority(slot, candidates[0])

    assert went_lenient, "no slot exercised the lenient pass; test proved nothing"


def test_reported_nodes_stay_within_the_aggregate_allowance():
    budget = SearchBudget()
    composition = KircherEngine(budget=budget).compose(**LENIENT_CASE)
    stats = composition.stats
    ceiling = stats.candidate_sets_built * budget.max_nodes_per_slot
    assert stats.nodes_visited <= ceiling
    assert stats.nodes_visited > 0


def test_shrinking_the_node_budget_actually_shrinks_the_work():
    """If the budget were decorative, these two runs would cost the same."""
    generous = KircherEngine(budget=SearchBudget(max_nodes_per_slot=5000))
    frugal = KircherEngine(budget=SearchBudget(max_nodes_per_slot=250))
    a = generous.compose(**LENIENT_CASE)
    b = frugal.compose(**LENIENT_CASE)
    per_slot_a = a.stats.nodes_visited / max(1, a.stats.candidate_sets_built)
    per_slot_b = b.stats.nodes_visited / max(1, b.stats.candidate_sets_built)
    assert per_slot_b < per_slot_a
    assert per_slot_b <= 250


def test_node_budget_hits_are_counted_when_the_cap_binds():
    frugal = KircherEngine(budget=SearchBudget(max_nodes_per_slot=120))
    composition = frugal.compose(**LENIENT_CASE)
    assert composition.stats.node_budget_hits > 0, (
        "a 120-node cap must bind somewhere in an eight-bar composition"
    )


def test_a_lenient_composition_is_still_lawful():
    """Bounded relaxation must not become an escape hatch from the Orthodox contract."""
    composition = KircherEngine().compose(**LENIENT_CASE)
    assert composition.stats.lenient_enumerations > 0
    assert composition.validation.defects == []
