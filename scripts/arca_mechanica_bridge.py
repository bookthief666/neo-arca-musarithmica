#!/usr/bin/env python3
"""Narrow development bridge between M1.0 and the M0.9 historical kernel.

The bridge validates the physical arrangement submitted by the frontend and only then
invokes :func:`arca_historica_kernel.build_default_fragment`. It does not duplicate or
repair historical musical logic. Untranscribed rod bands are intentionally unavailable.
"""
from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from arca_historica_kernel import (
    DEFAULT_RHYTHM,
    DEFAULT_TONE,
    DEFAULT_VPERM,
    build_default_fragment,
    load_json,
)

MANIFEST_FORMAT = "neo-arca-mechanica-manifest/v1"
REQUEST_FORMAT = "neo-arca-mechanica-alignment/v1"
BRIDGE_FORMAT = "neo-arca-mechanica-execution/v1"

PITCH_SOURCE_ID = "S1.P4.STROPHA1.VPERM01"
RHYTHM_SOURCE_ID = "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03"
REQUIRED_TEMPLATES = (
    ("pinax04-vperm-copy-1", PITCH_SOURCE_ID, 1),
    ("pinax04-vperm-copy-2", PITCH_SOURCE_ID, 2),
    ("pinax04-rperm03-copy-1", RHYTHM_SOURCE_ID, 1),
)


class ArcaMechanicaBridgeError(ValueError):
    """Raised when the visible physical state is not an authorised H0 alignment."""


def _unavailable_bands() -> list[dict[str, Any]]:
    return [
        {
            "index": index,
            "status": "untranscribed",
            "classification": "UNKNOWN",
            "label": f"Band {index:02d} · sealed",
            "content": None,
        }
        for index in range(2, 11)
    ]


def build_manifest() -> dict[str, Any]:
    """Expose source-owned visible material without making TypeScript historical authority."""
    vperm = load_json(DEFAULT_VPERM)
    rhythm = load_json(DEFAULT_RHYTHM)
    tone = load_json(DEFAULT_TONE)
    verified_pitch_band = {
        "index": 1,
        "status": "verified",
        "classification": "H0",
        "label": "Stropha I · Vperm 01",
        "content": {"rows": deepcopy(vperm["rows"])},
        "provenance_paths": [cell["path"] for cell in vperm["cell_provenance"]["cells"]],
    }
    verified_rhythm_band = {
        "index": 1,
        "status": "verified",
        "classification": "H0",
        "label": "Notae Temporis · Rperm 03",
        "content": {
            "glyphs": deepcopy(rhythm["glyph_sequence_normalized"]),
            "relative_minim_units": deepcopy(rhythm["relative_minim_units"]),
        },
        "provenance_paths": [cell["path"] for cell in rhythm["cell_provenance"]["cells"]],
    }
    return {
        "format": MANIFEST_FORMAT,
        "title": vperm["historical_scope"]["title"],
        "cell": {
            "syntagma": 1,
            "bank_label": "Dodecamorium",
            "pinax": 4,
            "cell_label": "Cell IV",
            "printed_page": vperm["historical_scope"]["printed_page"],
        },
        "source_columns": [
            {
                "id": PITCH_SOURCE_ID,
                "kind": "pitch",
                "label": "Columna musarithmica · Vperm 01",
                "bands": [verified_pitch_band, *_unavailable_bands()],
                "record": vperm["record"],
                "provenance_class": vperm["provenance_class"],
            },
            {
                "id": RHYTHM_SOURCE_ID,
                "kind": "rhythm",
                "label": "Notae Temporis · Rperm 03",
                "bands": [verified_rhythm_band, *_unavailable_bands()],
                "record": rhythm["record"],
                "provenance_class": rhythm["provenance_class"],
            },
        ],
        "rod_templates": [
            {
                "template_id": template_id,
                "source_column_id": source_id,
                "copy_index": copy_index,
                "label": (
                    f"Vperm exemplar {copy_index}" if source_id == PITCH_SOURCE_ID
                    else "Rperm exemplar 1"
                ),
            }
            for template_id, source_id, copy_index in REQUIRED_TEMPLATES
        ],
        "required_template_ids": [item[0] for item in REQUIRED_TEMPLATES],
        "canonical_read_band": 1,
        "tone": {
            "number": tone["historical_scope"]["tone"],
            "name": tone["historical_scope"]["tone_name"],
            "system": tone["historical_scope"]["system"],
            "witness": tone["witness_policy"]["witness"],
            "degree_to_pitch_class": deepcopy(tone["degree_to_pitch_class"]),
            "record": tone["record"],
            "provenance_class": tone["provenance_class"],
        },
        "physical_reconstruction": {
            "classification": "H1",
            "note": "Carrier-face layout, exact joinery, timber, and on-screen scale are restrained reconstruction choices.",
        },
        "limits": [
            "Only band 01 is populated as verified HISTORICA data.",
            "Bands 02–10 remain untranscribed and cannot execute.",
            "No octave, register, MIDI pitch, BPM, or modern beat semantics are supplied.",
        ],
    }


