"""B10 section 4: concurrent ``compose()`` requests are safe -- verified, not assumed.

``POST /compose`` is an ordinary synchronous ``def`` handler (see ``main.py``'s module
docstring), which FastAPI/Starlette runs on its worker threadpool rather than on the
event loop -- so two requests genuinely can call ``ENGINE.compose(...)`` on different
threads of the *same process* at the same time. An explicit read-only audit (recorded
here rather than only in a commit message) found:

* ``KircherEngine`` (the single shared ``ENGINE`` instance, ``kircher_engine.py``) only
  reads ``self.analyzer``/``self.budget`` in ``compose()``; every other value (`config`,
  `plan`, `frame`, `stats`, a fresh `VoicingSolver`/`DiminutionEngine`/`Renderer`) is a
  local created fresh per call. Nothing is written back onto ``self``.
* ``SemanticAnalyzer.analyze()`` (``semantics.py``) only reads module-level constant
  lookup tables (`LEXICON`, `MODE_AFFINITY`, `INSTRUMENTS`, `ARTICULATIONS`), populated
  once at import and never mutated afterward.
* The law profiles (``constraints.PROFILES``, `ORTHODOX`/`HERETICAL`) are frozen
  dataclasses built once at import; `get_profile()` only reads the dict.
* All randomness goes through a per-request ``determinism.SeedStream``, itself wrapping
  a private ``random.Random`` instance (never the global ``random.seed``/``random.random``
  functions -- grepping the whole codebase finds those names only in this docstring and
  in ``determinism.py``'s own docstring stating they are never called).
* ``midi_export.score_to_midi_bytes`` writes through ``tempfile.mkstemp`` (an atomic,
  collision-proof unique-file primitive), reads it back, and unlinks it in a ``finally``
  block -- two concurrent exports cannot collide on a filename.

No lock was added, because no shared mutable state was found that would need one. The
tests below exercise that conclusion under real concurrent execution rather than only
by inspection.
"""

from __future__ import annotations

import random
from concurrent.futures import ThreadPoolExecutor

import pytest

from kircher_engine import ENGINE

CONCURRENCY = 12


def test_identical_fixed_seed_requests_are_stable_under_concurrent_execution():
    """The same request, fired from many threads at once against the one shared
    ``ENGINE``, must all resolve to the identical composition -- proving no cross-request
    state leakage perturbs a deterministic result."""
    payload = dict(
        text="a solemn procession through the vaulted cloister", seed=418, measures=8,
    )

    def run(_):
        return ENGINE.compose(**payload)

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        results = list(pool.map(run, range(CONCURRENCY)))

    first = results[0]
    for other in results[1:]:
        assert other.provenance.seed == first.provenance.seed
        assert other.voice_payload() == first.voice_payload()
        assert other.validation.as_dict() == first.validation.as_dict()


def test_distinct_concurrent_requests_remain_independent():
    """Many *different* requests fired at once must each get their own, distinct,
    internally-consistent result -- not a result mixed up with a neighbour's."""
    payloads = [
        dict(text=f"phrase number {i} for the concurrency sweep", seed=1000 + i,
             measures=4 + (i % 5))
        for i in range(CONCURRENCY)
    ]

    def run(payload):
        return payload, ENGINE.compose(**payload)

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        results = list(pool.map(run, payloads))

    seeds_seen = set()
    for payload, composition in results:
        # Each result must actually correspond to what was asked -- not a neighbour's.
        assert composition.config.text == payload["text"]
        assert composition.config.measures == payload["measures"]
        assert composition.validation.defects == []
        seeds_seen.add(composition.provenance.seed)
    assert len(seeds_seen) == CONCURRENCY, "distinct requests collided onto one seed"


def test_concurrent_midi_export_does_not_collide_on_temporary_files():
    """Exercises the exact hazard a fixed/predictable temp filename would create: many
    threads calling the exporter at once."""
    from midi_export import composition_to_midi

    composition = ENGINE.compose(
        text="a solemn procession through the vaulted cloister", seed=418, measures=6,
    )

    def export(_):
        return composition_to_midi(composition)

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        blobs = list(pool.map(export, range(CONCURRENCY)))

    assert all(blob == blobs[0] for blob in blobs), (
        "concurrent MIDI export produced different bytes for the identical composition"
    )
    assert all(blob.startswith(b"MThd") for blob in blobs)


def test_global_random_state_is_untouched_by_concurrent_composition():
    """Mirrors tests/test_determinism.py's same-process invariant, but under genuine
    concurrent load: the engine must never touch the *global* random module state,
    on any thread."""
    random.seed(20260910)
    before = random.getstate()

    def run(i):
        return ENGINE.compose(
            text=f"concurrency random-state probe {i}", seed=i, measures=4,
        )

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        list(pool.map(run, range(CONCURRENCY)))

    assert random.getstate() == before


def test_concurrent_requests_through_the_real_api_all_succeed(client):
    """The same guarantee, exercised through the actual HTTP layer (TestClient) rather
    than by calling the engine directly, so the FastAPI/Starlette request-handling path
    is included in what's being verified."""
    def call(i):
        return client.post("/compose", json={
            "text": f"api concurrency probe {i}", "seed": i, "measures": 4,
        })

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        responses = list(pool.map(call, range(CONCURRENCY)))

    for response in responses:
        assert response.status_code == 200, response.text
        assert response.json()["validation"]["passed"] is True
