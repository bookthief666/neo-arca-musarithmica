"""determinism.py -- Provenance and controlled randomness.

Determinism is a first-class requirement of the Neo-Arca: for identical semantic input,
configuration, seed, law profile and engine version, the engine must emit byte-identical
compositions.  Two things follow, and this module enforces both:

1. **No global randomness.**  ``random.random`` / ``random.seed`` are never touched.
   Every stochastic decision draws from an explicit :class:`SeedStream` instance.
2. **Structured seed derivation.**  Sub-streams are derived by hashing the parent seed
   with a label, so adding a new decision point in (say) the diminution stage cannot
   perturb the pitches already chosen by the harmony stage.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, List, Mapping, Sequence, TypeVar

T = TypeVar("T")

#: Width of the derived integer seeds.  64 bits is ample and stays JSON-safe.
_SEED_BITS = 64
_SEED_MASK = (1 << _SEED_BITS) - 1


def stable_hash(*parts: Any) -> int:
    """A stable, cross-process, cross-version integer hash of *parts*.

    ``hash()`` is deliberately avoided: CPython randomises string hashing per process,
    which would silently break reproducibility between requests.
    """
    digest = hashlib.blake2b(digest_size=16)
    for part in parts:
        digest.update(repr(part).encode("utf-8"))
        digest.update(b"\x1f")  # unit separator, so ("ab","c") != ("a","bc")
    return int.from_bytes(digest.digest(), "big") & _SEED_MASK


def coerce_seed(seed: "int | str | None", *, fallback: Any = None) -> int:
    """Turn a user-supplied seed of any accepted shape into a stable integer.

    ``None`` derives the seed from *fallback* (normally the normalised request), so an
    omitted seed still yields a reproducible composition for the same request.
    """
    if seed is None:
        return stable_hash("auto-seed", fallback)
    if isinstance(seed, bool):  # bool is an int subclass; reject it explicitly
        raise TypeError("seed must be an integer or string, not bool")
    if isinstance(seed, int):
        return seed & _SEED_MASK
    return stable_hash("string-seed", str(seed))


@dataclass(frozen=True)
class Provenance:
    """Everything needed to reconstruct a composition later."""

    engine_version: str
    seed: int
    requested_seed: "int | str | None"
    law_profile: str
    config_fingerprint: str

    def as_dict(self) -> dict:
        return {
            "engine_version": self.engine_version,
            "seed": self.seed,
            "requested_seed": self.requested_seed,
            "law_profile": self.law_profile,
            "config_fingerprint": self.config_fingerprint,
        }


def fingerprint(payload: Mapping[str, Any]) -> str:
    """A short, stable hex fingerprint of a configuration mapping."""
    items = sorted((str(k), repr(v)) for k, v in payload.items())
    digest = hashlib.blake2b(digest_size=8)
    for key, value in items:
        digest.update(key.encode("utf-8"))
        digest.update(b"=")
        digest.update(value.encode("utf-8"))
        digest.update(b";")
    return digest.hexdigest()


class SeedStream:
    """A labelled, deterministically derivable pseudo-random stream.

    ``SeedStream`` wraps a private :class:`random.Random`.  Deriving a child stream is a
    pure function of ``(root_seed, label_path)``, so streams are stable under
    reordering of the *creation* of sibling streams -- only the label matters.
    """

    __slots__ = ("_root", "_path", "_rng")

    def __init__(self, seed: int, path: Sequence[str] = ()) -> None:
        self._root = seed & _SEED_MASK
        self._path = tuple(path)
        self._rng = random.Random(stable_hash(self._root, self._path))

    # -- construction ------------------------------------------------------------
    def derive(self, *labels: Any) -> "SeedStream":
        """A child stream identified by this stream's path plus *labels*."""
        return SeedStream(self._root, self._path + tuple(str(x) for x in labels))

    @property
    def root_seed(self) -> int:
        return self._root

    @property
    def path(self) -> tuple:
        return self._path

    # -- primitives --------------------------------------------------------------
    def random(self) -> float:
        return self._rng.random()

    def randint(self, low: int, high: int) -> int:
        """Inclusive integer in ``[low, high]``."""
        return self._rng.randint(low, high)

    def uniform(self, low: float, high: float) -> float:
        return self._rng.uniform(low, high)

    def chance(self, probability: float) -> bool:
        return self._rng.random() < probability

    def choice(self, items: Sequence[T]) -> T:
        if not items:
            raise IndexError("cannot choose from an empty sequence")
        return items[self._rng.randrange(len(items))]

    def weighted_choice(self, items: Sequence[T], weights: Sequence[float]) -> T:
        """Pick one item with probability proportional to its (non-negative) weight."""
        if len(items) != len(weights):
            raise ValueError("items and weights must be the same length")
        if not items:
            raise IndexError("cannot choose from an empty sequence")
        total = 0.0
        for w in weights:
            if w < 0:
                raise ValueError("weights must be non-negative")
            total += w
        if total <= 0.0:
            return self.choice(items)
        target = self._rng.random() * total
        cumulative = 0.0
        for item, weight in zip(items, weights):
            cumulative += weight
            if target < cumulative:
                return item
        return items[-1]  # pragma: no cover - float drift guard

    def weighted_order(
        self, items: Sequence[T], weights: Sequence[float]
    ) -> List[T]:
        """Weighted sampling *without* replacement -- a full randomised ranking.

        This is how the voicing solver turns "these candidates score well" into a
        concrete, backtrackable order: better candidates are very likely to come first,
        but a different seed genuinely explores a different (still good) realisation.
        """
        pool = list(items)
        pool_weights = [max(0.0, float(w)) for w in weights]
        ordered: List[T] = []
        while pool:
            total = sum(pool_weights)
            if total <= 0.0:
                ordered.extend(pool)
                break
            target = self._rng.random() * total
            cumulative = 0.0
            index = len(pool) - 1
            for i, weight in enumerate(pool_weights):
                cumulative += weight
                if target < cumulative:
                    index = i
                    break
            ordered.append(pool.pop(index))
            pool_weights.pop(index)
        return ordered

    def jitter(self, magnitude: float) -> float:
        """A symmetric perturbation in ``[-magnitude, +magnitude]``."""
        return (self._rng.random() * 2.0 - 1.0) * magnitude

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"SeedStream(root={self._root}, path={'/'.join(self._path) or '<root>'})"


__all__ = [
    "stable_hash", "coerce_seed", "fingerprint", "Provenance", "SeedStream",
]
