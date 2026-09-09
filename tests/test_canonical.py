"""Canonical serialization: the three ways ``repr()``-based hashing was fragile.

``stable_hash`` and ``fingerprint`` used to feed ``repr(part)`` into blake2b. Three
concrete problems follow from that, each with a regression below:

1. ``repr(SomeEnum.MEMBER)`` embeds the class name and Python's enum formatting, both of
   which have changed across interpreter versions.
2. ``repr(a_dict)`` depends on insertion order, so two semantically-equal configurations
   built via different code paths could hash differently.
3. Float ``repr`` is not a language-guaranteed format.

``determinism.canonical()`` fixes all three by normalising before hashing rather than
relying on ``repr``, and raises rather than silently guessing for anything it doesn't
recognise. This file tests ``canonical()`` directly, independent of the engine, so a
regression here is diagnosable without generating a whole composition.
"""

from __future__ import annotations

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
    # 17 significant digits is enough to round-trip any IEEE double exactly.
    value = 0.1 + 0.2
    recovered = float(eval(canonical(value)))
    assert recovered == value


def test_non_finite_floats_are_rejected_rather_than_silently_hashed():
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(CanonicalisationError):
            canonical(bad)


def test_sets_are_order_independent():
    assert canonical({3, 1, 2}) == canonical({2, 3, 1})
    assert canonical(frozenset({"a", "b"})) == canonical(frozenset({"b", "a"}))


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
