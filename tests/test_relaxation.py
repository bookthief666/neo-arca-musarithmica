"""Relaxation loosens the search, never the contract.

When a slot cannot be solved at full strictness the solver retries at successive
relaxation levels.  Five Orthodox rules are error-severity yet stop being hard at level 2
-- ``dissonant_sonority``, ``doubled_leading_tone``, ``leading_tone_unresolved``,
``nonchord_tone_unstepwise`` and ``suspension_unresolved`` -- so a relaxed search *can*
commit something the unrelaxed law forbids.

Previously that produced an ordinary HTTP 200 whose ``validation`` block quietly
contained unintended errors.  The contract is now explicit: a returned composition never
contains a defect.  If a relaxed search produces one, generation fails loudly instead.
``relaxation_level`` still reports that the search had to loosen, so degradation of the
*search* stays visible even though the *output* is guaranteed clean.

Most of these tests deliberately force relaxation by starving the backtracking budget,
rather than only exercising the cases that resolve at level 0.
"""

from __future__ import annotations

import dataclasses

import pytest

import kircher_engine
from constraints import ORTHODOX, RulePolicy, Rules, Severity
from kircher_engine import ENGINE, GenerationError, KircherEngine, SearchBudget
from theory import ModeName

#: A starved backtracking budget makes level 0 unsolvable for some modes and seeds, so
#: the solver has to relax -- without changing anything about the music it is asked for.
STARVED = SearchBudget(max_backtracks=0)


def relaxed_compositions():
    engine = KircherEngine(budget=STARVED)
    out = []
    for mode in ModeName:
        for seed in range(6):
            try:
                composition = engine.compose(
                    text="a solemn procession through the vaults", seed=seed,
                    mode=mode.value, measures=8, heretical=False,
                )
            except GenerationError:
                continue
            if composition.stats.relaxation_level > 0:
                out.append(composition)
    return out


@pytest.fixture(scope="module")
def relaxed():
    compositions = relaxed_compositions()
    if not compositions:
        pytest.fail("no configuration relaxed; these tests would prove nothing")
    return compositions


# --------------------------------------------------------------------------------------
# Relaxation happens, and is reported
# --------------------------------------------------------------------------------------


def test_starving_the_budget_actually_forces_relaxation(relaxed):
    assert relaxed, "expected at least one relaxed success"
    assert any(c.stats.relaxation_level >= 1 for c in relaxed)
    assert all(c.stats.solver_restarts >= 1 for c in relaxed)


def test_a_relaxed_search_still_returns_lawful_music(relaxed):
    """The point of the contract: loosening the search does not loosen the output."""
    for composition in relaxed:
        assert composition.validation.defects == [], (
            f"a composition relaxed to level {composition.stats.relaxation_level} "
            f"returned {len(composition.validation.defects)} defects"
        )
        assert composition.validation.passed is True


def test_relaxation_is_visible_in_the_response(relaxed):
    for composition in relaxed:
        payload = composition.stats.as_dict()
        assert payload["relaxation_level"] > 0
        assert payload["relaxed"] is True


def test_an_unrelaxed_composition_says_so():
    composition = ENGINE.compose(
        text="a solemn procession through the vaults", seed=31, measures=8
    )
    payload = composition.stats.as_dict()
    assert payload["relaxation_level"] == 0
    assert payload["relaxed"] is False


def test_relaxation_never_exceeds_the_configured_ceiling(relaxed):
    for composition in relaxed:
        assert composition.stats.relaxation_level <= STARVED.max_relaxation


# --------------------------------------------------------------------------------------
# The contract itself: defects are never returned
# --------------------------------------------------------------------------------------


def weakened_orthodox():
    """Orthodox law with the parallel-fifth prohibition no longer pruning the search.

    This stands in for what relaxation level 2 does to the five error-severity rules it
    drops: the solver stops rejecting the violation, so it commits one, and validation --
    which always grades against real Orthodox law -- classifies it as a defect.
    """
    policies = dict(ORTHODOX.policies)
    policies[Rules.PARALLEL_FIFTH] = RulePolicy(14.0, Severity.ERROR, hard_until=-1)
    policies[Rules.PARALLEL_OCTAVE] = RulePolicy(14.0, Severity.ERROR, hard_until=-1)
    return dataclasses.replace(ORTHODOX, policies=policies)


#: Searched rather than pinned: which seed first yields a parallel depends on the seed
#: derivation, which legitimately moves when ENGINE_VERSION changes.
DEFECT_CANDIDATES = [(mode, seed) for mode in ("ionian", "dorian", "aeolian")
                     for seed in range(6)]


def first_refusal(engine):
    for mode, seed in DEFECT_CANDIDATES:
        try:
            engine.compose(
                text="a solemn procession through the vaults", seed=seed, mode=mode,
                measures=8, heretical=False,
            )
        except GenerationError as error:
            if error.diagnostics.get("defects"):
                return mode, seed, error
    return None


def test_a_composition_containing_defects_is_refused_not_returned(monkeypatch):
    monkeypatch.setattr(
        kircher_engine, "get_profile", lambda heretical: weakened_orthodox()
    )
    refusal = first_refusal(KircherEngine())
    assert refusal is not None, (
        "removing the parallel prohibition produced no parallels anywhere in the "
        "candidate matrix; this test can no longer exercise the refusal path"
    )
    _, _, error = refusal
    diagnostics = error.diagnostics
    assert diagnostics["defects"], "the failure must say what was wrong"
    assert all(d["intent"] == "defect" for d in diagnostics["defects"])
    assert {d["rule"] for d in diagnostics["defects"]} & {
        "parallel_fifth", "parallel_octave"
    }
    assert "search" in diagnostics and "progression" in diagnostics


def test_the_refusal_reaches_the_api_as_a_structured_error(client, monkeypatch):
    monkeypatch.setattr(
        kircher_engine, "get_profile", lambda heretical: weakened_orthodox()
    )
    refusal = first_refusal(KircherEngine())
    assert refusal is not None, "no configuration exercises the refusal path"
    mode, seed, _ = refusal
    response = client.post("/compose", json={
        "text": "a solemn procession through the vaults", "seed": seed,
        "mode": mode, "measures": 8,
    })
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "generation_defect"
    assert body["diagnostics"]["kind"] == "defect_found"
    assert body["diagnostics"]["defects"]


def test_the_guard_does_not_fire_on_ordinary_generation():
    """It must catch real faults without rejecting healthy compositions."""
    for mode in ModeName:
        composition = ENGINE.compose(
            text="a solemn procession through the vaults", seed=31,
            mode=mode.value, measures=8,
        )
        assert composition.validation.defects == []


@pytest.mark.parametrize("heretical", [False, True])
def test_the_contract_holds_for_both_profiles(heretical):
    composition = ENGINE.compose(
        text="Forbidden abyss where the covenant fractures", seed=13,
        measures=8, heretical=heretical,
    )
    assert composition.validation.defects == []
    assert composition.validation.passed is True
