"""Base64 MIDI export: valid bytes, re-parsable, and genuinely four separate tracks."""

from __future__ import annotations

import base64
import binascii
import io
import os
import tempfile

import pytest
from music21 import midi

from conftest import events_by_voice

from kircher_engine import ENGINE
from midi_export import (
    SCORE_ORDER, VOICE_CHANNELS, build_score, composition_to_base64,
    composition_to_midi, read_midi_notes, score_to_midi_bytes,
)
from semantics import INSTRUMENTS
from theory import Voice


@pytest.fixture(scope="module")
def composition():
    return ENGINE.compose(
        text="I dreamed of a cathedral sinking slowly into a black sea",
        seed=1650, measures=8,
    )


@pytest.fixture(scope="module")
def midi_bytes(composition) -> bytes:
    return composition_to_midi(composition)


def _reparse(data: bytes) -> midi.MidiFile:
    parsed = midi.MidiFile()
    parsed.openFileLike(io.BytesIO(data))
    parsed.read()
    parsed.close()
    return parsed


# --------------------------------------------------------------------------------------
# Base64 and file validity
# --------------------------------------------------------------------------------------


def test_base64_decodes_into_nonempty_midi_bytes(orthodox):
    encoded = orthodox["midi_base64"]
    assert encoded
    data = base64.b64decode(encoded, validate=True)
    assert len(data) > 100
    assert data.startswith(b"MThd"), "not a Standard MIDI File header"


def test_base64_is_strictly_valid(orthodox):
    try:
        base64.b64decode(orthodox["midi_base64"], validate=True)
    except binascii.Error as exc:  # pragma: no cover - a failure is the assertion
        pytest.fail(f"midi_base64 is not valid Base64: {exc}")


def test_the_helper_and_the_api_agree(composition, midi_bytes):
    assert base64.b64decode(composition_to_base64(composition)) == midi_bytes


# --------------------------------------------------------------------------------------
# Re-parsing
# --------------------------------------------------------------------------------------


def test_generated_midi_can_be_parsed_again_by_music21(midi_bytes):
    parsed = _reparse(midi_bytes)
    assert parsed.tracks
    assert parsed.ticksPerQuarterNote > 0


def test_voices_survive_as_separate_midi_tracks(midi_bytes):
    parsed = _reparse(midi_bytes)
    # One conductor track carrying tempo/meter, plus one track per voice.
    assert len(parsed.tracks) == 5, [t.index for t in parsed.tracks]
    restored = midi.translate.midiFileToStream(parsed)
    assert len(restored.parts) == 4


def test_every_note_survives_the_round_trip(composition, midi_bytes):
    tracks = read_midi_notes(midi_bytes)
    assert len(tracks) == 4, "expected one note-bearing track per voice"
    written = sorted(len(notes) for notes in tracks.values())
    expected = sorted(len(events) for events in composition.events.values())
    assert written == expected


def test_the_midi_sounds_exactly_what_the_engine_composed(composition, midi_bytes):
    """Pitch, onset and duration must agree note for note, voice for voice."""
    from_midi = sorted(
        tuple((n["pitch"], n["offset"], n["duration"]) for n in notes)
        for notes in read_midi_notes(midi_bytes).values()
    )
    from_engine = sorted(
        tuple((e.midi, e.offset, e.duration) for e in events)
        for events in composition.events.values()
    )
    assert from_midi == from_engine


def test_a_note_held_across_a_bar_line_stays_one_note(composition, midi_bytes):
    """A suspension tied over the bar must be one note-on, not two.

    music21 re-notates such a note as tied components, which is correct notation; the
    file itself must still contain a single sounding note.
    """
    long_notes = [
        (voice, event)
        for voice, events in composition.events.items()
        for event in events
        if event.duration > 2.0
    ]
    if not long_notes:
        pytest.skip("this composition contains no note longer than a half note")
    sounded = {
        (n["pitch"], n["offset"], n["duration"])
        for notes in read_midi_notes(midi_bytes).values() for n in notes
    }
    for _, event in long_notes:
        assert (event.midi, event.offset, event.duration) in sounded


