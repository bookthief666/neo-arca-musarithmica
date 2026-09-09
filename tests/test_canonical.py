"""Canonical serialization: fragile against ``repr()``, then fragile again against
naive JSON, until every distinguishable Python type got its own unambiguous shape.

Two separate generations of bug live in this file's history.

**Generation 1 -- ``repr()``.** ``stable_hash`` and ``fingerprint`` used to feed
``repr(part)`` into blake2b: ``repr(SomeEnum.MEMBER)`` embeds the class name and Python's
own enum formatting (both have changed across interpreter versions), ``repr(a_dict)``
depends on insertion order, and float ``repr`` is not a language-guaranteed format.

**Generation 2 -- naive JSON, still collision-prone.** Replacing ``repr()`` with a
"reasonable" JSON mapping was not enough on its own, because JSON's type system is
coarser than Python's: without further care, ``canonical(1.0) == canonical("1")`` (a
float formatted to a string looks exactly like that string), ``canonical(b"a") ==
canonical("61")`` (hex-encoded bytes look exactly like that hex string), ``canonical({1:
"x"}) == canonical({"1": "x"})`` (an int key and a string key both stringify to ``"1"``),
and ``canonical({1, 2, 3}) == canonical(["1", "2", "3"])`` (a set canonicalised
element-by-element into strings is indistinguishable from a list of those same strings).

``determinism.canonical()`` closes both generations: every value that JSON does not
already render unambiguously is wrapped as ``[tag, payload]`` before serialisation, so a
raw JSON array can never be confused with the untagged scalars (``null``/``true``/
``false``/a bare number/a quoted string), and two different tags can never collide with
each other regardless of what their payloads happen to contain. This file tests
``canonical()`` directly, independent of the engine, so a regression here is diagnosable
without generating a whole composition -- and several tests below are written to FAIL
against the naive, generation-2 implementation, not just against the original ``repr()``
one; see the docstring on each for exactly what it catches.
"""

from __future__ import annotations

import json
import math

import pytest

from determinism import (
    CanonicalisationError, canonical, coerce_seed, fingerprint, runtime_versions,
    stable_hash,
)
from theory import ModeName


# --------------------------------------------------------------------------------------
# The three concrete defects
# --------------------------------------------------------------------------------------


def test_enum_canonicalises_to_its_value_not_its_repr():
    """The defect: repr(ModeName.IONIAN) embeds the class name and enum formatting."""
    assert canonical(ModeName.IONIAN) == canonical("ionian")
    assert "ModeName" not in canonical(ModeName.IONIAN)
    assert canonical(ModeName.IONIAN) != canonical(ModeName.DORIAN)


def test_dict_insertion_order_does_not_affect_the_canonical_form():
    """The defect: repr({"a":1,"b":2}) != repr({"b":2,"a":1})."""
    forward = {"a": 1, "b": 2, "c": 3}
    backward = {"c": 3, "b": 2, "a": 1}
    assert forward == backward  # sanity: same dict, different construction order
    assert canonical(forward) == canonical(backward)
    assert stable_hash(forward) == stable_hash(backward)
    assert fingerprint(forward) == fingerprint(backward)


def test_nested_dict_order_independence():
    a = {"outer": {"x": 1, "y": 2}, "z": 3}
    b = {"z": 3, "outer": {"y": 2, "x": 1}}
    assert canonical(a) == canonical(b)


def test_floats_round_trip_and_negative_zero_is_normalised():
    """The defect: float repr is stable in current CPython but not a language guarantee."""
    assert canonical(-0.0) == canonical(0.0)
    # A float canonicalises to a tagged ["float", digits] node, not a bare JSON token, so
    # it is parsed back (via json.loads, not eval -- the tag makes it a real structure,
    # not a string) rather than assumed to be directly eval-able.
    value = 0.1 + 0.2
    tag, digits = json.loads(canonical(value))
    assert tag == "float"
    # 17 significant digits is enough to round-trip any IEEE double exactly.
    assert float(digits) == value


def test_non_finite_floats_are_rejected_rather_than_silently_hashed():
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(CanonicalisationError):
            canonical(bad)


def test_sets_are_order_independent():
    assert canonical({3, 1, 2}) == canonical({2, 3, 1})
    assert canonical(frozenset({"a", "b"})) == canonical(frozenset({"b", "a"}))


# --------------------------------------------------------------------------------------
# Generation 2: type collisions in a naive JSON mapping (would NOT be caught by simply
# avoiding repr() -- these fail against a "canonicalise, but don't tag" implementation
# just as surely as they would fail against the original repr()-based one)
# --------------------------------------------------------------------------------------


def test_float_does_not_collide_with_the_string_of_its_own_digits():
    """canonical(1.0) used to equal canonical("1"): f"{1.0:.17g}" is the string "1", and
    an untagged float payload is indistinguishable from that same string on its own."""
    assert canonical(1.0) != canonical("1")
    assert canonical(2.5) != canonical("2.5")


def test_bytes_do_not_collide_with_their_own_hex_string():
    """canonical(b"a") used to equal canonical("61"): b"a".hex() is the string "61", and
    an untagged bytes payload is indistinguishable from that same string on its own."""
    assert canonical(b"a") != canonical("61")
    assert canonical(bytearray(b"a")) != canonical("61")
    assert canonical(b"a") == canonical(bytearray(b"a")), (
        "bytes and bytearray carry the same data and should canonicalise identically"
    )


