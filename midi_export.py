"""midi_export.py -- music21 score construction and Standard MIDI File serialisation.

The composition already exists as structured events before this module runs; nothing
here makes musical decisions.  Its two jobs are to build a faithful ``music21.stream.Score``
-- one :class:`~music21.stream.Part` per voice, so the parts survive as separate MIDI
tracks -- and to serialise that score to bytes.

On serialisation: music21's ``.write()`` is a filesystem API.  Rather than assume an
in-memory writer exists, this module writes to a securely created temporary file, reads
the bytes back and removes the file in a ``finally`` block, so no orphan files are left
behind on any platform, including when the write itself raises.
"""

from __future__ import annotations

import base64
import io
import os
import tempfile
from typing import Dict, List, Sequence

from music21 import (
    clef, instrument, key, metadata, meter as m21meter, note as m21note, pitch as m21pitch,
    stream, tempo as m21tempo,
)

from kircher_engine import Composition, ENGINE_NAME, ENGINE_VERSION, NoteEvent
from semantics import INSTRUMENTS
from theory import Speller, Voice

#: Score order, top staff first.
SCORE_ORDER = (Voice.SOPRANO, Voice.ALTO, Voice.TENOR, Voice.BASS)

#: One MIDI channel per voice so the four parts remain separately addressable.
VOICE_CHANNELS: Dict[Voice, int] = {
    Voice.SOPRANO: 1, Voice.ALTO: 2, Voice.TENOR: 3, Voice.BASS: 4,
}

_CLEFS = {
    Voice.SOPRANO: clef.TrebleClef,
    Voice.ALTO: clef.TrebleClef,
    Voice.TENOR: clef.Treble8vbClef,
    Voice.BASS: clef.BassClef,
}


class MidiExportError(RuntimeError):
    """Raised when a score cannot be serialised to a Standard MIDI File."""


def _m21_pitch(speller: Speller, midi: int) -> m21pitch.Pitch:
    """Build a correctly *spelled* pitch rather than letting music21 guess sharps."""
    spelled = speller.spell(midi)
    p = m21pitch.Pitch()
    p.step = spelled.step
    p.octave = spelled.octave
    p.accidental = m21pitch.Accidental(spelled.alter)
    if p.midi != midi:  # pragma: no cover - spelling is exact by construction
        p = m21pitch.Pitch(midi=midi)
    return p


def build_part(
    voice: Voice,
    events: Sequence[NoteEvent],
    composition: Composition,
    *,
    lead: bool,
) -> stream.Part:
    """One voice as a :class:`~music21.stream.Part`, ready to become a MIDI track."""
    config = composition.config
    speller = Speller(config.tonic, config.mode)
    part = stream.Part(id=voice.value)
    part.partName = voice.value.capitalize()
    part.partAbbreviation = voice.value[0].upper()

    timbre = config.instrumentation[voice.value]
    inst = instrument.Instrument()
    # music21 names the MIDI track after the instrument, so carry the voice in the name:
    # the four parts must stay identifiable as SATB in any DAW that opens the file.
    inst.instrumentName = f"{voice.value.capitalize()} ({INSTRUMENTS[timbre]['name']})"
    inst.partName = part.partName
    inst.midiProgram = int(INSTRUMENTS[timbre]["gm_program"])
    inst.midiChannel = VOICE_CHANNELS[voice]
    part.insert(0.0, inst)

    part.insert(0.0, _CLEFS[voice]())
    # A staff and a MIDI key-signature meta event can only carry +/-7 accidentals;
    # G# Ionian's true eight sharps has to be written enharmonically.
    part.insert(0.0, key.KeySignature(speller.notatable_signature()))
    part.insert(0.0, m21meter.TimeSignature(config.meter))
    if lead:
        part.insert(0.0, m21tempo.MetronomeMark(number=config.tempo))

    for event in events:
        n = m21note.Note()
        n.pitch = _m21_pitch(speller, event.midi)
        n.quarterLength = event.duration
        n.volume.velocity = event.velocity
        n.lyric = None
        # Keep the generative role on the note so a downstream consumer of the score
        # (or a MusicXML export) can still see why a pitch is there.
        n.editorial.role = event.role
        part.insert(event.offset, n)

    part.makeMeasures(inPlace=True)
    return part


