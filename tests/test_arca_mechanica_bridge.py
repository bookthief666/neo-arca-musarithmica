"""Acceptance tests for the M1.0 physical-state bridge."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "arca_mechanica_bridge.py"
SPEC = importlib.util.spec_from_file_location("arca_mechanica_bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


def _request() -> dict:
    manifest = bridge.build_manifest()
    return {
        "format": bridge.REQUEST_FORMAT,
        "read_band": 1,
        "tone": {"number": 2, "engaged": True},
        "rod_instances": [
            {
                "instance_id": f"rod-{item['copy_index']}-{order}",
                "template_id": item["template_id"],
                "source_column_id": item["source_column_id"],
                "copy_index": item["copy_index"],
                "location": "workspace",
                "vertical_offset": 0,
                "order": order,
            }
            for order, item in enumerate(manifest["rod_templates"])
        ],
    }


def test_manifest_separates_immutable_sources_from_physical_copies() -> None:
    manifest = bridge.build_manifest()
    pitch_templates = [
        item for item in manifest["rod_templates"]
        if item["source_column_id"] == bridge.PITCH_SOURCE_ID
    ]
    assert len(pitch_templates) == 2
    assert {item["copy_index"] for item in pitch_templates} == {1, 2}
    assert len(manifest["source_columns"]) == 2
    assert manifest["source_columns"][0]["bands"][0]["status"] == "verified"
    assert all(
        band["status"] == "untranscribed"
        for source in manifest["source_columns"]
        for band in source["bands"][1:]
    )


def test_canonical_physical_arrangement_executes_real_kernel_deterministically() -> None:
    request = _request()
    first = bridge.execute_arrangement(request)
    second = bridge.execute_arrangement(request)
    assert first == second
    assert first["fragment"] == bridge.build_default_fragment()
    assert len(first["fragment"]["events"]) == 6
    assert set(first["fragment"]["events"][0]["voices"]) == {
        "cantus", "altus", "tenor", "bassus"
    }


def test_visible_untranscribed_offset_cannot_masquerade_as_historica() -> None:
    request = _request()
    request["rod_instances"][1]["vertical_offset"] = 1
    with pytest.raises(bridge.ArcaMechanicaBridgeError, match="unavailable band"):
        bridge.execute_arrangement(request)


def test_wrong_tone_cannot_execute_tone_two_fragment() -> None:
    request = _request()
    request["tone"] = {"number": 1, "engaged": True}
    with pytest.raises(bridge.ArcaMechanicaBridgeError, match="Tone II"):
        bridge.execute_arrangement(request)


def test_missing_repeated_copy_is_rejected() -> None:
    request = _request()
    request["rod_instances"] = request["rod_instances"][:-1]
    with pytest.raises(bridge.ArcaMechanicaBridgeError, match="three required"):
        bridge.execute_arrangement(request)


def test_bridge_does_not_mutate_submitted_physical_state() -> None:
    request = _request()
    before = copy.deepcopy(request)
    bridge.execute_arrangement(request)
    assert request == before
