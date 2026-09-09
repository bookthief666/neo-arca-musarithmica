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
import json
import platform
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Sequence, TypeVar

T = TypeVar("T")

#: Width of the derived integer seeds.  64 bits is ample for the seed space, but it is
#: NOT "JSON-safe" in the sense that matters for a JS/Tone.js consumer: JavaScript's
#: ``Number`` only represents integers exactly up to 2**53 - 1, and this seed space goes
#: up to 2**64 - 1.  A seed at the top of this range serialised as a bare JSON number
#: would silently lose precision the moment a browser parses it.  The API therefore
#: serialises resolved seeds as decimal strings (see ``models.ProvenanceModel.seed`` and
#: ``docs/DETERMINISM.md``); this constant only bounds the internal integer, never the
#: wire representation.
_SEED_BITS = 64
_SEED_MASK = (1 << _SEED_BITS) - 1


class CanonicalisationError(TypeError):
    """Raised when a value cannot be serialised deterministically.

    Deliberately loud.  Silently falling back on ``repr`` for an unrecognised type is how
    a hash starts depending on something that was never meant to be part of it.
    """


#: Tags for the container/leaf types whose JSON rendering would otherwise be ambiguous.
#: Every tagged node is a two-element JSON array ``[tag, payload]``.  This is what makes
#: the scheme injective rather than merely "usually fine": a raw JSON array *always*
#: starts with ``[``, so a tagged node can never collide with an untagged scalar (which
#: always starts with ``"``, a digit, ``-``, or one of ``true``/``false``/``null``), and
#: two tagged nodes can only collide if both their tag string *and* their payload match --
#: the tag alone already rules out cross-type collisions such as a float and a bytes
#: value both formatting to the digits ``"61"``.
_FLOAT_TAG = "float"
_BYTES_TAG = "bytes"
_SET_TAG = "set"
_MAP_TAG = "map"
_LIST_TAG = "list"


