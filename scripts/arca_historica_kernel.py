#!/usr/bin/env python3
"""First executable ARCA HISTORICA fragment.

This module is intentionally separate from the Neo-Arca Ghost. It reads only
verified project-owned records, combines one Pinax-IV Vperm, one Pinax-IV
Syntagma-I rhythm, and one named 1650 tone-table witness, then emits symbolic
four-voice events with source-cell provenance.

No octave, MIDI, BPM, modern beat semantics, or SATB repair is inferred.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VPERM = ROOT / "historical_data/syntagma1_pinax04/vperm01_printed_p83_verified.json"
DEFAULT_RHYTHM = ROOT / "historical_data/syntagma1_pinax04/rhythm_duple_rperm03_printed_p83_verified.json"
DEFAULT_TONE = ROOT / "historical_data/mensa_tonographica/tone02_hypodorius_printed_p51_verified.json"
DEFAULT_WITNESSES = ROOT / "historical_data/source_witnesses.json"
VPERM, RHYTHM, TONE, WITNESSES = DEFAULT_VPERM, DEFAULT_RHYTHM, DEFAULT_TONE, DEFAULT_WITNESSES
VOICE_ORDER = ("cantus", "altus", "tenor", "bassus")
VOICES = VOICE_ORDER
FORMAT = "neo-arca-historica-symbolic/v1"


class ArcaHistoricaError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ArcaHistoricaError(f"{path}: root must be an object")
    return value


def need_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArcaHistoricaError(f"{label} must be non-empty text")
    return value


def unique_texts(value: Any, label: str, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ArcaHistoricaError(f"{label} requires at least {minimum} values")
    out = [need_text(item, label) for item in value]
    if len(out) != len(set(out)):
        raise ArcaHistoricaError(f"{label} must be distinct")
    return out


def witness_index(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = ledger.get("witnesses")
    if not isinstance(entries, list) or not entries:
        raise ArcaHistoricaError("witness ledger is empty")
    out: dict[str, dict[str, Any]] = {}
    keys: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ArcaHistoricaError("witness entries must be objects")
        wid = need_text(entry.get("id"), "witness.id")
        key = need_text(entry.get("independence_key"), f"{wid}.independence_key")
        if wid in out or key in keys:
            raise ArcaHistoricaError(f"duplicate witness id: {wid}" if wid in out else f"duplicate witness independence_key: {key}")
        out[wid] = entry
        keys.add(key)
    return out


def verified_record(record: dict[str, Any], label: str, witnesses: dict[str, dict[str, Any]]) -> list[str]:
    if record.get("canonical") is not True or record.get("verification_status") != "verified":
        raise ArcaHistoricaError(f"{label} is not canonical" if record.get("canonical") is not True else f"{label} is not verified")
    need_text(record.get("transcription_protocol"), f"{label}.transcription_protocol")
    verification = record.get("verification")
    if not isinstance(verification, dict):
        raise ArcaHistoricaError(f"{label}.verification is required")
    ids = unique_texts(verification.get("primary_witness_ids"), f"{label}.primary_witness_ids", 2)
    keys = unique_texts(verification.get("independence_keys"), f"{label}.independence_keys", 2)
    if len(ids) != len(keys) or verification.get("primary_witness_count") != len(ids):
        raise ArcaHistoricaError(f"{label}: witness counts disagree")
    if verification.get("all_cells_verified") is not True:
        raise ArcaHistoricaError(f"{label}: not all cells are verified")
    if verification.get("editorial_corrections_applied") is not False:
        raise ArcaHistoricaError(f"{label}: editorial corrections are forbidden in PRINT_1650")
    ledger_keys = []
    for wid in ids:
        witness = witnesses.get(wid)
        if witness is None:
            raise ArcaHistoricaError(f"{label}: unknown witness {wid}")
        ledger_keys.append(need_text(witness.get("independence_key"), f"{wid}.independence_key"))
        direct = witness.get("direct_inspection")
        if not isinstance(direct, dict) or direct.get("directly_inspected") is not True:
            raise ArcaHistoricaError(f"{label}: witness {wid} is not directly inspected")
        rights = " ".join(str(witness.get(k, "")) for k in ("rights", "license", "rights_note"))
        if "public domain" not in rights.lower().replace("-", " "):
            raise ArcaHistoricaError(f"{label}: witness {wid} lacks public-domain authority")
    if set(keys) != set(ledger_keys):
        raise ArcaHistoricaError(f"{label}: independence keys disagree with witness ledger")
    return ids


def readings(cell: dict[str, Any], ids: list[str], path: str) -> dict[str, Any]:
    if cell.get("path") != path or cell.get("status") != "verified":
        raise ArcaHistoricaError(f"{path}: missing or unverified provenance")
    if cell.get("active_value_origin") != "source_reading":
        raise ArcaHistoricaError(f"{path}: active value must originate in source reading")
    if cell.get("editorial_correction_applied") is not False:
        raise ArcaHistoricaError(f"{path}: silent editorial correction")
    if "readings" in cell:
        raw = cell.get("readings")
        if not isinstance(raw, dict):
            raise ArcaHistoricaError(f"{path}: readings must be an object")
        out = dict(raw)
    else:
        raw = cell.get("witness_readings")
        if not isinstance(raw, list):
            raise ArcaHistoricaError(f"{path}: witness_readings are required")
        out = {}
        for item in raw:
            if not isinstance(item, dict):
                raise ArcaHistoricaError(f"{path}: witness reading must be an object")
            wid = need_text(item.get("witness_id"), f"{path}.witness_id")
            need_text(item.get("source_locator"), f"{path}.source_locator")
            if wid in out or item.get("source_reading") is None:
                raise ArcaHistoricaError(f"{path}: invalid witness reading")
            out[wid] = item["source_reading"]
    if set(out) != set(ids):
        raise ArcaHistoricaError(f"{path}: witness readings do not match record witnesses")
    return out


def provenance_cells(record: dict[str, Any], ids: list[str], label: str) -> dict[str, dict[str, Any]]:
    provenance = record.get("cell_provenance")
    if not isinstance(provenance, dict):
        raise ArcaHistoricaError(f"{label}: cell_provenance is required")
    declared = unique_texts(provenance.get("witnesses"), f"{label}.cell_provenance.witnesses", 2)
    if set(declared) != set(ids):
        raise ArcaHistoricaError(f"{label}: cell witness set disagrees with verification")
    cells = provenance.get("cells")
    if not isinstance(cells, list) or not cells:
        raise ArcaHistoricaError(f"{label}: provenance cells are required")
    out: dict[str, dict[str, Any]] = {}
    for cell in cells:
        if not isinstance(cell, dict):
            raise ArcaHistoricaError(f"{label}: cell must be an object")
        path = need_text(cell.get("path"), f"{label}.cell.path")
        if path in out:
            raise ArcaHistoricaError(f"{label}: duplicate cell path {path}")
        out[path] = cell
    return out


def validate_vperm(record: dict[str, Any], witnesses: dict[str, dict[str, Any]]):
    ids = verified_record(record, "vperm", witnesses)
    scope = record.get("historical_scope")
    if not isinstance(scope, dict) or (scope.get("syntagma"), scope.get("pinax"), scope.get("stropha"), scope.get("vperm")) != (1, 4, 1, 1):
        raise ArcaHistoricaError("kernel accepts only S1/P4/Stropha1/Vperm1")
    if record.get("voice_order_top_to_bottom") != list(VOICES):
        raise ArcaHistoricaError("vperm voice order must be cantus/altus/tenor/bassus")
    rows = record.get("rows")
    if not isinstance(rows, dict):
        raise ArcaHistoricaError("vperm.rows is required")
    normalized: dict[str, list[int]] = {}
    lengths = set()
    for voice in VOICES:
        row = rows.get(voice)
        if not isinstance(row, list) or not row:
            raise ArcaHistoricaError(f"vperm.{voice} row is required")
        if any(not isinstance(x, int) or isinstance(x, bool) or not 1 <= x <= 8 for x in row):
            raise ArcaHistoricaError(f"vperm.{voice} contains invalid scale degrees")
        normalized[voice] = row[:]
        lengths.add(len(row))
    if len(lengths) != 1:
        raise ArcaHistoricaError("vperm rows must have equal length")
    cells = provenance_cells(record, ids, "vperm")
    paths: dict[tuple[str, int], str] = {}
    for voice in VOICES:
        for pos, value in enumerate(normalized[voice], 1):
            path = f"S1.P4.STROPHA1.VPERM01.{voice.upper()}.N{pos:02d}"
            cell = cells.get(path)
            if cell is None:
                raise ArcaHistoricaError(f"missing vperm cell {path}")
            source = readings(cell, ids, path)
            if cell.get("active_value") != value:
                raise ArcaHistoricaError(f"{path}: active value disagrees with row")
            for wid, source_value in source.items():
                try:
                    parsed = int(str(source_value))
                except ValueError as exc:
                    raise ArcaHistoricaError(f"{path}: nonnumeric source reading from {wid}") from exc
                if parsed != value:
                    raise ArcaHistoricaError(f"{path}: witness disagreement")
            paths[(voice, pos)] = path
    if len(cells) != len(VOICES) * next(iter(lengths)):
        raise ArcaHistoricaError("vperm contains unexpected/missing provenance cells")
    return normalized, paths, ids


def validate_tone(record: dict[str, Any], witnesses: dict[str, dict[str, Any]]):
    ids = verified_record(record, "tone", witnesses)
    scope = record.get("historical_scope")
    if not isinstance(scope, dict) or scope.get("tone") != 2 or scope.get("printed_page") != "51":
        raise ArcaHistoricaError("kernel accepts only printed-p.51 Tone II")
    policy = record.get("witness_policy")
    if not isinstance(policy, dict) or policy.get("witness_specific") is not True:
        raise ArcaHistoricaError("tone witness policy must remain witness-specific")
    raw = record.get("degree_to_pitch_class")
    if not isinstance(raw, dict) or set(raw) != {str(i) for i in range(1, 9)}:
        raise ArcaHistoricaError("tone must define exactly degrees 1..8")
    mapping = {int(k): need_text(v, f"tone degree {k}") for k, v in raw.items()}
    cells = provenance_cells(record, ids, "tone")
    paths: dict[int, str] = {}
    flat, sharp = chr(0x266D), chr(0x266F)
    normalize = lambda value: str(value).replace(flat, "b").replace(sharp, "#")
    for degree in range(1, 9):
        path = f"MENSA.P51.TONE02.DEGREE{degree:02d}"
        cell = cells.get(path)
        if cell is None:
            raise ArcaHistoricaError(f"missing tone cell {path}")
        source = readings(cell, ids, path)
        active = need_text(cell.get("active_value"), f"{path}.active_value")
        if active != mapping[degree]:
            raise ArcaHistoricaError(f"{path}: active_value disagrees with tone mapping")
        if any(normalize(value) != active for value in source.values()):
            raise ArcaHistoricaError(f"{path}: witness disagreement")
        paths[degree] = path
    if len(cells) != 8:
        raise ArcaHistoricaError("tone contains unexpected/missing provenance cells")
    return mapping, paths, ids


def validate_rhythm(record: dict[str, Any], witnesses: dict[str, dict[str, Any]]):
    ids = verified_record(record, "rhythm", witnesses)
    scope = record.get("historical_scope")
    if not isinstance(scope, dict) or (scope.get("syntagma"), scope.get("pinax")) != (1, 4):
        raise ArcaHistoricaError("kernel accepts only Syntagma-I/Pinax-IV rhythm")
    rperm = scope.get("rperm")
    if not isinstance(rperm, int) or isinstance(rperm, bool) or rperm < 1:
        raise ArcaHistoricaError("rhythm rperm must be positive")
    glyphs = record.get("glyph_sequence_normalized")
    units = record.get("relative_minim_units")
    if not isinstance(glyphs, list) or not isinstance(units, list) or not glyphs or len(glyphs) != len(units):
        raise ArcaHistoricaError("rhythm glyph/duration arrays must agree")
    glyphs = [need_text(g, "rhythm glyph") for g in glyphs]
    if any(not isinstance(x, int) or isinstance(x, bool) or x <= 0 for x in units):
        raise ArcaHistoricaError("rhythm units must be positive integers")
    if scope.get("event_count") != len(glyphs) or record.get("total_relative_minim_units") != sum(units):
        raise ArcaHistoricaError("rhythm counts/totals disagree")
    norm = record.get("normalization")
    rules = norm.get("rules") if isinstance(norm, dict) and norm.get("unit") == "relative minim" else None
    if not isinstance(rules, dict) or any(rules.get(g) != u for g, u in zip(glyphs, units)):
        raise ArcaHistoricaError("rhythm normalization is inconsistent")
    cells = provenance_cells(record, ids, "rhythm")
    paths = []
    for pos, (glyph, unit) in enumerate(zip(glyphs, units), 1):
        path = f"S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM{rperm:02d}.N{pos:02d}"
        cell = cells.get(path)
        if cell is None:
            raise ArcaHistoricaError(f"missing rhythm cell {path}")
        source = readings(cell, ids, path)
        if cell.get("active_value") != glyph or cell.get("source_glyph_class") != glyph:
            raise ArcaHistoricaError(f"{path}: glyph disagreement")
        if cell.get("normalized_relative_minim_units") != unit:
            raise ArcaHistoricaError(f"{path}: duration disagreement")
        if any(value != glyph for value in source.values()):
            raise ArcaHistoricaError(f"{path}: witness disagrees with active glyph")
        paths.append(path)
    if len(cells) != len(glyphs):
        raise ArcaHistoricaError("rhythm contains unexpected/missing provenance cells")
    return glyphs, units[:], paths, ids


def build_fragment(*, vperm: dict[str, Any], rhythm: dict[str, Any], tone: dict[str, Any], witness_ledger: dict[str, Any]) -> dict[str, Any]:
    witnesses = witness_index(witness_ledger)
    rows, vpaths, vids = validate_vperm(vperm, witnesses)
    mapping, tpaths, tids = validate_tone(tone, witnesses)
    glyphs, units, rpaths, rids = validate_rhythm(rhythm, witnesses)
    count = len(units)
    if any(len(rows[v]) != count for v in VOICES):
        raise ArcaHistoricaError("Vperm and Rperm event counts must agree")
    protocols = {vperm.get("transcription_protocol"), rhythm.get("transcription_protocol"), tone.get("transcription_protocol")}
    if len(protocols) != 1:
        raise ArcaHistoricaError("historical components must share one transcription protocol")
    vscope, rscope, tscope = vperm["historical_scope"], rhythm["historical_scope"], tone["historical_scope"]
    if (vscope.get("syntagma"), vscope.get("pinax")) != (rscope.get("syntagma"), rscope.get("pinax")):
        raise ArcaHistoricaError("Vperm and Rperm must belong to the same Pinax")
    events, offset = [], 0
    for pos in range(1, count + 1):
        voices = {}
        for voice in VOICES:
            degree = rows[voice][pos - 1]
            voices[voice] = {
                "degree": degree,
                "pitch_class": mapping[degree],
                "provenance": {"vperm_cell": vpaths[(voice, pos)], "tone_cell": tpaths[degree]},
            }
        events.append({
            "index": pos,
            "offset_minim_units": offset,
            "duration_minim_units": units[pos - 1],
            "duration_symbol": glyphs[pos - 1],
            "rhythm_provenance": {"cell": rpaths[pos - 1]},
            "voices": voices,
        })
        offset += units[pos - 1]
    component_ids = {"pitch_permutation": vids, "rhythm": rids, "tone_lookup": tids}
    used = sorted({wid for ids in component_ids.values() for wid in ids})
    return {
        "format": FORMAT,
        "canonical": True,
        "status": "verified-historical-fragment",
        "edition_policy": "PRINT_1650",
        "description": "Pinax-IV historical fragment",
        "selection": {
            "syntagma": vscope.get("syntagma"), "pinax": vscope.get("pinax"),
            "stropha": vscope.get("stropha"), "vperm": vscope.get("vperm"),
            "rperm": rscope.get("rperm"), "tone": tscope.get("tone"),
            "tone_name": tscope.get("tone_name"), "system": tscope.get("system"),
            "tone_witness": tone["witness_policy"].get("witness"),
        },
        "time_unit": "relative minim",
        "total_duration_minim_units": offset,
        "events": events,
        "provenance": {
            "transcription_protocol": next(iter(protocols)),
            "components": {
                name: {"record": rec.get("record"), "witness_ids": component_ids[name]}
                for name, rec in (("pitch_permutation", vperm), ("rhythm", rhythm), ("tone_lookup", tone))
            },
            "witnesses": [
                {"id": wid, "independence_key": witnesses[wid]["independence_key"],
                 "institution": witnesses[wid].get("institution"), "record": witnesses[wid].get("record")}
                for wid in used
            ],
        },
        "explicitly_not_claimed": [
            "absolute octave/register placement", "modern MIDI note numbers",
            "absolute tempo or BPM", "modern beat-unit semantics",
            "phrase-level musica-ficta beyond the selected printed-p.51 tone witness",
            "identity with Kircher's prose Ave maris stella worked example",
        ],
    }


def build_default_fragment() -> dict[str, Any]:
    return build_fragment(vperm=load_json(VPERM), rhythm=load_json(RHYTHM), tone=load_json(TONE), witness_ledger=load_json(WITNESSES))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vperm", type=Path, default=VPERM)
    parser.add_argument("--rhythm", type=Path, default=RHYTHM)
    parser.add_argument("--tone", type=Path, default=TONE)
    parser.add_argument("--witnesses", type=Path, default=WITNESSES)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = build_fragment(vperm=load_json(args.vperm), rhythm=load_json(args.rhythm), tone=load_json(args.tone), witness_ledger=load_json(args.witnesses))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        s = result["selection"]
        print(f"ARCA HISTORICA - S{s['syntagma']} P{s['pinax']} Vperm {s['vperm']} / Rperm {s['rperm']} / Tone {s['tone']} {s['tone_name']} ({s['system']})")
        print("PRINT_1650 / VERIFIED HISTORICAL FRAGMENT\n")
        print("pos  off  dur  glyph        cantus  altus  tenor  bassus")
        for event in result["events"]:
            vv = "  ".join(f"{event['voices'][v]['degree']}:{event['voices'][v]['pitch_class']}" for v in VOICES)
            print(f"{event['index']:>3}  {event['offset_minim_units']:>3}  {event['duration_minim_units']:>3}  {event['duration_symbol']:<10}  {vv}")
        print(f"\nTotal: {result['total_duration_minim_units']} relative minim units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
