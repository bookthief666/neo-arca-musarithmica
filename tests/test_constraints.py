"""LEX MUSICA: the contrapuntal guarantees, checked independently of the engine.

The rule-engine unit tests below construct sonorities by hand and assert what the rules
report.  The composition tests re-derive parallel motion, crossing and range compliance
from the JSON response using the helpers in ``conftest``, which know nothing about
``constraints.py`` -- so a bug in the engine's own checker cannot hide a bug in its
output.
"""

from __future__ import annotations

import pytest

from conftest import (
    VOICES_LOW_TO_HIGH, crossings, events_by_voice, melodic_intervals,
    outer_motion_types, parallel_perfects, sample_grid,
)

import constraints as law
from constraints import (
    HERETICAL, MomentContext, MusicalFrame, ORTHODOX, Rules, Severity, Sonority,
    collect_findings, evaluate_moment, get_profile,
)
from theory import MODES, ModeName, VOICE_RANGES, Voice

FRAME = MusicalFrame.build(0, ModeName.IONIAN, VOICE_RANGES)

#: A handful of texts chosen to exercise different modes, meters and densities.
CASES = [
    ("Sorrowful lament beneath a dying winter sun", 418),
    ("Radiant triumph ascending into golden heaven", 7),
    ("I dreamed of a cathedral sinking slowly into a black sea", 1650),
    ("A thousand iron gears turning in the frost", 99),
    ("Still hollow silence under ancient stone", 2),
]


def _sonority(pitches, **kwargs):
    kwargs.setdefault("chord_pcs", frozenset({0, 4, 7}))
    kwargs.setdefault("root_pc", 0)
    kwargs.setdefault("third_pc", 4)
    return Sonority(offset=kwargs.pop("offset", 0.0), pitches=pitches, **kwargs)


# --------------------------------------------------------------------------------------
# Rule engine unit tests
# --------------------------------------------------------------------------------------


def test_parallel_fifths_are_detected():
    # C major -> D minor, bass and tenor a fifth apart throughout.
    before = _sonority((48, 55, 64, 72))
    after = _sonority((50, 57, 66, 74), offset=2.0,
                      chord_pcs=frozenset({2, 5, 9}), root_pc=2, third_pc=5)
    rules = {f.rule for f in collect_findings(MomentContext(after, before), FRAME)}
    assert Rules.PARALLEL_FIFTH in rules
    assert Rules.PARALLEL_OCTAVE in rules  # the outer voices move in octaves too


def test_oblique_motion_into_a_fifth_is_not_parallel():
    before = _sonority((48, 55, 64, 72))
    after = _sonority((48, 55, 65, 72), offset=2.0)
    rules = {f.rule for f in collect_findings(MomentContext(after, before), FRAME)}
    assert Rules.PARALLEL_FIFTH not in rules
    assert Rules.PARALLEL_OCTAVE not in rules


def test_contrary_motion_between_perfect_intervals_is_reported_separately():
    before = _sonority((48, 60, 64, 67))     # bass/tenor an octave apart
    after = _sonority((53, 65, 69, 72), offset=2.0,
                      chord_pcs=frozenset({5, 9, 0}), root_pc=5, third_pc=9)
    findings = {f.rule for f in collect_findings(MomentContext(after, before), FRAME)}
    assert Rules.PARALLEL_OCTAVE in findings  # both rose: genuinely parallel
    contrary = _sonority((60, 48, 64, 67), offset=2.0)
    assert contrary.pitches[0] > contrary.pitches[1]  # sanity: this one crosses


def test_voice_crossing_is_detected_and_measured():
    crossed = _sonority((60, 55, 64, 72))  # bass above tenor
    findings = [f for f in collect_findings(MomentContext(crossed), FRAME)
                if f.rule == Rules.VOICE_CROSSING]
    assert findings and findings[0].voices == ("bass", "tenor")
    assert findings[0].magnitude == 5.0


def test_range_violations_are_detected():
    too_low = _sonority((30, 55, 64, 72))
    findings = [f for f in collect_findings(MomentContext(too_low), FRAME)
                if f.rule == Rules.RANGE_VIOLATION]
    assert findings and findings[0].voices == ("bass",)


