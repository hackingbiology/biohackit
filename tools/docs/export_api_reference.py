# SPDX-License-Identifier: AGPL-3.0-or-later
"""Export docs/api-*.md to frontend/src/content/api-reference.json.

Every `##`/`###` heading of each doc becomes a section; a heading that holds a
`METHOD /api/path` code span (also `GET|POST`) documents those endpoints. The
documented endpoints are joined to the routes of the Django URL resolver under
`/api/`: a route without documentation, a documented endpoint that does not
resolve, or a method set that differs from the view's, is reported and makes the
script exit 1. Use ``--check`` to also exit 1 when the committed JSON differs.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"
OUTPUT = REPO / "frontend" / "src" / "content" / "api-reference.json"

HEADING = re.compile(r"^(#{1,3}) (.+?)\s*$")
ENDPOINT = re.compile(
    r"`((?:GET|POST|PUT|PATCH|DELETE)(?:\|(?:GET|POST|PUT|PATCH|DELETE))*)"
    r" (/api/[^`\s?]*)(?:\?[^`]*)?`"
)
PARAM = re.compile(r"<[^>]*>")


def normalise(path: str) -> str:
    """`/api/x/<int:pk>/` and `/api/x/<id>/` both become `/api/x/<>/`."""
    return PARAM.sub("<>", path)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_doc(text: str, stem: str) -> dict[str, Any]:
    """Return the title and the sections of one `docs/api-*.md` file."""
    title = ""
    sections: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line)
        if match is None:
            if sections:
                sections[-1]["lines"].append(line)
            continue
        level, heading = len(match.group(1)), match.group(2)
        if level == 1:
            title = title or heading
            continue
        endpoints = [
            {"method": m, "path": path}
            for methods, path in ENDPOINT.findall(heading)
            for m in methods.split("|")
        ]
        anchor = f"{stem}-{_slug(heading)}"
        seen[anchor] = seen.get(anchor, 0) + 1
        if seen[anchor] > 1:
            anchor = f"{anchor}-{seen[anchor]}"
        sections.append(
            {
                "anchor": anchor,
                "endpoints": endpoints,
                "heading": heading,
                "level": level,
                "lines": [],
            }
        )
    for section in sections:
        section["body"] = "\n".join(section.pop("lines")).strip()
    return {"file": f"docs/{stem}.md", "sections": sections, "title": title}


def parse_all(docs_dir: Path = DOCS) -> list[dict[str, Any]]:
    return [
        parse_doc(p.read_text(encoding="utf-8"), p.stem)
        for p in sorted(docs_dir.glob("api-*.md"))
    ]


def documented(docs: list[dict[str, Any]]) -> dict[str, set[str]]:
    """Normalised path -> documented methods, across all docs."""
    found: dict[str, set[str]] = {}
    for doc in docs:
        for section in doc["sections"]:
            for e in section["endpoints"]:
                found.setdefault(normalise(e["path"]), set()).add(e["method"])
    return found


def _view_methods(callback: Any) -> set[str]:
    view_class = getattr(callback, "view_class", None)
    if view_class is None:
        return set()
    return {
        m.upper()
        for m in view_class.http_method_names
        if m not in ("options", "head") and hasattr(view_class, m)
    }


def _walk(patterns: Any, prefix: str) -> dict[str, set[str]]:
    routes: dict[str, set[str]] = {}
    for p in patterns:
        route = prefix + str(p.pattern)
        if hasattr(p, "url_patterns"):
            for path, methods in _walk(p.url_patterns, route).items():
                routes.setdefault(path, set()).update(methods)
        else:
            routes.setdefault(normalise("/" + route), set()).update(
                _view_methods(p.callback)
            )
    return routes


def routes() -> dict[str, set[str]]:
    """Normalised `/api/` route -> methods the view implements."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biohackit.settings")
    sys.path.insert(0, str(REPO / "backend"))
    import django
    from django.urls import get_resolver

    django.setup()
    found = _walk(get_resolver().url_patterns, "")
    return {p: m for p, m in found.items() if p.startswith("/api/")}


def problems(
    docs: list[dict[str, Any]], found: dict[str, set[str]] | None = None
) -> list[str]:
    """Messages naming every undocumented route, unresolved endpoint or method gap."""
    real = routes() if found is None else found
    doc = documented(docs)
    out = [f"route not documented: {p}" for p in sorted(real) if p not in doc]
    out += [
        f"documented path does not resolve: {p}" for p in sorted(doc) if p not in real
    ]
    for path in sorted(real.keys() & doc.keys()):
        if real[path] != doc[path]:
            out.append(
                f"methods differ for {path}: code {sorted(real[path])},"
                f" documented {sorted(doc[path])}"
            )
    return out


def build(docs: list[dict[str, Any]]) -> dict[str, Any]:
    index = sorted(
        (
            {"anchor": s["anchor"], "method": e["method"], "path": e["path"]}
            for d in docs
            for s in d["sections"]
            for e in s["endpoints"]
        ),
        key=lambda r: (normalise(r["path"]), r["method"]),
    )
    return {"docs": docs, "endpoints": index}


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(
    argv: list[str],
    docs_dir: Path = DOCS,
    output: Path = OUTPUT,
    found: dict[str, set[str]] | None = None,
) -> int:
    docs = parse_all(docs_dir)
    issues = problems(docs, found)
    for issue in issues:
        print(issue)
    if issues:
        return 1
    expected = render(build(docs))
    if "--check" in argv:
        current = output.read_text(encoding="utf-8") if output.exists() else None
        if current != expected:
            print(
                f"{output} is out of date: run python3 tools/docs/export_api_reference.py"
            )
            return 1
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