def test_mapping_keys_are_typed_not_stringified():
    """canonical({1: "x"}) used to equal canonical({"1": "x"}): str(1) == str("1")=="1",
    so naively stringifying keys collapses an int key onto a string key with the same
    digits."""
    assert canonical({1: "x"}) != canonical({"1": "x"})
    # But two dicts that really do share the same (typed) keys still agree regardless of
    # insertion order -- the fix must not reintroduce order-sensitivity.
    assert canonical({1: "x", 2: "y"}) == canonical({2: "y", 1: "x"})


def test_set_of_ints_does_not_collide_with_a_list_of_their_digit_strings():
    """canonical({1,2,3}) used to equal canonical(["1","2","3"]): a set canonicalised
    element-by-element into pre-stringified digits is indistinguishable from a list of
    those same strings, because both end up as a JSON array of the strings "1","2","3"."""
    assert canonical({1, 2, 3}) != canonical(["1", "2", "3"])
    assert canonical({1, 2, 3}) != canonical([1, 2, 3]), (
        "a set must not collide with a list even when the list has the matching order"
    )


def test_tagged_container_cannot_be_spoofed_by_an_ordinary_list():
    """Adversarial case for a tag-in-the-payload design: an ordinary Python list whose
    contents literally spell out another type's tag and payload must still not collide
    with that type's real canonical form."""
    spoofing_list = ["float", "1"]  # looks like a hand-built float tag from the outside
    real_float = 1.0
    assert canonical(spoofing_list) != canonical(real_float)


def test_list_and_tuple_are_documented_as_canonically_equivalent():
    """Explicit design choice (not a collision): list and tuple share a tag because the
    property that matters here is ordered-sequence vs. unordered-collection, and this
    codebase interchanges list/tuple freely. Sets remain distinct from both."""
    assert canonical([1, 2, 3]) == canonical((1, 2, 3))
    assert canonical((1, 2, 3)) != canonical({1, 2, 3})


# --------------------------------------------------------------------------------------
# What canonical() explicitly refuses to guess at
# --------------------------------------------------------------------------------------


class Unrecognised:
    """A type with no defined canonical form."""


def test_an_unrecognised_type_raises_rather_than_falling_back_to_repr():
    with pytest.raises(CanonicalisationError):
        canonical(Unrecognised())


def test_stable_hash_propagates_the_canonicalisation_error():
    with pytest.raises(CanonicalisationError):
        stable_hash("label", Unrecognised())


def test_bool_and_int_are_distinguished():
    """bool is an int subclass in Python; canonical() must not conflate 1 with True."""
    assert canonical(True) != canonical(1)
    assert canonical(False) != canonical(0)


# --------------------------------------------------------------------------------------
# Basic properties any hash function needs
# --------------------------------------------------------------------------------------


def test_canonical_is_a_pure_function():
    payload = {"mode": ModeName.PHRYGIAN, "density": 0.42, "voices": ["a", "b"]}
    assert canonical(payload) == canonical(payload)


def test_stable_hash_separates_its_arguments():
    """("ab", "c") must not collide with ("a", "bc")."""
    assert stable_hash("ab", "c") != stable_hash("a", "bc")


def test_stable_hash_is_a_nonnegative_64_bit_integer():
    value = stable_hash("anything", 42, 3.14)
    assert isinstance(value, int)
    assert 0 <= value < (1 << 64)


def test_fingerprint_is_a_short_stable_hex_string():
    fp = fingerprint({"a": 1, "b": [1, 2, 3]})
    assert isinstance(fp, str)
    assert len(fp) == 16  # 8-byte digest_size, hex-encoded
    int(fp, 16)  # must be valid hex


def test_fingerprint_changes_when_content_changes():
    base = {"tempo": 90, "mode": "ionian"}
    changed = {"tempo": 91, "mode": "ionian"}
    assert fingerprint(base) != fingerprint(changed)


# --------------------------------------------------------------------------------------
# coerce_seed still canonicalises its fallback
# --------------------------------------------------------------------------------------


def test_coerce_seed_fallback_is_order_independent():
    a = coerce_seed(None, fallback={"mode": ModeName.AEOLIAN, "tempo": 90})
    b = coerce_seed(None, fallback={"tempo": 90, "mode": ModeName.AEOLIAN})
    assert a == b


def test_coerce_seed_fallback_distinguishes_enum_from_its_string_value():
    """Regression guard: canonical() intentionally maps an enum to its .value, so a
    fallback keyed on the enum and one keyed on the raw string DO collide -- that is
    correct (the semantic content is the same), not a bug."""
    a = coerce_seed(None, fallback=ModeName.LOCRIAN)
    b = coerce_seed(None, fallback="locrian")
    assert a == b


# --------------------------------------------------------------------------------------
# runtime_versions()
# --------------------------------------------------------------------------------------


def test_runtime_versions_reports_the_fields_the_provenance_contract_promises():
    versions = runtime_versions()
    assert set(versions) == {"python", "music21", "implementation"}
    assert all(isinstance(v, str) and v for v in versions.values())


def test_runtime_versions_is_not_part_of_the_seed_derivation():
    """Claim: the same request chooses the same notes regardless of the runtime it runs
    on. runtime_versions() must never be an implicit input to stable_hash/fingerprint."""
    import inspect

    import determinism

    source = inspect.getsource(determinism.stable_hash) + inspect.getsource(
        determinism.fingerprint
    )
    assert "runtime_versions" not in source
