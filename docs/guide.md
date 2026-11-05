# Guide

## Concepts

- **Axiom** — a name plus a predicate. The predicate returns `bool` or
  `(bool, message)`. Exceptions raised by a predicate count as failures.
- **Verifier** — an ordered list of axioms. `verify(value, strict=False, fail_fast=False)`
  returns a **Report**.
- **Report** — `passed`, `failures`, `summary()`, `to_dict()`.
- **Decorators** — `precondition(pred, message)` and `postcondition(pred_or_axiom, message)`
  raise `AxiomViolation` when violated.

## Built-in checks (`axiomguard.checks`)

| Factory | Passes when |
|---|---|
| `is_type(*types)` | value is an instance of one of `types` |
| `in_range(lo, hi)` | `lo <= value <= hi` (either bound optional) |
| `non_empty()` | value is not `None` and has length > 0 |
| `has_keys(keys)` | every key is present in a mapping |
| `monotonic(strict, decreasing)` | sequence is ordered |
| `hash_matches(expected, algorithm)` | hex digest of value equals `expected` |

## Rule files

`checks.from_spec(dict)` builds an axiom from JSON. Keys: `check` (required),
check parameters, optional `path` (dot-separated, list indices allowed) and
`name`. `is_type` accepts `str int float bool list dict null`.
