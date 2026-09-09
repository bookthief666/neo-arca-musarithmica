"""Cadence formulae claim only what they can support.

Historically a cadence in this repertoire is a **clausula**: a dyadic, intervallic event
in which two voices approach an octave or unison by step -- the *cantizans* rising a
semitone, the *tenorizans* falling a step, the *bassizans* a third below it leaping a
fourth down or a fifth up.  The identity of the cadence is that voice-leading.

The engine selects cadences as **pairs of scale degrees** and lets the voicing solver find
the voices.  That is a chordal reduction of a contrapuntal event, and naming one of the
pairs "phrygian" invites a reader to think otherwise.  These tests pin the classification
in code so the vocabulary cannot quietly overstate itself, and check the two claims the
implementation *can* make: the Phrygian close really does descend a semitone in the bass,
and the Locrian close really is our own invention.
"""

from __future__ import annotations

import pytest

from harmony import CADENCE_PROVENANCE, CadenceKind, cadence_provenance
from kircher_engine import ENGINE
from theory import ModeName, Voice

VALID_CLASSES = {"H0", "H1", "N1", "HAERETIC"}


def structural_bass(composition, slot_index: int) -> int:
    position = {slot.index: i for i, slot in enumerate(composition.plan.slots)}
    return composition.structural[position[slot_index]].pitch(Voice.BASS)


# --------------------------------------------------------------------------------------
# The classification exists and is complete
# --------------------------------------------------------------------------------------


def test_every_cadence_kind_is_classified():
    assert set(CADENCE_PROVENANCE) == set(CadenceKind), (
        "a cadence formula exists with no provenance classification; it would reach the "
        "API making an unbounded claim"
    )


@pytest.mark.parametrize("kind", list(CadenceKind))
def test_each_classification_is_a_known_class_with_a_reason(kind):
    provenance = cadence_provenance(kind)
    assert provenance.classification in VALID_CLASSES
    assert len(provenance.note) > 40, "a classification without an explanation is a label"


def test_only_the_authentic_close_claims_period_practice():
    """Everything else is ours, and must say so."""
    historical = {
        kind for kind in CadenceKind
        if cadence_provenance(kind).classification in {"H0", "H1"}
    }
    assert historical == {CadenceKind.AUTHENTIC}


def test_the_locrian_close_is_declared_an_invention():
    provenance = cadence_provenance(CadenceKind.PLAGAL_DIMINISHED)
    assert provenance.classification == "N1"
    assert "no historical warrant" in provenance.note.lower()


def test_the_phrygian_close_admits_it_is_not_a_clausula():
    provenance = cadence_provenance(CadenceKind.PHRYGIAN)
    assert provenance.classification == "N1"
    assert "clausula" in provenance.note.lower()


def test_the_heretical_closes_are_declared_transgressions():
    for kind in (CadenceKind.TRITONE_FALL, CadenceKind.SUSPENDED):
        assert cadence_provenance(kind).classification == "HAERETIC"


# --------------------------------------------------------------------------------------
# The claims the implementation *can* support
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4, 5])
def test_the_phrygian_close_really_does_fall_a_semitone_in_the_bass(seed):
    """The one genuinely characteristic gesture we do reproduce."""
    composition = ENGINE.compose(
        text="a solemn procession through the vaults", seed=seed, mode="phrygian",
        measures=8, heretical=False,
    )
    closes = [p for p in composition.plan.phrases
              if p.cadence is CadenceKind.PHRYGIAN]
    if not closes:
        pytest.skip("this seed produced no phrygian close")
    for phrase in closes:
        step = (structural_bass(composition, phrase.last_slot)
                - structural_bass(composition, phrase.last_slot - 1))
        assert step == -1, (
            f"the phrygian close moved {step:+d} in the bass; the descending semitone is "
            f"the gesture this formula exists to produce"
        )


def test_the_locrian_close_really_does_land_on_a_diminished_final():
    """Confirming what is being classified: the final triad is genuinely unstable."""
    composition = ENGINE.compose(
        text="a solemn procession", seed=3, mode="locrian", measures=8, heretical=False,
    )
    final = composition.plan.slots[-1]
    assert final.is_final
    assert final.triad.quality.value == "diminished"
    assert composition.plan.phrases[-1].cadence is CadenceKind.PLAGAL_DIMINISHED


def test_locrian_reports_a_reduced_cadence_ceiling():
    """The mode's inability to close firmly is modelled, not hidden."""
    from theory import MODES

    locrian = MODES[ModeName.LOCRIAN].cadence_ceiling
    assert locrian < min(
        spec.cadence_ceiling for name, spec in MODES.items()
        if name is not ModeName.LOCRIAN
    )


@pytest.mark.parametrize("mode", ["dorian", "aeolian", "mixolydian"])
def test_the_authentic_close_earns_its_h1_by_actually_raising_the_seventh(mode):
    composition = ENGINE.compose(
        text="a solemn procession through the vaults", seed=5, mode=mode, measures=8,
    )
    assert composition.plan.ficta_by_slot(), (
        f"{mode} claims an authentic close but never raised its seventh"
    )
    assert any("#" in label for label in composition.plan.progression())


# --------------------------------------------------------------------------------------
# It reaches the consumer
# --------------------------------------------------------------------------------------


def test_the_api_publishes_the_classification_with_every_phrase(client):
    response = client.post("/compose", json={
        "text": "a solemn procession", "seed": 3, "mode": "locrian", "measures": 8,
    })
    assert response.status_code == 200
    phrases = response.json()["score"]["phrases"]
    assert phrases
    for phrase in phrases:
        assert phrase["cadence_provenance"] in VALID_CLASSES
        assert phrase["cadence_note"]
    assert any(p["cadence_provenance"] == "N1" for p in phrases)


def test_a_consumer_can_tell_invented_closes_from_practised_ones(client):
    seen = {}
    for mode in ("ionian", "phrygian", "locrian"):
        response = client.post("/compose", json={
            "text": "a solemn procession", "seed": 3, "mode": mode, "measures": 8,
        })
        for phrase in response.json()["score"]["phrases"]:
            seen[phrase["cadence"]] = phrase["cadence_provenance"]
    assert seen, "no cadences observed"
    assert set(seen.values()) <= VALID_CLASSES
    # The distinction must actually be visible in real output, not just in the table.
    assert len(set(seen.values())) > 1, (
        f"every observed cadence carried the same classification ({seen}); the "
        f"distinction is not reaching consumers"
    )
