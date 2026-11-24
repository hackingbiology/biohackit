"""Unit tests for the dependency licence classifier (tools/licence/check_licences.py)."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "licence" / "check_licences.py"
_spec = importlib.util.spec_from_file_location("check_licences", SCRIPT)
assert _spec is not None and _spec.loader is not None
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)


@pytest.mark.parametrize(
    "raw",
    [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "LGPL-3.0-or-later",
        "AGPL-3.0-only",
        "MIT OR Apache-2.0",
        "ISC",
    ],
)
def test_allowed_licences(raw: str) -> None:
    assert gate.classify(raw) == "allowed"


@pytest.mark.parametrize("raw", ["SSPL-1.0", "Proprietary", "BUSL-1.1"])
def test_incompatible_licences(raw: str) -> None:
    assert gate.classify(raw) == "incompatible"


@pytest.mark.parametrize(
    "raw", ["", "   ", "Something Custom", "GPL-3.0-only", "MIT AND Something Custom"]
)
def test_unknown_licences(raw: str) -> None:
    assert gate.classify(raw) == "unknown"


def test_incompatible_dependency_is_rejected(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # scenario: ecosystem-reuse::incompatible-dependency-rejected
    pkgs = [
        gate.Package("backend", "good-pkg", "1.0", "MIT"),
        gate.Package("frontend", "evil-pkg", "2.3.4", "SSPL-1.0"),
        gate.Package("backend", "mystery-pkg", "0.1", ""),
    ]
    bad = gate.offenders(pkgs, {})
    assert [(p.name, v) for p, v in bad] == [
        ("evil-pkg", "incompatible"),
        ("mystery-pkg", "unknown"),
    ]


def test_main_exits_nonzero_and_names_package(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # scenario: ecosystem-reuse::incompatible-dependency-rejected
    monkeypatch.setattr(
        gate,
        "backend_packages",
        lambda: [gate.Package("backend", "evil-pkg", "9.9", "SSPL-1.0")],
    )
    monkeypatch.setattr(gate, "frontend_packages", lambda: [])
    monkeypatch.setattr(gate, "load_overrides", lambda: {})
    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "evil-pkg" in out and "9.9" in out and "SSPL-1.0" in out


@pytest.mark.parametrize(
    "raw",
    [
        "BSD",
        "BSD License",
        "BSD LICENSE",
        "Apache Software License",
        "OSI Approved :: BSD License",
        "OSI Approved :: Apache Software License",
    ],
)
def test_generic_licence_names_are_unknown(raw: str) -> None:
    assert gate.classify(raw) == "unknown"


def test_generic_bsd_package_needs_override() -> None:
    pkg = gate.Package("backend", "bsdish", "1.0", "BSD")
    assert gate.verdict(pkg, {}) == "unknown"
    assert gate.verdict(pkg, {("bsdish", "1.0"): "BSD-3-Clause"}) == "allowed"


def test_missing_site_packages_yields_no_packages(tmp_path: Path) -> None:
    assert gate.backend_packages(tmp_path / "no-venv") == []


def test_main_fails_closed_without_backend_packages(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(gate, "backend_packages", lambda: [])
    monkeypatch.setattr(gate, "frontend_packages", lambda: [])
    monkeypatch.setattr(gate, "load_overrides", lambda: {})
    assert gate.main() == 1
    assert "failing closed" in capsys.readouterr().out


def test_override_takes_precedence() -> None:
    pkg = gate.Package("backend", "odd-pkg", "1.0", "Apache-2.0 License")
    assert gate.verdict(pkg, {}) == "unknown"
    assert gate.verdict(pkg, {("odd-pkg", "1.0"): "Apache-2.0"}) == "allowed"
    assert gate.verdict(pkg, {("odd-pkg", "2.0"): "Apache-2.0"}) == "unknown"


def test_data_licence_only_through_override() -> None:
    pkg = gate.Package("frontend", "data-pkg", "1.0", "CC-BY-4.0")
    assert gate.verdict(pkg, {}) == "unknown"
    assert gate.verdict(pkg, {("data-pkg", "1.0"): "CC-BY-4.0"}) == "allowed"


def test_mit0_only_through_override() -> None:
    pkg = gate.Package("backend", "cffi", "2.1.1", "MIT-0")
    assert gate.verdict(pkg, {}) == "unknown"
    assert gate.verdict(pkg, {("cffi", "2.1.1"): "MIT-0"}) == "allowed"
    assert gate.verdict(pkg, {("cffi", "2.2.0"): "MIT-0"}) == "unknown"


def test_override_requires_source_url(tmp_path: Path) -> None:
    path = tmp_path / "o.toml"
    path.write_text('[[override]]\npackage = "x"\nversion = "1"\nlicence = "MIT"\n')
    with pytest.raises(ValueError, match="source_url"):
        gate.load_overrides(path)
