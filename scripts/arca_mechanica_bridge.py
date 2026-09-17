#!/usr/bin/env python3
"""Strict critical-edition reading boundary; M0.9 remains the sole musical kernel."""
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
    DEFAULT_RHYTHM, DEFAULT_TONE, DEFAULT_VPERM, build_default_fragment, load_json,
)

MANIFEST_FORMAT = "neo-arca-mechanica-manifest/v2"
REQUEST_FORMAT = "neo-arca-mechanica-reading/v2"
EXECUTION_FORMAT = "neo-arca-mechanica-execution/v2"
MANIFEST_ID = "m1.2.1r.pinax04.fragment01"
CARRIER_ID = "S1.P4.CRITICAL_EDITION.FRAGMENT01"
EDITION_ID = "neo-arca-critical-edition/1"
PITCH_SOURCE_ID = "S1.P4.STROPHA1.VPERM01"
RHYTHM_SOURCE_ID = "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03"


class ArcaMechanicaBridgeError(ValueError):
    """A reading does not match the server-owned edition."""


def _content_digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_manifest() -> dict[str, Any]:
    vperm = load_json(DEFAULT_VPERM)
    rhythm = load_json(DEFAULT_RHYTHM)
    tone = load_json(DEFAULT_TONE)
    carrier = {
        "carrier_id": CARRIER_ID, "edition_id": EDITION_ID,
        "label": "Pinax IV critical-edition extract", "classification": "H1",
        "editorial_pairing": {
            "classification": "H1",
            "note": "Vperm01 and Rperm03 are separately verified selections; their pairing and carrier layout are editorial reconstruction, not a recovered complete historical column.",
        },
        "pitch_source": {
            "source_column_id": PITCH_SOURCE_ID, "immutable_record": vperm["record"],
            "provenance_paths": [cell["path"] for cell in vperm["cell_provenance"]["cells"]],
            "content": {"rows": deepcopy(vperm["rows"])},
        },
        "rhythm_source": {
            "source_column_id": RHYTHM_SOURCE_ID, "immutable_record": rhythm["record"],
            "provenance_paths": [cell["path"] for cell in rhythm["cell_provenance"]["cells"]],
            "content": {
                "glyphs": deepcopy(rhythm["glyph_sequence_normalized"]),
                "glyphs_classification": "H0",
                "relative_minim_units": deepcopy(rhythm["relative_minim_units"]),
                "relative_minim_units_classification": "derived project normalization",
            },
        },
    }
    tone_policy = {
        "number": tone["historical_scope"]["tone"],
        "name": tone["historical_scope"]["tone_name"],
        "system": tone["historical_scope"]["system"],
        "witness": tone["witness_policy"]["witness"],
        "degree_to_pitch_class": deepcopy(tone["degree_to_pitch_class"]),
        "record": tone["record"], "provenance_class": tone["provenance_class"],
        "witness_classification": "H0", "operating_policy_classification": "H1",
        "known_conflict": "The printed-p.51 table conflicts with the engraved tone table. This edition retains the M0.9 p.51 witness policy; it does not claim a preferred general operating authority.",
    }
    return {
        "format": MANIFEST_FORMAT, "manifest_id": MANIFEST_ID,
        "content_digest": _content_digest({"carrier": carrier, "tone": tone_policy}),
        "title": vperm["historical_scope"]["title"],
        "cell": {"syntagma": 1, "bank_label": "Dodecamorium", "pinax": 4,
                 "cell_label": "Cell IV", "printed_page": vperm["historical_scope"]["printed_page"]},
        "critical_edition_carrier": carrier, "tone": tone_policy,
        "physical_reconstruction": {"classification": "H1",
            "note": "Carrier face, workstation capacity and six-event inspection mechanism are reconstruction, not historical transverse reading."},
        "limits": [
            "One editorially selected fragment; no selectable untranscribed bands.",
            "Symbolic content is source-backed; its software representation is modern.",
            "No octave, register, MIDI pitch, BPM, beat semantics, ficta or SATB repair.",
        ],
    }


def _exact_object(value: Any, label: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArcaMechanicaBridgeError(f"{label} must be an object")
    if set(value) - keys:
        raise ArcaMechanicaBridgeError(f"{label} has unexpected fields")
    if keys - set(value):
        raise ArcaMechanicaBridgeError(f"{label} is missing fields")
    return value


def _normalize_reading(request: Any, manifest: dict[str, Any]) -> dict[str, Any]:
    value = _exact_object(request, "request", {"format", "manifest_id", "content_digest", "carrier_instance"})
    if value["format"] != REQUEST_FORMAT:
        raise ArcaMechanicaBridgeError("unknown reading format")
    if value["manifest_id"] != manifest["manifest_id"]:
        raise ArcaMechanicaBridgeError("manifest identity mismatch")
    if value["content_digest"] != manifest["content_digest"]:
        raise ArcaMechanicaBridgeError("content identity mismatch")
    instance = _exact_object(value["carrier_instance"], "carrier_instance",
                             {"instance_id", "carrier_id", "edition_id", "location"})
    carrier = manifest["critical_edition_carrier"]
    for key in ("carrier_id", "edition_id"):
        if instance[key] != carrier[key]:
            raise ArcaMechanicaBridgeError(f"{key} identity mismatch")
    if instance["location"] != "workspace":
        raise ArcaMechanicaBridgeError("carrier is not seated")
    identity = instance["instance_id"]
    if not isinstance(identity, str) or not identity.strip():
        raise ArcaMechanicaBridgeError("instance_id must be a nonempty string")
    return {"format": REQUEST_FORMAT, "manifest_id": manifest["manifest_id"],
            "content_digest": manifest["content_digest"],
            "carrier_instance": {"instance_id": identity, "carrier_id": carrier["carrier_id"],
                                 "edition_id": carrier["edition_id"], "location": "workspace"}}


def validate_reading(request: Any) -> dict[str, Any]:
    return _normalize_reading(request, build_manifest())


def execute_reading(request: Any) -> dict[str, Any]:
    manifest = build_manifest()
    normalized = _normalize_reading(request, manifest)
    return {
        "format": EXECUTION_FORMAT, "request_fingerprint": _content_digest(normalized),
        "reading": {
            "manifest_id": manifest["manifest_id"], "content_digest": manifest["content_digest"],
            "carrier_instance": normalized["carrier_instance"],
            "tone": {"number": manifest["tone"]["number"], "witness": manifest["tone"]["witness"]},
            "classification": "H0-backed content through H1 critical-edition carrier",
        },
        "fragment": build_default_fragment(),
    }


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"manifest", "execute"}:
        print("usage: arca_mechanica_bridge.py manifest|execute", file=sys.stderr)
        return 2
    try:
        payload = build_manifest() if sys.argv[1] == "manifest" else execute_reading(json.loads(sys.stdin.read()))
    except (ArcaMechanicaBridgeError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
