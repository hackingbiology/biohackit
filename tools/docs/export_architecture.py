#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Export docs/architecture.md to frontend/src/content/architecture.json.

Cells are copied verbatim from the Markdown tables; nothing is inferred.
Use ``--check`` to exit 1 when the committed JSON differs from the docs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "architecture.md"
OUTPUT = REPO / "frontend" / "src" / "content" / "architecture.json"
SECTIONS = {
    "Built components": ("built", ("component", "layer", "path", "purpose")),
    "Specified, not yet built": ("specified", ("component", "requirement")),
}


def parse(text: str) -> dict[str, Any]:
    """Return the title and the rows of each `## ` section's table."""
    title = ""
    tables: dict[str, list[dict[str, str]]] = {key: [] for key, _ in SECTIONS.values()}
    section: tuple[str, tuple[str, ...]] | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            section = SECTIONS.get(line[3:].strip())
        elif section and line.startswith("|"):
            key, columns = section
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) != len(columns):
                raise ValueError(
                    f"line {number}: expected {len(columns)} cells, got {len(cells)}"
                )
            if cells[0] == "component" or set(cells[0]) <= {"-"}:
                continue
            tables[key].append(dict(zip(columns, cells, strict=True)))
    return {"title": title, **tables}


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str], source: Path = SOURCE, output: Path = OUTPUT) -> int:
    expected = render(parse(source.read_text(encoding="utf-8")))
    if "--check" in argv:
        current = output.read_text(encoding="utf-8") if output.exists() else None
        if current != expected:
            print(f"{output} is out of date: run python3 tools/docs/export_architecture.py")
            return 1
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
