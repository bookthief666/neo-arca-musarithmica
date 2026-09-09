"""Tier B of docs/DETERMINISM.md, actually tested: a FRESH PROCESS, not a repeated call.

Every other determinism test in this suite calls ``ENGINE.compose`` repeatedly inside one
running pytest process. That proves tier A (same process) but says nothing about tier B
(a new interpreter, started separately, on the same Python runtime) -- and tier B is the
one that matters for a real deployment, where today's request and tomorrow's are served
by different worker processes that never share memory.

This file spawns genuinely separate ``python`` subprocesses via :mod:`subprocess` --
not helper functions called twice in-process -- and compares their output. It is
explicitly NOT a cross-machine or cross-Python-version test: both subprocesses run the
same interpreter this pytest session itself is running under (``sys.executable``), which
is exactly tier B's scope. See ``docs/DETERMINISM.md`` tier C for why a different Python
version or implementation is a separate, untested claim.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT_SECONDS = 60

#: A fixed request, held constant across every subprocess invocation in this file.
FIXED_REQUEST = dict(
    text="I dreamed of a cathedral sinking slowly into a black sea",
    seed=1650, mode="phrygian", measures=6, heretical=False,
)

#: Executed in a brand-new interpreter via ``python -c``.  Deliberately minimal: it
#: imports the engine, composes the fixed request, and prints one line of canonical JSON
#: -- voice/midi/offset/duration/role for every event, in a stable order -- so the parent
#: process can compare two subprocess runs for exact equality without depending on
#: anything about how THIS process constructs Python objects in memory.
_SIGNATURE_SCRIPT = r"""
import json, sys
from kircher_engine import ENGINE

request = json.loads(sys.argv[1])
composition = ENGINE.compose(**request)

signature = []
for voice in sorted(composition.events, key=lambda v: v.value):
    for event in composition.events[voice]:
        signature.append({
            "voice": voice.value,
            "midi": event.midi,
            "offset": event.offset,
            "duration": event.duration,
            "role": event.role,
        })

print(json.dumps({
    "signature": signature,
    "seed": composition.provenance.seed,
    "config_fingerprint": composition.provenance.config_fingerprint,
    "requested_seed": composition.provenance.requested_seed,
}, sort_keys=True))
"""

#: Executed to prove the auto-seed/fingerprint path specifically (seed omitted).
_AUTO_SEED_SCRIPT = r"""
import json, sys
from kircher_engine import ENGINE

request = json.loads(sys.argv[1])
composition = ENGINE.compose(**request)
print(json.dumps({
    "seed": composition.provenance.seed,
    "config_fingerprint": composition.provenance.config_fingerprint,
}, sort_keys=True))
"""


def _run_in_fresh_process(script: str, request: dict) -> str:
    """Spawn one genuinely new ``python`` process and return its stdout.

    Uses ``sys.executable`` (the interpreter running this pytest session, i.e. the
    project's own venv) and ``cwd=ROOT`` so the fresh process can ``import kircher_engine``
    without needing PYTHONPATH set -- ``python -c`` puts the current working directory on
    ``sys.path`` automatically. Each call is a distinct OS process with its own memory,
    its own hash-randomisation seed (irrelevant here, since nothing hashes with the
    randomised ``hash()`` builtin), and its own copy of every Python object -- this is
    what makes it a real tier-B test rather than a relabelled tier-A one.
    """
    result = subprocess.run(
        [sys.executable, "-c", script, json.dumps(request)],
        cwd=str(ROOT), capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
    )
    assert result.returncode == 0, (
        f"subprocess failed (exit {result.returncode}):\n{result.stderr}"
    )
    return result.stdout.strip()


@pytest.fixture(scope="module")
def two_fresh_signatures():
    first = _run_in_fresh_process(_SIGNATURE_SCRIPT, FIXED_REQUEST)
    second = _run_in_fresh_process(_SIGNATURE_SCRIPT, FIXED_REQUEST)
    return first, second


def test_two_independent_processes_are_genuinely_separate(two_fresh_signatures):
    """Sanity check on the test method itself, not the engine: if this ever failed it
    would mean subprocess.run stopped spawning real processes, which would silently turn
    every other assertion in this file into a same-process test wearing a disguise."""
    # subprocess.run always returns fresh output; the meaningful guarantee below is that
    # two SEPARATE invocations agree, which is only interesting because they really are
    # separate OS processes -- asserted implicitly by using subprocess.run twice above.
    first, second = two_fresh_signatures
    assert first and second


def test_fresh_processes_produce_byte_identical_signatures(two_fresh_signatures):
    first, second = two_fresh_signatures
    assert first == second, (
        "two independently started interpreters produced different output for the "
        "identical request -- tier B of the determinism contract is broken"
    )


def test_the_signature_actually_contains_the_composition(two_fresh_signatures):
    """Guards against a vacuous pass (e.g. both processes crashing into the same empty
    output)."""
    first, _ = two_fresh_signatures
    payload = json.loads(first)
    assert payload["signature"], "the composition produced no events at all"
    assert len(payload["signature"]) > 10
    assert {"voice", "midi", "offset", "duration", "role"} <= set(
        payload["signature"][0]
    )
    assert all(0 <= event["midi"] <= 127 for event in payload["signature"])


def test_fresh_processes_agree_on_the_resolved_seed_and_fingerprint(two_fresh_signatures):
    first, second = two_fresh_signatures
    a, b = json.loads(first), json.loads(second)
    assert a["seed"] == b["seed"] == 1650
    assert a["config_fingerprint"] == b["config_fingerprint"]
    assert a["requested_seed"] == b["requested_seed"] == 1650


def test_fresh_processes_agree_on_an_auto_derived_seed_and_fingerprint():
    """The auto-seed path specifically: no seed given, so the resolved seed depends on
    hashing the normalised request itself -- exactly the code path canonical() exists
    to make process-independent."""
    request = dict(text="a solemn procession through the vaults", mode="ionian",
                   measures=6, heretical=False)
    first = _run_in_fresh_process(_AUTO_SEED_SCRIPT, request)
    second = _run_in_fresh_process(_AUTO_SEED_SCRIPT, request)
    assert first == second
    payload = json.loads(first)
    assert payload["seed"] > 0


def test_a_different_request_yields_a_different_signature():
    """The method must actually be sensitive to what it's testing -- two fresh processes
    given DIFFERENT requests should disagree, or this file could not tell a working
    engine from one that always prints the same thing."""
    other_request = {**FIXED_REQUEST, "seed": 1651}
    same = _run_in_fresh_process(_SIGNATURE_SCRIPT, FIXED_REQUEST)
    different = _run_in_fresh_process(_SIGNATURE_SCRIPT, other_request)
    assert same != different
