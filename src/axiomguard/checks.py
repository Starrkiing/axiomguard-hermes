"""Built-in generic axiom factories."""
from __future__ import annotations

import hashlib
from typing import Any, Iterable, Optional

from .core import Axiom


def is_type(*types: type, name: Optional[str] = None) -> Axiom:
    names = "|".join(t.__name__ for t in types)
    return Axiom(name or f"is_type[{names}]",
                 lambda v: (isinstance(v, types), f"expected {names}, got {type(v).__name__}"))


def in_range(lo: Any = None, hi: Any = None, name: Optional[str] = None) -> Axiom:
    def chk(v):
        ok = (lo is None or v >= lo) and (hi is None or v <= hi)
        return ok, f"{v!r} {'within' if ok else 'outside'} [{lo}, {hi}]"
    return Axiom(name or f"in_range[{lo},{hi}]", chk)


def non_empty(name: Optional[str] = None) -> Axiom:
    return Axiom(name or "non_empty",
                 lambda v: (v is not None and len(v) > 0, "value is empty"))


def has_keys(keys: Iterable[str], name: Optional[str] = None) -> Axiom:
    keys = list(keys)
    def chk(v):
        missing = [k for k in keys if k not in v]
        return not missing, f"missing keys: {missing}" if missing else "all keys present"
    return Axiom(name or "has_keys", chk)


def monotonic(strict: bool = False, decreasing: bool = False,
              name: Optional[str] = None) -> Axiom:
    def chk(seq):
        seq = list(seq)
        for i, (a, b) in enumerate(zip(seq, seq[1:])):
            if decreasing:
                a, b = b, a
            if (a >= b) if strict else (a > b):
                return False, f"order broken at index {i + 1}"
        return True, "monotonic"
    return Axiom(name or "monotonic", chk)


def digest(data: Any, algorithm: str = "sha256") -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.new(algorithm, data).hexdigest()


def hash_matches(expected: str, algorithm: str = "sha256",
                 name: Optional[str] = None) -> Axiom:
    def chk(v):
        got = digest(v, algorithm)
        return got == expected.lower(), f"{algorithm} {got}"
    return Axiom(name or f"hash_matches[{algorithm}]", chk)


_TYPES = {"str": str, "int": int, "float": (int, float), "bool": bool,
          "list": list, "dict": dict, "null": type(None)}


def from_spec(spec: dict) -> Axiom:
    """Build an axiom from a JSON-friendly dict, e.g. {"check": "in_range", "lo": 0}.

    An optional "path" (dot-separated) selects a nested field first.
    """
    spec = dict(spec)
    kind = spec.pop("check")
    path = spec.pop("path", None)
    label = spec.pop("name", None)
    if kind == "is_type":
        t = spec["type"]
        types = tuple(_TYPES[x] for x in (t if isinstance(t, list) else [t]))
        flat = tuple(x for t2 in types for x in (t2 if isinstance(t2, tuple) else (t2,)))
        ax = is_type(*flat)
    elif kind == "in_range":
        ax = in_range(spec.get("lo"), spec.get("hi"))
    elif kind == "non_empty":
        ax = non_empty()
    elif kind == "has_keys":
        ax = has_keys(spec["keys"])
    elif kind == "monotonic":
        ax = monotonic(spec.get("strict", False), spec.get("decreasing", False))
    elif kind == "hash_matches":
        ax = hash_matches(spec["expected"], spec.get("algorithm", "sha256"))
    else:
        raise ValueError(f"unknown check: {kind}")
    if path:
        inner = ax.check
        def resolve(v, _parts=path.split(".")):
            for p in _parts:
                v = v[int(p)] if isinstance(v, list) else v[p]
            return v
        ax = Axiom(label or f"{path}:{ax.name}", lambda v: inner(resolve(v)))
    elif label:
        ax = Axiom(label, ax.check)
    return ax
