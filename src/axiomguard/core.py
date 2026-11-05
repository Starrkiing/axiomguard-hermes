"""Core types: Axiom, Result, Report, Verifier."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, List, Optional


class AxiomViolation(Exception):
    """Raised when verification fails in strict mode."""

    def __init__(self, report: "Report"):
        self.report = report
        super().__init__(report.summary())


@dataclass(frozen=True)
class Result:
    name: str
    passed: bool
    message: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "message": self.message}


@dataclass
class Axiom:
    """A named predicate. ``check`` returns bool, or (bool, message)."""

    name: str
    check: Callable[[Any], Any]
    description: str = ""

    def evaluate(self, value: Any) -> Result:
        try:
            out = self.check(value)
        except Exception as exc:  # a crashing check is a failure, not a crash
            return Result(self.name, False, f"error: {type(exc).__name__}: {exc}")
        if isinstance(out, tuple):
            ok, msg = bool(out[0]), str(out[1]) if len(out) > 1 else ""
        else:
            ok, msg = bool(out), ""
        if not msg:
            msg = "ok" if ok else (self.description or "check failed")
        return Result(self.name, ok, msg)


@dataclass
class Report:
    results: List[Result] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failures(self) -> List[Result]:
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        total, bad = len(self.results), len(self.failures)
        head = f"{total - bad}/{total} axioms passed"
        lines = [head] + [f"  FAIL {r.name}: {r.message}" for r in self.failures]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"passed": self.passed, "results": [r.to_dict() for r in self.results]}


class Verifier:
    """Runs a collection of axioms against a value."""

    def __init__(self, axioms: Optional[Iterable[Axiom]] = None):
        self.axioms: List[Axiom] = list(axioms or [])

    def add(self, axiom: Axiom) -> "Verifier":
        self.axioms.append(axiom)
        return self

    def rule(self, name: Optional[str] = None, description: str = ""):
        """Decorator registering a function as an axiom."""
        def deco(fn):
            self.add(Axiom(name or fn.__name__, fn, description))
            return fn
        return deco

    def verify(self, value: Any, strict: bool = False, fail_fast: bool = False) -> Report:
        report = Report()
        for ax in self.axioms:
            res = ax.evaluate(value)
            report.results.append(res)
            if fail_fast and not res.passed:
                break
        if strict and not report.passed:
            raise AxiomViolation(report)
        return report
