# SPDX-License-Identifier: AGPL-3.0-or-later
"""Posology provenance and the heightened activation acknowledgment (M03 TG-d). Synthetic data."""

from typing import Any

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from protocols.models import (
    ActivationAcknowledgment,
    ImmutableRecordError,
    Protocol,
    ProtocolVersion,
)
from protocols.omop import intervention_to_omop_drug_exposure

URL = "/api/protocols/"
SRC = "Synthetic study X, table 2"


def _w(**kw: Any) -> dict[str, Any]:
    base = {
        "name": "Synth A",
        "amount": "2",
        "unit": "mg/kg",
        "basis": "per_body_weight",
    }
    return {**base, **kw}


@pytest.fixture
def client(db):
    c = APIClient()
    c.force_authenticate(
        User.objects.create_user(email="p@example.com", password="correct-horse-9")
    )
    return c


def _create(client, interventions, level="medical", **extra):
    body = {"title": "T", "level": level, "interventions": interventions, **extra}
    r = client.post(URL, body, format="json")
    assert r.status_code == 201, r.content
    return r.json()


def _activate(client, pid, **extra):
    body = {"state": "active", "reason": "go", **extra}
    return client.patch(f"{URL}{pid}/", body, format="json")


# scenario: interventions-and-catalog::weight-relative-posology-without-provenance-is-not-accepted-as-a-dose
def test_per_weight_without_provenance_saves_in_draft_but_is_not_a_dose(client):
    p = _create(client, [_w()])
    assert any("per body weight" in m for m in p["missing"])
    assert p["interventions"][0]["absolute_dose"] is None
    r = _activate(client, p["id"])
    assert r.status_code == 400 and "interventions" in r.json()
    assert not ProtocolVersion.objects.exists()
    assert not ActivationAcknowledgment.objects.exists()
    assert Protocol.objects.get(pk=p["id"]).state == "draft"


def test_later_edit_with_untagged_per_weight_is_refused(client):
    p = _create(client, [{"name": "x"}])
    assert _activate(client, p["id"]).status_code == 200
    body = {"interventions": [_w()], "reason": "r"}
    r = client.patch(f"{URL}{p['id']}/", body, format="json")
    assert r.status_code == 400


@pytest.mark.parametrize(
    "extra",
    [
        {"provenance": "human-derived"},
        {"provenance": "rat", "provenance_source": SRC},
        {"basis": "per_kg"},
        {"provenance": "human-derived", "provenance_source": "s" * 501},
        {"provenance_source": SRC},
        {"provenance": "human-derived", "provenance_source": "a\x00b"},
    ],
)
def test_bad_posology_keys_are_a_400(client, extra):
    r = client.post(URL, {"title": "T", "interventions": [_w(**extra)]}, format="json")
    assert r.status_code == 400


# scenario: interventions-and-catalog::animal-derived-dose-is-marked
def test_provenance_tags_are_stored_with_source(client):
    items = [
        _w(provenance="human-derived", provenance_source=SRC),
        _w(name="B", provenance="animal-derived", provenance_source=SRC),
    ]
    p = _create(client, items)
    got = client.get(f"{URL}{p['id']}/").json()["interventions"]
    assert [i["provenance"] for i in got] == ["human-derived", "animal-derived"]
    assert all(i["provenance_source"] == SRC for i in got)


# scenario: interventions-and-catalog::animal-derived-per-weight-dose-is-not-converted-to-an-absolute-human-dose
def test_animal_derived_per_weight_is_shown_as_stored_and_exported_without_quantity(
    client,
):
    p = _create(client, [_w(provenance="animal-derived", provenance_source=SRC)])
    assert _activate(client, p["id"], acknowledge=True).status_code == 200
    item = client.get(f"{URL}{p['id']}/").json()["interventions"][0]
    assert (item["amount"], item["unit"]) == ("2", "mg/kg")
    assert item["provenance"] == "animal-derived" and item["provenance_source"] == SRC
    assert item["absolute_dose"] is None
    version = ProtocolVersion.objects.get(protocol_id=p["id"])
    row = intervention_to_omop_drug_exposure(version, 0)
    assert row["quantity"] is None
    assert row["dose_unit_source_value"] == "mg/kg"
    assert "2" not in {str(v) for v in row.values()}


