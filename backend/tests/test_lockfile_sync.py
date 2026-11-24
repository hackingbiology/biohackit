"""Static check that backend/pyproject.toml and backend/uv.lock agree."""

import re
import tomllib
from pathlib import Path
from typing import Any

BACKEND = Path(__file__).resolve().parent.parent
_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")


def _normalize(requirement: str) -> str:
    """PEP 503 name of a requirement string (extras/specifiers dropped)."""
    match = _NAME.match(requirement.strip())
    assert match, requirement
    return re.sub(r"[-_.]+", "-", match.group(0)).lower()


def _load(name: str) -> dict[str, Any]:
    with (BACKEND / name).open("rb") as handle:
        return tomllib.load(handle)


def _packages() -> dict[str, dict[str, Any]]:
    return {p["name"]: p for p in _load("uv.lock")["package"]}


# scenario: dev-process::lockfile-in-sync
def test_every_declared_dependency_is_locked_and_referenced() -> None:
    declared = [
        _normalize(r) for r in _load("pyproject.toml")["project"]["dependencies"]
    ]
    packages = _packages()
    referenced = {d["name"] for d in packages["biohackit"]["dependencies"]}
    for name in declared:
        assert name in packages, f"{name} missing from uv.lock"
        assert name in referenced, f"{name} not in biohackit dependencies in uv.lock"


# scenario: dev-process::lockfile-in-sync
def test_gunicorn_artifacts_have_sha256_hashes() -> None:
    gunicorn = _packages()["gunicorn"]
    artifacts = [gunicorn["sdist"], *gunicorn["wheels"]]
    assert len(artifacts) >= 2
    for artifact in artifacts:
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", artifact["hash"])
