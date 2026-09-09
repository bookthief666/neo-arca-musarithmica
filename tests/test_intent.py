"""Intentionality is evidence, not inference.

``validate`` used to set a single ``intended`` flag straight from the active profile's
policy, so *every* parallel fifth in a Heretical composition was reported as intentional
merely because MODUS HAERETICUS rewards parallel fifths as a class.  That tells you
nothing: an engine bug that produced parallel fifths by accident would have been labelled
deliberate too, which is exactly the case the flag exists to exclude.

Two independent questions are now asked and answered separately:

``licensed``
    does the active law permit this rule class?  A property of the profile.  Decides
    whether the composition passes.

``intent``
    how did *this occurrence* arise?  DELIBERATE only when the generator wrote down a
    decision that explains it; EMERGENT when the law licenses it but nothing sought it;
    DEFECT when it is an unlicensed error.
"""

from __future__ import annotations

import pytest

import constraints as law
from constraints import (
    HERETICAL, INTENT_RULES, Intent, IntentLedger, MusicalFrame, ORTHODOX, Rules,
    Sonority, validate,
)
from kircher_engine import ENGINE, TRANSGRESSIVE_FIGURES
from theory import ModeName, VOICE_RANGES

FRAME = MusicalFrame.build(0, ModeName.IONIAN, VOICE_RANGES)

HERETICAL_CASES = [
    ("Forbidden abyss where the covenant fractures", 13),
    ("Blasphemous machine grinding in the black vault", 404),
    ("A calm and holy dawn", 1),
]


def parallel_fifth_grid():
    """C major to D minor with bass and tenor locked a fifth apart -- a real parallel."""
    before = Sonority(
        offset=0.0, pitches=(48, 55, 64, 72), chord_pcs=frozenset({0, 4, 7}),
        root_pc=0, third_pc=4, slot_index=0,
    )
    after = Sonority(
        offset=2.0, pitches=(50, 57, 66, 74), chord_pcs=frozenset({2, 5, 9}),
        root_pc=2, third_pc=5, slot_index=1,
    )
    return [before, after]


# --------------------------------------------------------------------------------------
# The ledger's matching rules
# --------------------------------------------------------------------------------------


def test_a_record_only_explains_its_own_slot_rule_and_voices():
    ledger = IntentLedger()
    ledger.record(
        reason="chromatic_ornament", slot_index=5, voices=("soprano",),
        rules=INTENT_RULES["chromatic_ornament"],
    )
    explains = ledger.explanation

    assert explains(Rules.CHROMATIC_ALTERATION, ("soprano",), 5) is not None
    # Wrong slot.
    assert explains(Rules.CHROMATIC_ALTERATION, ("soprano",), 6) is None
    # Wrong voice: an ornament in the soprano cannot excuse the bass.
    assert explains(Rules.CHROMATIC_ALTERATION, ("bass",), 5) is None
    # Wrong rule class: a chromatic ornament does not excuse a parallel fifth.
    assert explains(Rules.PARALLEL_FIFTH, ("soprano",), 5) is None
    # No slot resolved at all.
    assert explains(Rules.CHROMATIC_ALTERATION, ("soprano",), None) is None


def test_an_ornament_in_one_voice_cannot_excuse_a_fault_between_two_others():
    """The precise failure mode of matching on place alone."""
    ledger = IntentLedger()
    ledger.record(
        reason="chromatic_ornament", slot_index=1, voices=("soprano",),
        rules=INTENT_RULES["chromatic_ornament"],
    )
    report = validate(parallel_fifth_grid(), FRAME, HERETICAL, ledger=ledger)
    fifths = [v for v in report.violations if v.rule == Rules.PARALLEL_FIFTH]
    assert fifths, "the test grid should contain a parallel fifth"
    assert all(v.intent is Intent.EMERGENT for v in fifths), (
        "a soprano ornament was allowed to claim credit for a bass/tenor parallel"
    )


# --------------------------------------------------------------------------------------
# The same finding, judged with and without evidence
# --------------------------------------------------------------------------------------


def test_the_identical_finding_is_emergent_without_a_record_and_deliberate_with_one():
    grid = parallel_fifth_grid()

    without = validate(grid, FRAME, HERETICAL, ledger=None)
    emergent = [v for v in without.violations if v.rule == Rules.PARALLEL_FIFTH]
    assert emergent and all(v.intent is Intent.EMERGENT for v in emergent)
    assert all(v.licensed for v in emergent), "Heretical law licenses parallel fifths"
    assert all(v.reason is None for v in emergent)

    ledger = IntentLedger()
    ledger.record(
        reason="alien_triad", slot_index=1, voices=("bass", "tenor"),
        rules=frozenset({Rules.PARALLEL_FIFTH}),
    )
    with_record = validate(grid, FRAME, HERETICAL, ledger=ledger)
    deliberate = [v for v in with_record.violations if v.rule == Rules.PARALLEL_FIFTH]
    assert deliberate and all(v.intent is Intent.DELIBERATE for v in deliberate)
    assert all(v.reason == "alien_triad" for v in deliberate)


