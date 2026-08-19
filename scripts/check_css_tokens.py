#!/usr/bin/env python3
"""Fail on Svelte components referencing CSS custom properties nothing defines.

An undefined `var(--x)` is not a build error. It is not a warning either --
vite and svelte compile it happily, and the browser resolves it to
"guaranteed-invalid", which makes the whole declaration behave as `unset`.
A background silently becomes transparent, a color silently becomes
inherited, and nothing anywhere reports a problem.

This is not hypothetical: `--color-destructive` and
`--color-destructive-foreground` were referenced 38 times across 15 files,
with no fallback, while being defined nowhere at all. Every delete, revoke
and remove button in the admin screens rendered with a transparent
background for as long as that lasted, and a green CI said nothing.

A reference with a fallback -- `var(--x, 8px)` -- is fine by definition and
is not reported.

Usage:
    python scripts/check_css_tokens.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
THEME_CSS = REPO_ROOT / "frontend" / "src" / "theme.css"
SVELTE_GLOB = "frontend/src/**/*.svelte"

# `--name:` anywhere -- inside :root, a .dark block, a scoped <style>, or a
# Svelte inline style="--name: {value}" attribute. All of them are definitions.
DECL_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")

# `var(--name` followed by `,` (has a fallback) or `)` (does not).
VAR_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*([,)])")


def declared_in(text: str) -> set[str]:
    return set(DECL_RE.findall(text))


def main() -> int:
    if not THEME_CSS.exists():
        print(f"error: {THEME_CSS} not found", file=sys.stderr)
        return 2

    theme_text = THEME_CSS.read_text(encoding="utf-8")
    global_tokens = declared_in(theme_text)

    files = sorted(REPO_ROOT.glob(SVELTE_GLOB))
    if not files:
        print("error: no .svelte files found", file=sys.stderr)
        return 2

    failures: list[tuple[Path, int, str]] = []

    # theme.css is checked against itself: a token defined as var(--other)
    # where --other does not exist fails the same way.
    for path in [THEME_CSS, *files]:
        text = path.read_text(encoding="utf-8")
        # A component may define its own custom properties (SignupCTA passes
        # sizing in through inline style, for instance). Those are legitimate,
        # so a file's own declarations count as defined for that file.
        known = global_tokens | declared_in(text)

        for lineno, line in enumerate(text.splitlines(), start=1):
            for name, terminator in VAR_RE.findall(line):
                if terminator == ",":
                    continue  # has a fallback, cannot resolve to unset
                if name not in known:
                    failures.append((path, lineno, name))

    if not failures:
        checked = len(files) + 1
        print(f"OK: {len(global_tokens)} tokens defined in theme.css; "
              f"no undefined references across {checked} files.")
        return 0

    print(f"Found {len(failures)} reference(s) to undefined CSS custom "
          f"properties.\n", file=sys.stderr)
    print("These compile without error but resolve to 'unset' at runtime, "
          "silently\nblanking whatever they style. Define them in "
          "frontend/src/theme.css, or give\nthe reference a fallback: "
          "var(--name, <value>).\n", file=sys.stderr)

    by_token: dict[str, list[tuple[Path, int]]] = {}
    for path, lineno, name in failures:
        by_token.setdefault(name, []).append((path, lineno))

    for name in sorted(by_token):
        sites = by_token[name]
        print(f"  {name}  ({len(sites)} reference(s))", file=sys.stderr)
        for path, lineno in sites[:10]:
            print(f"      {path.relative_to(REPO_ROOT).as_posix()}:{lineno}",
                  file=sys.stderr)
        if len(sites) > 10:
            print(f"      ... and {len(sites) - 10} more", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
