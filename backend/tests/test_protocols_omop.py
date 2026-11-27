# SPDX-License-Identifier: AGPL-3.0-or-later
"""Protocol intervention -> OMOP DRUG_EXPOSURE mapping (M03 TG-j part 1). Synthetic values only."""

import re
from pathlib import Path

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from protocols.models import ProtocolVersion
from protocols.omop import DRUG_EXPOSURE_COLUMNS, intervention_to_omop_drug_exposure

DOC = Path(__file__).resolve().parents[2] / "docs" / "omop" / "drug-exposure-mapping.md"
URL = "/api/protocols/"
NAME = "Rapamicina sintetica à ß"
UNIT = "µg"


@pytest.fixture
def version(db) -> ProtocolVersion:
    user = User.objects.create_user(email="a@example.com", password="correct-horse-9")
    client = APIClient()
    client.force_authenticate(user)
    body = {
        "title": "Synthetic protocol",
        "level": "research",
        "interventions": [
            {"name": NAME, "amount": "0.5", "unit": UNIT, "schedule": "weekly"},
            {"name": "plain-name"},
        ],
    }
    pid = client.post(URL, body, format="json").json()["id"]
    r = client.patch(
        f"{URL}{pid}/", {"state": "active", "reason": "start"}, format="json"
    )
    assert r.status_code == 200, r.content
    return ProtocolVersion.objects.get(protocol_id=pid, number=1)


def test_exported_intervention_has_no_invented_concept_id(version):
    # scenario: protocols::an-exported-intervention-has-no-invented-concept-id
    row = intervention_to_omop_drug_exposure(version, 0)
    concept_keys = [k for k in row if k.endswith("_concept_id")]
    assert (
        "drug_concept_id" in concept_keys and "drug_source_concept_id" in concept_keys
    )
    assert all(row[k] is None for k in concept_keys)
    assert row["drug_source_value"].encode() == NAME.encode()
    assert row["dose_unit_source_value"].encode() == UNIT.encode()


def test_amount_and_schedule_go_to_no_column(version):
    row = intervention_to_omop_drug_exposure(version, 0)
    assert row["quantity"] is None and row["sig"] is None and row["days_supply"] is None
    assert "0.5" not in map(str, row.values()) and "weekly" not in row.values()


def test_missing_unit_is_empty_and_start_date_comes_from_stored_date(version):
    row = intervention_to_omop_drug_exposure(version, 1)
    assert row["dose_unit_source_value"] is None
    assert row["drug_exposure_start_date"] == version.created_at.date()
    assert row["drug_exposure_end_date"] is None and row["person_id"] is None


def test_keys_are_exactly_the_documented_columns(version):
    text = DOC.read_text(encoding="utf-8")
    table = text.split("## Columns (DDL order)")[1]
    documented = re.findall(r"^\| `([a-z_]+)` \|", table, re.M)
    row = intervention_to_omop_drug_exposure(version, 0)
    assert list(row) == documented == list(DRUG_EXPOSURE_COLUMNS)


def test_document_cites_ddl_commit_path_and_fetch_date():
    text = DOC.read_text(encoding="utf-8")
    assert "dd85c0d30bb3dd4bd16c5dbef7dbf9dd93075fa2" in text
    assert "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql" in text
    assert re.search(r"Fetched 20\d\d-\d\d-\d\d", text)


def test_later_version_start_date_is_not_the_protocol_date(version):
    # an intervention added in v2 starts at v2; an unchanged one keeps the v1 start
    from datetime import date

    from protocols.models import Protocol

    protocol = Protocol.objects.get(pk=version.protocol_id)
    protocol.in_effect_since = date(2020, 1, 1)
    protocol.save(update_fields=["in_effect_since"])
    user = protocol.owner
    client = APIClient()
    client.force_authenticate(user)
    items = [*version.snapshot["interventions"], {"name": "added-later"}]
    r = client.patch(
        f"{URL}{protocol.pk}/",
        {"interventions": items, "reason": "add one"},
        format="json",
    )
    assert r.status_code == 200, r.content
    v2 = ProtocolVersion.objects.get(protocol=protocol, number=2)
    assert intervention_to_omop_drug_exposure(v2, 0)["drug_exposure_start_date"] == (
        date(2020, 1, 1)
    )
    added = intervention_to_omop_drug_exposure(v2, 2)
    assert added["drug_exposure_start_date"] == v2.created_at.date()


def test_future_in_effect_since_is_not_exported_as_start_date(version):
    from datetime import timedelta

    from protocols.models import Protocol

    protocol = Protocol.objects.get(pk=version.protocol_id)
    protocol.in_effect_since = version.created_at.date() + timedelta(days=30)
    protocol.save(update_fields=["in_effect_since"])
    row = intervention_to_omop_drug_exposure(version, 0)
    assert row["drug_exposure_start_date"] == version.created_at.date()
