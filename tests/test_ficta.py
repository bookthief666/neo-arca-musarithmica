"""Musica ficta is a cadential licence, not a change of scale.

Dorian, Mixolydian and Aeolian have a whole tone below the final, so their degree-V
triad cannot form a leading tone.  Sixteenth- and seventeenth-century practice raised
that third *at the cadence*, unwritten.  The defect this file guards against is treating
that raised pitch class as globally diatonic: once ``MusicalFrame`` carried a flat
``ficta_pcs`` set, a G# raised to lead into one cadence in A Aeolian stopped being a
chromatic alteration anywhere in the piece, and quietly joined the pool of ornamental
tones the diminution layer could reach for at will.

The licence is now per slot.  These tests demonstrate the distinction directly: the same
pitch, at two different slots, must be judged differently.
"""

from __future__ import annotations

import pytest

import constraints as law
from constraints import MomentContext, MusicalFrame, Rules, Sonority, collect_findings
from determinism import SeedStream
from harmony import build_plan
from kircher_engine import (
    ENGINE, ENGINE_VERSION, DiminutionEngine, GenesisConfig, KircherEngine, SearchStats,
)
from rhythm import meter_spec
from theory import MODES, VOICE_ORDER, VOICE_RANGES, ModeName, Voice, shifted_range

# A Aeolian: pitch classes {9,11,0,2,4,5,7}.  Its seventh degree is G (pc 7); raised by
# ficta it becomes G# (pc 8), which is *not* in the mode -- exactly the pitch whose scope
# is at issue.
TONIC_PC = 9
FICTA_PC = 8
FICTA_SLOT = 5
PLAIN_SLOT = 6

#: E major over A Aeolian -- the cadential dominant that ficta creates.
#: bass E3, tenor B3, alto E4, soprano G#4.
DOMINANT_PITCHES = (52, 59, 64, 68)


def frame_with_ficta():
    return MusicalFrame.build(
        TONIC_PC, ModeName.AEOLIAN, VOICE_RANGES,
        ficta_by_slot={FICTA_SLOT: {FICTA_PC}},
    )


def sonority_at(slot_index: int) -> Sonority:
    return Sonority(
        offset=float(slot_index),
        pitches=DOMINANT_PITCHES,
        chord_pcs=frozenset({4, 8, 11}),
        root_pc=4,
        third_pc=8,
        slot_index=slot_index,
    )


def chromatic_findings(frame, sonority):
    return [
        f for f in collect_findings(MomentContext(sonority), frame)
        if f.rule == Rules.CHROMATIC_ALTERATION
    ]


# --------------------------------------------------------------------------------------
# The rule-level distinction
# --------------------------------------------------------------------------------------


def test_the_raised_seventh_is_licensed_at_the_cadence_that_asked_for_it():
    frame = frame_with_ficta()
    assert chromatic_findings(frame, sonority_at(FICTA_SLOT)) == []


def test_the_same_pitch_elsewhere_is_still_a_chromatic_alteration():
    """The whole point: identical pitches, different slot, different judgement."""
    frame = frame_with_ficta()
    findings = chromatic_findings(frame, sonority_at(PLAIN_SLOT))
    assert findings, (
        "the ficta pitch was accepted at a slot that never asked for it -- the licence "
        "has leaked back to global scope"
    )
    assert {f.voices for f in findings} == {("soprano",)}
    assert str(FICTA_PC) in findings[0].detail


def test_a_frame_with_no_ficta_flags_the_pitch_everywhere():
    bare = MusicalFrame.build(TONIC_PC, ModeName.AEOLIAN, VOICE_RANGES)
    assert chromatic_findings(bare, sonority_at(FICTA_SLOT))
    assert chromatic_findings(bare, sonority_at(PLAIN_SLOT))


