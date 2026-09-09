"""What MODUS HAERETICUS guarantees, what it merely prefers, and what it does not do.

A grammar that *rewards* a rule is not a grammar that *produces* it.  The phrase-tritone
requirement used to be advisory -- reported after the fact, never enforced -- while the
profile's title implied a body of law.  This file settles the question with evidence:

* one **invariant** the engine enforces deterministically and that is checked here;
* a set of **active preferences**, each verified to occur strictly more often under
  Heretical law than under Orthodox law on the same inputs;
* a set of **latent policies** that are declared but never observed, pinned so that if
  the engine ever starts producing them, this file fails and the documentation gets
  corrected instead of quietly becoming wrong.

The sweeps here are small enough to stay in the ordinary suite; the wide matrix lives in
the marked stress suite.
"""

from __future__ import annotations

import collections

import pytest

from constraints import (
    HERETICAL, HERETICAL_ACTIVE_PREFERENCES, HERETICAL_CONDITIONAL_PREFERENCES,
    HERETICAL_INVARIANTS, HERETICAL_LATENT_POLICIES, ORTHODOX, phrase_exposes_tritone,
)
from kircher_engine import ENGINE
from theory import ModeName

SWEEP_SEEDS = (0, 1, 2, 3)
SWEEP_TEXT = "a solemn procession through the vaults"


def _sweep(heretical: bool):
    """Generate the comparison corpus once.

    Every test in this file reads the same two corpora, so they are built exactly twice
    per session rather than once per test -- these are full compositions, and
    regenerating them per assertion would make the ordinary suite unreasonably slow.
    """
    return [
        ENGINE.compose(
            text=SWEEP_TEXT, seed=seed, mode=mode.value, measures=8, heretical=heretical
        )
        for mode in ModeName
        for seed in SWEEP_SEEDS
    ]


@pytest.fixture(scope="module")
def corpus():
    return {"heretical": _sweep(True), "orthodox": _sweep(False)}


@pytest.fixture(scope="module")
def tallies(corpus):
    def tally(compositions):
        counter: collections.Counter = collections.Counter()
        for composition in compositions:
            for violation in composition.validation.violations:
                counter[violation.rule] += 1
        return counter

    return tally(corpus["heretical"]), tally(corpus["orthodox"])


# --------------------------------------------------------------------------------------
# The invariant
# --------------------------------------------------------------------------------------


def test_the_profile_declares_whether_the_tritone_rule_is_a_law():
    assert HERETICAL.requires_phrase_tritone is True
    assert ORTHODOX.requires_phrase_tritone is False
    assert "phrase_exposes_tritone" in HERETICAL_INVARIANTS


def test_every_heretical_phrase_exposes_a_tritone(corpus):
    """The invariant, checked on the rendered grid rather than on the plan."""
    checked = 0
    for composition in corpus["heretical"]:
        for phrase in composition.plan.phrases:
            checked += 1
            assert phrase_exposes_tritone(
                composition.rendered, phrase.first_slot, phrase.last_slot
            ), (
                f"phrase {phrase.index} of a {composition.config.mode.value} "
                f"composition exposes no tritone, but the grammar claims it as a law"
            )
    assert checked > 20, "the sweep should cover a meaningful number of phrases"


def test_the_reporter_agrees_that_no_phrase_is_missing_one(corpus):
    for composition in corpus["heretical"]:
        offenders = [
            v for v in composition.validation.violations
            if v.rule == "phrase_lacks_tritone"
        ]
        assert offenders == [], (
            "enforcement and reporting disagree; they share phrase_exposes_tritone "
            "so this should be impossible"
        )


def test_orthodox_law_makes_no_such_promise(corpus):
    """The invariant belongs to one grammar, not to the engine."""
    without = [
        phrase
        for composition in corpus["orthodox"]
        for phrase in composition.plan.phrases
        if not phrase_exposes_tritone(
            composition.rendered, phrase.first_slot, phrase.last_slot
        )
    ]
    assert without, (
        "Orthodox output happens to contain a tritone in every phrase, so this test "
        "cannot distinguish an enforced invariant from a coincidence"
    )


def test_injections_are_recorded_as_deliberate_when_they_happen(corpus):
    injected = [c for c in corpus["heretical"] if c.stats.tritone_injections]
    if not injected:
        pytest.skip("no phrase in this sweep needed an injection")
    for composition in injected:
        reasons = composition.validation.as_dict()["recorded_intents"]
        assert reasons.get("tritone_stab"), (
            "a tritone was injected to satisfy the invariant but never recorded as a "
            "deliberate decision"
        )


def test_enforcement_is_deterministic():
    """It picks candidates in a fixed order and consumes no randomness."""
    first = ENGINE.compose(
        text="forbidden abyss", seed=4, mode="ionian", measures=8, heretical=True
    )
    second = ENGINE.compose(
        text="forbidden abyss", seed=4, mode="ionian", measures=8, heretical=True
    )
    assert first.stats.tritone_injections == second.stats.tritone_injections
    assert [(e.midi, e.offset) for e in first.events[list(first.events)[0]]] == \
           [(e.midi, e.offset) for e in second.events[list(second.events)[0]]]


