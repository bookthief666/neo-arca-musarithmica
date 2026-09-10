"""B10 section 1: the seed public-input boundary never reaches Python's own integer-
string conversion limit uncontrolled.

B9's stress matrix recorded a real defect: ``determinism._parse_decimal_seed`` calls
``int(text)`` on any string that looks like a bare decimal integer, and Python (3.11+)
refuses to convert an integer literal above ``sys.int_info.default_max_str_digits``
(4300) at all, raising a bare ``ValueError``. Through ``POST /compose`` this reached the
client as an unhandled 500, not a clean validation response.

``ComposeRequest`` now bounds a string ``seed`` to ``MAX_SEED_STRING_LENGTH`` (128
characters) *before* it is ever coerced -- see the constant's docstring in models.py for
why 128 was chosen (option (A) from the B10 brief: keep the existing masking-into-uint64
numeric grammar exactly as it was, bounded by a generous textual length cap applied
before ``int()``, rather than narrowing the public grammar to reject any seed a previous
version would have accepted).
"""

from __future__ import annotations

import pytest

from determinism import _SEED_MASK, coerce_seed
from models import MAX_SEED_STRING_LENGTH, ComposeRequest

UINT64_MAX = (1 << 64) - 1
assert UINT64_MAX == _SEED_MASK


# --------------------------------------------------------------------------------------
# The bound itself: unit level
# --------------------------------------------------------------------------------------


def test_the_bound_is_far_more_generous_than_any_legitimate_replay_seed_needs():
    """A resubmitted ``provenance.seed`` is a uint64 value, at most 20 decimal digits."""
    assert len(str(UINT64_MAX)) <= 20
    assert MAX_SEED_STRING_LENGTH >= 20 * 4  # generous headroom, not a tight fit


def test_the_bound_stays_far_below_pythons_own_integer_conversion_limit():
    import sys
    limit = getattr(sys, "get_int_max_str_digits", lambda: 4300)()
    assert MAX_SEED_STRING_LENGTH < limit


@pytest.mark.parametrize("length", [1, 20, 64, MAX_SEED_STRING_LENGTH])
def test_a_digit_string_at_or_under_the_bound_is_accepted(length):
    request = ComposeRequest(text="x", seed="9" * length)
    assert request.seed == "9" * length


@pytest.mark.parametrize("length", [MAX_SEED_STRING_LENGTH + 1, 500, 5000, 100_000])
def test_a_digit_string_over_the_bound_is_rejected_with_a_clean_error(length):
    with pytest.raises(ValueError, match="at most"):
        ComposeRequest(text="x", seed="9" * length)


@pytest.mark.parametrize("length", [MAX_SEED_STRING_LENGTH + 1, 5000])
def test_a_textual_seed_over_the_bound_is_also_rejected(length):
    """The length bound applies to *any* string seed, not only digit strings -- an
    unbounded textual seed is still an unbounded input, even though it never reaches
    ``int()``."""
    with pytest.raises(ValueError, match="at most"):
        ComposeRequest(text="x", seed="a" * length)


def test_a_textual_seed_at_the_bound_is_accepted_and_remains_textual():
    request = ComposeRequest(text="x", seed="a" * MAX_SEED_STRING_LENGTH)
    assert request.seed == "a" * MAX_SEED_STRING_LENGTH
    # Confirms it still resolves through the textual/hash path, not as a parse failure.
    resolved = coerce_seed(request.seed)
    assert isinstance(resolved, int)
    assert 0 <= resolved <= UINT64_MAX


def test_coerce_seed_itself_is_unbounded_only_the_api_boundary_is_capped():
    """The B10 brief is explicit: fix this at the public input boundary, not by
    narrowing ``coerce_seed``'s own semantics -- internal callers (tests, the stress
    harness) keep full flexibility; only ``ComposeRequest`` enforces the length cap."""
    # A digit string just past ComposeRequest's own bound still resolves at the
    # determinism-module level, proving the cap is a request-validation concern, not a
    # change to seed semantics.
    text = "9" * (MAX_SEED_STRING_LENGTH + 1)
    assert coerce_seed(text) == int(text) & _SEED_MASK


# --------------------------------------------------------------------------------------
# Through the real API
# --------------------------------------------------------------------------------------


def test_thousands_of_digits_returns_a_clean_422_not_a_500(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "seed": "7" * 5000,
    })
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "invalid_request"
    assert "128" in str(body["diagnostics"])


def test_just_beyond_the_limit_is_rejected(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "seed": "9" * (MAX_SEED_STRING_LENGTH + 1),
    })
    assert response.status_code == 422


def test_the_maximum_accepted_numeric_seed_length_still_generates(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "seed": "9" * MAX_SEED_STRING_LENGTH,
    })
    assert response.status_code == 200
    assert int(response.json()["provenance"]["seed"]) == (
        int("9" * MAX_SEED_STRING_LENGTH) & UINT64_MAX
    )


def test_a_large_textual_seed_at_the_bound_still_generates(client):
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "seed": "a" * MAX_SEED_STRING_LENGTH,
    })
    assert response.status_code == 200


def test_replay_of_a_legitimate_64bit_seed_is_unaffected_by_the_new_bound(client):
    """The bound must not disturb ordinary replay: generate with a seed above 2**53,
    read the resolved decimal-string seed back, and resubmit it verbatim."""
    large_seed = 2**60 + 777
    payload = {"text": "a solemn procession", "measures": 4, "seed": large_seed}
    original = client.post("/compose", json=payload).json()
    seed_text = original["provenance"]["seed"]
    assert len(seed_text) <= 20 <= MAX_SEED_STRING_LENGTH

    replay = client.post("/compose", json={**payload, "seed": seed_text}).json()
    assert replay["provenance"]["seed"] == original["provenance"]["seed"]
    assert replay["score"] == original["score"]


def test_error_response_never_leaks_a_raw_python_conversion_error(client):
    """The literal defect B9 found: an unhandled ValueError from Python's own
    int-string conversion limit must never reach the client as a bare 500."""
    response = client.post("/compose", json={
        "text": "x", "measures": 1, "seed": "3" * 10_000,
    })
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert "error" in body and "message" in body
    assert "Exceeds the limit" not in response.text  # no raw CPython error message