def test_a_chordal_diminished_fifth_is_not_an_unprepared_dissonance():
    """vii(dim)6 in B-D-F: the tritone is the harmony's, not a clash to forbid."""
    son = _sonority((50, 65, 71, 74), chord_pcs=frozenset({11, 2, 5}),
                    root_pc=11, third_pc=2)
    rules = {f.rule for f in collect_findings(MomentContext(son), FRAME)}
    assert Rules.HARMONIC_DISSONANCE in rules
    assert Rules.DISSONANT_SONORITY not in rules
    assert not evaluate_moment(MomentContext(son), FRAME, ORTHODOX).hard_failures


#: C3 G3 D4 C5 over a C major triad: the alto's D is a second above the bass and is not
#: a chord tone -- a genuine unprepared dissonance unless something explains it.
UNPREPARED = (48, 55, 62, 72)


def test_an_unprepared_non_chord_tone_is_a_hard_orthodox_failure():
    result = evaluate_moment(MomentContext(_sonority(UNPREPARED)), FRAME, ORTHODOX)
    assert not result.feasible
    assert any(v.rule == Rules.DISSONANT_SONORITY for v in result.hard_failures)


def test_the_same_dissonance_is_licensed_once_it_is_an_ornament():
    """The identical pitches pass once the alto's D is declared a passing tone."""
    son = _sonority(
        UNPREPARED, strong=False,
        roles=(law.ROLE_STRUCTURAL, law.ROLE_STRUCTURAL,
               law.ROLE_PASSING, law.ROLE_STRUCTURAL),
    )
    result = evaluate_moment(MomentContext(son), FRAME, ORTHODOX)
    assert result.feasible
    assert not any(v.rule == Rules.DISSONANT_SONORITY for v in result.hard_failures)


def test_an_ornament_does_not_license_dissonance_on_a_strong_beat():
    """A passing tone may clash off the beat; only a suspension may clash on it."""
    passing = _sonority(
        UNPREPARED, strong=True,
        roles=(law.ROLE_STRUCTURAL, law.ROLE_STRUCTURAL,
               law.ROLE_PASSING, law.ROLE_STRUCTURAL),
    )
    assert not evaluate_moment(MomentContext(passing), FRAME, ORTHODOX).feasible
    suspended = _sonority(
        UNPREPARED, strong=True,
        roles=(law.ROLE_STRUCTURAL, law.ROLE_STRUCTURAL,
               law.ROLE_SUSPENSION, law.ROLE_STRUCTURAL),
    )
    assert evaluate_moment(MomentContext(suspended), FRAME, ORTHODOX).feasible


def test_line_rules_require_ornaments_to_be_approached_and_left_by_step():
    stepwise = [(60, 0.0, law.ROLE_STRUCTURAL), (62, 1.0, law.ROLE_PASSING),
                (64, 2.0, law.ROLE_STRUCTURAL)]
    assert not [f for f in law.line_findings(Voice.SOPRANO, stepwise)
                if f.rule == Rules.NONCHORD_TONE_UNSTEPWISE]

    leapt_away = [(60, 0.0, law.ROLE_STRUCTURAL), (62, 1.0, law.ROLE_PASSING),
                  (69, 2.0, law.ROLE_STRUCTURAL)]
    assert [f for f in law.line_findings(Voice.SOPRANO, leapt_away)
            if f.rule == Rules.NONCHORD_TONE_UNSTEPWISE]


def test_a_sustaining_voice_is_not_a_repeated_note():
    """The line rules see attacks; three grid samples of one held note are one note."""
    held = [(60, 0.0, law.ROLE_STRUCTURAL), (64, 4.0, law.ROLE_STRUCTURAL)]
    assert not [f for f in law.line_findings(Voice.SOPRANO, held)
                if f.rule == Rules.REPEATED_NOTE_EXCESS]
    struck = [(60, 0.0, law.ROLE_STRUCTURAL), (60, 1.0, law.ROLE_STRUCTURAL),
              (60, 2.0, law.ROLE_STRUCTURAL)]
    assert [f for f in law.line_findings(Voice.SOPRANO, struck)
            if f.rule == Rules.REPEATED_NOTE_EXCESS]


# --------------------------------------------------------------------------------------
# The two profiles judge the same findings oppositely
# --------------------------------------------------------------------------------------


def test_the_profiles_invert_each_other_on_the_same_material():
    before = _sonority((48, 55, 64, 72))
    after = _sonority((50, 57, 66, 74), offset=2.0,
                      chord_pcs=frozenset({2, 5, 9}), root_pc=2, third_pc=5)
    ctx = MomentContext(after, before)
    orthodox = evaluate_moment(ctx, FRAME, ORTHODOX)
    heretical = evaluate_moment(ctx, FRAME, HERETICAL)
    assert not orthodox.feasible, "parallel perfects must be fatal under Orthodox law"
    assert heretical.feasible, "Modus Haereticus seeks them"
    assert heretical.penalty < 0 < orthodox.penalty