def test_the_midi_describes_the_same_composition_as_the_json(orthodox):
    """Onsets and pitches in the MIDI must match the event payload voice for voice."""
    data = base64.b64decode(orthodox["midi_base64"])
    from_midi = sorted(
        tuple((n["pitch"], n["offset"]) for n in notes)
        for notes in read_midi_notes(data).values()
    )
    from_json = sorted(
        tuple((e["midi"], round(e["offset"], 6)) for e in events)
        for events in events_by_voice(orthodox).values()
    )
    assert from_midi == from_json


def test_midi_tracks_are_identifiable_by_voice(composition, midi_bytes):
    from music21 import midi as m21midi

    parsed = m21midi.MidiFile()
    parsed.openFileLike(io.BytesIO(midi_bytes))
    parsed.read()
    parsed.close()
    names = " ".join(
        str(event.data) for track in parsed.tracks for event in track.events
        if event.type == m21midi.MetaEvents.SEQUENCE_TRACK_NAME
    )
    for voice in SCORE_ORDER:
        assert voice.value.capitalize() in names, f"{voice.value} track is unlabelled"


# --------------------------------------------------------------------------------------
# Score construction
# --------------------------------------------------------------------------------------


def test_the_score_has_one_named_part_per_voice(composition):
    score = build_score(composition)
    assert [part.partName for part in score.parts] == \
        [voice.value.capitalize() for voice in SCORE_ORDER]
    assert len(set(VOICE_CHANNELS.values())) == 4


def test_each_part_carries_its_recommended_instrument(composition):
    score = build_score(composition)
    for part, voice in zip(score.parts, SCORE_ORDER):
        instruments = list(part.recurse().getElementsByClass("Instrument"))
        assert instruments
        expected = INSTRUMENTS[composition.config.instrumentation[voice.value]]
        assert instruments[0].midiProgram == expected["gm_program"]


def test_the_score_carries_tempo_meter_and_key(composition):
    score = build_score(composition)
    tempos = list(score.recurse().getElementsByClass("MetronomeMark"))
    assert tempos and tempos[0].number == composition.config.tempo
    meters = list(score.recurse().getElementsByClass("TimeSignature"))
    assert meters and meters[0].ratioString == composition.config.meter
    assert list(score.recurse().getElementsByClass("KeySignature"))


def test_pitches_are_spelled_for_the_mode_not_defaulted_to_sharps():
    composition = ENGINE.compose(
        text="A solemn procession", seed=5, tonic="Eb", mode="aeolian", measures=4
    )
    score = build_score(composition)
    names = {n.pitch.name for part in score.parts for n in part.recurse().notes}
    assert names, "no notes to inspect"
    assert not any("#" in name for name in names), (
        f"Eb aeolian should be spelled with flats, got {sorted(names)}"
    )


def test_velocities_are_carried_into_the_score(composition):
    score = build_score(composition)
    velocities = {n.volume.velocity for part in score.parts
                  for n in part.recurse().notes}
    assert velocities - {None}
    assert len(velocities) > 1, "every note has the same velocity"
    assert all(28 <= v <= 115 for v in velocities if v is not None)


# --------------------------------------------------------------------------------------
# Temporary files
# --------------------------------------------------------------------------------------


def test_serialisation_leaves_no_temporary_files_behind(composition):
    directory = tempfile.gettempdir()
    before = {n for n in os.listdir(directory) if n.startswith("neoarca-")}
    for _ in range(3):
        score_to_midi_bytes(build_score(composition))
    after = {n for n in os.listdir(directory) if n.startswith("neoarca-")}
    assert after == before


def test_a_failed_write_still_cleans_up(composition, monkeypatch):
    from midi_export import MidiExportError

    score = build_score(composition)
    directory = tempfile.gettempdir()
    before = {n for n in os.listdir(directory) if n.startswith("neoarca-")}

    def explode(*args, **kwargs):
        raise OSError("disk on fire")

    monkeypatch.setattr(type(score), "write", explode)
    with pytest.raises(MidiExportError):
        score_to_midi_bytes(score)
    after = {n for n in os.listdir(directory) if n.startswith("neoarca-")}
    assert after == before


@pytest.mark.parametrize("heretical", [False, True])
def test_both_law_profiles_export_valid_midi(heretical):
    composition = ENGINE.compose(
        text="Forbidden abyss where the covenant fractures",
        seed=13, measures=6, heretical=heretical,
    )
    data = composition_to_midi(composition)
    assert data.startswith(b"MThd")
    assert len(_reparse(data).tracks) == 5
