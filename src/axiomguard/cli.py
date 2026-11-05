"""Command line: axiomguard DATA.json RULES.json [--json]"""
from __future__ import annotations

import argparse
import json
import sys

from .checks import from_spec
from .core import Verifier


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="axiomguard", description="Verify JSON data against a rules file.")
    p.add_argument("data")
    p.add_argument("rules", help='JSON file: {"rules": [{"check": ..., ...}]}')
    p.add_argument("--json", action="store_true", help="emit machine-readable report")
    a = p.parse_args(argv)
    try:
        with open(a.data, encoding="utf-8") as f:
            data = json.load(f)
        with open(a.rules, encoding="utf-8") as f:
            rules = json.load(f)
        v = Verifier(from_spec(r) for r in rules["rules"])
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    report = v.verify(data)
    print(json.dumps(report.to_dict(), indent=2) if a.json else report.summary())
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
