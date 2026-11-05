import pytest
from axiomguard import Axiom, Verifier, AxiomViolation


def test_pass_and_fail():
    v = Verifier([Axiom("pos", lambda x: x > 0), Axiom("even", lambda x: x % 2 == 0, "must be even")])
    r = v.verify(3)
    assert not r.passed and len(r.failures) == 1
    assert r.failures[0].message == "must be even"
    assert "1/2 axioms passed" in r.summary()
    assert v.verify(4).passed


def test_tuple_message_and_exception():
    assert Axiom("t", lambda x: (False, "bad")).evaluate(1).message == "bad"
    res = Axiom("boom", lambda x: 1 / 0).evaluate(1)
    assert not res.passed and "ZeroDivisionError" in res.message


def test_strict_and_fail_fast():
    v = Verifier([Axiom("a", lambda x: False), Axiom("b", lambda x: True)])
    assert len(v.verify(0, fail_fast=True).results) == 1
    with pytest.raises(AxiomViolation) as ei:
        v.verify(0, strict=True)
    assert not ei.value.report.passed


def test_rule_decorator_and_dict():
    v = Verifier()
    @v.rule(description="non-negative")
    def nonneg(x):
        return x >= 0
    d = v.verify(-1).to_dict()
    assert d == {"passed": False, "results": [{"name": "nonneg", "passed": False, "message": "non-negative"}]}
    assert v.add(Axiom("x", lambda x: True)) is v
