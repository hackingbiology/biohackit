"""User guide: committed JSON in sync, cited files and requirements exist."""

import importlib.util
import re
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "user-guide.md"
SCRIPT = REPO / "tools" / "docs" / "export_user_guide.py"
OUTPUT = REPO / "frontend" / "src" / "content" / "user-guide.json"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_user_guide", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = _load()
DATA = exporter.parse(SOURCE.read_text(encoding="utf-8"))


def _requirement_exists(citation: str) -> bool:
    """True when `<capability>/<Requirement title>` is in specs or an open change."""
    capability, _, title = citation.partition("/")
    if not capability or not title:
        return False
    heading = f"### Requirement: {title}\n"
    specs = [REPO / "openspec" / "specs" / capability / "spec.md"]
    changes = (REPO / "openspec" / "changes").glob(f"*/specs/{capability}/spec.md")
    specs += [p for p in changes if "archive" not in p.parts]
    return any(p.is_file() and heading in p.read_text(encoding="utf-8") for p in specs)


def _missing_rows(data: dict[str, Any]) -> list[str]:
    missing = [r["step"] for r in data["steps"] if not (REPO / r["route"]).is_file()]
    missing += [
        r["method"] for r in data["signin"] if not (REPO / r["source"]).exists()
    ]
    missing += [
        r["feature"] for r in data["later"] if not _requirement_exists(r["requirement"])
    ]
    return missing


# scenario: dev-process::user-guide-page-in-sync
def test_committed_json_matches_exporter_output() -> None:
    assert OUTPUT.read_text(encoding="utf-8") == exporter.render(DATA)


# scenario: dev-process::user-guide-page-in-sync
def test_check_flag_reports_stale_output(tmp_path: Path) -> None:
    stale = tmp_path / "out.json"
    stale.write_text("{}\n", encoding="utf-8")
    assert exporter.main(["--check"], SOURCE, stale) == 1
    assert exporter.main([], SOURCE, stale) == 0
    assert exporter.main(["--check"], SOURCE, stale) == 0
    stale.write_text(stale.read_text(encoding="utf-8").replace("Email", "Mail"))
    assert exporter.main(["--check"], SOURCE, stale) == 1


# scenario: dev-process::user-guide-steps-exist
def test_every_step_route_and_requirement_exists() -> None:
    assert len(DATA["steps"]) >= 5
    assert DATA["later"]
    assert _missing_rows(DATA) == []


# scenario: dev-process::user-guide-steps-exist
def test_bad_route_and_bad_requirement_are_named() -> None:
    bad = {
        "steps": [
            {
                "step": "Ghost step",
                "action": "x",
                "route": "frontend/src/app/ghost/page.tsx",
            }
        ],
        "signin": [],
        "later": [
            {
                "feature": "Ghost feature",
                "requirement": "accounts-and-profiles/No such requirement",
            },
            {
                "feature": "Ghost capability",
                "requirement": "no-such-capability/Anything",
            },
        ],
    }
    assert _missing_rows(bad) == ["Ghost step", "Ghost feature", "Ghost capability"]


# scenario: dev-process::user-guide-steps-exist
def test_sign_in_methods_match_what_the_code_enables() -> None:
    form = (REPO / "frontend/src/components/SignInForm.tsx").read_text(encoding="utf-8")
    settings = (REPO / "backend/biohackit/settings.py").read_text(encoding="utf-8")
    methods = " ".join(r["method"] for r in DATA["signin"]).lower()
    assert (
        "requestLoginCode" in form
        and "ACCOUNT_LOGIN_BY_CODE_ENABLED = True" in settings
    )
    assert "loginWithPasskey" in form and "MFA_PASSKEY_LOGIN_ENABLED = True" in settings
    assert 'p.id === "discourse_connect"' in form and "rapamycin.news" in methods
    for name in ("google", "microsoft", "apple", "facebook", "wechat", "github"):
        assert name not in methods


# scenario: dev-process::user-guide-steps-exist
def test_guide_has_no_numbers_urls_or_citations() -> None:
    text = SOURCE.read_text(encoding="utf-8").split("\n", 2)[2]
    prose = "\n".join(line for line in text.splitlines() if line.startswith("|"))
    assert not re.search(r"https?://|www\.", prose)
    assert not re.search(r"\d", prose)


# scenario: dev-process::user-guide-steps-exist
def test_malformed_table_row_is_rejected() -> None:
    text = "# T\n\n## Coming later\n\n| feature | requirement |\n|---|---|\n| a |\n"
    with pytest.raises(ValueError, match="line 7"):
        exporter.parse(text)


# scenario: dev-process::user-guide-steps-exist
def test_guide_does_not_promise_unbuilt_privacy_or_passkey_setup() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "make a single measurement" not in text
    assert "Use a passkey" in text
    assert "accounts-and-profiles/Public-by-default profile" in text


# scenario: dev-process::user-guide-steps-exist
@pytest.mark.django_db
def test_email_code_for_unknown_address_creates_no_account() -> None:
    from django.test import Client

    from accounts.models import User

    response = Client().post(
        "/_allauth/browser/v1/auth/code/request",
        {"email": "new-person@example.com"},
        content_type="application/json",
    )
    assert response.status_code == 401
    assert not User.objects.filter(email="new-person@example.com").exists()
    text = SOURCE.read_text(encoding="utf-8")
    assert "An email code does not create a new account." in text


# scenario: dev-process::user-guide-steps-exist
def test_provider_rows_match_installed_provider_apps() -> None:
    from django.conf import settings

    providers = [a for a in settings.INSTALLED_APPS if ".providers." in a]
    assert providers == ["accounts.providers.discourse_connect"]
    sources = [r["source"] for r in DATA["signin"]]
    assert "backend/accounts/providers/discourse_connect" in sources
    assert "backend/biohackit/settings.py" not in sources


# scenario: dev-process::user-guide-steps-exist
def test_passkey_row_states_browser_support_and_existing_passkey() -> None:
    form = (REPO / "frontend/src/components/SignInForm.tsx").read_text(encoding="utf-8")
    assert "setPasskeys(passkeysSupported())" in form
    row = next(r for r in DATA["signin"] if r["method"] == "Passkey")
    assert "supports passkeys" in row["availability"]
    assert "works only with a passkey you already have" in row["availability"]
