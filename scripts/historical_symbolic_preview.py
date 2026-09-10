#!/usr/bin/env python3
"""Render the bounded M0 historical phrase as symbolic events.

This is deliberately *not* an ARCA HISTORICA engine yet.  It consumes the explicit
research-preview record assembled from Kircher's worked example and the staged Pinax-IV
rhythm reading, validates its internal structure, and emits deterministic symbolic events
without inventing octaves, MIDI note numbers, tempo, or unresolved musica-ficta.

The script refuses a staging record unless --allow-staging is passed.  That guard exists
so a future caller cannot accidentally treat provisional archaeology as canonical data.
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


class HistoricalPreviewError(ValueError):
    """Raised when a research record is structurally unsafe to render."""


def load_record(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise HistoricalPreviewError("historical preview root must be a JSON object")
    return data


def validate_record(data: dict[str, Any], *, allow_staging: bool) -> None:
    canonical = data.get("canonical") is True
    if not canonical and not allow_staging:
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
        if any(not isinstance(d, int) or isinstance(d, bool) or not 1 <= d <= 8 for d in degrees):
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
        rendered_events.append(
            {
                "index": source_event["index"],
                "syllable": source_event["syllable"],
                "offset_minim_units": offset,
                "duration_minim_units": duration,
                "duration_symbol": source_event["duration_symbol"],
                "voices": voices,
            }
        )
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