def test_research_activation_needs_acknowledgment(client):
    p = _create(client, [{"name": "x"}], level="research")
    assert _activate(client, p["id"]).status_code == 400
    assert not ProtocolVersion.objects.filter(protocol_id=p["id"]).exists()
    assert _activate(client, p["id"], acknowledge="yes").status_code == 400
    assert _activate(client, p["id"], acknowledge=True).status_code == 200
    (ack,) = ActivationAcknowledgment.objects.filter(protocol_id=p["id"])
    assert ack.level == "research" and ack.statement and ack.version.number == 1
    assert ack.animal_derived_items == []
    with pytest.raises(ImmutableRecordError):
        ack.save()


def test_animal_derived_activation_needs_acknowledgment_naming_items(client):
    items = [_w(provenance="animal-derived", provenance_source=SRC)]
    p = _create(client, items)
    assert _activate(client, p["id"]).status_code == 400
    assert _activate(client, p["id"], acknowledge=True).status_code == 200
    (ack,) = ActivationAcknowledgment.objects.filter(protocol_id=p["id"])
    assert ack.level == "medical" and ack.animal_derived_items == ["Synth A"]


def test_medical_without_animal_needs_no_acknowledgment(client):
    p = _create(client, [_w(provenance="human-derived", provenance_source=SRC)])
    assert _activate(client, p["id"]).status_code == 200
    assert not ActivationAcknowledgment.objects.exists()


def test_import_running_path_is_gated(client):
    body = {
        "title": "T",
        "level": "research",
        "interventions": [{"name": "x"}],
        "already_running": True,
        "in_effect_since": "2026-01-01",
    }
    r = client.post(URL, body, format="json")
    assert r.status_code == 400 and not ProtocolVersion.objects.exists()
    r = client.post(URL, {**body, "acknowledge": True}, format="json")
    assert r.status_code == 201
    assert ActivationAcknowledgment.objects.count() == 1


def test_resume_from_paused_asks_again(client):
    p = _create(client, [{"name": "x"}], level="research")
    assert _activate(client, p["id"], acknowledge=True).status_code == 200
    pause = {"state": "paused", "reason": "pause"}
    client.patch(f"{URL}{p['id']}/", pause, format="json")
    assert _activate(client, p["id"]).status_code == 400
    assert _activate(client, p["id"], acknowledge=True).status_code == 200
    assert ActivationAcknowledgment.objects.count() == 2


def _patch(client, pid, **body):
    return client.patch(f"{URL}{pid}/", {"reason": "edit", **body}, format="json")


def test_active_edit_to_research_needs_acknowledgment(client):
    p = _create(client, [{"name": "x"}])
    assert _activate(client, p["id"]).status_code == 200
    assert _patch(client, p["id"], level="research").status_code == 400
    assert Protocol.objects.get(pk=p["id"]).level == "medical"
    assert not ActivationAcknowledgment.objects.exists()
    r = _patch(client, p["id"], level="research", acknowledge=True)
    assert r.status_code == 200
    (ack,) = ActivationAcknowledgment.objects.filter(protocol_id=p["id"])
    assert ack.level == "research" and ack.version.number == 2
    # an unrelated later edit asks for nothing more
    assert _patch(client, p["id"], title="T2").status_code == 200
    assert ActivationAcknowledgment.objects.count() == 1


def test_active_edit_adding_animal_item_needs_acknowledgment(client):
    p = _create(client, [{"name": "x"}])
    assert _activate(client, p["id"]).status_code == 200
    items = [{"name": "x"}, _w(provenance="animal-derived", provenance_source=SRC)]
    assert _patch(client, p["id"], interventions=items).status_code == 400
    assert not ActivationAcknowledgment.objects.exists()
    r = _patch(client, p["id"], interventions=items, acknowledge=True)
    assert r.status_code == 200
    (ack,) = ActivationAcknowledgment.objects.filter(protocol_id=p["id"])
    assert ack.animal_derived_items == ["Synth A"]


def test_old_facets_without_new_keys_read_and_diff(client):
    p = _create(client, [{"name": "x", "amount": "1", "unit": "mg"}])
    stored = Protocol.objects.get(pk=p["id"]).interventions
    assert stored == [{"name": "x", "amount": "1", "unit": "mg", "schedule": ""}]
    item = client.get(f"{URL}{p['id']}/").json()["interventions"][0]
    assert item["basis"] == "absolute" and item["provenance"] == ""
    assert "absolute_dose" not in item
    assert _activate(client, p["id"]).status_code == 200
    body = {
        "interventions": [{"name": "x", "amount": "2", "unit": "mg"}],
        "reason": "up",
    }
    assert client.patch(f"{URL}{p['id']}/", body, format="json").status_code == 200
    d = client.get(f"{URL}{p['id']}/diff/?from=1&to=2").json()
    assert d["changes"] == [{"field": "doses[0].amount", "old": "1", "new": "2"}]
