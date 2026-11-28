# SPDX-License-Identifier: AGPL-3.0-or-later
"""Intake event state (M04 TG-b). Synthetic values only."""

from datetime import date

import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from accounts.models import User
from core.cadence import Cadence
from protocols.intake import generate_intake_events, set_intake_state
from protocols.models import IntakeEvent, ProtocolVersion

START = date(2026, 1, 1)
END = date(2026, 1, 4)
CADENCE = Cadence(mode="daily", times_per_day=2)


@pytest.fixture
def owner(db) -> User:
    return User.objects.create_user(email="o@example.com", password="correct-horse-9")


@pytest.fixture
def version(owner) -> ProtocolVersion:
    client = APIClient()
    client.force_authenticate(owner)
    body = {"title": "Synthetic", "level": "medical", "interventions": [{"name": "x"}]}
    pid = client.post("/api/protocols/", body, format="json").json()["id"]
    r = client.patch(
        f"/api/protocols/{pid}/", {"state": "active", "reason": "go"}, format="json"
    )
    assert r.status_code == 200, r.content
    return ProtocolVersion.objects.get(protocol_id=pid, number=1)


def _generate(version):
    return generate_intake_events(version, "0", CADENCE, START, START, END)


def test_pending_event_has_no_state(version) -> None:
    # scenario: daily-log-and-adherence::a-pending-event-has-no-state
    events = _generate(version)
    assert len(events) == 8
    for e in IntakeEvent.objects.all():
        assert (e.state, e.state_set_by, e.state_set_at) == (None, None, None)
    counted = IntakeEvent.objects.filter(state__in=["done", "skipped", "missed"])
    assert counted.count() == 0


def test_regenerate_keeps_state_and_adds_no_duplicate(version, owner) -> None:
    first = _generate(version)[0]
    set_intake_state(first, owner, "skipped")
    _generate(version)
    assert IntakeEvent.objects.count() == 8
    first.refresh_from_db()
    assert first.state == "skipped"
    assert first.state_set_by == owner


def test_set_state_records_actor_time_amount(version, owner) -> None:
    event = _generate(version)[0]
    set_intake_state(event, owner, "partial", "0.5", "mg")
    event.refresh_from_db()
    assert event.state == "partial" and event.state_set_by == owner
    assert event.state_set_at is not None
    assert str(event.entered_amount) == "0.5000000000" and event.entered_unit == "mg"


def test_set_state_refusals(version, owner) -> None:
    event = _generate(version)[0]
    other = User.objects.create_user(email="p@example.com", password="correct-horse-9")
    with pytest.raises(PermissionError):
        set_intake_state(event, other, "done")
    with pytest.raises(ValueError, match="state must be one of"):
        set_intake_state(event, owner, "taken")
    with pytest.raises(ValueError, match="UCUM unit"):
        set_intake_state(event, owner, "done", "1", "")
    with pytest.raises(ValueError, match="needs an amount"):
        set_intake_state(event, owner, "done", None, "mg")
    with pytest.raises(ValueError, match="done or partial"):
        set_intake_state(event, owner, "skipped", "1", "mg")
    for bad in ("١٢", "1e3", "-1", "1,5", "", "x"):
        with pytest.raises(ValueError, match="amount"):
            set_intake_state(event, owner, "done", bad, "mg")
    with pytest.raises(ValueError, match="amount"):
        set_intake_state(event, owner, "done", 1.5, "mg")  # type: ignore[arg-type]
    event.refresh_from_db()
    assert event.state is None


def test_amount_must_fit_the_column_exactly(version, owner) -> None:
    event = _generate(version)[0]
    for too_precise in ("0.00000000001", "1" * 21):
        with pytest.raises(ValueError, match="amount"):
            set_intake_state(event, owner, "done", too_precise, "mg")
    set_intake_state(event, owner, "done", "1" * 19 + "." + "1" * 10, "mg")
    event.refresh_from_db()
    assert str(event.entered_amount) == "1" * 19 + "." + "1" * 10


def test_unknown_intervention_key_refused(version) -> None:
    for key in ("5", "-1", "a", "00", "01"):
        with pytest.raises(ValueError):
            generate_intake_events(version, key, CADENCE, START, START, END)


def test_db_refuses_state_without_actor(version) -> None:
    event = _generate(version)[0]
    with pytest.raises(IntegrityError), transaction.atomic():
        IntakeEvent.objects.filter(pk=event.pk).update(state="done")


def test_db_refuses_amount_without_unit(version) -> None:
    event = _generate(version)[0]
    with pytest.raises(IntegrityError), transaction.atomic():
        IntakeEvent.objects.filter(pk=event.pk).update(entered_amount=1)


def test_account_erasure_deletes_intake_events(version, owner) -> None:
    set_intake_state(_generate(version)[0], owner, "done")
    client = APIClient()
    client.force_authenticate(owner)
    body = {"choice": "delete_everything", "confirm": True}
    r = client.post("/api/auth/me/erase/", body, format="json")
    assert r.status_code == 200, r.content
    assert IntakeEvent.objects.count() == 0
