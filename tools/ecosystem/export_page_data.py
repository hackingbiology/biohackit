#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Export docs/ecosystem scans and the give-back register to frontend/src/content/ecosystem.json.

Field values are copied verbatim from the Markdown; nothing is inferred.
Use ``--check`` to exit 1 when the committed JSON differs from the docs.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs" / "ecosystem"
OUTPUT = REPO / "frontend" / "src" / "content" / "ecosystem.json"
SKIPPED = {"README.md", "GIVEBACK.md"}
_FIELD = re.compile(r"^- \*\*(?P<key>[^:*]+):\*\*\s*(?P<value>.*)$")
GIVEBACK_COLUMNS = ("date", "upstream", "contribution", "status", "link")


def parse_scan(text: str) -> dict[str, Any]:
    """Return the first `# ` title and every `### ` entry with its field lines."""
    title = ""
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("### "):
            current = {"name": line[4:].strip(), "fields": {}}
            entries.append(current)
        elif line.startswith("#"):
            current = None
        elif current is not None:
            match = _FIELD.match(line)
            if match:
                current["fields"][match["key"].strip()] = match["value"].strip()
    return {"title": title, "entries": entries}


def parse_giveback(text: str) -> list[dict[str, str]]:
    """Return one object per data row of the register table."""
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != len(GIVEBACK_COLUMNS):
            continue
        if cells[0] == "date" or set(cells[0]) <= {"-"}:
            continue
        rows.append(dict(zip(GIVEBACK_COLUMNS, cells, strict=True)))
    return rows


def build(docs: Path = DOCS) -> dict[str, Any]:
    scans = []
    for path in sorted(docs.glob("*.md")):
        if path.name in SKIPPED:
            continue
        scans.append(
            {"file": path.name, **parse_scan(path.read_text(encoding="utf-8"))}
        )
    giveback_path = docs / "GIVEBACK.md"
    giveback: list[dict[str, str]] = []
    if giveback_path.exists():
        giveback = parse_giveback(giveback_path.read_text(encoding="utf-8"))
    return {"giveback": giveback, "scans": scans}


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str], docs: Path = DOCS, output: Path = OUTPUT) -> int:
    expected = render(build(docs))
    if "--check" in argv:
        current = output.read_text(encoding="utf-8") if output.exists() else None
        if current != expected:
            print(
                f"{output} is out of date: run python3 tools/ecosystem/export_page_data.py"
            )
            return 1
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