def build_score(composition: Composition) -> stream.Score:
    """The complete four-part score."""
    score = stream.Score()
    md = metadata.Metadata()
    md.title = composition.config.text.strip()[:120] or "Neo-Arca Musarithmica"
    md.composer = f"{ENGINE_NAME} {ENGINE_VERSION} ({composition.profile.name})"
    score.insert(0, md)
    for position, voice in enumerate(SCORE_ORDER):
        score.insert(0.0, build_part(
            voice, composition.events[voice], composition, lead=(position == 0)
        ))
    return score


def score_to_midi_bytes(score: stream.Score) -> bytes:
    """Serialise *score* as a Standard MIDI File.

    Uses a securely created temporary file and removes it in a ``finally`` block, so a
    failed write leaves nothing behind.
    """
    handle, path = tempfile.mkstemp(suffix=".mid", prefix="neoarca-")
    os.close(handle)
    try:
        score.write("midi", fp=path)
        with open(path, "rb") as fh:
            data = fh.read()
    except Exception as exc:  # noqa: BLE001 - re-raised as a domain error below
        raise MidiExportError(f"music21 failed to write a MIDI file: {exc}") from exc
    finally:
        try:
            os.unlink(path)
        except OSError:  # pragma: no cover - already gone
            pass
    if not data.startswith(b"MThd"):
        raise MidiExportError("music21 produced a file without a MIDI header")
    return data


def read_midi_notes(data: bytes) -> Dict[int, List[Dict[str, object]]]:
    """Decode a MIDI file into ``{track index: [{pitch, offset, duration}, ...]}``.

    Reads the note-on/note-off stream directly, in quarter-lengths.  This is what a
    player actually sounds, and it is deliberately *not* the same thing as re-notating
    the file: music21's ``midiFileToStream`` will split a note held across a bar line
    into tied notes, which is correct notation but would misrepresent the file's
    contents when comparing it against the event payload.
    """
    from music21 import midi as m21midi

    parsed = m21midi.MidiFile()
    parsed.openFileLike(io.BytesIO(data))
    try:
        parsed.read()
    finally:
        parsed.close()
    ticks = parsed.ticksPerQuarterNote or 1024
    tracks: Dict[int, List[Dict[str, object]]] = {}
    for track in parsed.tracks:
        elapsed = 0
        pending: Dict[int, int] = {}
        notes: List[Dict[str, object]] = []
        for event in track.events:
            if event.isDeltaTime():
                elapsed += event.time or 0
                continue
            is_on = (
                event.type == m21midi.ChannelVoiceMessages.NOTE_ON
                and (event.velocity or 0) > 0
            )
            is_off = (
                event.type == m21midi.ChannelVoiceMessages.NOTE_OFF
                or (event.type == m21midi.ChannelVoiceMessages.NOTE_ON
                    and (event.velocity or 0) == 0)
            )
            if is_on:
                pending[event.pitch] = elapsed
            elif is_off and event.pitch in pending:
                start = pending.pop(event.pitch)
                notes.append({
                    "pitch": event.pitch,
                    "offset": round(start / ticks, 6),
                    "duration": round((elapsed - start) / ticks, 6),
                })
        if notes:
            notes.sort(key=lambda n: (n["offset"], n["pitch"]))
            tracks[track.index] = notes
    return tracks


def composition_to_midi(composition: Composition) -> bytes:
    return score_to_midi_bytes(build_score(composition))


def composition_to_base64(composition: Composition) -> str:
    """The finished four-part composition as Base64-encoded Standard MIDI."""
    return base64.b64encode(composition_to_midi(composition)).decode("ascii")


__all__ = [
    "SCORE_ORDER", "VOICE_CHANNELS", "MidiExportError", "build_part", "build_score",
    "score_to_midi_bytes", "composition_to_midi", "composition_to_base64",
    "read_midi_notes",
]