def _dumps(node: Any) -> str:
    return json.dumps(node, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def canonical(value: Any) -> str:
    """A deterministic, **type-unambiguous** textual form of *value*.

    ``repr`` is not a serialisation format and must not be treated as one -- see the
    module docstring for the concrete failures that motivated this function. But
    avoiding ``repr`` is not sufficient by itself: naively mapping every Python value onto
    a "natural" JSON shape reintroduces the same class of bug one level down, because
    JSON's own type system is coarser than Python's.  Untagged, all of the following would
    silently collide:

    * ``1.0`` and ``"1"``, because ``f"{1.0:.17g}"`` is the string ``"1"``;
    * ``b"a"`` and ``"61"``, because ``b"a".hex()`` is the string ``"61"``;
    * ``{1: "x"}`` and ``{"1": "x"}``, because a naive canonicaliser stringifies keys
      with ``str(k)``;
    * ``{1, 2, 3}`` and ``["1", "2", "3"]``, because a set canonicalised element-by-element
      into strings looks exactly like a list of those same strings.

    So every value that is not already unambiguous in JSON -- floats, bytes/bytearray,
    sets/frozensets, mappings, and sequences (including plain JSON-representable lists,
    so an actual Python list can never be mistaken for one of the tagged forms above) --
    is wrapped as ``[tag, payload]`` before serialisation.  ``None``, ``bool``, ``int``
    and ``str`` are left bare: JSON already renders them as mutually distinct token
    shapes (``null``, ``true``/``false``, a bare number, a quoted string), and none of
    those shapes can ever equal a tagged array's shape, which always starts with ``[``.

    Explicit design choices, each intentional and each tested in
    ``tests/test_canonical.py``:

    * **Enum reduces transparently to its ``.value``.**  ``ModeName.IONIAN`` and the bare
      string ``"ionian"`` canonicalise identically and are treated as the same
      configuration value -- the class name is an implementation detail that renaming
      an enum should not change the music, so no separate enum tag is added.
    * **``list`` and ``tuple`` are canonically equivalent.**  Both use the ``"list"`` tag
      and preserve element order.  The codebase interchanges them freely (a dataclass
      field typed as a tuple, a JSON payload built as a list), and the property that
      matters here is *ordered sequence* vs. *unordered collection* (list/tuple vs.
      set), which remains fully distinct.
    * **``-0.0`` canonicalises identically to ``0.0``.**  Both are tagged ``"float"`` (so
      neither collides with any other type), and within that tag they render as the same
      payload, since the sign of zero carries no meaning for any parameter this engine
      hashes.
    * **``bool`` stays distinct from ``int``.**  Left untagged deliberately: JSON already
      renders ``True`` as ``true`` and ``1`` as ``1``, two token shapes that cannot
      collide, so no extra tagging is needed here.
    * **NaN and +/-infinity are refused, not hashed.**  A silently-accepted non-finite
      float would make two "equal" configurations hash differently depending on platform
      floating-point behaviour, which is precisely the fragility this function exists to
      remove.
    * **An unrecognised type raises `CanonicalisationError`.**  Guessing a shape for a
      type nobody has reasoned about is how a hash starts depending on something it was
      never meant to.
    """
    return _dumps(_normalise(value))


def _normalise(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, Enum):
        return _normalise(value.value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise CanonicalisationError(f"cannot canonicalise non-finite float {value!r}")
        # 17 significant digits round-trips any IEEE double exactly; normalise -0.0 so it
        # cannot hash differently from 0.0.  Tagged, so this can never collide with a
        # plain string or int that happens to look like the same digits.
        return [_FLOAT_TAG, f"{value + 0.0:.17g}"]
    if isinstance(value, (bytes, bytearray)):
        # Tagged, so hex digits can never collide with an ordinary string of the same
        # characters (e.g. b"a" -> "61" would otherwise equal the string "61").
        return [_BYTES_TAG, value.hex()]
    if isinstance(value, Mapping):
        # Keys are canonicalised through this same function, not str()-ed, so an int key
        # and a string key with the same digits never collide (canonical(1) == "1", a
        # 1-character token; canonical("1") == "\"1\"", a 3-character token -- distinct
        # once the outer serialiser re-quotes them). Sorting by that text keeps insertion
        # order from mattering, and works regardless of the key's original type because
        # the sort key is always a plain string.
        entries = sorted((canonical(k), _normalise(v)) for k, v in value.items())
        return [_MAP_TAG, [[k, v] for k, v in entries]]
    if isinstance(value, (set, frozenset)):
        # Elements are normalised (not pre-stringified) so the payload is a real nested
        # structure, not a list of strings that could be confused with an ordinary list
        # of strings -- the "list" tag on genuine lists is what actually prevents that
        # confusion, but storing normalised nodes here keeps the structure uniform too.
        normalised = [_normalise(v) for v in value]
        normalised.sort(key=_dumps)
        return [_SET_TAG, normalised]
    if isinstance(value, Sequence):
        return [_LIST_TAG, [_normalise(v) for v in value]]
    raise CanonicalisationError(
        f"no deterministic form defined for {type(value).__name__}; add one to "
        f"determinism._normalise rather than relying on repr()"
    )


def stable_hash(*parts: Any) -> int:
    """A stable, cross-process, cross-version integer hash of *parts*.

    ``hash()`` is deliberately avoided: CPython randomises string hashing per process,
    which would silently break reproducibility between requests.  Each part is
    canonicalised (see :func:`canonical`) rather than ``repr``-ed.
    """
    digest = hashlib.blake2b(digest_size=16)
    for part in parts:
        digest.update(canonical(part).encode("utf-8"))
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
    #: Versions the byte-identical MIDI claim is scoped to.  Not part of the seed.
    #: ``default_factory=dict`` rather than a bare mutable default: a frozen dataclass
    #: still shares one bound default object across every instance that doesn't override
    #: it, and an empty mapping literal used as a field default is the classic version of
    #: that trap, so a factory is used even though the field is never mutated in place.
    runtime: Mapping[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "engine_version": self.engine_version,
            "seed": self.seed,
            "requested_seed": self.requested_seed,
            "law_profile": self.law_profile,
            "config_fingerprint": self.config_fingerprint,
            "runtime": dict(self.runtime),
        }


def fingerprint(payload: Mapping[str, Any]) -> str:
    """A short, stable hex fingerprint of a configuration mapping.

    Canonicalised, so two configurations that are equal fingerprint identically no matter
    what order their keys were built in.
    """
    digest = hashlib.blake2b(canonical(payload).encode("utf-8"), digest_size=8)
    return digest.hexdigest()


def runtime_versions() -> Dict[str, str]:
    """The versions a byte-identical reproduction depends on.

    Recorded in provenance, and deliberately **not** hashed into the seed: the same
    request must choose the same notes on any machine.  What these versions affect is the
    final serialisation -- music21 decides how a score becomes MIDI bytes -- so they bound
    the *byte-identical* claim, not the *same-composition* claim.  See
    ``docs/DETERMINISM.md``.
    """
    try:
        from music21 import VERSION_STR as music21_version
    except Exception:  # pragma: no cover - music21 is a hard dependency
        music21_version = "unknown"
    return {
        "python": platform.python_version(),
        "music21": music21_version,
        "implementation": platform.python_implementation(),
    }


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
    "canonical", "CanonicalisationError", "runtime_versions",
]
