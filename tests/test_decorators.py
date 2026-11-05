import pytest
from axiomguard import precondition, postcondition, AxiomViolation, checks


@precondition(lambda x: x >= 0, "x must be non-negative")
@postcondition(lambda r: r >= 0)
def root(x):
    return x ** 0.5


@postcondition(checks.in_range(0, 1))
def ratio(a, b):
    return a / b


def test_pre_post():
    assert root(4) == 2
    with pytest.raises(AxiomViolation, match="non-negative"):
        root(-1)
    assert ratio(1, 2) == 0.5
    with pytest.raises(AxiomViolation):
        ratio(3, 1)
    assert root.__name__ == "root"


def test_plain_post_fail():
    @postcondition(lambda r: r is not None, "no result")
    def f():
        return None
    with pytest.raises(AxiomViolation, match="no result"):
        f()
