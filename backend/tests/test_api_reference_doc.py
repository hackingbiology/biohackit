"""API reference: every /api/ route documented, every documented path resolves, JSON in sync."""

import importlib.util
from pathlib import Path
from types import ModuleType

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "docs" / "export_api_reference.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_api_reference", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = _load()
DOCS = exporter.parse_all()
ROUTES = exporter.routes()


def _without(heading_part: str) -> list[dict]:
    """The docs with every section whose heading contains `heading_part` removed."""
    return [
        {
            **d,
            "sections": [s for s in d["sections"] if heading_part not in s["heading"]],
        }
        for d in DOCS
    ]


# scenario: dev-process::api-routes-documented
def test_every_api_route_is_documented_and_every_endpoint_resolves() -> None:
    assert len(ROUTES) >= 20
    assert exporter.problems(DOCS, ROUTES) == []


# scenario: dev-process::api-routes-documented
def test_all_url_files_routes_are_in_the_reference() -> None:
    paths = {e["path"] for e in exporter.build(DOCS)["endpoints"]}
    normalised = {exporter.normalise(p) for p in paths}
    assert normalised == set(ROUTES)
    assert "/api/auth/me/erase/" in paths


# scenario: dev-process::api-routes-documented
def test_removed_heading_is_named() -> None:
    issues = exporter.problems(_without("/api/auth/token/refresh/"), ROUTES)
    assert issues == ["route not documented: /api/auth/token/refresh/"]


# scenario: dev-process::api-routes-documented
def test_documented_path_that_does_not_resolve_is_named() -> None:
    fake = [
        {
            **DOCS[0],
            "sections": [
                *DOCS[0]["sections"],
                {
                    "anchor": "x",
                    "endpoints": [{"method": "GET", "path": "/api/ghost/<id>/"}],
                    "heading": "`GET /api/ghost/<id>/`",
                    "level": 2,
                    "body": "",
                },
            ],
        },
        *DOCS[1:],
    ]
    assert exporter.problems(fake, ROUTES) == [
        "documented path does not resolve: /api/ghost/<>/"
    ]


# scenario: dev-process::api-routes-documented
def test_method_missing_from_docs_is_named() -> None:
    issues = exporter.problems(DOCS, {**ROUTES, "/api/auth/me/": {"GET", "DELETE"}})
    assert len(issues) == 1 and issues[0].startswith("methods differ for /api/auth/me/")


# scenario: dev-process::api-routes-documented
def test_heading_forms_are_parsed() -> None:
    text = (
        "# T\n\n## `GET|POST /api/a/<int:pk>/?x=<y>`\n\nbody\n\n"
        "```\n## not a heading\n```\n\n### Note on `PATCH /api/b/`\n"
    )
    doc = exporter.parse_doc(text, "api-t")
    first, second = doc["sections"]
    assert [(e["method"], e["path"]) for e in first["endpoints"]] == [
        ("GET", "/api/a/<int:pk>/"),
        ("POST", "/api/a/<int:pk>/"),
    ]
    assert "## not a heading" in first["body"]
    assert second["level"] == 3 and second["endpoints"][0]["path"] == "/api/b/"


# scenario: dev-process::api-reference-page-in-sync
def test_committed_json_matches_exporter_output() -> None:
    expected = exporter.render(exporter.build(DOCS))
    assert exporter.OUTPUT.read_text(encoding="utf-8") == expected


# scenario: dev-process::api-reference-page-in-sync
def test_check_flag_reports_stale_output(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    out.write_text("{}\n", encoding="utf-8")
    assert exporter.main(["--check"], exporter.DOCS, out, ROUTES) == 1
    assert exporter.main([], exporter.DOCS, out, ROUTES) == 0
    assert exporter.main(["--check"], exporter.DOCS, out, ROUTES) == 0
    out.write_text(out.read_text(encoding="utf-8").replace("POST", "PUT"))
    assert exporter.main(["--check"], exporter.DOCS, out, ROUTES) == 1