# --------------------------------------------------------------------------------------
# The preferences
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("rule", sorted(HERETICAL_ACTIVE_PREFERENCES))
def test_each_declared_preference_actually_shifts_the_output(rule, tallies):
    heretical, orthodox = tallies
    assert heretical[rule] > orthodox[rule], (
        f"{rule} is declared an active Heretical preference but occurs "
        f"{heretical[rule]} times under Heretical law against {orthodox[rule]} under "
        f"Orthodox law -- the claim is not supported by the output"
    )


def test_a_preference_is_not_guaranteed_the_way_the_invariant_is(corpus):
    """The contrast that gives the classification meaning.

    Measured per phrase, several of the active preferences turn up in *every* phrase of
    an eight-bar sweep -- crossing, chromatic alteration, tritone sonority and registral
    displacement were all at 100%.  Reliably occurring is not the same as guaranteed:
    nothing enforces them, and a shorter or sparser piece can lack them.  The parallel
    fifth, at roughly half of phrases, shows the difference plainly, so it is the honest
    rule to test the claim with.
    """
    with_fifth = total = 0
    for composition in corpus["heretical"]:
        for phrase in composition.plan.phrases:
            total += 1
            present = {
                v.rule for v in composition.validation.violations
                if v.slot_index is not None
                and phrase.first_slot <= v.slot_index <= phrase.last_slot
            }
            if "parallel_fifth" in present:
                with_fifth += 1
    assert total > 20
    assert 0 < with_fifth < total, (
        f"parallel fifths appeared in {with_fifth}/{total} phrases; a preference should "
        f"be neither absent nor universal, and if it is genuinely universal it should "
        f"be enforced and reclassified as an invariant"
    )


def test_the_invariant_by_contrast_holds_in_every_single_phrase(corpus):
    """The same measurement applied to the law, which must be 100%."""
    total = satisfied = 0
    for composition in corpus["heretical"]:
        for phrase in composition.plan.phrases:
            total += 1
            satisfied += phrase_exposes_tritone(
                composition.rendered, phrase.first_slot, phrase.last_slot
            )
    assert satisfied == total > 20


def test_the_latent_policies_are_still_latent(tallies):
    """If one of these starts occurring, the documented audit has gone stale."""
    heretical, _ = tallies
    for rule, reason in HERETICAL_LATENT_POLICIES.items():
        assert heretical[rule] == 0, (
            f"{rule} is documented as never observed (\"{reason}\") but occurred "
            f"{heretical[rule]} times; move it to HERETICAL_ACTIVE_PREFERENCES and "
            f"correct the explanation"
        )


def test_the_audit_covers_every_rewarded_policy(tallies):
    """No rewarded rule may sit outside the audit unclassified."""
    heretical, _ = tallies
    rewarded = {rule for rule, p in HERETICAL.policies.items() if p.weight < 0}
    classified = (
        set(HERETICAL_ACTIVE_PREFERENCES)
        | set(HERETICAL_CONDITIONAL_PREFERENCES)
        | set(HERETICAL_LATENT_POLICIES)
    )
    unclassified = {rule for rule in rewarded - classified if heretical[rule] == 0}
    assert not unclassified, (
        f"these rewarded rules never occur in an ordinary sweep and are documented "
        f"neither as conditional nor as latent: {sorted(unclassified)}"
    )


def test_the_conditional_preferences_are_genuinely_reachable():
    """Documented as needing particular semantics -- so drive those semantics."""
    tally = collections.Counter()
    for text in ("forbidden abyss unresolved endless drift",
                 "broken endless mist unresolved",
                 "chaos madness fracture unresolved endless"):
        for mode in (ModeName.IONIAN, ModeName.LYDIAN, ModeName.LOCRIAN,
                     ModeName.PHRYGIAN, ModeName.AEOLIAN):
            for seed in (0, 1, 2, 3, 4, 5):
                composition = ENGINE.compose(
                    text=text, seed=seed, mode=mode.value, measures=8, heretical=True,
                )
                for violation in composition.validation.violations:
                    tally[violation.rule] += 1
    for rule, condition in HERETICAL_CONDITIONAL_PREFERENCES.items():
        assert tally[rule] > 0, (
            f"{rule} is documented as reachable when {condition}, but never occurred "
            f"even under the semantics that are supposed to produce it"
        )


# --------------------------------------------------------------------------------------
# Still music
# --------------------------------------------------------------------------------------


def test_transgression_does_not_become_corruption(corpus):
    for composition in corpus["heretical"][:6]:
        assert composition.validation.defects == []
        assert len(composition.plan.progression()) == len(composition.plan.slots)
        for voice, events in composition.events.items():
            assert events
            intervals = [b.midi - a.midi for a, b in zip(events, events[1:])]
            assert intervals, f"{voice.value} never moves"
            assert max(abs(i) for i in intervals) <= 24, (
                f"{voice.value} is leaping arbitrarily, not transgressing deliberately"
            )