def test_heretical_keeps_range_and_gross_crossing_inviolable():
    out_of_range = _sonority((30, 55, 64, 72))
    assert not evaluate_moment(MomentContext(out_of_range), FRAME, HERETICAL).feasible
    collapsed = _sonority((70, 55, 64, 72))  # bass a major sixth above the tenor
    assert not evaluate_moment(MomentContext(collapsed), FRAME, HERETICAL).feasible


def test_get_profile_selects_the_law():
    assert get_profile(False) is ORTHODOX
    assert get_profile(True) is HERETICAL
    assert ORTHODOX.name == "orthodox" and HERETICAL.name == "hereticus"


# --------------------------------------------------------------------------------------
# Guarantees over real compositions
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("text,seed", CASES)
def test_orthodox_output_stays_within_the_satb_ranges(compose, text, seed):
    body = compose(text=text, seed=seed, heretical=False)
    for name, events in events_by_voice(body).items():
        limits = VOICE_RANGES[Voice(name)]
        for event in events:
            assert limits.low <= event["midi"] <= limits.high, (
                f"{name} sings MIDI {event['midi']} at offset {event['offset']}, "
                f"outside [{limits.low}, {limits.high}]"
            )


@pytest.mark.parametrize("text,seed", CASES)
def test_orthodox_output_has_no_voice_crossing(compose, text, seed):
    body = compose(text=text, seed=seed, heretical=False)
    assert crossings(body) == []


@pytest.mark.parametrize("text,seed", CASES)
def test_orthodox_output_has_no_parallel_fifths(compose, text, seed):
    body = compose(text=text, seed=seed, heretical=False)
    found = [p for p in parallel_perfects(body) if p["interval"] == "fifth"]
    assert found == []


@pytest.mark.parametrize("text,seed", CASES)
def test_orthodox_output_has_no_parallel_octaves(compose, text, seed):
    body = compose(text=text, seed=seed, heretical=False)
    found = [p for p in parallel_perfects(body) if p["interval"] == "octave"]
    assert found == []


@pytest.mark.parametrize("mode", [m.value for m in ModeName])
def test_every_mode_produces_lawful_orthodox_counterpoint(compose, mode):
    body = compose(text="A solemn procession through the vaults", mode=mode,
                   heretical=False, seed=31)
    assert parallel_perfects(body) == []
    assert crossings(body) == []
    assert body["validation"]["unintended_error_count"] == 0


@pytest.mark.parametrize("text,seed", CASES)
def test_the_engine_reports_its_own_output_as_lawful(compose, text, seed):
    body = compose(text=text, seed=seed, heretical=False)
    assert body["validation"]["passed"] is True
    assert body["validation"]["unintended_error_count"] == 0
    errors = [v for v in body["validation"]["violations"]
              if v["severity"] == Severity.ERROR.value]
    assert errors == []


def test_the_composition_closes_on_the_final(compose):
    body = compose(text="A solemn procession", heretical=False, seed=5)
    tonic_pc = body["configuration"]["tonic_pitch_class"]
    bass = events_by_voice(body)["bass"]
    assert bass[-1]["midi"] % 12 == tonic_pc


def test_musica_ficta_is_declared_when_a_mode_needs_a_leading_tone(compose):
    for mode in ("dorian", "aeolian", "mixolydian"):
        body = compose(text="A solemn procession", mode=mode, heretical=False, seed=5)
        assert MODES[ModeName(mode)].needs_ficta
        assert body["score"]["musica_ficta_pitch_classes"], (
            f"{mode} closed without raising its seventh"
        )
        assert any("#" in label for label in body["score"]["progression"])


# --------------------------------------------------------------------------------------
# The quality bar of section XXIV: four voices, not one melody in four registers
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("text,seed", CASES)
def test_voices_are_not_transpositions_of_one_another(compose, text, seed):
    """A melody copied into four registers would give four identical interval series."""
    body = compose(text=text, seed=seed)
    intervals = melodic_intervals(body)
    for a in VOICES_LOW_TO_HIGH:
        for b in VOICES_LOW_TO_HIGH:
            if a >= b:
                continue
            assert intervals[a] != intervals[b], f"{a} and {b} move identically"


