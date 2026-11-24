# SPDX-License-Identifier: AGPL-3.0-or-later
"""Staging stack: compose file, noindex header, demo seed."""

import re
from pathlib import Path

import pytest
from allauth.account.models import EmailAddress
from django.apps import apps
from django.core.management import call_command

from accounts.models import User

COMPOSE = Path(__file__).resolve().parents[2] / "docker-compose.staging.yml"


def _service(name: str) -> str:
    """Text of one top-level service block (stdlib only: no PyYAML)."""
    text = COMPOSE.read_text()
    match = re.search(rf"^  {name}:\n(.*?)(?=^  \w|^\w|\Z)", text, re.M | re.S)
    assert match, f"service {name} missing"
    return match.group(1)


# scenario: dev-process::staging-runs-production-servers
def test_backend_runs_gunicorn_with_debug_off_and_seed() -> None:
    backend = _service("backend")
    assert "gunicorn biohackit.wsgi:application --bind 0.0.0.0:8000" in backend
    assert "manage.py seed_demo" in backend
    assert "manage.py migrate" in backend
    assert "manage.py collectstatic --noinput" in backend
    assert 'DEBUG: "false"' in backend
    assert 'NOINDEX: "true"' in backend
    assert "runserver" not in backend


# scenario: dev-process::staging-runs-production-servers
def test_secret_key_is_required_without_default() -> None:
    backend = _service("backend")
    assert "SECRET_KEY: ${SECRET_KEY:?" in backend
    assert not re.search(r"SECRET_KEY:.*:-", backend)


# scenario: dev-process::staging-runs-production-servers
def test_frontend_is_production_build_with_noindex() -> None:
    frontend = _service("frontend")
    assert 'NOINDEX: "1"' in frontend
    assert "BACKEND_INTERNAL_URL" in frontend


# scenario: dev-process::staging-single-port
def test_only_frontend_publishes_18800() -> None:
    text = COMPOSE.read_text()
    assert re.findall(r"^\s+- \"(\d+:\d+)\"", text, re.M) == ["18800:3000"]
    assert '"18800:3000"' in _service("frontend")
    assert "ports:" not in _service("db")
    assert "ports:" not in _service("backend")


# scenario: dev-process::staging-not-indexed
def test_noindex_header_on_django_response(client, settings) -> None:
    settings.NOINDEX = True
    assert client.get("/api/").headers["X-Robots-Tag"] == "noindex"


# scenario: dev-process::staging-not-indexed
def test_noindex_header_on_append_slash_redirect(client, settings) -> None:
    settings.NOINDEX = True
    response = client.get("/admin")
    assert response.status_code == 301
    assert response.headers["X-Robots-Tag"] == "noindex"


# scenario: dev-process::staging-not-indexed
def test_noindex_header_on_disallowed_host(client, settings) -> None:
    settings.NOINDEX = True
    response = client.get("/api/", HTTP_HOST="evil.invalid")
    assert response.status_code == 400
    assert response.headers["X-Robots-Tag"] == "noindex"


# scenario: dev-process::staging-not-indexed
def test_noindex_header_on_whitenoise_static_file(client, settings, tmp_path) -> None:
    from whitenoise.middleware import WhiteNoiseMiddleware

    (tmp_path / "x.txt").write_text("x")
    settings.NOINDEX = True
    settings.STATIC_ROOT = tmp_path
    settings.WHITENOISE_AUTOREFRESH = True
    middleware = WhiteNoiseMiddleware(lambda request: None)
    middleware.add_files(str(tmp_path), prefix="/static/")
    # Build the real stack's first layer around a WhiteNoise instance.
    from django.test import RequestFactory

    from core.middleware import NoIndexMiddleware

    response = NoIndexMiddleware(middleware)(RequestFactory().get("/static/x.txt"))
    assert response.status_code == 200
    assert response.headers["X-Robots-Tag"] == "noindex"


# scenario: dev-process::staging-not-indexed
def test_noindex_is_first_middleware() -> None:
    from django.conf import settings as s

    assert s.MIDDLEWARE[0] == "core.middleware.NoIndexMiddleware"


# scenario: dev-process::staging-not-indexed
def test_no_noindex_header_by_default(client, settings) -> None:
    settings.NOINDEX = False
    assert "X-Robots-Tag" not in client.get("/api/").headers


# scenario: dev-process::staging-holds-only-demo-data
@pytest.mark.django_db
def test_seed_demo_is_idempotent_and_creates_only_one_user(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_USERNAME", "demo@example.com")
    monkeypatch.setenv("DEMO_PASSWORD", "correct-horse-battery-9")
    before = {
        m: m.objects.count() for m in apps.get_models() if m not in (User, EmailAddress)
    }
    call_command("seed_demo")
    call_command("seed_demo")
    assert User.objects.count() == 1
    assert User.objects.get().check_password("correct-horse-battery-9")
    after = {
        m: m.objects.count() for m in apps.get_models() if m not in (User, EmailAddress)
    }
    assert after == before


# scenario: dev-process::staging-holds-only-demo-data
@pytest.mark.django_db
def test_seed_demo_skips_when_unset(monkeypatch) -> None:
    monkeypatch.delenv("DEMO_USERNAME", raising=False)
    monkeypatch.delenv("DEMO_PASSWORD", raising=False)
    call_command("seed_demo")
    assert User.objects.count() == 0


# scenario: dev-process::staging-holds-only-demo-data
@pytest.mark.django_db
def test_seed_demo_user_has_verified_email_and_can_log_in(monkeypatch, client) -> None:
    monkeypatch.setenv("DEMO_USERNAME", "demo@example.com")
    monkeypatch.setenv("DEMO_PASSWORD", "correct-horse-battery-9")
    call_command("seed_demo")
    call_command("seed_demo")
    address = EmailAddress.objects.get()
    assert address.verified
    assert address.primary
    assert client.login(email="demo@example.com", password="correct-horse-battery-9")


# scenario: dev-process::staging-runs-production-servers
def test_staging_backend_uses_console_email_backend() -> None:
    backend = _service("backend")
    assert "EMAIL_BACKEND: django.core.mail.backends.console.EmailBackend" in backend
