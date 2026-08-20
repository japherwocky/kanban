#!/usr/bin/env python3
"""Turn an ESLint JSON report into GitHub Actions warning annotations.

Lint is advisory here: `npm run lint` already prints a readable report to the
job log, but log output is only found by someone who goes looking. Annotations
attach each finding to its line in the PR's Files view, which is where a
reviewer actually is.

Always exits 0. A lint finding must never fail the workflow, and neither may a
problem with this script -- an unreadable or missing report says so and moves
on, rather than turning an advisory step into a broken one.

Usage:
    python3 scripts/eslint_annotations.py <report.json> [path-prefix]

The prefix is prepended to each path so annotations resolve from the repo root
even though eslint runs inside frontend/ (pass "frontend/").
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    report_path = Path(sys.argv[1] if len(sys.argv) > 1 else "eslint-report.json")
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ESLint annotations: no usable report at {report_path} ({exc})")
        return 0

    cwd = Path.cwd()
    total = 0

    for entry in report:
        raw = Path(entry.get("filePath", ""))
        try:
            rel = raw.relative_to(cwd).as_posix()
        except ValueError:
            rel = raw.name
        rel = prefix + rel

        for msg in entry.get("messages", []):
            total += 1
            # Annotations are one line; collapse any wrapping in the message.
            text = " ".join(str(msg.get("message", "")).split())
            rule = msg.get("ruleId") or "eslint"
            line = msg.get("line", 1)
            print(f"::warning file={rel},line={line},title=ESLint {rule}::{text}")

    print(f"ESLint: {total} advisory finding(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
