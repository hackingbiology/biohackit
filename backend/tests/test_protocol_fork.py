# SPDX-License-Identifier: AGPL-3.0-or-later
"""Fork a published protocol (M03 TG-f part 2a) and the public throttle proxy fix. Synthetic data."""

from datetime import date
from typing import Any

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from accounts.models import User
from protocols.models import ChangeEvent, Protocol, ProtocolVersion, Publication
from substances.models import Product

URL = "/api/protocols/"
PUBLIC = "/api/public/protocols/"


def _user(email: str) -> APIClient:
    c = APIClient()
    c.force_authenticate(
        User.objects.create_user(email=email, password="correct-horse-9")
    )
    return c


@pytest.fixture
def owner(db):
    return _user("o@example.com")


@pytest.fixture
def other(db):
    return _user("x@example.com")


def _product() -> Product:
    return Product.objects.create(
        owner=User.objects.get(email="o@example.com"),
        name="Synth product",
        label_source="synthetic label",
        label_fetched_on=date(2026, 1, 1),
    )


def _published(owner: APIClient, product_id: int | None = None) -> int:
    first: dict[str, Any] = {
        "name": "Synth A",
        "amount": "1",
        "unit": "mg",
        "provenance": "animal-derived",
        "provenance_source": "synthetic source",
        "route": "oral",
        "formulation": "capsule",
    }
    if product_id is not None:
        first.update(product_id=product_id, units_per_day="2")
    body = {
        "title": "Synth protocol",
        "level": "research",
        "interventions": [
            first,
            {"name": "Synth B", "genomic": True},
            {"name": "Synth C"},
        ],
        "measures": [
            {"loinc_code": "11111-1", "purpose": "efficacy"},
            {"loinc_code": "33333-3", "purpose": "safety"},
            {"loinc_code": "22222-2", "purpose": "baseline", "genomic": True},
        ],
    }
    pid = owner.post(URL, body, format="json").json()["id"]
    r = owner.patch(
        f"{URL}{pid}/",
        {"state": "active", "reason": "go", "acknowledge": True},
        format="json",
    )
    assert r.status_code == 200, r.content
    r = owner.post(
        f"{URL}{pid}/publish/",
        {"reason": "share", "withheld_items": ["interventions[2]", "measures[1]"]},
        format="json",
    )
    assert r.status_code == 200, r.content
    return int(pid)


# scenario: protocols::forking-preserves-lineage-and-safety
def test_fork_records_source_and_version_and_carries_level_and_tags(owner, other):
    pid = _published(owner)
    r = other.post(f"{URL}{pid}/fork/", format="json")
    assert r.status_code == 201, r.content
    body = r.json()
    assert body["state"] == "draft" and body["origin"] == "community"
    assert body["forked_from"] == {
        "protocol": pid,
        "version": 1,
        "version_id": ProtocolVersion.objects.get(protocol_id=pid, number=1).pk,
    }
    assert body["level"] == "research"
    [item] = body["interventions"]
    assert item["name"] == "Synth A"
    for key in ("provenance", "provenance_source", "route", "formulation", "amount"):
        assert (
            item[key]
            == {
                "provenance": "animal-derived",
                "provenance_source": "synthetic source",
                "route": "oral",
                "formulation": "capsule",
                "amount": "1",
            }[key]
        )
    copy = Protocol.objects.get(pk=body["id"])
    assert copy.forked_from_protocol_id == pid
    assert copy.forked_from_version.number == 1
    assert copy.owner.email == "x@example.com"


# scenario: protocols::fork-then-diverge
def test_editing_the_fork_changes_only_the_fork(owner, other):
    pid = _published(owner)
    fid = other.post(f"{URL}{pid}/fork/", format="json").json()["id"]

    def source_state() -> tuple[Any, ...]:
        return (
            list(ProtocolVersion.objects.filter(protocol_id=pid).values()),
            list(Publication.objects.values("protocol_id", "version_id", "withheld")),
            list(ChangeEvent.objects.filter(version__protocol_id=pid).values()),
            Protocol.objects.filter(pk=pid).values().get(),
        )

    before = source_state()
    r = other.patch(
        f"{URL}{fid}/",
        {"state": "active", "reason": "start", "acknowledge": True},
        format="json",
    )
    assert r.status_code == 200, r.content
    r = other.patch(
        f"{URL}{fid}/", {"title": "My copy", "reason": "rename"}, format="json"
    )
    assert r.status_code == 200, r.content
    assert [v.number for v in ProtocolVersion.objects.filter(protocol_id=fid)] == [1, 2]
    assert source_state() == before
    assert r.json()["forked_from"]["version"] == 1


