#!/usr/bin/env python3
"""Render the bounded M0 historical phrase as symbolic events.

This is deliberately *not* an ARCA HISTORICA engine yet. It consumes an explicit
research-preview record, validates structure and provenance, and emits deterministic
symbolic events without inventing octaves, MIDI note numbers, tempo, or unresolved
musica ficta.

Noncanonical staging requires --allow-staging. A top-level ``canonical: true`` flag is
not sufficient: canonical records must carry independently witnessed, cell-level
provenance for pitch permutation, tone lookup, and rhythm.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = (
    ROOT
    / "historical_data"
    / "worked_examples"
    / "ave_maris_stella_stropha1_symbolic_preview.json"
)
VOICE_ORDER = ("cantus", "altus", "tenor", "bassus")
CANONICAL_COMPONENTS = ("pitch_permutation", "tone_lookup", "rhythm")


class HistoricalPreviewError(ValueError):
    """Raised when a research record is structurally or evidentially unsafe to render."""


def load_record(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise HistoricalPreviewError("historical preview root must be a JSON object")
    return data


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HistoricalPreviewError(f"{label} must be a non-empty string")
    return value


def _unique_nonempty_strings(values: Any, label: str) -> list[str]:
    if not isinstance(values, list) or len(values) < 2:
        raise HistoricalPreviewError(f"{label} must contain at least two entries")
    result = [_require_nonempty_string(value, label) for value in values]
    if len(set(result)) != len(result):
        raise HistoricalPreviewError(f"{label} must contain distinct entries")
    return result


def validate_canonical_provenance(data: dict[str, Any]) -> None:
    """Require evidence, not a Boolean flag, before accepting canonical data.

    The first HISTORICA policy is intentionally strict: canonical preview components
    must be verified against at least two independently identified, directly inspected
    primary witnesses. Every active cell must preserve two witness readings and must
    use the source reading without an editorial correction. A later critical-edition
    policy may add explicit editorial variants, but they may not enter this canonical
    path silently.
    """
    provenance = data.get("canonical_provenance")
    if not isinstance(provenance, dict):
        raise HistoricalPreviewError(
            "canonical=true requires canonical_provenance; the flag alone is not authority"
        )

    _require_nonempty_string(
        provenance.get("protocol_version"), "canonical_provenance.protocol_version"
    )
    witnesses = provenance.get("witnesses")
    if not isinstance(witnesses, list) or len(witnesses) < 2:
        raise HistoricalPreviewError("canonical provenance requires at least two primary witnesses")

    witness_by_id: dict[str, dict[str, Any]] = {}
    independence_keys: set[str] = set()
    for witness in witnesses:
        if not isinstance(witness, dict):
            raise HistoricalPreviewError("canonical witness entries must be objects")
        witness_id = _require_nonempty_string(witness.get("id"), "witness.id")
        independence_key = _require_nonempty_string(
            witness.get("independence_key"), f"witness {witness_id} independence_key"
        )
        _require_nonempty_string(
            witness.get("source_locator"), f"witness {witness_id} source_locator"
        )
        if witness.get("directly_inspected") is not True:
            raise HistoricalPreviewError(
                f"canonical witness {witness_id} must be directly_inspected=true"
            )
        if witness_id in witness_by_id:
            raise HistoricalPreviewError(f"duplicate canonical witness id: {witness_id}")
        if independence_key in independence_keys:
            raise HistoricalPreviewError(
                "canonical witnesses must have distinct independence_key values"
            )
        witness_by_id[witness_id] = witness
        independence_keys.add(independence_key)

    components = provenance.get("components")
    if not isinstance(components, dict):
        raise HistoricalPreviewError("canonical_provenance.components is required")

    for component_name in CANONICAL_COMPONENTS:
        component = components.get(component_name)
        if not isinstance(component, dict):
            raise HistoricalPreviewError(f"canonical component {component_name} is required")
        if component.get("verification_status") != "verified":
            raise HistoricalPreviewError(
                f"canonical component {component_name} must be verified"
            )

        component_witness_ids = _unique_nonempty_strings(
            component.get("witness_ids"),
            f"canonical component {component_name} witness_ids",
        )
        unknown = [wid for wid in component_witness_ids if wid not in witness_by_id]
        if unknown:
            raise HistoricalPreviewError(
                f"canonical component {component_name} references unknown witness ids: "
                + ", ".join(unknown)
            )

        cells = component.get("cells")
        if not isinstance(cells, list) or not cells:
            raise HistoricalPreviewError(
                f"canonical component {component_name} must contain verified cells"
            )

        seen_paths: set[str] = set()
        for cell in cells:
            if not isinstance(cell, dict):
                raise HistoricalPreviewError(
                    f"canonical component {component_name} cells must be objects"
                )
            path = _require_nonempty_string(
                cell.get("path"), f"canonical component {component_name} cell.path"
            )
            if path in seen_paths:
                raise HistoricalPreviewError(f"duplicate canonical cell path: {path}")
            seen_paths.add(path)

            if cell.get("status") != "verified":
                raise HistoricalPreviewError(f"canonical cell {path} must be verified")
            if cell.get("active_value_origin") != "source_reading":
                raise HistoricalPreviewError(
                    f"canonical cell {path} must use active_value_origin=source_reading"
                )
            if cell.get("editorial_correction_applied") is not False:
                raise HistoricalPreviewError(
                    f"canonical cell {path} may not silently apply an editorial correction"
                )

            readings = cell.get("witness_readings")
            if not isinstance(readings, list) or len(readings) < 2:
                raise HistoricalPreviewError(
                    f"canonical cell {path} requires at least two witness readings"
                )

            reading_ids: set[str] = set()
            for reading in readings:
                if not isinstance(reading, dict):
                    raise HistoricalPreviewError(
                        f"canonical cell {path} witness readings must be objects"
                    )
                witness_id = _require_nonempty_string(
                    reading.get("witness_id"), f"canonical cell {path} witness_id"
                )
                if witness_id not in witness_by_id:
                    raise HistoricalPreviewError(
                        f"canonical cell {path} references unknown witness {witness_id}"
                    )
                _require_nonempty_string(
                    reading.get("source_locator"), f"canonical cell {path} source_locator"
                )
                if "source_reading" not in reading or reading["source_reading"] is None:
                    raise HistoricalPreviewError(
                        f"canonical cell {path} witness reading lacks source_reading"
                    )
                if witness_id in reading_ids:
                    raise HistoricalPreviewError(
                        f"canonical cell {path} repeats witness {witness_id}"
                    )
                reading_ids.add(witness_id)

            if len(reading_ids) < 2:
                raise HistoricalPreviewError(
                    f"canonical cell {path} requires two distinct primary witnesses"
                )
            if not reading_ids.issubset(set(component_witness_ids)):
                raise HistoricalPreviewError(
                    f"canonical cell {path} uses a witness outside its component witness_ids"
                )


def validate_record(data: dict[str, Any], *, allow_staging: bool) -> None:
    canonical = data.get("canonical") is True
    if canonical:
        validate_canonical_provenance(data)
    elif not allow_staging:
        raise HistoricalPreviewError(
            "record is noncanonical research staging; pass --allow-staging explicitly"
        )

    selection = data.get("historical_selection")
    rhythm = data.get("shared_rhythm")
    voices = data.get("voices")
    events = data.get("events_by_syllable")
    if not all(isinstance(x, dict) for x in (selection, rhythm, voices)):
        raise HistoricalPreviewError("selection/rhythm/voices objects are required")
    if not isinstance(events, list) or not events:
        raise HistoricalPreviewError("events_by_syllable must be a non-empty list")

    syllables = selection.get("syllables")
    durations = rhythm.get("relative_minim_units")
    symbols = rhythm.get("source_glyphs_normalized")
    if not isinstance(syllables, list) or not isinstance(durations, list):
        raise HistoricalPreviewError("syllables and duration arrays are required")
    if not isinstance(symbols, list):
        raise HistoricalPreviewError("duration-symbol array is required")

    size = len(syllables)
    if len(durations) != size or len(symbols) != size or len(events) != size:
        raise HistoricalPreviewError("syllable, rhythm, and event lengths must agree")
    if any(not isinstance(d, int) or isinstance(d, bool) or d <= 0 for d in durations):
        raise HistoricalPreviewError("relative duration units must be positive integers")

    for voice in VOICE_ORDER:
        voice_data = voices.get(voice)
        if not isinstance(voice_data, dict):
            raise HistoricalPreviewError(f"missing voice: {voice}")
        degrees = voice_data.get("degrees")
        letters = voice_data.get("source_letters")
        if not isinstance(degrees, list) or not isinstance(letters, list):
            raise HistoricalPreviewError(f"{voice}: degrees/source_letters required")
        if len(degrees) != size or len(letters) != size:
            raise HistoricalPreviewError(f"{voice}: event count must equal syllable count")
        if any(
            not isinstance(d, int) or isinstance(d, bool) or not 1 <= d <= 8
            for d in degrees
        ):
            raise HistoricalPreviewError(f"{voice}: scale degrees must be integers 1..8")
        if any(not isinstance(letter, str) or not letter for letter in letters):
            raise HistoricalPreviewError(f"{voice}: source letters must be non-empty strings")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise HistoricalPreviewError("every event must be an object")
        if event.get("index") != index + 1:
            raise HistoricalPreviewError("event indices must be consecutive and one-based")
        if event.get("syllable") != syllables[index]:
            raise HistoricalPreviewError("event syllable disagrees with selection")
        if event.get("duration_minim_units") != durations[index]:
            raise HistoricalPreviewError("event duration disagrees with shared rhythm")
        if event.get("duration_symbol") != symbols[index]:
            raise HistoricalPreviewError("event duration symbol disagrees with shared rhythm")
        for voice in VOICE_ORDER:
            cell = event.get(voice)
            if not isinstance(cell, dict):
                raise HistoricalPreviewError(f"event {index + 1}: missing {voice}")
            if cell.get("degree") != voices[voice]["degrees"][index]:
                raise HistoricalPreviewError(f"event {index + 1}: {voice} degree mismatch")
            if cell.get("letter") != voices[voice]["source_letters"][index]:
                raise HistoricalPreviewError(f"event {index + 1}: {voice} letter mismatch")


def render_symbolic(data: dict[str, Any]) -> dict[str, Any]:
    """Return a compact deterministic event model without making pitch-height claims."""
    selection = data["historical_selection"]
    events = data["events_by_syllable"]
    offset = 0
    rendered_events: list[dict[str, Any]] = []
    for source_event in events:
        duration = source_event["duration_minim_units"]
        voices = {
            voice: {
                "degree": source_event[voice]["degree"],
                "source_letter": source_event[voice]["letter"],
            }
            for voice in VOICE_ORDER
        }
        rendered_events.append({
            "index": source_event["index"],
            "syllable": source_event["syllable"],
            "offset_minim_units": offset,
            "duration_minim_units": duration,
            "duration_symbol": source_event["duration_symbol"],
            "voices": voices,
        })
        offset += duration

    return {
        "format": "neo-arca-historical-symbolic-preview/v1",
        "canonical": data.get("canonical") is True,
        "status": data.get("status"),
        "selection": {
            "syntagma": selection["syntagma"],
            "pinax": selection["pinax"],
            "stropha": selection["stropha"],
            "tone": selection["tone"],
            "tone_name": selection["tone_name"],
            "system": selection["system"],
            "text_line": selection["text_line"],
        },
        "time_unit": "relative minim",
        "total_duration_minim_units": offset,
        "events": rendered_events,
        "unresolved": data.get("explicitly_not_claimed", []),
    }


def print_human(rendered: dict[str, Any]) -> None:
    selection = rendered["selection"]
    print(
        f"{selection['text_line']} — S{selection['syntagma']} P{selection['pinax']} "
        f"Stropha {selection['stropha']} / Tone {selection['tone']} "
        f"{selection['tone_name']} ({selection['system']})"
    )
    print("RESEARCH PREVIEW — NONCANONICAL" if not rendered["canonical"] else "CANONICAL")
    print()
    print("pos  syll  dur   cantus  altus  tenor  bassus")
    for event in rendered["events"]:
        voices = event["voices"]
        voice_text = "  ".join(
            f"{voices[v]['degree']}:{voices[v]['source_letter']}" for v in VOICE_ORDER
        )
        print(
            f"{event['index']:>3}  {event['syllable']:<4}  "
            f"{event['duration_minim_units']:>3}   {voice_text}"
        )
    print(f"\nTotal: {rendered['total_duration_minim_units']} relative minim units")
    if rendered.get("unresolved"):
        print("Unresolved: " + "; ".join(rendered["unresolved"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument(
        "--allow-staging",
        action="store_true",
        help="explicitly permit noncanonical archaeology records",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON rather than a table")
    args = parser.parse_args()

    data = load_record(args.record)
    validate_record(data, allow_staging=args.allow_staging)
    rendered = render_symbolic(data)
    if args.json:
        print(json.dumps(rendered, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_human(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
