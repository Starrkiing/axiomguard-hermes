# axiomguard-hermes

`axiomguard` is a small, dependency-free Python library for declaring and
checking **invariants** ("axioms") on data and function outputs.

## Install

```bash
pip install .
```

## Usage

```python
from axiomguard import Verifier, Axiom, checks, postcondition

v = Verifier([
    checks.has_keys(["prices"]),
    Axiom("prices_sorted", lambda d: checks.monotonic().check(d["prices"])),
])
report = v.verify({"prices": [1, 2, 3]})
print(report.passed, report.summary())

@postcondition(checks.in_range(0, 1))
def ratio(a, b):
    return a / b
```

Use `v.verify(value, strict=True)` to raise `AxiomViolation` on failure.

## CLI

```bash
axiomguard data.json rules.json [--json]   # exit 0 pass, 1 fail, 2 error
```

`rules.json`:

```json
{"rules": [
  {"check": "has_keys", "keys": ["values"]},
  {"check": "monotonic", "path": "values", "strict": true}
]}
```

See [docs/](docs/) for details. Tests: `pip install -e .[test] && pytest`.

## License

MIT