@pytest.mark.parametrize("text,seed", CASES)
def test_the_outer_voices_genuinely_oppose_each_other(compose, text, seed):
    """Real counterpoint needs contrary and oblique motion, not only parallel thirds."""
    body = compose(text=text, seed=seed, heretical=False)
    tally = outer_motion_types(body)
    independent = tally["contrary"] + tally["oblique"]
    assert tally["contrary"] > 0, "bass and soprano never move in contrary motion"
    assert independent >= tally["similar"], (
        f"the outer voices move mostly in parallel: {tally}"
    )


def test_voices_can_move_at_different_times(compose):
    """Rhythmic independence: the four parts must not share one attack pattern."""
    body = compose(text="A thousand swarming gears in the frost", seed=11, density=0.6)
    onsets = {name: tuple(e["offset"] for e in events)
              for name, events in events_by_voice(body).items()}
    assert len(set(onsets.values())) > 1, "all four voices attack together throughout"


def test_the_surface_carries_more_than_block_chords(compose):
    """At least one composition in the set should show real diminution."""
    roles = set()
    for text, seed in CASES:
        body = compose(text=text, seed=seed, heretical=False)
        for events in events_by_voice(body).values():
            roles.update(e["role"] for e in events)
    assert roles - {"structural"}, "no ornaments survived anywhere"


# --------------------------------------------------------------------------------------
# MODUS HAERETICUS
# --------------------------------------------------------------------------------------


HERETICAL_CASES = [
    ("Forbidden abyss where the covenant fractures", 13),
    ("Blasphemous machine grinding in the black vault", 404),
    ("A calm and holy dawn", 1),  # forced heretical despite an orthodox text
]


@pytest.mark.parametrize("text,seed", HERETICAL_CASES)
def test_heretical_mode_produces_intended_violations_without_crashing(
    compose, text, seed
):
    body = compose(text=text, seed=seed, heretical=True)
    validation = body["validation"]
    assert validation["profile"] == "hereticus"
    assert validation["intended_violation_count"] > 0, (
        "Modus Haereticus produced nothing the Orthodox law would object to"
    )
    assert validation["unintended_error_count"] == 0, (
        "an unintended error is an implementation defect, not a transgression"
    )
    assert validation["passed"] is True


@pytest.mark.parametrize("text,seed", HERETICAL_CASES)
def test_heretical_violations_are_labelled_as_deliberate(compose, text, seed):
    body = compose(text=text, seed=seed, heretical=True)
    transgressive = {"parallel_fifth", "parallel_octave", "tritone_sonority",
                     "semitone_cluster", "chromatic_alteration", "voice_crossing",
                     "melodic_forbidden_interval", "dissonant_sonority"}
    seen = {v["rule"] for v in body["validation"]["violations"] if v["intended"]}
    assert seen & transgressive, f"no recognisable transgression: {seen}"
    for violation in body["validation"]["violations"]:
        if violation["rule"] in transgressive:
            assert violation["intended"] is True


def test_heretical_still_respects_the_voices_ranges(compose):
    for text, seed in HERETICAL_CASES:
        body = compose(text=text, seed=seed, heretical=True)
        for name, events in events_by_voice(body).items():
            limits = VOICE_RANGES[Voice(name)]
            for event in events:
                assert limits.low <= event["midi"] <= limits.high


def test_heretical_is_transgression_not_noise(compose):
    """It must still be a composition: bounded lines, a real harmonic plan, four parts."""
    body = compose(text="Forbidden abyss where the covenant fractures",
                   heretical=True, seed=13)
    assert len(body["score"]["progression"]) == len(body["score"]["slots"])
    assert body["score"]["phrases"]
    for name, intervals in melodic_intervals(body).items():
        assert intervals, f"{name} never moves"
        assert max(abs(i) for i in intervals) <= 24, f"{name} is jumping arbitrarily"
    grid = sample_grid(body)
    assert len(grid) >= len(body["score"]["slots"])


def test_the_two_profiles_diverge_on_identical_input(compose):
    kwargs = dict(text="A solemn procession through the vaults", seed=77,
                  mode="aeolian", tonic="D", meter="4/4")
    orthodox = compose(heretical=False, **kwargs)
    heretical = compose(heretical=True, **kwargs)
    assert orthodox["score"]["progression"] != heretical["score"]["progression"]
    assert (events_by_voice(orthodox)["soprano"]
            != events_by_voice(heretical)["soprano"])
    assert heretical["validation"]["intended_violation_count"] > \
        orthodox["validation"]["intended_violation_count"]
