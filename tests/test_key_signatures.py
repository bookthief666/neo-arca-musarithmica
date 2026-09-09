"""Key signatures follow the spelling of the final, not its pitch class.

``Speller.signature_sharps`` used to look the final up in a pitch-class table, which
collapsed every enharmonic pair and, worse, silently picked one member of each: G#
Ionian came back as four flats when it is eight sharps, and D# Ionian as three flats when
it is nine sharps.  Because the same value also chose the direction for spelling
chromatic pitches, the error propagated into the notes themselves.

The signature is now the circle-of-fifths position of the final *as written* -- each
sharp worth seven positions, each flat minus seven -- plus the mode's offset.  It can
legitimately exceed the seven accidentals a staff can carry, so a separate notatable
value handles what notation and MIDI must actually write.
"""

from __future__ import annotations

import base64

import pytest

from kircher_engine import ENGINE
from midi_export import build_score, composition_to_midi
from theory import MODES, ModeName, Speller

ENHARMONIC_PAIRS = [("C#", "Db"), ("F#", "Gb"), ("G#", "Ab"), ("D#", "Eb"), ("A#", "Bb")]

#: Independently known signatures, from the circle of fifths rather than from the code.
KNOWN_IONIAN = {
    "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6, "C#": 7,
    "F": -1, "Bb": -2, "Eb": -3, "Ab": -4, "Db": -5, "Gb": -6, "Cb": -7,
    "G#": 8, "D#": 9, "A#": 10,
}


# --------------------------------------------------------------------------------------
# The enharmonic distinction
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("sharp,flat", ENHARMONIC_PAIRS)
@pytest.mark.parametrize("mode", [m.value for m in ModeName])
def test_enharmonic_finals_get_different_signatures(sharp, flat, mode):
    sharp_side = Speller(sharp, ModeName(mode)).signature_sharps()
    flat_side = Speller(flat, ModeName(mode)).signature_sharps()
    assert sharp_side != flat_side, (
        f"{sharp} and {flat} {mode} both report {sharp_side}; the signature is being "
        f"derived from the pitch class rather than the spelling"
    )
    assert sharp_side > flat_side, (
        f"the sharp spelling {sharp} should sit higher on the circle of fifths than "
        f"{flat}, got {sharp_side} against {flat_side}"
    )
    assert sharp_side - flat_side == 12, "an enharmonic pair is twelve fifths apart"


@pytest.mark.parametrize("tonic,expected", sorted(KNOWN_IONIAN.items()))
def test_signatures_match_the_circle_of_fifths(tonic, expected):
    assert Speller(tonic, ModeName.IONIAN).signature_sharps() == expected


@pytest.mark.parametrize("tonic,expected", [
    ("A", 0), ("E", 1), ("D", -1), ("C", -3), ("Eb", -6), ("G#", 5),
])
def test_aeolian_signatures_are_three_flats_from_ionian(tonic, expected):
    assert Speller(tonic, ModeName.AEOLIAN).signature_sharps() == expected


def test_each_mode_offsets_its_ionian_by_the_documented_amount():
    for name, spec in MODES.items():
        ionian = Speller("C", ModeName.IONIAN).signature_sharps()
        actual = Speller("C", name).signature_sharps()
        assert actual - ionian == spec.signature_offset


# --------------------------------------------------------------------------------------
# Signatures notation cannot write
# --------------------------------------------------------------------------------------


def test_a_signature_beyond_seven_is_reported_honestly_not_hidden():
    speller = Speller("G#", ModeName.IONIAN)
    assert speller.signature_sharps() == 8
    assert speller.signature_is_notatable() is False
    assert speller.notatable_signature() == -4, "eight sharps is written as Ab's four flats"


def test_writable_signatures_are_left_alone():
    for tonic in ("C", "G", "F", "Bb", "F#", "Db"):
        speller = Speller(tonic, ModeName.IONIAN)
        assert speller.signature_is_notatable() is True
        assert speller.notatable_signature() == speller.signature_sharps()


