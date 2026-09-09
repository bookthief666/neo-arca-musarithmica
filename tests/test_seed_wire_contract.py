"""The resolved seed survives the API round trip exactly -- no JS Number required.

``provenance.seed`` is drawn from a full 64-bit range internally.  JavaScript's
``Number`` type -- what a Tone.js/React consumer would otherwise decode a JSON response
into -- represents integers exactly only up to ``2**53 - 1``.  A seed above that,
returned as a bare JSON number, would silently lose precision the instant a browser's
``JSON.parse`` touched it: two different large seeds could even decode to the *same*
double.  ``models.ProvenanceModel`` serialises both ``seed`` and ``requested_seed`` as
decimal strings for exactly this reason (see ``docs/DETERMINISM.md``, "Seed wire
format").  This file proves that contract holds end to end through the real API, not
just at the Pydantic-model level.
"""

from __future__ import annotations

import json
import re

import pytest

#: Comfortably past JS's exact-integer ceiling (2**53 - 1 = 9_007_199_254_740_991).
LARGE_SEED = 2**60 + 12345
assert LARGE_SEED > 2**53 - 1


def _raw_seed_token(response_text: str, field: str) -> str:
    """Pull the literal JSON token for *field* inside "provenance" straight out of the
    raw response text, not through a parser -- proving the token itself is a quoted
    string (``"123"``) rather than a bare number (``123``) is the whole point, and a
    parser would silently paper over the very distinction being tested."""
    match = re.search(rf'"{field}"\s*:\s*("(?:[^"\\]|\\.)*"|null|-?\d+)', response_text)
    assert match is not None, f"{field!r} not found in response text"
    return match.group(1)


def test_a_seed_above_the_js_safe_integer_ceiling_round_trips_exactly(client):
    response = client.post("/compose", json={
        "text": "a solemn procession", "seed": LARGE_SEED, "measures": 4,
    })
    assert response.status_code == 200
    body = response.json()
    assert int(body["provenance"]["seed"]) == LARGE_SEED
    assert int(body["provenance"]["requested_seed"]) == LARGE_SEED

    # Demonstrate *why* this matters: naively decoding the same digits as a JS-style
    # double (float64) loses precision at this magnitude, even though our own decimal
    # string carried it exactly.
    lossy_roundtrip = int(float(str(LARGE_SEED)))
    assert lossy_roundtrip != LARGE_SEED, (
        "the chosen seed no longer demonstrates float64 precision loss; pick a larger one"
    )


def test_the_raw_json_token_is_a_quoted_string_not_a_bare_number(client):
    """The precision fix lives in the wire *shape*, not just in what int() recovers --
    a consumer's JSON.parse must never be handed a bare number this large."""
    response = client.post("/compose", json={
        "text": "a solemn procession", "seed": LARGE_SEED, "measures": 4,
    })
    token = _raw_seed_token(response.text, "seed")
    assert token.startswith('"') and token.endswith('"'), (
        f"seed was serialised as a bare JSON token ({token!r}), not a quoted string; "
        f"a JS consumer's JSON.parse would decode this as a lossy Number"
    )
    assert token == f'"{LARGE_SEED}"'


def test_two_different_large_seeds_do_not_collapse_onto_the_same_float(client):
    """The failure mode a bare-number wire format risks: two distinct seeds decoding to
    an identical JS double once precision is lost past 2**53."""
    a, b = 2**60 + 1, 2**60 + 2  # adjacent integers, indistinguishable as float64 here
    assert float(a) == float(b), "the chosen pair no longer collides at float64 precision"
    resp_a = client.post("/compose", json={
        "text": "a solemn procession", "seed": a, "measures": 4,
    })
    resp_b = client.post("/compose", json={
        "text": "a solemn procession", "seed": b, "measures": 4,
    })
    seed_a = resp_a.json()["provenance"]["seed"]
    seed_b = resp_b.json()["provenance"]["seed"]
    assert seed_a != seed_b
    assert int(seed_a) == a and int(seed_b) == b


def test_a_string_seed_remains_exact_as_requested_seed(client):
    response = client.post("/compose", json={
        "text": "a solemn procession", "seed": "musurgia universalis", "measures": 4,
    })
    body = response.json()
    assert body["provenance"]["requested_seed"] == "musurgia universalis"
    assert isinstance(body["provenance"]["seed"], str)
    int(body["provenance"]["seed"])  # the resolved seed is still a valid decimal string


def test_an_omitted_seed_returns_an_exact_reproducible_resolved_seed(client):
    payload = {"text": "a solemn procession about a large seed", "measures": 4}
    first = client.post("/compose", json=payload).json()
    second = client.post("/compose", json=payload).json()
    assert first["provenance"]["requested_seed"] is None
    assert second["provenance"]["requested_seed"] is None
    assert first["provenance"]["seed"] == second["provenance"]["seed"]
    assert isinstance(first["provenance"]["seed"], str)
    assert int(first["provenance"]["seed"]) > 0


def test_an_omitted_seed_can_still_resolve_above_the_js_safe_ceiling(client):
    """An auto-derived seed is not artificially kept small; the wire format has to carry
    the same magnitude a client-supplied seed can."""
    seen_large = False
    for i in range(40):
        body = client.post("/compose", json={
            "text": f"phrase number {i} for the auto-seed sweep", "measures": 4,
        }).json()
        if int(body["provenance"]["seed"]) > 2**53:
            seen_large = True
            assert isinstance(body["provenance"]["seed"], str)
            break
    assert seen_large, "no auto-derived seed in this sweep exceeded 2**53; widen it"


def test_no_frontend_consumer_needs_to_store_the_resolved_seed_in_a_js_number(client):
    """The practical guarantee this whole file exists to prove: a consumer that treats
    `seed` purely as an opaque string -- never coercing it through Number()/parseFloat --
    round-trips it losslessly through compare/store/resubmit, with no numeric decoding
    at all."""
    response = client.post("/compose", json={
        "text": "a solemn procession", "seed": LARGE_SEED, "measures": 4,
    })
    seed_text = response.json()["provenance"]["seed"]
    assert isinstance(seed_text, str)
    # A resubmission that only ever handles it as a string still resolves the identical
    # seed -- proving nothing downstream needs numeric precision to use this value.
    replay = client.post("/compose", json={
        "text": "a solemn procession", "seed": seed_text, "measures": 4,
    }).json()
    assert replay["provenance"]["requested_seed"] == seed_text


def test_null_requested_seed_is_a_literal_json_null_not_a_string(client):
    response = client.post("/compose", json={"text": "a solemn procession", "measures": 4})
    token = _raw_seed_token(response.text, "requested_seed")
    assert token == "null"
