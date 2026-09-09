"""Determinism and provenance.

The contract: for identical semantic input, configuration, seed, law profile and engine
version, the engine emits an identical composition -- and it does so without touching
global randomness, so a request cannot be perturbed by anything else in the process.
"""

from __future__ import annotations

import random

import pytest

from conftest import events_by_voice, strip_timing

from determinism import SeedStream, coerce_seed, fingerprint, stable_hash
from kircher_engine import ENGINE, ENGINE_VERSION


# --------------------------------------------------------------------------------------
# Seed primitives
# --------------------------------------------------------------------------------------


def test_stable_hash_is_stable_and_separates_its_parts():
    assert stable_hash("a", "b") == stable_hash("a", "b")
    assert stable_hash("ab", "c") != stable_hash("a", "bc")
    assert stable_hash(1) != stable_hash("1")


def test_seed_streams_depend_only_on_root_and_label_path():
    a = SeedStream(418)
    b = SeedStream(418)
    # Draw the children in a different order: the labels, not the order, decide.
    first = [a.derive("bass", i).randint(0, 999) for i in range(4)]
    second = [b.derive("bass", i).randint(0, 999) for i in reversed(range(4))][::-1]
    assert first == second
    assert SeedStream(419).derive("bass", 0).randint(0, 999) != first[0]


def test_derived_streams_are_independent_of_one_another():
    root = SeedStream(7)
    before = root.derive("harmony").randint(0, 10**6)
    root.derive("diminution").randint(0, 10**6)  # consuming one must not move the other
    assert SeedStream(7).derive("harmony").randint(0, 10**6) == before


def test_string_seeds_are_hashed_stably_and_differ_from_integers():
    assert coerce_seed("lament") == coerce_seed("lament")
    assert coerce_seed("lament") != coerce_seed("triumph")
    assert coerce_seed(418) == 418


def test_a_bool_is_rejected_as_a_seed():
    with pytest.raises(TypeError):
        coerce_seed(True)


def test_weighted_order_is_a_permutation():
    stream = SeedStream(3)
    items = list("abcdefgh")
    ordered = stream.weighted_order(items, [8, 7, 6, 5, 4, 3, 2, 1])
    assert sorted(ordered) == sorted(items)
    assert SeedStream(3).weighted_order(items, [8, 7, 6, 5, 4, 3, 2, 1]) == ordered


def test_fingerprint_ignores_key_order():
    assert fingerprint({"a": 1, "b": 2}) == fingerprint({"b": 2, "a": 1})
    assert fingerprint({"a": 1}) != fingerprint({"a": 2})


# --------------------------------------------------------------------------------------
# End-to-end reproducibility
# --------------------------------------------------------------------------------------

REQUEST = {
    "text": "I dreamed of a cathedral sinking slowly into a black sea",
    "seed": 1650,
    "measures": 8,
}


def test_identical_requests_produce_identical_compositions(compose):
    first = compose(**REQUEST)
    second = compose(**REQUEST)
    assert strip_timing(first) == strip_timing(second)


def test_identical_requests_produce_identical_midi(compose):
    assert compose(**REQUEST)["midi_base64"] == compose(**REQUEST)["midi_base64"]


def test_different_seeds_produce_different_compositions(compose):
    seen = set()
    for seed in (1, 2, 3, 4, 5):
        body = compose(**{**REQUEST, "seed": seed})
        seen.add(tuple(
            (e["midi"], e["offset"]) for e in events_by_voice(body)["soprano"]
        ))
    assert len(seen) >= 4, "different seeds collapsed onto the same soprano line"


def test_string_seeds_work_end_to_end(compose):
    first = compose(**{**REQUEST, "seed": "musurgia universalis"})
    second = compose(**{**REQUEST, "seed": "musurgia universalis"})
    other = compose(**{**REQUEST, "seed": "polygraphia nova"})
    assert strip_timing(first) == strip_timing(second)
    assert first["midi_base64"] != other["midi_base64"]
    assert first["provenance"]["requested_seed"] == "musurgia universalis"
    # Wire-safe: the resolved seed is a decimal string, not a JSON number, so a value
    # near the top of the 64-bit range survives a browser's JSON parser exactly. See
    # tests/test_seed_wire_contract.py for the full round-trip proof.
    assert isinstance(first["provenance"]["seed"], str)
    assert int(first["provenance"]["seed"]) > 0


def test_an_omitted_seed_is_still_reproducible(compose):
    payload = {"text": "A silver bell above the frost", "measures": 6,
               "seed": None}
    first = compose(**payload)
    second = compose(**payload)
    assert strip_timing(first) == strip_timing(second)
    assert first["provenance"]["requested_seed"] is None
    assert isinstance(first["provenance"]["seed"], str)
    assert int(first["provenance"]["seed"]) > 0


def test_the_law_profile_changes_the_composition_under_the_same_seed(compose):
    orthodox = compose(**REQUEST, heretical=False)
    heretical = compose(**REQUEST, heretical=True)
    assert orthodox["provenance"]["seed"] == heretical["provenance"]["seed"]
    assert orthodox["provenance"]["law_profile"] == "orthodox"
    assert heretical["provenance"]["law_profile"] == "hereticus"
    assert orthodox["midi_base64"] != heretical["midi_base64"]


def test_provenance_records_everything_needed_to_reconstruct(compose):
    body = compose(**REQUEST)
    provenance = body["provenance"]
    assert provenance["engine_version"] == ENGINE_VERSION
    # Wire-safe decimal string, not a JSON number -- see test_seed_wire_contract.py.
    assert provenance["seed"] == "1650"
    assert int(provenance["seed"]) == 1650
    assert provenance["law_profile"] == body["configuration"]["law_profile"]
    assert provenance["config_fingerprint"]
    # The fingerprint tracks the configuration, not the seed.
    other_seed = compose(**{**REQUEST, "seed": 999})
    assert other_seed["provenance"]["config_fingerprint"] == \
        provenance["config_fingerprint"]
    other_config = compose(**{**REQUEST, "tempo": 61})
    assert other_config["provenance"]["config_fingerprint"] != \
        provenance["config_fingerprint"]


# --------------------------------------------------------------------------------------
# No global randomness
# --------------------------------------------------------------------------------------


def test_composition_does_not_touch_the_global_random_state():
    random.seed(12345)
    before = random.getstate()
    ENGINE.compose(text="A thousand iron gears", seed=5, measures=6)
    assert random.getstate() == before, "the engine used module-level randomness"


def test_the_global_random_seed_cannot_influence_the_result():
    random.seed(1)
    first = ENGINE.compose(text="A thousand iron gears", seed=5, measures=6)
    random.seed(999999)
    second = ENGINE.compose(text="A thousand iron gears", seed=5, measures=6)
    for voice in first.events:
        assert [(e.midi, e.offset) for e in first.events[voice]] == \
            [(e.midi, e.offset) for e in second.events[voice]]


def test_repeated_composition_is_stable_across_many_runs():
    reference = None
    for _ in range(5):
        composition = ENGINE.compose(
            text="Forbidden abyss", seed="alpha", measures=6, heretical=True
        )
        signature = tuple(
            (voice.value, tuple((e.midi, e.offset, e.velocity) for e in events))
            for voice, events in sorted(
                composition.events.items(), key=lambda item: item[0].value
            )
        )
        if reference is None:
            reference = signature
        assert signature == reference
