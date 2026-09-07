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


def test_generation_failure_is_reported_as_a_structured_error(client, monkeypatch):
    import main
    from kircher_engine import GenerationError

    def fail(*args, **kwargs):
        raise GenerationError("bounded search exhausted", {"search": {"backtracks": 7}})

    monkeypatch.setattr(main.ENGINE, "compose", fail)
    response = client.post("/compose", json={"text": "x"})
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "generation_failed"
    assert body["diagnostics"]["search"]["backtracks"] == 7
