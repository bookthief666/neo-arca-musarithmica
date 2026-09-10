"""Negative and positive gates for the M0 historical symbolic preview.

These tests deliberately use synthetic canonical provenance. They do not promote the
current Ave maris stella research preview, whose rhythm remains unverified.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "historical_symbolic_preview.py"
SPEC = importlib.util.spec_from_file_location("historical_symbolic_preview", MODULE_PATH)
assert SPEC and SPEC.loader
preview = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preview)


def _record() -> dict:
    syllables = ["la", "la"]
    durations = [1, 2]
    symbols = ["minim", "semibreve"]
    voice_degrees = {
        "cantus": [1, 2],
        "altus": [3, 4],
        "tenor": [5, 6],
        "bassus": [7, 8],
    }
    voice_letters = {
        "cantus": ["G", "A"],
        "altus": ["B", "C"],
        "tenor": ["D", "E"],
        "bassus": ["F", "G"],
    }
    events = []
    for index in range(2):
        event = {
            "index": index + 1,
            "syllable": syllables[index],
            "duration_symbol": symbols[index],
            "duration_minim_units": durations[index],
        }
        for voice in preview.VOICE_ORDER:
            event[voice] = {
                "degree": voice_degrees[voice][index],
                "letter": voice_letters[voice][index],
            }
        events.append(event)

    return {
        "record": "synthetic-test-record",
        "status": "synthetic",
        "canonical": False,
        "historical_selection": {
            "syntagma": 1,
            "pinax": 4,
            "stropha": 1,
            "tone": 2,
            "tone_name": "Hypodorius",
            "system": "mollis",
            "text_line": "la la",
            "syllables": syllables,
        },
        "shared_rhythm": {
            "relative_minim_units": durations,
            "source_glyphs_normalized": symbols,
        },
        "voices": {
            voice: {
                "degrees": voice_degrees[voice],
                "source_letters": voice_letters[voice],
            }
            for voice in preview.VOICE_ORDER
        },
        "events_by_syllable": events,
    }


def _canonical_provenance() -> dict:
    witness_ids = ["PRIMARY_A", "PRIMARY_B"]

    def component(name: str) -> dict:
        return {
            "verification_status": "verified",
            "witness_ids": witness_ids.copy(),
            "cells": [
                {
                    "path": f"SYNTHETIC.{name}.CELL01",
                    "status": "verified",
                    "active_value_origin": "source_reading",
                    "editorial_correction_applied": False,
                    "witness_readings": [
                        {
                            "witness_id": "PRIMARY_A",
                            "source_locator": f"synthetic {name} witness A",
                            "source_reading": "x",
                        },
                        {
                            "witness_id": "PRIMARY_B",
                            "source_locator": f"synthetic {name} witness B",
                            "source_reading": "x",
                        },
                    ],
                }
            ],
        }

    return {
        "protocol_version": "synthetic-test-v1",
        "witnesses": [
            {
                "id": "PRIMARY_A",
                "independence_key": "COPY-A",
                "directly_inspected": True,
                "source_locator": "synthetic primary witness A",
            },
            {
                "id": "PRIMARY_B",
                "independence_key": "COPY-B",
                "directly_inspected": True,
                "source_locator": "synthetic primary witness B",
            },
        ],
        "components": {name: component(name) for name in preview.CANONICAL_COMPONENTS},
    }


def _canonical_record() -> dict:
    data = _record()
    data["canonical"] = True
    data["canonical_provenance"] = _canonical_provenance()
    return data


def test_current_staging_record_requires_allow_staging() -> None:
    data = preview.load_record(preview.DEFAULT_RECORD)
    assert data["canonical"] is False
    with pytest.raises(preview.HistoricalPreviewError, match="noncanonical research staging"):
        preview.validate_record(data, allow_staging=False)


def test_current_staging_record_passes_with_explicit_opt_in() -> None:
    data = preview.load_record(preview.DEFAULT_RECORD)
    preview.validate_record(data, allow_staging=True)


def test_canonical_flag_alone_cannot_bypass_provenance_gate() -> None:
    data = _record()
    data["canonical"] = True
    with pytest.raises(preview.HistoricalPreviewError, match="canonical_provenance"):
        preview.validate_record(data, allow_staging=False)


def test_one_primary_witness_is_not_enough() -> None:
    data = _canonical_record()
    data["canonical_provenance"]["witnesses"] = data["canonical_provenance"]["witnesses"][:1]
    with pytest.raises(preview.HistoricalPreviewError, match="at least two primary witnesses"):
        preview.validate_record(data, allow_staging=False)


def test_duplicate_independence_key_is_rejected() -> None:
    data = _canonical_record()
    witnesses = data["canonical_provenance"]["witnesses"]
    witnesses[1]["independence_key"] = witnesses[0]["independence_key"]
    with pytest.raises(preview.HistoricalPreviewError, match="distinct independence_key"):
        preview.validate_record(data, allow_staging=False)


def test_unverified_component_is_rejected() -> None:
    data = _canonical_record()
    data["canonical_provenance"]["components"]["rhythm"]["verification_status"] = "probable"
    with pytest.raises(preview.HistoricalPreviewError, match="rhythm must be verified"):
        preview.validate_record(data, allow_staging=False)


def test_unverified_cell_is_rejected() -> None:
    data = _canonical_record()
    cell = data["canonical_provenance"]["components"]["tone_lookup"]["cells"][0]
    cell["status"] = "probable"
    with pytest.raises(preview.HistoricalPreviewError, match="must be verified"):
        preview.validate_record(data, allow_staging=False)


def test_cell_with_one_witness_reading_is_rejected() -> None:
    data = _canonical_record()
    cell = data["canonical_provenance"]["components"]["pitch_permutation"]["cells"][0]
    cell["witness_readings"] = cell["witness_readings"][:1]
    with pytest.raises(preview.HistoricalPreviewError, match="at least two witness readings"):
        preview.validate_record(data, allow_staging=False)


def test_silent_editorial_correction_is_rejected() -> None:
    data = _canonical_record()
    cell = data["canonical_provenance"]["components"]["tone_lookup"]["cells"][0]
    cell["active_value_origin"] = "editorial_correction"
    cell["editorial_correction_applied"] = True
    with pytest.raises(preview.HistoricalPreviewError, match="source_reading"):
        preview.validate_record(data, allow_staging=False)


def test_fully_verified_synthetic_canonical_fixture_passes() -> None:
    data = _canonical_record()
    preview.validate_record(data, allow_staging=False)
    rendered = preview.render_symbolic(data)
    assert rendered["canonical"] is True
    assert rendered["total_duration_minim_units"] == 3


def test_structural_length_mismatch_still_fails() -> None:
    data = _record()
    data["shared_rhythm"]["relative_minim_units"] = [1]
    with pytest.raises(preview.HistoricalPreviewError, match="lengths must agree"):
        preview.validate_record(data, allow_staging=True)


def test_invalid_degree_still_fails() -> None:
    data = _record()
    data["voices"]["cantus"]["degrees"][0] = 9
    with pytest.raises(preview.HistoricalPreviewError, match="scale degrees"):
        preview.validate_record(data, allow_staging=True)


def test_event_mismatch_still_fails() -> None:
    data = _record()
    data["events_by_syllable"][0]["cantus"]["degree"] = 2
    with pytest.raises(preview.HistoricalPreviewError, match="degree mismatch"):
        preview.validate_record(data, allow_staging=True)
