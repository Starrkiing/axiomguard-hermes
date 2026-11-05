"""Pre/post-condition decorators."""
from __future__ import annotations

import functools
import inspect
from typing import Callable

from .core import Axiom, Report, AxiomViolation


def _fail(name: str, msg: str):
    from .core import Result
    raise AxiomViolation(Report([Result(name, False, msg)]))


def precondition(pred: Callable[..., bool], message: str = "precondition failed"):
    """Check ``pred(*args, **kwargs)`` before calling the function."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not pred(*args, **kwargs):
                _fail(f"pre:{fn.__name__}", message)
            return fn(*args, **kwargs)
        return wrapper
    return deco


def postcondition(check, message: str = "postcondition failed"):
    """Check the return value with a predicate or an Axiom."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            out = fn(*args, **kwargs)
            if isinstance(check, Axiom):
                res = check.evaluate(out)
                if not res.passed:
                    _fail(f"post:{fn.__name__}", res.message)
            elif not check(out):
                _fail(f"post:{fn.__name__}", message)
            return out
        return wrapper
    return deco