def test_the_same_finding_under_orthodox_law_is_a_defect():
    report = validate(parallel_fifth_grid(), FRAME, ORTHODOX, ledger=None)
    fifths = [v for v in report.violations if v.rule == Rules.PARALLEL_FIFTH]
    assert fifths
    assert all(v.intent is Intent.DEFECT for v in fifths)
    assert all(not v.licensed for v in fifths)
    assert report.passed is False


def test_only_defects_fail_a_composition():
    heretical = validate(parallel_fifth_grid(), FRAME, HERETICAL, ledger=None)
    assert heretical.defects == []
    assert heretical.passed is True
    assert heretical.emergent_violations, "these should be licensed but unsought"


# --------------------------------------------------------------------------------------
# End to end
# --------------------------------------------------------------------------------------


def test_orthodox_generation_seeks_nothing_and_claims_nothing():
    composition = ENGINE.compose(
        text="A solemn procession through the vaults", seed=31, measures=8,
        heretical=False,
    )
    report = composition.validation
    assert report.as_dict()["recorded_intents"] == {}
    assert report.deliberate_violations == [], (
        "Orthodox generation recorded no decisions, so nothing can be deliberate"
    )
    assert report.defects == []


@pytest.mark.parametrize("text,seed", HERETICAL_CASES)
def test_heretical_generation_records_what_it_actually_chose(text, seed):
    composition = ENGINE.compose(text=text, seed=seed, measures=8, heretical=True)
    report = composition.validation
    recorded = report.as_dict()["recorded_intents"]
    assert recorded, "Modus Haereticus made no recorded transgressive decision at all"
    known = set(TRANSGRESSIVE_FIGURES.values()) | {"alien_triad", "heretical_cadence"}
    assert set(recorded) <= known, f"unrecognised decision kinds: {set(recorded) - known}"
    assert report.defects == []


@pytest.mark.parametrize("text,seed", HERETICAL_CASES)
def test_not_every_licensed_violation_is_claimed_as_deliberate(text, seed):
    """The regression: the old code stamped all of them intentional."""
    report = ENGINE.compose(
        text=text, seed=seed, measures=8, heretical=True
    ).validation
    licensed = len(report.licensed_violations)
    deliberate = len(report.deliberate_violations)
    assert licensed > 0
    assert deliberate < licensed, (
        f"all {licensed} licensed violations were claimed as deliberate; intent is "
        f"being inferred from the policy rather than from recorded decisions"
    )
    assert len(report.emergent_violations) == licensed - deliberate


@pytest.mark.parametrize("text,seed", HERETICAL_CASES)
def test_every_deliberate_violation_names_a_decision_that_was_recorded(text, seed):
    composition = ENGINE.compose(text=text, seed=seed, measures=8, heretical=True)
    report = composition.validation
    recorded = report.as_dict()["recorded_intents"]
    for violation in report.deliberate_violations:
        assert violation.reason is not None
        assert violation.reason in recorded, (
            f"{violation.rule} claims reason {violation.reason!r}, which the generator "
            f"never recorded"
        )
        assert violation.rule in INTENT_RULES[violation.reason], (
            f"{violation.reason} is not supposed to produce {violation.rule}"
        )


def test_intent_partitions_every_violation_exactly_once():
    composition = ENGINE.compose(
        text="Forbidden abyss where the covenant fractures", seed=13, measures=8,
        heretical=True,
    )
    report = composition.validation
    counts = report.counts_by_intent()
    assert sum(counts.values()) == len(report.violations)
    assert set(counts) == {i.value for i in Intent}


def test_the_api_exposes_both_axes(client):
    response = client.post("/compose", json={
        "text": "Forbidden abyss where the covenant fractures",
        "seed": 13, "measures": 8, "heretical": True,
    })
    assert response.status_code == 200
    validation = response.json()["validation"]
    for key in ("counts_by_intent", "defect_count", "deliberate_count",
                "emergent_count", "licensed_count", "recorded_intents"):
        assert key in validation, key
    assert validation["defect_count"] == 0
    assert validation["deliberate_count"] < validation["licensed_count"]
    for violation in validation["violations"]:
        assert violation["intent"] in {i.value for i in Intent}
        assert isinstance(violation["licensed"], bool)
        if violation["intent"] == Intent.DELIBERATE.value:
            assert violation["reason"]
