"""Reading-v2 authority and rejection tests."""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import arca_mechanica_bridge as bridge

def request():
    m = bridge.build_manifest()
    c = m["critical_edition_carrier"]
    return {"format": "neo-arca-mechanica-reading/v2", "manifest_id": m["manifest_id"],
            "content_digest": m["content_digest"],
            "carrier_instance": {"instance_id": "carrier-pinax04-fragment-1",
                "carrier_id": c["carrier_id"], "edition_id": c["edition_id"], "location": "workspace"}}

def test_manifest_authority():
    m = bridge.build_manifest()
    assert m["format"] == "neo-arca-mechanica-manifest/v2"
    c = m["critical_edition_carrier"]
    assert c["classification"] == c["editorial_pairing"]["classification"] == "H1"
    assert c["pitch_source"]["content"]["rows"] == {
        "cantus": [5,5,3,2,3,3], "altus": [8,7,5,7,7,7],
        "tenor": [3,2,3,4,5,5], "bassus": [8,5,8,7,3,3]}
    r = c["rhythm_source"]["content"]
    assert r["glyphs"] == ["minim"]*4 + ["semibreve"]*2
    assert r["glyphs_classification"] == "H0"
    assert r["relative_minim_units"] == [1,1,1,1,2,2]
    assert r["relative_minim_units_classification"] == "derived project normalization"
    assert "physical_bands" not in c
    assert m["tone"]["witness_classification"] == "H0"
    assert m["tone"]["operating_policy_classification"] == "H1"
    assert m["tone"]["known_conflict"]
    assert c["rhythm_source"]["source_column_id"] == bridge.RHYTHM_SOURCE_ID
    assert c["rhythm_source"]["immutable_record"] == bridge.load_json(bridge.DEFAULT_RHYTHM)["record"]

def test_execution_parity_normalization_and_no_mutation():
    req = request()
    before = copy.deepcopy(req)
    first = bridge.execute_reading(req)
    assert req == before
    assert bridge.execute_reading(dict(reversed(list(req.items())))) == first
    assert first["request_fingerprint"] == hashlib.sha256(json.dumps(req, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    assert first["format"] == "neo-arca-mechanica-execution/v2"
    assert first["fragment"] == bridge.build_default_fragment()
    assert first["reading"]["tone"]["witness"] == bridge.build_manifest()["tone"]["witness"]

@pytest.mark.parametrize("mutate", [
    lambda x: x.update(extra=True),
    lambda x: x.update(format="neo-arca-mechanica-alignment/v1"),
    lambda x: x.update(manifest_id="stale"),
    lambda x: x.update(content_digest="0"*64),
    lambda x: x.update(tone={"number": 2}),
    lambda x: x.update(readingPosition=0),
    lambda x: x["carrier_instance"].update(extra=True),
    lambda x: x["carrier_instance"].update(carrier_id="wrong"),
    lambda x: x["carrier_instance"].update(edition_id="wrong"),
    lambda x: x["carrier_instance"].update(location="hand"),
    lambda x: x["carrier_instance"].update(instance_id=" "),
    lambda x: x["carrier_instance"].update(instance_id=True),
    lambda x: x.pop("manifest_id"),
])
def test_rejects_invalid_requests(mutate):
    req = request()
    mutate(req)
    with pytest.raises(bridge.ArcaMechanicaBridgeError):
        bridge.execute_reading(req)

@pytest.mark.parametrize("value", [None, [], True, 12, "reading"])
def test_non_objects_fail_closed(value):
    with pytest.raises(bridge.ArcaMechanicaBridgeError):
        bridge.execute_reading(value)

def test_cli_v1_rejection_and_v2_execution():
    cmd = [sys.executable, str(ROOT / "scripts/arca_mechanica_bridge.py"), "execute"]
    bad = subprocess.run(cmd, input=json.dumps({"format":"neo-arca-mechanica-alignment/v1"}), text=True, capture_output=True)
    assert bad.returncode == 1
    assert bad.stdout == ""
    good = subprocess.run(cmd, input=json.dumps(request()), text=True, capture_output=True)
    assert good.returncode == 0, good.stderr
    assert json.loads(good.stdout)["fragment"] == bridge.build_default_fragment()

def test_digest_tracks_content_without_shared_mutable_data(monkeypatch):
    original = bridge.load_json
    m = bridge.build_manifest()
    m["critical_edition_carrier"]["pitch_source"]["content"]["rows"]["bassus"][1] = 6
    assert bridge.build_manifest()["critical_edition_carrier"]["pitch_source"]["content"]["rows"]["bassus"][1] == 5
    def changed(path):
        record = original(path)
        if path == bridge.DEFAULT_VPERM:
            record["rows"]["bassus"][1] = 6
        return record
    monkeypatch.setattr(bridge, "load_json", changed)
    assert bridge.build_manifest()["content_digest"] != m["content_digest"]