def test_the_notatable_value_always_fits_a_staff():
    for tonic in list(KNOWN_IONIAN) + ["Db", "Gb", "Cb"]:
        for mode in ModeName:
            assert abs(Speller(tonic, mode).notatable_signature()) <= 7


# --------------------------------------------------------------------------------------
# The knock-on effect on chromatic spelling
# --------------------------------------------------------------------------------------


def test_a_sharp_final_spells_chromatic_pitches_with_sharps():
    """The old table said G# Ionian was flat-side, so its chromatics came out flat."""
    speller = Speller("G#", ModeName.IONIAN)
    names = [speller.name(m) for m in range(60, 72)]
    assert any("#" in n for n in names)
    assert not any(n.count("b") for n in names), (
        f"a final of G# should not spell its chromatic notes with flats: {names}"
    )


def test_a_flat_final_spells_chromatic_pitches_with_flats():
    speller = Speller("Db", ModeName.IONIAN)
    names = [speller.name(m) for m in range(60, 72)]
    assert any("b" in n for n in names)
    assert not any("#" in n for n in names), names


@pytest.mark.parametrize("tonic", ["C#", "Db", "F#", "Gb", "G#", "Ab"])
def test_diatonic_spelling_uses_each_letter_exactly_once(tonic):
    """A correct scale spelling walks the alphabet; it never repeats or skips a letter."""
    speller = Speller(tonic, ModeName.IONIAN)
    degrees = [
        speller.spell((speller.tonic_pc + i) % 12 + 60).step
        for i in MODES[ModeName.IONIAN].intervals
    ]
    assert len(set(degrees)) == 7, f"{tonic} major spells letters {degrees}"


# --------------------------------------------------------------------------------------
# End to end
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("tonic", ["C#", "Db", "F#", "Gb", "Bb", "Eb"])
def test_explicit_enharmonic_tonics_survive_a_full_composition(tonic):
    composition = ENGINE.compose(
        text="a solemn procession through the vaults", seed=5, tonic=tonic,
        mode="ionian", measures=6,
    )
    assert composition.config.tonic == tonic
    assert composition.validation.defects == []
    data = composition_to_midi(composition)
    assert data.startswith(b"MThd")


def test_the_two_spellings_produce_different_notation_but_the_same_sounds():
    sharp = ENGINE.compose(
        text="a solemn procession through the vaults", seed=5, tonic="F#",
        mode="ionian", measures=6,
    )
    flat = ENGINE.compose(
        text="a solemn procession through the vaults", seed=5, tonic="Gb",
        mode="ionian", measures=6,
    )
    sharp_pitches = [e.pitch for e in sharp.events[list(sharp.events)[0]]]
    flat_pitches = [e.pitch for e in flat.events[list(flat.events)[0]]]
    assert sharp_pitches != flat_pitches, "the two spellings should read differently"
    assert any("#" in p for p in sharp_pitches)
    assert any("b" in p for p in flat_pitches)


def test_the_score_carries_a_signature_a_staff_can_write():
    for tonic in ("G#", "D#", "A#", "C#", "Db"):
        composition = ENGINE.compose(
            text="a solemn procession", seed=5, tonic=tonic, mode="ionian", measures=4,
        )
        for part in build_score(composition).parts:
            for signature in part.recurse().getElementsByClass("KeySignature"):
                assert abs(signature.sharps) <= 7


def test_the_api_reports_both_the_true_and_the_writable_signature(client):
    response = client.post("/compose", json={
        "text": "a solemn procession", "seed": 5, "tonic": "G#",
        "mode": "ionian", "measures": 4,
    })
    assert response.status_code == 200
    score = response.json()["score"]
    assert score["key_signature_sharps"] == 8
    assert score["key_signature_notatable"] == -4
    assert score["key_signature_is_notatable"] is False


def test_a_conventional_key_reports_itself_as_writable(client):
    response = client.post("/compose", json={
        "text": "a solemn procession", "seed": 5, "tonic": "Bb",
        "mode": "ionian", "measures": 4,
    })
    score = response.json()["score"]
    assert score["key_signature_sharps"] == -2
    assert score["key_signature_notatable"] == -2
    assert score["key_signature_is_notatable"] is True