def test_licensed_ficta_is_empty_for_unlisted_slots():
    frame = frame_with_ficta()
    assert frame.licensed_ficta(FICTA_SLOT) == frozenset({FICTA_PC})
    assert frame.licensed_ficta(PLAIN_SLOT) == frozenset()
    assert frame.licensed_ficta(9999) == frozenset()
    # The union remains available for reporting, but no rule consults it.
    assert frame.ficta_pcs == frozenset({FICTA_PC})


# --------------------------------------------------------------------------------------
# The diminution layer must not borrow the pitch either
# --------------------------------------------------------------------------------------


def build_diminution(mode: str = "aeolian", seed: int = 5):
    engine = KircherEngine()
    config, _ = engine.configure(
        text="A solemn procession through the vaults", mode=mode,
        meter="4/4", measures=8,
    )
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
    diminution = DiminutionEngine(
        plan, frame, profile, config, root.derive("diminution"), SearchStats()
    )
    return diminution, plan, frame


def test_ornaments_may_use_the_raised_pitch_only_at_its_own_slot():
    diminution, plan, frame = build_diminution()
    licensed_slots = plan.ficta_by_slot()
    assert licensed_slots, "this mode should have produced a ficta cadence"

    ficta_slot = next(iter(licensed_slots))
    raised = next(iter(licensed_slots[ficta_slot]))
    other = next(s.index for s in plan.slots if s.index not in licensed_slots)

    at_cadence = {p % 12 for p in diminution._scale(Voice.SOPRANO, ficta_slot)}
    elsewhere = {p % 12 for p in diminution._scale(Voice.SOPRANO, other)}

    assert raised in at_cadence, "the cadence cannot reach its own leading tone"
    assert raised not in elsewhere, (
        "the raised seventh is available as an ornamental tone away from its cadence"
    )
    assert elsewhere < at_cadence, "the two pools should differ only by the ficta pitch"


# --------------------------------------------------------------------------------------
# Plan-level bookkeeping
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["dorian", "aeolian", "mixolydian"])
def test_only_slots_whose_triad_carries_ficta_are_licensed(mode):
    _, plan, _ = build_diminution(mode=mode)
    assert MODES[ModeName(mode)].needs_ficta
    by_slot = plan.ficta_by_slot()
    assert by_slot, f"{mode} closed without raising its seventh"
    for index, pcs in by_slot.items():
        slot = next(s for s in plan.slots if s.index == index)
        assert slot.triad.ficta, f"slot {index} licenses ficta but its triad has none"
        assert pcs == frozenset({slot.triad.third_pc})
    unlicensed = [s.index for s in plan.slots if s.triad.ficta and s.index not in by_slot]
    assert not unlicensed, f"ficta triads without a licence: {unlicensed}"


@pytest.mark.parametrize("mode", ["ionian", "lydian", "phrygian", "locrian"])
def test_modes_that_need_no_ficta_license_none(mode):
    _, plan, _ = build_diminution(mode=mode)
    assert plan.ficta_by_slot() == {}


# --------------------------------------------------------------------------------------
# End to end
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["dorian", "aeolian", "mixolydian"])
def test_generated_music_never_sounds_the_raised_seventh_unlicensed(mode):
    """Any occurrence of the ficta pitch outside its slot must be reported, not hidden."""
    composition = ENGINE.compose(
        text="A solemn procession through the vaults", mode=mode, seed=5, measures=8,
    )
    licensed = composition.plan.ficta_by_slot()
    raised = set().union(*licensed.values()) if licensed else set()
    assert raised, f"{mode} produced no ficta"

    reported = {
        (v.position, tuple(v.voices)) for v in composition.validation.violations
        if v.rule == "chromatic_alteration"
    }
    for voice, events in composition.events.items():
        for event in events:
            if event.midi % 12 not in raised:
                continue
            if event.slot_index in licensed:
                continue  # licensed here
            assert (event.offset, (voice.value,)) in reported, (
                f"{voice.value} sounds the ficta pitch at offset {event.offset} "
                f"(slot {event.slot_index}), which never licensed it, and no chromatic "
                f"alteration was reported"
            )