def _need_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArcaMechanicaBridgeError(f"{label} must be an object")
    return value


def validate_arrangement(request: dict[str, Any]) -> list[dict[str, Any]]:
    if request.get("format") != REQUEST_FORMAT:
        raise ArcaMechanicaBridgeError("unknown physical alignment format")
    if request.get("read_band") != 1:
        raise ArcaMechanicaBridgeError("the selected transverse band is not transcribed")

    tone = _need_object(request.get("tone"), "tone")
    if tone.get("engaged") is not True or tone.get("number") != 2:
        raise ArcaMechanicaBridgeError("printed-p.51 Tone II must be physically engaged")

    instances = request.get("rod_instances")
    if not isinstance(instances, list):
        raise ArcaMechanicaBridgeError("rod_instances must be an array")
    by_template: dict[str, dict[str, Any]] = {}
    for instance in instances:
        current = _need_object(instance, "rod instance")
        template_id = current.get("template_id")
        if not isinstance(template_id, str) or template_id in by_template:
            raise ArcaMechanicaBridgeError("rod templates must be present exactly once")
        by_template[template_id] = current

    if set(by_template) != {item[0] for item in REQUIRED_TEMPLATES}:
        raise ArcaMechanicaBridgeError("the three required Pinax-IV carriers are not on the rule")

    ordered: list[dict[str, Any]] = []
    for order, (template_id, source_id, copy_index) in enumerate(REQUIRED_TEMPLATES):
        instance = by_template[template_id]
        if instance.get("source_column_id") != source_id or instance.get("copy_index") != copy_index:
            raise ArcaMechanicaBridgeError(f"{template_id} does not match its immutable source")
        if instance.get("location") != "workspace" or instance.get("order") != order:
            raise ArcaMechanicaBridgeError("the rods must be placed side-by-side in canonical order")
        offset = instance.get("vertical_offset")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset != 0:
            raise ArcaMechanicaBridgeError(
                f"{template_id} exposes an unavailable band; align verified band 01"
            )
        instance_id = instance.get("instance_id")
        if not isinstance(instance_id, str) or not instance_id.strip():
            raise ArcaMechanicaBridgeError("every physical rod requires an instance id")
        ordered.append(deepcopy(instance))
    return ordered


def execute_arrangement(request: dict[str, Any]) -> dict[str, Any]:
    ordered = validate_arrangement(request)
    canonical_request = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    fragment = build_default_fragment()
    return {
        "format": BRIDGE_FORMAT,
        "request_fingerprint": hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        "arrangement": {
            "read_band": 1,
            "rod_instances": ordered,
            "classification": "H0 data through H1 physical reconstruction",
        },
        "fragment": fragment,
    }


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"manifest", "execute"}:
        print("usage: arca_mechanica_bridge.py manifest|execute", file=sys.stderr)
        return 2
    try:
        if sys.argv[1] == "manifest":
            payload = build_manifest()
        else:
            raw = sys.stdin.read()
            request = json.loads(raw)
            payload = execute_arrangement(_need_object(request, "request"))
    except (ArcaMechanicaBridgeError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
