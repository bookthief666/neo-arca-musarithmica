"""B10 section 2/3: hostile-but-benign request inputs, and the error-response contract.

Goal per the B10 brief: "a predictable musical API", not security theater. Every case
here is something a real (if careless or adversarial) client could send by accident or
on purpose, and the bar is: never an unhandled 500, never a raw Python traceback or
exception object in the response, and always the same ``{error, message, diagnostics}``
envelope regardless of which layer rejected the request.
"""

from __future__ import annotations

import json

import pytest


def _post_raw(client, raw_json: str):
    return client.post(
        "/compose", content=raw_json.encode(), headers={"content-type": "application/json"}
    )


# --------------------------------------------------------------------------------------
# NaN / Infinity -- a literal token Python's own json.loads accepts by default
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("field, token", [
    ("density", "NaN"), ("density", "Infinity"), ("density", "-Infinity"),
    ("tempo", "Infinity"), ("tempo", "NaN"),
])
def test_nan_and_infinity_are_rejected_with_a_clean_422_not_a_500(client, field, token):
    response = _post_raw(client, f'{{"text":"x","measures":1,"{field}":{token}}}')
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["error"] == "invalid_request"
    # The offending value must never appear as a raw non-JSON-compliant float; json.loads
    # on our own response text must succeed at all (proves the body itself is valid JSON).
    json.loads(response.text)


def test_a_nan_diagnostic_is_still_informative_after_sanitisation(client):
    response = _post_raw(client, '{"text":"x","measures":1,"density": NaN}')
    body = response.json()
    rendered = json.dumps(body["diagnostics"])
    assert "nan" in rendered.lower()


# --------------------------------------------------------------------------------------
# Coercion surprises: documented, not necessarily "fixed"
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["yes", "true", "1", "on"])
def test_heretical_accepts_lax_truthy_strings_pydantic_v2_default(client, value):
    """Documented behaviour (docs/API.md), not a defect: Pydantic v2's lax bool
    coercion accepts these. A frontend should still only ever *send* a JSON boolean."""
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "heretical": value,
    })
    assert response.status_code == 200
    assert response.json()["configuration"]["heretical"] is True


def test_heretical_rejects_an_unrecognised_string(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "heretical": "banana",
    })
    assert response.status_code == 422


def test_seed_true_is_rejected_not_silently_widened_to_one(client):
    """A bool is an int subclass in Python; without the explicit guard in models.py,
    Pydantic's smart-union would silently accept `seed: true` as the integer seed 1."""
    response = client.post("/compose", json={"text": "x", "measures": 1, "seed": True})
    assert response.status_code == 422


# --------------------------------------------------------------------------------------
# Oversized / malformed structured fields
# --------------------------------------------------------------------------------------


def test_a_grossly_oversized_tonic_is_rejected_cleanly(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "tonic": "Q" * 100_000,
    })
    assert response.status_code == 422
    assert len(response.text) < 5000, "the oversized input must not be echoed verbatim"


def test_a_grossly_oversized_mode_is_rejected_cleanly(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "mode": "z" * 100_000,
    })
    assert response.status_code == 422
    assert len(response.text) < 5000


def test_text_beyond_max_length_is_rejected(client):
    response = client.post("/compose", json={"text": "a" * 100_000, "measures": 1})
    assert response.status_code == 422


def test_unknown_top_level_fields_are_rejected(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "totally_unexpected_field": 123,
    })
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_request"


def test_a_bare_huge_json_integer_literal_never_reaches_a_500(client):
    """A JSON body containing a >4300-digit bare integer literal (not a quoted string)
    is rejected by the ASGI stack's own body parsing before it ever reaches our models;
    it must still come back as a well-formed error, not a raw 500/connection drop."""
    response = _post_raw(client, '{"text":"x","measures":%s}' % ("7" * 5000))
    assert response.status_code in (400, 422)
    json.loads(response.text)  # still a parseable body


@pytest.mark.parametrize("value", [-5, 0])
def test_non_positive_measures_are_rejected(client, value):
    response = client.post("/compose", json={"text": "x", "measures": value})
    assert response.status_code == 422


def test_seed_as_a_float_is_rejected_not_silently_truncated(client):
    response = client.post("/compose", json={"text": "x", "measures": 1, "seed": 3.14})
    assert response.status_code == 422


def test_seed_as_a_list_is_rejected(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "seed": [1, 2, 3],
    })
    assert response.status_code == 422


# --------------------------------------------------------------------------------------
# The error envelope is consistent across every failure path
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("payload", [
    {"text": "x", "mode": "klingon"},
    {"text": "x", "meter": "7/16"},
    {"text": "x", "tonic": "H"},
    {"text": "x", "measures": 1, "unexpected": True},
    {"text": "x", "measures": 1, "seed": True},
])
def test_every_validation_failure_shares_the_same_envelope_shape(client, payload):
    response = client.post("/compose", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"error", "message", "diagnostics"}
    assert isinstance(body["error"], str) and body["error"]
    assert isinstance(body["message"], str) and body["message"]
    assert isinstance(body["diagnostics"], dict)


def test_request_validation_errors_no_longer_use_fastapis_bare_detail_shape(client):
    response = client.post("/compose", json={"text": "x", "mode": "klingon"})
    body = response.json()
    assert "detail" not in body
    assert body["error"] == "invalid_request"
    assert "errors" in body["diagnostics"]


def test_no_response_body_ever_contains_a_raw_traceback(client):
    for payload in (
        {"text": "x", "mode": "klingon"},
        {"text": "x", "measures": 1, "seed": "9" * 9000},
    ):
        response = client.post("/compose", json=payload)
        assert "Traceback" not in response.text
        assert "site-packages" not in response.text
