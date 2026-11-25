#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Export docs/CHANGELOG.md to frontend/src/content/changelog.json.

Each `## YYYY-MM-DD` section holds a table `| change | commit | what changed |`.
Cells are copied verbatim; nothing is inferred from git. Use ``--check`` to
exit 1 when the committed JSON differs from the docs.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "CHANGELOG.md"
OUTPUT = REPO / "frontend" / "src" / "content" / "changelog.json"
COLUMNS = ("change", "commit", "summary")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
COMMIT = re.compile(r"[0-9a-f]{7}")
CHANGE_ID = re.compile(r"[a-z0-9][a-z0-9-]*")
SEPARATOR = re.compile(r":?-+:?")
HEADER = ("change", "commit", "what changed")


def _iso_date(heading: str, number: int) -> str:
    try:
        if not ISO_DATE.fullmatch(heading):
            raise ValueError(heading)
        date.fromisoformat(heading)
    except ValueError:
        raise ValueError(
            f"line {number}: heading {heading!r} is not an ISO YYYY-MM-DD date"
        ) from None
    return heading


def _row(line: str, number: int) -> dict[str, str] | None:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) != len(COLUMNS):
        raise ValueError(f"line {number}: expected 3 cells, got {len(cells)}")
    if tuple(cells) == HEADER or all(SEPARATOR.fullmatch(c) for c in cells):
        return None
    if not CHANGE_ID.fullmatch(cells[0]) or cells[0] == "archive":
        raise ValueError(f"line {number}: change {cells[0]!r} is not a change id")
    if not COMMIT.fullmatch(cells[1]):
        raise ValueError(f"line {number}: commit {cells[1]!r} is not a 7-char hash")
    if not cells[2]:
        raise ValueError(f"line {number}: empty summary")
    return dict(zip(COLUMNS, cells, strict=True))


def parse(text: str) -> dict[str, Any]:
    """Return the title and the dated sections, in file order."""
    title = ""
    days: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            days.append({"date": _iso_date(line[3:].strip(), number), "entries": []})
        elif days and line.startswith("|"):
            row = _row(line, number)
            if row:
                days[-1]["entries"].append(row)
    return {"title": title, "days": days}


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str], source: Path = SOURCE, output: Path = OUTPUT) -> int:
    expected = render(parse(source.read_text(encoding="utf-8")))
    if "--check" in argv:
        current = output.read_text(encoding="utf-8") if output.exists() else None
        if current != expected:
            print(
                f"{output} is out of date: run python3 tools/docs/export_changelog.py"
            )
            return 1
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
