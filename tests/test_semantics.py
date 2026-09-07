"""POLYGRAPHIA: the text -> parameter mapping must be predictable and inspectable."""

from __future__ import annotations

import pytest

from semantics import (
    INSTRUMENTS, LEXICON, MODE_AFFINITY, analyze, lookup, normalize_text, stem,
    tokenize,
)
from theory import ModeName


def axes(text: str):
    return analyze(text).axes


def suggestion(text: str):
    return analyze(text).suggestion


# --------------------------------------------------------------------------------------
# Normalisation and lookup
# --------------------------------------------------------------------------------------


def test_normalisation_folds_case_accents_and_whitespace():
    assert normalize_text("  Sórrowful   LAMENT\n") == "sorrowful lament"
    assert tokenize("A dying, winter sun!") == ["a", "dying", "winter", "sun"]


def test_stemming_and_prefix_matching_reach_the_lexicon():
    assert stem("lamenting").startswith("lament")
    assert lookup("lamenting")[0] == "lament"
    assert lookup("cathedrals")[0] == "cathedral"
    assert lookup("sinking")[0] == "sinking"
    assert lookup("qqqzzz") is None


def test_the_lexicon_only_uses_declared_axes():
    from semantics import AXIS_NAMES

    for lexeme, deltas in LEXICON.items():
        unknown = set(deltas) - set(AXIS_NAMES)
        assert not unknown, f"{lexeme} references unknown axes {unknown}"
        assert all(-1.0 <= v <= 1.0 for v in deltas.values()), lexeme


# --------------------------------------------------------------------------------------
# The three target mappings from the specification
# --------------------------------------------------------------------------------------


def test_sorrow_maps_to_a_dark_slow_descending_configuration():
    grief = suggestion("Sorrowful lament beneath a dying winter sun")
    bright = suggestion("Radiant triumph ascending into golden heaven")
    assert grief.tempo < bright.tempo
    assert grief.contour_bias < 0, "a lament should tend downward"
    assert grief.register_shift <= bright.register_shift
    assert grief.density < bright.density
    assert grief.mode in (ModeName.PHRYGIAN, ModeName.AEOLIAN, ModeName.DORIAN)


def test_radiance_maps_to_a_bright_rising_configuration():
    bright = suggestion("Radiant triumph ascending into golden heaven")
    assert bright.contour_bias > 0
    assert bright.mode in (ModeName.IONIAN, ModeName.LYDIAN, ModeName.MIXOLYDIAN)
    assert bright.cadence_strength > 0.5


def test_transgression_maps_to_tension_and_the_left_hand_path():
    forbidden = analyze("Forbidden abyss where the covenant fractures")
    calm = analyze("A calm and holy dawn")
    assert forbidden.suggestion.heresy > calm.suggestion.heresy
    assert forbidden.suggestion.tension > calm.suggestion.tension
    assert forbidden.suggestion.mode in (ModeName.LOCRIAN, ModeName.PHRYGIAN)
    assert forbidden.suggestion.heretical is True
    assert calm.suggestion.heretical is False


def test_the_mapping_is_not_hardcoded_to_those_three_phrases():
    """Unseen sentences built from the same vocabulary must behave the same way."""
    a = suggestion("A grieving widow weeping in the buried dark")
    b = suggestion("Exultant bells and bright silver flight")
    assert a.tempo < b.tempo
    assert a.contour_bias < b.contour_bias
    assert a.mode != b.mode


# --------------------------------------------------------------------------------------
# Individual axes
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("low,high,axis", [
    ("still silence", "raging storm", "energy"),
    ("empty hollow", "a teeming swarm", "density"),
    ("the deep abyss below", "heaven above the tower", "register"),
    ("a sinking descent", "a rising ascent", "contour"),
    ("black night", "bright sun", "luminosity"),
    ("a fragile thin thread", "immense ancient stone", "weight"),
    ("pure holy chant", "profane blasphemous curse", "heresy"),
])
def test_axes_order_texts_as_expected(low, high, axis):
    assert getattr(axes(low), axis) < getattr(axes(high), axis), axis


def test_negation_inverts_the_following_term():
    assert axes("not radiant").valence < axes("radiant").valence
    assert axes("without sorrow").valence > axes("sorrow").valence


def test_intensifiers_and_diminishers_scale_the_following_term():
    assert axes("utterly radiant").valence > axes("radiant").valence
    assert axes("faintly radiant").valence < axes("radiant").valence


def test_modifiers_do_not_reach_across_an_unrelated_word():
    """'not' should colour the next lexeme, not everything after it."""
    assert axes("not gibberish radiant").valence > 0


# --------------------------------------------------------------------------------------
# Determinism and fallback
# --------------------------------------------------------------------------------------


def test_analysis_is_deterministic():
    first = analyze("A cathedral sinking into a black sea")
    second = analyze("A cathedral sinking into a black sea")
    assert first.as_dict() == second.as_dict()


def test_unknown_text_falls_back_deterministically_but_not_uniformly():
    a = analyze("qwrtp zxcvb mnbvc")
    b = analyze("qwrtp zxcvb mnbvc")
    c = analyze("plkjh ytrew asdfg")
    assert a.fallback_used and c.fallback_used
    assert a.as_dict() == b.as_dict()
    assert a.axes != c.axes, "every unknown text collapsed to the same configuration"


def test_partial_matches_do_not_trigger_the_fallback():
    analysis = analyze("qwrtp lament zxcvb")
    assert not analysis.fallback_used
    assert analysis.unmatched_tokens == ["qwrtp", "zxcvb"]
    assert [m.lexeme for m in analysis.matched_terms] == ["lament"]


def test_the_analysis_reports_its_own_reasoning():
    analysis = analyze("Sorrowful lament beneath a dying winter sun")
    assert analysis.normalized_text
    assert analysis.matched_terms
    assert set(analysis.mode_scores) == {m.value for m in ModeName}
    chosen = analysis.suggestion.mode.value
    assert analysis.mode_scores[chosen] == max(analysis.mode_scores.values())


# --------------------------------------------------------------------------------------
# Downstream recommendations
# --------------------------------------------------------------------------------------


def test_every_mode_has_an_affinity_vector():
    assert set(MODE_AFFINITY) == set(ModeName)


def test_instrumentation_is_drawn_from_the_declared_vocabulary():
    for text in ("Forbidden abyss", "Immense ancient stone cathedral",
                 "Swift bright dance", "A grieving lament", "quiet"):
        recommended = suggestion(text)
        assert recommended.ensemble in INSTRUMENTS
        assert set(recommended.instrumentation) == {"soprano", "alto", "tenor", "bass"}
        assert all(v in INSTRUMENTS for v in recommended.instrumentation.values())


def test_transgressive_texts_recommend_transgressive_timbres():
    assert suggestion("Forbidden blasphemous abyss").ensemble == "crusher"
    assert suggestion("An immense stone cathedral").ensemble == "organ"


def test_articulation_tracks_energy():
    assert suggestion("still quiet sleep").articulation in ("legato", "sostenuto")
    assert suggestion("raging swift storm").articulation in ("detached", "martellato")


def test_mode_is_structure_and_mood_is_metadata():
    """The mood label must never be confused with the mode's interval structure."""
    from theory import MODES

    for mode, spec in MODES.items():
        assert isinstance(spec.mood, str) and spec.mood
        assert len(spec.intervals) == 7
        assert spec.intervals[0] == 0
        assert sorted(spec.intervals) == list(spec.intervals)
    moods = {spec.mood for spec in MODES.values()}
    assert len(moods) == len(MODES), "each mode should carry a distinct mood label"
