"""API contract: /health, /compose, overrides, and clean failure on bad input."""

from __future__ import annotations

import pytest

from conftest import VOICES_LOW_TO_HIGH, events_by_voice
from rhythm import SUPPORTED_METERS, meter_spec
from theory import ModeName


# --------------------------------------------------------------------------------------
# /health
# --------------------------------------------------------------------------------------


def test_health_succeeds(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["engine"] == "neo-arca-musarithmica"
    assert body["version"]
    assert set(body["modes"]) == {m.value for m in ModeName}
    assert set(body["meters"]) == set(SUPPORTED_METERS)
    assert set(body["law_profiles"]) == {"orthodox", "hereticus"}


# --------------------------------------------------------------------------------------
# /compose -- shape
# --------------------------------------------------------------------------------------


def test_compose_returns_four_named_voices(orthodox):
    voices = events_by_voice(orthodox)
    assert set(voices) == set(VOICES_LOW_TO_HIGH)
    for name, events in voices.items():
        assert events, f"{name} produced no notes"


def test_response_carries_every_contracted_section(orthodox):
    for section in ("engine", "provenance", "configuration", "semantics",
                    "score", "validation", "search", "midi_base64"):
        assert section in orthodox, f"missing {section}"
    assert orthodox["engine"]["law_profile"] == "orthodox"
    assert orthodox["engine"]["law_title"]


def test_events_are_ordered_gapless_and_cover_the_whole_piece(orthodox):
    total = orthodox["score"]["total_quarter_length"]
    spec = meter_spec(orthodox["score"]["meter"])
    assert total == pytest.approx(spec.measure_ql * orthodox["score"]["measures"])
    for name, events in events_by_voice(orthodox).items():
        cursor = 0.0
        for event in events:
            assert event["offset"] == pytest.approx(cursor), f"{name} has a gap/overlap"
            assert event["duration"] > 0
            assert 0 <= event["midi"] <= 127
            assert 0 <= event["velocity"] <= 127
            cursor += event["duration"]
        assert cursor == pytest.approx(total), f"{name} does not fill the piece"


@pytest.mark.parametrize("heretical", [False, True])
def test_every_event_is_finite_bounded_and_never_exceeds_the_composition(compose, heretical):
    """B10 section 5: offsets/durations are finite and nonnegative, sounding_duration is
    a valid fraction of the notated duration, and no event -- in either law profile --
    extends past the composition's own total_quarter_length."""
    import math

    body = compose(
        text="a forbidden abyss of chromatic anguish" if heretical
        else "a solemn procession through the vaulted cloister",
        heretical=heretical,
    )
    total = body["score"]["total_quarter_length"]
    for name, events in events_by_voice(body).items():
        for event in events:
            assert math.isfinite(event["offset"]) and event["offset"] >= 0
            assert math.isfinite(event["duration"]) and event["duration"] > 0
            assert math.isfinite(event["sounding_duration"])
            assert 0 < event["sounding_duration"] <= event["duration"] + 1e-9
            assert event["offset"] + event["duration"] <= total + 1e-6, (
                f"{name} event at {event['offset']} extends past total_ql={total}"
            )


def test_duration_seconds_is_consistent_with_total_ql_and_tempo(orthodox):
    """B10 section 5: score metadata is internally consistent."""
    score = orthodox["score"]
    expected = score["total_quarter_length"] * 60.0 / score["tempo"]
    # duration_seconds is rounded to 3 decimals on the wire (models.py); tolerance must
    # cover that rounding, not just floating-point noise.
    assert score["duration_seconds"] == pytest.approx(expected, abs=5e-4)


def test_every_note_belongs_to_a_declared_harmonic_slot(orthodox):
    slot_indices = {slot["index"] for slot in orthodox["score"]["slots"]}
    for events in events_by_voice(orthodox).values():
        for event in events:
            assert event["slot"] in slot_indices


def test_phrases_partition_the_measures(orthodox):
    phrases = orthodox["score"]["phrases"]
    assert phrases
    assert phrases[0]["first_measure"] == 0
    assert phrases[-1]["last_measure"] == orthodox["score"]["measures"] - 1
    for earlier, later in zip(phrases, phrases[1:]):
        assert later["first_measure"] == earlier["last_measure"] + 1


def test_semantic_analysis_is_inspectable(orthodox):
    semantics = orthodox["semantics"]
    assert semantics["normalized_text"] == semantics["normalized_text"].lower()
    assert semantics["tokens"]
    assert {m["lexeme"] for m in semantics["matched_terms"]} >= {"lament"}
    assert len(semantics["axes"]) == 10
    assert set(semantics["mode_scores"]) == {m.value for m in ModeName}
    assert semantics["suggestion"]["mode"] in semantics["mode_scores"]


# --------------------------------------------------------------------------------------
# /compose -- overrides
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("mode", [m.value for m in ModeName])
def test_explicit_mode_overrides_the_semantics(compose, mode):
    body = compose(text="Radiant triumph ascending", mode=mode)
    assert body["configuration"]["mode"] == mode
    assert body["score"]["mode"] == mode


@pytest.mark.parametrize("meter", SUPPORTED_METERS)
def test_explicit_meter_is_honoured_and_sizes_the_piece(compose, meter):
    body = compose(meter=meter, measures=6)
    assert body["score"]["meter"] == meter
    expected = meter_spec(meter).measure_ql * 6
    assert body["score"]["total_quarter_length"] == pytest.approx(expected)


def test_explicit_tonic_tempo_and_measures_are_honoured(compose):
    body = compose(tonic="F#", tempo=143, measures=5)
    assert body["configuration"]["tonic"] == "F#"
    assert body["configuration"]["tempo"] == 143
    assert body["score"]["measures"] == 5
    assert body["score"]["duration_seconds"] > 0


def test_explicit_density_overrides_the_semantics(compose):
    """B10 section 6: explicit density must override semantics, matching every other
    overridable field, and the response must let a consumer see both what the text
    suggested and what was actually used when they diverge."""
    suggested = compose(text="Sorrowful lament beneath a dying winter sun")
    suggested_density = suggested["semantics"]["suggestion"]["density"]
    forced = 0.05 if suggested_density > 0.5 else 0.95
    overridden = compose(
        text="Sorrowful lament beneath a dying winter sun", density=forced,
    )
    assert overridden["configuration"]["density"] == pytest.approx(forced)
    # The suggestion itself is untouched by the override -- the text's own analysis is
    # not overwritten by what the caller asked for.
    assert overridden["semantics"]["suggestion"]["density"] == pytest.approx(
        suggested_density
    )
    assert overridden["configuration"]["density"] != pytest.approx(suggested_density)


def test_response_distinguishes_suggested_from_effective_configuration(compose):
    """`semantics.suggestion` and `configuration` must genuinely be two different
    fields, not the same value copied twice -- the frontend needs both: what the text
    suggested, and what was actually used, and the two can legitimately disagree."""
    body = compose(text="Radiant triumph ascending", mode="phrygian", tempo=200)
    assert body["semantics"]["suggestion"]["mode"] != "phrygian" or body[
        "semantics"]["suggestion"]["tempo"] != 200, (
        "the override values coincide with the suggestion by chance; pick different "
        "override values so this test actually distinguishes the two"
    )
    assert body["configuration"]["mode"] == "phrygian"
    assert body["configuration"]["tempo"] == 200


def test_unspecified_parameters_come_from_the_semantics(compose):
    body = compose(text="Sorrowful lament beneath a dying winter sun")
    suggestion = body["semantics"]["suggestion"]
    config = body["configuration"]
    for field in ("mode", "tonic", "tempo", "meter", "density", "register_shift"):
        assert config[field] == suggestion[field], field


def test_heretical_flag_overrides_the_semantic_recommendation(compose):
    forced_off = compose(text="Forbidden abyss where the covenant fractures",
                         heretical=False)
    assert forced_off["configuration"]["heretical"] is False
    assert forced_off["engine"]["law_profile"] == "orthodox"

    forced_on = compose(text="A calm and holy dawn", heretical=True)
    assert forced_on["configuration"]["heretical"] is True
    assert forced_on["engine"]["law_profile"] == "hereticus"


def test_instrumentation_is_recommended_for_every_voice(orthodox):
    from semantics import INSTRUMENTS

    instrumentation = orthodox["configuration"]["instrumentation"]
    assert set(instrumentation) == set(VOICES_LOW_TO_HIGH)
    assert all(value in INSTRUMENTS for value in instrumentation.values())
    for voice in orthodox["score"]["voices"]:
        assert voice["instrument"] in INSTRUMENTS
        assert voice["instrument_name"] == INSTRUMENTS[voice["instrument"]]["name"]


# --------------------------------------------------------------------------------------
# /compose -- invalid input
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("payload", [
    {},                                       # text is required
    {"text": ""},                             # empty
    {"text": "   "},                          # whitespace only
    {"text": "x", "mode": "klingon"},         # unknown mode
    {"text": "x", "meter": "7/16"},           # unsupported meter
    {"text": "x", "tonic": "H"},              # not a note name
    {"text": "x", "tonic": "C####"},          # unparseable accidental
    {"text": "x", "tempo": 5},                # below the floor
    {"text": "x", "tempo": 900},              # above the ceiling
    {"text": "x", "measures": 0},             # too short
    {"text": "x", "measures": 500},           # too long
    {"text": "x", "density": 1.5},            # out of range
    {"text": "x", "seed": True},              # a bool is not a seed
    {"text": "x", "phrase_measures": 0},      # too short
    {"text": "x", "unexpected": "field"},     # unknown parameter
])
def test_invalid_requests_fail_cleanly(client, payload):
    response = client.post("/compose", json=payload)
    assert response.status_code == 422, response.text
    assert response.json()  # a structured body, not an empty crash


def test_invalid_request_never_reaches_the_engine(client, monkeypatch):
    import kircher_engine

    def explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("the engine was invoked with invalid input")

    monkeypatch.setattr(kircher_engine.ENGINE, "compose", explode)
    assert client.post("/compose", json={"text": "x", "mode": "nope"}).status_code == 422


def test_search_exhausted_generation_failure_is_reported_as_422(client, monkeypatch):
    """A bounded search that exhausted its budget is a property of *this request*, not
    an engine fault: a different seed/density/mode/measure count can succeed where this
    one didn't, so the client can usefully retry -- see kircher_engine.GenerationError
    and its `kind` (GENERATION_ERROR_KINDS)."""
    import main
    from kircher_engine import GenerationError

    def fail(*args, **kwargs):
        raise GenerationError(
            "bounded search exhausted", {"search": {"backtracks": 7}},
            kind="search_exhausted",
        )

    monkeypatch.setattr(main.ENGINE, "compose", fail)
    response = client.post("/compose", json={"text": "x"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "unrealizable_request"
    assert body["diagnostics"]["kind"] == "search_exhausted"
    assert body["diagnostics"]["search"]["backtracks"] == 7


def test_defect_found_generation_failure_is_reported_as_500(client, monkeypatch):
    """A relaxed search that returned a composition breaking the law it claims to
    follow is an implementation fault: retrying the identical request cannot fix it."""
    import main
    from kircher_engine import GenerationError

    def fail(*args, **kwargs):
        raise GenerationError(
            "the composition violates laws the active profile does not license",
            {"defects": [{"rule": "parallel_fifth"}]}, kind="defect_found",
        )

    monkeypatch.setattr(main.ENGINE, "compose", fail)
    response = client.post("/compose", json={"text": "x"})
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "generation_defect"
    assert body["diagnostics"]["kind"] == "defect_found"
    assert body["diagnostics"]["defects"]


def test_generation_error_defaults_to_the_defect_kind_when_unspecified(client, monkeypatch):
    """A safe default: a caller that constructs GenerationError without naming a kind
    is treated as an internal fault (500), never silently downgraded to a retryable
    422 -- the conservative direction to fail in."""
    import main
    from kircher_engine import GenerationError

    def fail(*args, **kwargs):
        raise GenerationError("unspecified failure", {})

    monkeypatch.setattr(main.ENGINE, "compose", fail)
    response = client.post("/compose", json={"text": "x"})
    assert response.status_code == 500
    assert response.json()["error"] == "generation_defect"
