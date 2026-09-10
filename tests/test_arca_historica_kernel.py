"""Focused acceptance tests for the M0.9 ARCA HISTORICA kernel."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "arca_historica_kernel.py"
SPEC = importlib.util.spec_from_file_location("arca_historica_kernel", MODULE_PATH)
assert SPEC and SPEC.loader
kernel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kernel)


def _load_inputs() -> tuple[dict, dict, dict, dict]:
    return (
        kernel.load_json(kernel.DEFAULT_VPERM),
        kernel.load_json(kernel.DEFAULT_RHYTHM),
        kernel.load_json(kernel.DEFAULT_TONE),
        kernel.load_json(kernel.DEFAULT_WITNESSES),
    )


def test_default_fragment_is_exact_and_deterministic() -> None:
    first = kernel.build_default_fragment()
    second = kernel.build_default_fragment()
    assert first == second
    assert first["format"] == "neo-arca-historica-symbolic/v1"
    assert first["canonical"] is True
    assert first["edition_policy"] == "PRINT_1650"
    assert first["description"] == "Pinax-IV historical fragment"
    assert first["selection"]["vperm"] == 1
    assert first["selection"]["rperm"] == 3
    assert first["selection"]["tone"] == 2
    assert first["total_duration_minim_units"] == 8

    assert [event["duration_minim_units"] for event in first["events"]] == [1, 1, 1, 1, 2, 2]
    assert [event["duration_symbol"] for event in first["events"]] == [
        "minim", "minim", "minim", "minim", "semibreve", "semibreve"
    ]
    assert [event["voices"]["cantus"]["pitch_class"] for event in first["events"]] == [
        "D", "D", "Bb", "A", "Bb", "Bb"
    ]
    assert [event["voices"]["altus"]["pitch_class"] for event in first["events"]] == [
        "G", "F#", "D", "F#", "F#", "F#"
    ]
    assert [event["voices"]["tenor"]["pitch_class"] for event in first["events"]] == [
        "Bb", "A", "Bb", "C", "D", "D"
    ]
    assert [event["voices"]["bassus"]["pitch_class"] for event in first["events"]] == [
        "G", "D", "G", "F#", "Bb", "Bb"
    ]


def test_every_event_carries_cell_level_provenance() -> None:
    fragment = kernel.build_default_fragment()
    for event in fragment["events"]:
        assert event["rhythm_provenance"]["cell"].startswith("S1.P4.NOTAE_TEMPORIS")
        for voice in kernel.VOICE_ORDER:
            provenance = event["voices"][voice]["provenance"]
            assert provenance["vperm_cell"].startswith("S1.P4.STROPHA1.VPERM01")
            assert provenance["tone_cell"].startswith("MENSA.P51.TONE02.DEGREE")


def test_output_does_not_invent_modern_realization_fields() -> None:
    fragment = kernel.build_default_fragment()
    forbidden = {"midi", "midi_note", "bpm", "tempo", "octave", "frequency", "velocity"}

    def visit(value: object) -> None:
        if isinstance(value, dict):
            assert forbidden.isdisjoint(value.keys())
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(fragment)


def test_noncanonical_component_is_rejected() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    rhythm["canonical"] = False
    with pytest.raises(kernel.ArcaHistoricaError, match="rhythm is not canonical"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_unverified_component_is_rejected() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    vperm["verification_status"] = "probable"
    with pytest.raises(kernel.ArcaHistoricaError, match="vperm is not verified"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_unknown_witness_is_rejected() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    vperm["verification"]["primary_witness_ids"][0] = "UNKNOWN"
    with pytest.raises(kernel.ArcaHistoricaError, match="unknown witness UNKNOWN"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_duplicate_independence_key_in_ledger_is_rejected() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    witnesses["witnesses"][1]["independence_key"] = witnesses["witnesses"][0]["independence_key"]
    with pytest.raises(kernel.ArcaHistoricaError, match="duplicate witness independence_key"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_silent_editorial_correction_is_rejected() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    cell = tone["cell_provenance"]["cells"][0]
    cell["editorial_correction_applied"] = True
    with pytest.raises(kernel.ArcaHistoricaError, match="editorial correction"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_mismatched_vperm_and_rhythm_lengths_are_rejected() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    rhythm["glyph_sequence_normalized"] = rhythm["glyph_sequence_normalized"][:-1]
    rhythm["relative_minim_units"] = rhythm["relative_minim_units"][:-1]
    rhythm["total_relative_minim_units"] = sum(rhythm["relative_minim_units"])
    rhythm["historical_scope"]["event_count"] = len(rhythm["glyph_sequence_normalized"])
    rhythm["cell_provenance"]["cells"] = rhythm["cell_provenance"]["cells"][:-1]
    with pytest.raises(kernel.ArcaHistoricaError, match="Vperm and Rperm event counts must agree"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_invalid_degree_is_rejected_before_tone_resolution() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    vperm["rows"]["cantus"][0] = 9
    with pytest.raises(kernel.ArcaHistoricaError, match="invalid scale degrees"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_tone_cell_must_agree_with_mapping() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    tone["cell_provenance"]["cells"][2]["active_value"] = "B"
    with pytest.raises(kernel.ArcaHistoricaError, match="active_value disagrees with tone mapping"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_rhythm_witness_disagreement_is_rejected() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    rhythm["cell_provenance"]["cells"][0]["witness_readings"][0]["source_reading"] = "semibreve"
    with pytest.raises(kernel.ArcaHistoricaError, match="disagrees with active glyph"):
        kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)


def test_input_objects_are_not_mutated() -> None:
    vperm, rhythm, tone, witnesses = _load_inputs()
    originals = tuple(copy.deepcopy(item) for item in (vperm, rhythm, tone, witnesses))
    kernel.build_fragment(vperm=vperm, rhythm=rhythm, tone=tone, witness_ledger=witnesses)
    assert (vperm, rhythm, tone, witnesses) == originals
