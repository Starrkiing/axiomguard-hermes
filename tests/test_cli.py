import json
from axiomguard.cli import main


def _w(p, name, obj):
    f = p / name
    f.write_text(json.dumps(obj))
    return str(f)


def test_cli_pass_fail(tmp_path, capsys):
    data = _w(tmp_path, "d.json", {"values": [1, 2, 3]})
    ok = _w(tmp_path, "ok.json", {"rules": [{"check": "monotonic", "path": "values"}]})
    bad = _w(tmp_path, "bad.json", {"rules": [{"check": "has_keys", "keys": ["missing"]}]})
    assert main([data, ok]) == 0
    assert main([data, bad, "--json"]) == 1
    out = capsys.readouterr().out
    assert '"passed": false' in out


def test_cli_errors(tmp_path):
    data = _w(tmp_path, "d.json", {})
    assert main([str(tmp_path / "nope.json"), data]) == 2
    assert main([data, _w(tmp_path, "r.json", {"x": 1})]) == 2
    assert main([data, _w(tmp_path, "r2.json", {"rules": [{"check": "zzz"}]})]) == 2
