"""The seed replay contract: a resolved seed read back from a response can actually be
resubmitted to reproduce the same composition -- not merely echoed back as text.

B8.1 made ``provenance.seed`` a JS-safe decimal string, which fixed *display* precision
but left a gap: ``coerce_seed`` still hashed every string -- digits included -- as a
textual seed, so resubmitting the exact string a client was handed produced a DIFFERENT
composition. B8.2 closes that gap: an unsigned decimal string is now numeric seed syntax
first (see ``determinism._parse_decimal_seed``), so ``seed=418`` and ``seed="418"``
resolve identically, and only a genuinely non-numeric string still falls through to
stable hashing. This file is the regression for that contract specifically; see
``tests/test_seed_wire_contract.py`` for the JS-number-precision property and
``tests/test_determinism.py`` for same-process/general determinism.
"""

from __future__ import annotations

from determinism import coerce_seed

#: Comfortably past JS's exact-integer ceiling (2**53 - 1 = 9_007_199_254_740_991), and
#: the same magnitude ``tests/test_seed_wire_contract.py`` uses for its own large seed.
LARGE_SEED = 2**60 + 98765
assert LARGE_SEED > 2**53 - 1


# ----------------------------------------------------------------------------------
# 1. A large numeric seed supplied as a decimal string resolves exactly.
# ----------------------------------------------------------------------------------


def test_a_large_decimal_string_seed_resolves_exactly():
    assert coerce_seed(str(LARGE_SEED)) == LARGE_SEED & ((1 << 64) - 1)


# ----------------------------------------------------------------------------------
# 2. An integer seed and its equivalent decimal-string form resolve to the same root
#    seed -- at unit level and through the real API.
# ----------------------------------------------------------------------------------


def test_integer_and_equivalent_decimal_string_seed_resolve_identically():
    assert coerce_seed(418) == coerce_seed("418")
    assert coerce_seed(LARGE_SEED) == coerce_seed(str(LARGE_SEED))
    # Leading zeros are permitted and insignificant, matching plain int() parsing.
    assert coerce_seed(7) == coerce_seed("007")


def test_integer_and_decimal_string_seed_produce_the_same_composition_via_the_api(client):
    payload = {"text": "a solemn procession", "measures": 4}
    as_int = client.post("/compose", json={**payload, "seed": 418}).json()
    as_str = client.post("/compose", json={**payload, "seed": "418"}).json()
    assert as_int["provenance"]["seed"] == as_str["provenance"]["seed"]
    assert as_int["score"]["voices"] == as_str["score"]["voices"]
    assert as_int["midi_base64"] == as_str["midi_base64"]


# ----------------------------------------------------------------------------------
# 3. Full replay proof: generate with a large seed, read provenance.seed back from the
#    JSON response, resubmit that exact string, and prove the resolved seed, the score
#    event JSON, and the MIDI bytes are all identical. This is the regression B8.1
#    intended to have but did not.
# ----------------------------------------------------------------------------------


def test_the_resolved_seed_read_back_from_a_response_replays_the_identical_composition(
    client,
):
    payload = {"text": "a solemn procession across a vaulted nave", "measures": 6,
               "seed": LARGE_SEED}
    original = client.post("/compose", json=payload).json()
    resolved_seed_text = original["provenance"]["seed"]
    assert isinstance(resolved_seed_text, str)
    int(resolved_seed_text)  # sanity: it is a valid decimal string

    replay = client.post("/compose", json={**payload, "seed": resolved_seed_text}).json()

    assert replay["provenance"]["seed"] == original["provenance"]["seed"]
    assert replay["score"] == original["score"]
    assert replay["midi_base64"] == original["midi_base64"]


# ----------------------------------------------------------------------------------
# 4. A nonnumeric textual seed remains a stable textual/hash seed -- the numeric-first
#    parsing rule must not reinterpret it.
# ----------------------------------------------------------------------------------


def test_a_nonnumeric_textual_seed_remains_a_stable_textual_seed():
    resolved = coerce_seed("musurgia universalis")
    assert resolved == coerce_seed("musurgia universalis")
    # It must not collide with any plausible numeric reading of the same characters.
    assert resolved != coerce_seed("0")

    # Signed decimal forms are deliberately rejected as numeric (see
    # determinism._parse_decimal_seed) and so remain textual/hashed, not parsed as
    # +/-5 -- this is the asymmetry documented in docs/DETERMINISM.md.
    assert coerce_seed("-5") != (-5 & ((1 << 64) - 1))
    assert coerce_seed("+5") != 5
    assert coerce_seed("-5") == coerce_seed("-5")


def test_a_nonnumeric_textual_seed_still_reproduces_via_the_api(client):
    payload = {"text": "a solemn procession", "measures": 4,
               "seed": "musurgia universalis"}
    first = client.post("/compose", json=payload).json()
    second = client.post("/compose", json=payload).json()
    assert first["provenance"]["requested_seed"] == "musurgia universalis"
    assert first["provenance"]["seed"] == second["provenance"]["seed"]
    assert first["score"] == second["score"]


# ----------------------------------------------------------------------------------
# 5. Two distinct large decimal-string seeds remain distinct.
# ----------------------------------------------------------------------------------


def test_two_distinct_large_decimal_string_seeds_remain_distinct():
    a, b = str(2**60 + 1), str(2**60 + 2)
    assert coerce_seed(a) != coerce_seed(b)


def test_two_distinct_large_decimal_string_seeds_produce_distinct_compositions(client):
    payload = {"text": "a solemn procession", "measures": 4}
    a = client.post("/compose", json={**payload, "seed": str(2**60 + 1)}).json()
    b = client.post("/compose", json={**payload, "seed": str(2**60 + 2)}).json()
    assert a["provenance"]["seed"] != b["provenance"]["seed"]
    assert a["score"] != b["score"]


# ----------------------------------------------------------------------------------
# 6. No JS Number conversion is required anywhere in the replay path: the resolved seed
#    can be handled as an opaque decimal string throughout, with plain int() parsing
#    (never float()) as the only thing ever applied to it, and only for sanity-checking
#    in this test file -- the production replay path itself never parses it at all.
# ----------------------------------------------------------------------------------


def test_no_js_number_conversion_is_required_to_replay_a_seed(client):
    payload = {"text": "a solemn procession", "measures": 4, "seed": LARGE_SEED}
    original = client.post("/compose", json=payload).json()
    seed_text = original["provenance"]["seed"]

    # A client that only ever treats the seed as an opaque string -- no float(), no
    # Number(), no JSON round trip through a double -- can still replay it exactly.
    assert isinstance(seed_text, str)
    lossy = int(float(seed_text))
    assert lossy != int(seed_text), (
        "the chosen seed no longer demonstrates float64 precision loss; pick a larger one"
    )

    replay = client.post("/compose", json={**payload, "seed": seed_text}).json()
    assert replay["provenance"]["seed"] == seed_text
    assert replay["score"] == original["score"]