def test_newer_source_version_does_not_change_the_fork(owner, other):
    pid = _published(owner)
    fid = other.post(f"{URL}{pid}/fork/", format="json").json()["id"]
    owner.patch(f"{URL}{pid}/", {"title": "v2", "reason": "r"}, format="json")
    owner.post(
        f"{URL}{pid}/publish/", {"reason": "again", "withheld_items": []}, format="json"
    )
    assert Publication.objects.get(protocol_id=pid).version.number == 2
    assert Protocol.objects.get(pk=fid).forked_from_version.number == 1
    assert other.get(f"{URL}{fid}/").json()["forked_from"]["version"] == 1


# scenario: protocols::only-a-published-protocol-can-be-forked
def test_only_an_active_publication_can_be_forked(owner, other):
    draft = owner.post(URL, {"title": "D"}, format="json").json()["id"]
    assert other.post(f"{URL}{draft}/fork/").status_code == 404
    pid = _published(owner)
    owner.post(f"{URL}{pid}/unpublish/", {"reason": "stop"}, format="json")
    assert other.post(f"{URL}{pid}/fork/").status_code == 404
    assert other.post(f"{URL}999999/fork/").status_code == 404
    assert APIClient().post(f"{URL}{pid}/fork/").status_code == 401
    assert Protocol.objects.count() == 2


# scenario: protocols::fork-copies-only-public-items
def test_withheld_and_genomic_items_are_not_copied(owner, other):
    pid = _published(owner)
    body = other.post(f"{URL}{pid}/fork/", format="json").json()
    assert [i["name"] for i in body["interventions"]] == ["Synth A"]
    assert [m["loinc_code"] for m in body["measures"]] == ["11111-1"]
    text = str(body)
    assert "Synth B" not in text and "Synth C" not in text
    assert "33333-3" not in text and "22222-2" not in text


def test_product_kept_only_if_it_is_the_forking_users_own(owner, other):
    pid = _published(owner, _product().pk)
    body = other.post(f"{URL}{pid}/fork/", format="json").json()
    assert body["interventions"][0]["product_id"] is None
    assert body["interventions"][0]["units_per_day"] == ""
    own = owner.post(f"{URL}{pid}/fork/", format="json").json()
    assert own["interventions"][0]["product_id"] is not None
    assert own["forked_from"]["protocol"] == pid


def test_public_view_shows_lineage_only_while_source_is_published(owner, other):
    pid = _published(owner)
    fid = other.post(f"{URL}{pid}/fork/", format="json").json()["id"]
    other.patch(
        f"{URL}{fid}/",
        {"state": "active", "reason": "s", "acknowledge": True},
        format="json",
    )
    other.post(f"{URL}{fid}/publish/", {"reason": "share"}, format="json")
    anon = APIClient()
    assert anon.get(f"{PUBLIC}{fid}/").json()["forked_from"] == {
        "protocol": pid,
        "version": 1,
    }
    owner.post(f"{URL}{pid}/unpublish/", {"reason": "stop"}, format="json")
    assert anon.get(f"{PUBLIC}{fid}/").json()["forked_from"] is None


@pytest.mark.django_db(transaction=True)
def test_erasing_the_source_owner_keeps_the_fork():
    # Q57: erasure must not be blocked by a fork of the user's published protocol.
    owner, other = _user("a@example.com"), _user("b@example.com")
    pid = _published(owner)
    fid = other.post(f"{URL}{pid}/fork/", format="json").json()["id"]
    r = owner.post(
        "/api/auth/me/erase/",
        {"choice": "delete_everything", "confirm": True},
        format="json",
    )
    assert r.status_code == 200, r.content
    copy = Protocol.objects.get(pk=fid)
    assert copy.forked_from_protocol is None and copy.forked_from_version is None


def test_x_forwarded_for_cannot_dodge_the_public_throttle(db, monkeypatch, settings):
    # DRF reads NUM_PROXIES from settings at call time; the default is 0 (no proxy).
    assert settings.REST_FRAMEWORK["NUM_PROXIES"] == 0
    rates = {**ScopedRateThrottle.THROTTLE_RATES, "public_protocols": "2/min"}
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", rates)
    cache.clear()
    anon = APIClient()
    codes = [
        anon.get(PUBLIC, HTTP_X_FORWARDED_FOR=f"10.0.0.{i}").status_code
        for i in range(3)
    ]
    assert codes == [200, 200, 429]
    cache.clear()
