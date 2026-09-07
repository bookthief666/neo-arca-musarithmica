"""Shared fixtures and *independent* analysis helpers for the test suite.

The checkers below (``sample_grid``, ``parallel_perfects``, ``crossings``, ...) are
written from the definitions of the rules, not from the engine's implementation of them.
They consume the public JSON response only.  If the engine's own constraint module and
these helpers ever disagree, one of them is wrong -- which is the point.
"""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

VOICES_LOW_TO_HIGH = ("bass", "tenor", "alto", "soprano")
EPS = 1e-9


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def compose(client: TestClient):
    """POST /compose, asserting success, and return the parsed body."""

    def _compose(**payload) -> dict:
        payload.setdefault("text", "Sorrowful lament beneath a dying winter sun")
        payload.setdefault("seed", 418)
        payload.setdefault("measures", 8)
        response = client.post("/compose", json=payload)
        assert response.status_code == 200, response.text
        return response.json()

    return _compose


@pytest.fixture(scope="session")
def orthodox(compose) -> dict:
    return compose(heretical=False)


# --------------------------------------------------------------------------------------
# Independent analysis of a response
# --------------------------------------------------------------------------------------


def events_by_voice(body: dict) -> Dict[str, List[dict]]:
    return {v["voice"]: v["events"] for v in body["score"]["voices"]}


def sounding_at(events: Sequence[dict], moment: float) -> Optional[dict]:
    """The event a voice is sounding at *moment* -- the last one attacked by then."""
    found = None
    for event in events:
        if event["offset"] <= moment + EPS:
            found = event
        else:
            break
    return found


def sample_grid(body: dict) -> List[Tuple[float, Dict[str, int]]]:
    """Every attack point in the piece, with each voice's sounding pitch."""
    voices = events_by_voice(body)
    moments = sorted({e["offset"] for events in voices.values() for e in events})
    grid: List[Tuple[float, Dict[str, int]]] = []
    for moment in moments:
        row: Dict[str, int] = {}
        for name, events in voices.items():
            event = sounding_at(events, moment)
            assert event is not None, f"{name} is silent at offset {moment}"
            row[name] = event["midi"]
        grid.append((moment, row))
    return grid


def parallel_perfects(body: dict) -> List[dict]:
    """Consecutive perfect fifths, octaves or unisons between any pair of voices."""
    grid = sample_grid(body)
    found: List[dict] = []
    for (_, before), (moment, now) in zip(grid, grid[1:]):
        for lower, upper in combinations(VOICES_LOW_TO_HIGH, 2):
            pl, pu = before[lower], before[upper]
            cl, cu = now[lower], now[upper]
            if cl == pl or cu == pu:
                continue  # oblique or static motion cannot be parallel
            interval_before = abs(pu - pl) % 12
            interval_now = abs(cu - cl) % 12
            if interval_before != interval_now or interval_now not in (0, 7):
                continue
            if ((cl - pl) > 0) != ((cu - pu) > 0):
                continue  # contrary motion, a separate and lesser matter
            found.append({
                "position": moment,
                "voices": [lower, upper],
                "interval": "octave" if interval_now == 0 else "fifth",
            })
    return found


def crossings(body: dict) -> List[dict]:
    """Moments where a lower voice sounds above a higher one."""
    found: List[dict] = []
    for moment, row in sample_grid(body):
        for lower, upper in zip(VOICES_LOW_TO_HIGH, VOICES_LOW_TO_HIGH[1:]):
            if row[lower] > row[upper]:
                found.append({
                    "position": moment,
                    "voices": [lower, upper],
                    "pitches": [row[lower], row[upper]],
                })
    return found


def melodic_intervals(body: dict) -> Dict[str, List[int]]:
    """Each voice's successive melodic intervals in semitones."""
    return {
        name: [b["midi"] - a["midi"] for a, b in zip(events, events[1:])]
        for name, events in events_by_voice(body).items()
    }


def outer_motion_types(body: dict) -> Dict[str, int]:
    """Tally of contrary / oblique / similar / static motion between bass and soprano."""
    tally = {"contrary": 0, "oblique": 0, "similar": 0, "static": 0}
    grid = sample_grid(body)
    for (_, before), (_, now) in zip(grid, grid[1:]):
        db = now["bass"] - before["bass"]
        ds = now["soprano"] - before["soprano"]
        if db == 0 and ds == 0:
            tally["static"] += 1
        elif db == 0 or ds == 0:
            tally["oblique"] += 1
        elif (db > 0) == (ds > 0):
            tally["similar"] += 1
        else:
            tally["contrary"] += 1
    return tally


def strip_timing(body: dict) -> dict:
    """A copy of the response with wall-clock measurements removed."""
    import copy

    stable = copy.deepcopy(body)
    stable["search"].pop("elapsed_ms", None)
    return stable
