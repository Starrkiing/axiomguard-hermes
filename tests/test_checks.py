import pytest
from axiomguard import checks as c


def test_is_type():
    assert c.is_type(int).evaluate(1).passed
    assert not c.is_type(int, float).evaluate("x").passed


def test_in_range():
    assert c.in_range(0, 10).evaluate(5).passed
    assert not c.in_range(0, 10).evaluate(11).passed
    assert c.in_range(lo=0).evaluate(10**9).passed
    assert not c.in_range(hi=0).evaluate(1).passed


def test_non_empty_and_keys():
    assert c.non_empty().evaluate([1]).passed
    assert not c.non_empty().evaluate("").passed
    assert not c.non_empty().evaluate(None).passed
    r = c.has_keys(["a", "b"]).evaluate({"a": 1})
    assert not r.passed and "b" in r.message
    assert c.has_keys(["a"]).evaluate({"a": 1}).passed


@pytest.mark.parametrize("seq,kw,ok", [
    ([1, 2, 2, 3], {}, True), ([1, 2, 2], {"strict": True}, False),
    ([3, 2, 1], {"decreasing": True, "strict": True}, True), ([1, 0], {}, False), ([], {}, True)])
def test_monotonic(seq, kw, ok):
    assert c.monotonic(**kw).evaluate(seq).passed is ok


def test_hash():
    h = c.digest("hello")
    assert c.hash_matches(h).evaluate("hello").passed
    assert c.hash_matches(h.upper()).evaluate(b"hello").passed
    assert not c.hash_matches(h).evaluate("world").passed
    assert c.hash_matches(c.digest("x", "md5"), "md5").evaluate("x").passed


def test_from_spec():
    data = {"items": [1, 2, 3], "meta": {"n": 3}, "tag": "x"}
    specs = [
        {"check": "is_type", "type": "dict"},
        {"check": "is_type", "type": ["int", "float"], "path": "meta.n"},
        {"check": "in_range", "lo": 1, "hi": 5, "path": "items.2"},
        {"check": "non_empty", "path": "items", "name": "items_present"},
        {"check": "has_keys", "keys": ["items", "meta"]},
        {"check": "monotonic", "strict": True, "path": "items"},
        {"check": "hash_matches", "expected": c.digest("x"), "path": "tag"},
        {"check": "non_empty", "name": "labelled"},
    ]
    axs = [c.from_spec(s) for s in specs]
    assert all(a.evaluate(data).passed for a in axs)
    assert axs[3].name == "items_present" and axs[-1].name == "labelled"
    with pytest.raises(ValueError):
        c.from_spec({"check": "nope"})
