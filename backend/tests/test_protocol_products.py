# SPDX-License-Identifier: AGPL-3.0-or-later
"""Route, formulation, products and label-contents totals (M03 TG-e). Synthetic data."""

from decimal import Decimal
from typing import Any

import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from accounts.models import User
from protocols.models import ProtocolVersion
from protocols.omop import intervention_to_omop_drug_exposure
from substances.models import Product, ProductIngredient, Substance

URL = "/api/protocols/"
PRODUCTS = "/api/substances/products/"
LABEL = "Synthetic label A, page 2"


def _user(email: str) -> APIClient:
    c = APIClient()
    c.force_authenticate(
        User.objects.create_user(email=email, password="correct-horse-9")
    )
    return c


@pytest.fixture
def client(db):
    return _user("p@example.com")


def _product(client, name="Prod", **kw) -> int:
    body = {"name": name, "label_source": LABEL, "label_fetched_on": "2026-01-02", **kw}
    r = client.post(PRODUCTS, body, format="json")
    assert r.status_code == 201, r.content
    return r.json()["id"]


def _ingredient(client, pid, sid, amount="1", unit="mg", **kw):
    body = {
        "substance": sid,
        "amount_per_unit": amount,
        "unit": unit,
        "label_source": LABEL,
        **kw,
    }
    return client.post(f"{PRODUCTS}{pid}/ingredients/", body, format="json")


def _protocol(client, interventions) -> dict[str, Any]:
    r = client.post(
        URL,
        {"title": "T", "level": "medical", "interventions": interventions},
        format="json",
    )
    assert r.status_code == 201, r.content
    return r.json()


def _totals(client, pid) -> dict[str, Any]:
    r = client.get(f"{URL}{pid}/ingredient-totals/")
    assert r.status_code == 200, r.content
    return r.json()


@pytest.fixture
def substance(db) -> Substance:
    return Substance.objects.create(name="Synthetic X")


# scenario: interventions-and-catalog::topical-item-is-distinguished-from-oral
def test_topical_item_is_recorded_apart_from_oral(client):
    p = _protocol(
        client,
        [
            {"name": "Oral one", "route": "oral", "amount": "5", "unit": "mg"},
            {"name": "Scalp prep", "route": "topical", "formulation": "foam"},
        ],
    )
    routes = [i["route"] for i in p["interventions"]]
    assert routes == ["oral", "topical"]
    stored = client.get(f"{URL}{p['id']}/").json()["interventions"]
    assert stored[1]["route"] == "topical" and stored[1]["amount"] == ""


@pytest.mark.parametrize(
    ("item", "path"),
    [
        ({"route": "rectal"}, "interventions[0].route"),
        ({"route": 3}, "interventions[0].route"),
        ({"formulation": "f" * 101}, "interventions[0].formulation"),
        ({"formulation": 5}, "interventions[0].formulation"),
        ({"product_id": 0}, "interventions[0].product_id"),
        ({"product_id": True}, "interventions[0].product_id"),
        ({"units_per_day": "2"}, "interventions[0].product_id"),
        ({"product_id": 1, "units_per_day": "0"}, "interventions[0].units_per_day"),
        ({"product_id": 1, "units_per_day": "-1"}, "interventions[0].units_per_day"),
        ({"product_id": 1, "units_per_day": "٣"}, "interventions[0].units_per_day"),
        ({"product_id": 1, "units_per_day": 2}, "interventions[0].units_per_day"),
    ],
)
def test_bad_route_formulation_or_product_use_is_400_naming_the_path(
    client, item, path
):
    r = client.post(
        URL, {"title": "T", "interventions": [{"name": "x", **item}]}, format="json"
    )
    assert r.status_code == 400 and path in r.json()


def test_long_formulation_is_rejected_not_cut_and_limit_is_accepted(client):
    ok = _protocol(client, [{"name": "x", "formulation": "f" * 100}])
    assert ok["interventions"][0]["formulation"] == "f" * 100
    r = client.patch(
        f"{URL}{ok['id']}/",
        {"interventions": [{"name": "x", "formulation": "f" * 101}]},
        format="json",
    )
    assert r.status_code == 400
    assert (
        client.get(f"{URL}{ok['id']}/").json()["interventions"][0]["formulation"]
        == "f" * 100
    )


def test_route_and_formulation_never_change_amount_dose_or_omop_quantity(client):
    base = {"name": "A", "amount": "6", "unit": "mg"}
    p = _protocol(client, [base])
    client.patch(f"{URL}{p['id']}/", {"state": "active", "reason": "go"}, format="json")
    r = client.patch(
        f"{URL}{p['id']}/",
        {
            "interventions": [
                {**base, "route": "sublingual", "formulation": "liposomal"}
            ],
            "reason": "r",
        },
        format="json",
    )
    assert r.status_code == 200, r.content
    item = r.json()["interventions"][0]
    assert (item["amount"], item["unit"]) == ("6", "mg")
    assert "absolute_dose" not in item
    version = ProtocolVersion.objects.get(protocol_id=p["id"], number=2)
    row = intervention_to_omop_drug_exposure(version, 0)
    assert row["route_source_value"] == "sublingual"
    assert row["route_concept_id"] is None and row["quantity"] is None
    assert row["dose_unit_source_value"] == "mg"
    plain = intervention_to_omop_drug_exposure(
        ProtocolVersion.objects.get(protocol_id=p["id"], number=1), 0
    )
    assert plain["route_source_value"] is None


def test_route_only_item_has_no_amount_in_per_weight_case(client):
    p = _protocol(
        client,
        [
            {
                "name": "A",
                "route": "oral",
                "amount": "2",
                "unit": "mg/kg",
                "basis": "per_body_weight",
            }
        ],
    )
    assert p["interventions"][0]["absolute_dose"] is None


def test_route_change_is_a_change_event_and_shows_in_the_diff(client):
    p = _protocol(client, [{"name": "A", "route": "oral"}])
    client.patch(f"{URL}{p['id']}/", {"state": "active", "reason": "go"}, format="json")
    r = client.patch(
        f"{URL}{p['id']}/",
        {"interventions": [{"name": "A", "route": "topical"}], "reason": "r"},
        format="json",
    )
    events = [e["field"] for e in r.json()["version"]["events"]]
    assert events == ["interventions[0].route"]
    d = client.get(f"{URL}{p['id']}/diff/?from=1&to=2").json()
    assert d["facets"]["interventions"]["changed"] is True


def test_product_must_be_the_users_own(client, substance):
    other = _user("o@example.com")
    theirs = _product(other)
    r = client.post(
        URL,
        {
            "title": "T",
            "interventions": [
                {"name": "x", "product_id": theirs, "units_per_day": "1"}
            ],
        },
        format="json",
    )
    assert r.status_code == 400 and "interventions[0].product_id" in r.json()
    p = _protocol(client, [{"name": "x"}])
    r = client.patch(
        f"{URL}{p['id']}/",
        {"interventions": [{"name": "x", "product_id": 999999}]},
        format="json",
    )
    assert r.status_code == 400 and "interventions[0].product_id" in r.json()


# scenario: interventions-and-catalog::same-ingredient-in-two-products-is-summed-from-declared-amounts
def test_same_ingredient_in_two_products_is_summed_exactly(client, substance):
    a, b = _product(client, "A"), _product(client, "B")
    assert _ingredient(client, a, substance.pk, "0.5", "mg").status_code == 201
    assert (
        _ingredient(
            client, b, substance.pk, "1.25", "mg", label_source="Label B"
        ).status_code
        == 201
    )
    p = _protocol(
        client,
        [
            {"name": "A", "product_id": a, "units_per_day": "2"},
            {"name": "B", "product_id": b, "units_per_day": "1"},
        ],
    )
    out = _totals(client, p["id"])
    assert out["kind"] == "label-contents-total"
    assert not {"posology", "absolute_dose", "dose"} & set(out)
    [sub] = out["substances"]
    [total] = sub["totals"]
    assert (total["unit"], total["amount"]) == ("mg", "2.25")
    assert Decimal(total["amount"]) == Decimal("2") * Decimal("0.5") + Decimal("1.25")
    assert [c["label_source"] for c in total["contributions"]] == [LABEL, LABEL]
    assert [c["ingredient_label_source"] for c in total["contributions"]] == [
        LABEL,
        "Label B",
    ]
    assert all(
        "posology" not in k and "dose" not in k
        for c in total["contributions"]
        for k in c
    )
    assert "not a recommended" in out["note"]


def test_sum_is_exact_where_floats_are_not(client, substance):
    a = _product(client)
    _ingredient(client, a, substance.pk, "0.1", "mg")
    p = _protocol(
        client,
        [
            {"name": "n", "product_id": a, "units_per_day": "3"},
            {"name": "m", "product_id": a, "units_per_day": "0.0000000000001"},
        ],
    )
    [total] = _totals(client, p["id"])["substances"][0]["totals"]
    assert total["amount"] == "0.30000000000001"


# scenario: interventions-and-catalog::an-ingredient-without-a-label-amount-is-not-summed
def test_ingredient_without_amount_is_listed_and_not_summed(client, substance):
    a, b = _product(client, "A"), _product(client, "B")
    _ingredient(client, a, substance.pk, "3", "mg")
    r = client.post(
        f"{PRODUCTS}{b}/ingredients/",
        {"substance": substance.pk, "label_source": LABEL},
        format="json",
    )
    assert r.status_code == 201 and r.json()["amount_per_unit"] is None
    p = _protocol(
        client,
        [
            {"name": "A", "product_id": a, "units_per_day": "1"},
            {"name": "B", "product_id": b, "units_per_day": "4"},
        ],
    )
    [sub] = _totals(client, p["id"])["substances"]
    assert [t["amount"] for t in sub["totals"]] == ["3"]
    [missing] = sub["without_amount"]
    assert missing["amount"] is None and missing["product"] == b
    assert len(sub["totals"][0]["contributions"]) == 1


def test_only_missing_amounts_gives_no_total(client, substance):
    a = _product(client)
    client.post(
        f"{PRODUCTS}{a}/ingredients/",
        {"substance": substance.pk, "label_source": LABEL},
        format="json",
    )
    p = _protocol(client, [{"name": "A", "product_id": a, "units_per_day": "1"}])
    [sub] = _totals(client, p["id"])["substances"]
    assert sub["totals"] == [] and len(sub["without_amount"]) == 1


def test_different_unit_strings_are_never_summed_or_converted(client, substance):
    a, b = _product(client, "A"), _product(client, "B")
    _ingredient(client, a, substance.pk, "1", "mg")
    _ingredient(client, b, substance.pk, "1000", "mcg")
    p = _protocol(
        client,
        [
            {"name": "A", "product_id": a, "units_per_day": "1"},
            {"name": "B", "product_id": b, "units_per_day": "1"},
        ],
    )
    [sub] = _totals(client, p["id"])["substances"]
    assert sorted((t["unit"], t["amount"]) for t in sub["totals"]) == [
        ("mcg", "1000"),
        ("mg", "1"),
    ]


def test_item_without_units_per_day_contributes_nothing(client, substance):
    a = _product(client)
    _ingredient(client, a, substance.pk)
    p = _protocol(client, [{"name": "A", "product_id": a}, {"name": "plain"}])
    out = _totals(client, p["id"])
    assert out["substances"] == []
    assert out["items_without_units_per_day"] == [
        {"intervention_index": 0, "product": a}
    ]


def test_totals_are_owner_only(client, substance):
    p = _protocol(client, [{"name": "x"}])
    assert (
        _user("o@example.com").get(f"{URL}{p['id']}/ingredient-totals/").status_code
        == 404
    )
    assert APIClient().get(f"{URL}{p['id']}/ingredient-totals/").status_code in (
        401,
        403,
    )


def test_ingredient_rows_follow_later_label_corrections(client, substance):
    a = _product(client)
    ing = _ingredient(client, a, substance.pk, "1", "mg").json()
    p = _protocol(client, [{"name": "A", "product_id": a, "units_per_day": "2"}])
    r = client.patch(
        f"{PRODUCTS}{a}/ingredients/{ing['id']}/",
        {"amount_per_unit": "5"},
        format="json",
    )
    assert r.status_code == 200
    assert _totals(client, p["id"])["substances"][0]["totals"][0]["amount"] == "10"


@pytest.mark.parametrize(
    "body",
    [
        {"name": "P", "label_fetched_on": "2026-01-02"},
        {"name": "P", "label_source": "  ", "label_fetched_on": "2026-01-02"},
        {"name": "P", "label_source": LABEL},
        {"name": "P", "label_source": LABEL, "label_fetched_on": "2999-01-01"},
        {"name": "", "label_source": LABEL, "label_fetched_on": "2026-01-02"},
        {
            "name": "P",
            "label_source": LABEL,
            "label_fetched_on": "2026-01-02",
            "owner": 1,
        },
    ],
)
def test_product_without_label_source_or_with_bad_fields_is_refused(client, body):
    assert client.post(PRODUCTS, body, format="json").status_code == 400
    assert not Product.objects.exists()


@pytest.mark.parametrize(
    "extra",
    [
        {"label_source": ""},
        {"amount_per_unit": "1", "unit": ""},
        {"amount_per_unit": "-1"},
        {"amount_per_unit": "1,5"},
        {"amount_per_unit": 1.5},
        {"amount_per_unit": "1.1234567890123"},
        {"amount_per_unit": "1" * 19},
        {"substance": 999999},
        {"substance": "1"},
    ],
)
def test_bad_ingredient_is_refused_and_nothing_is_rounded(client, substance, extra):
    a = _product(client)
    body = {
        "substance": substance.pk,
        "amount_per_unit": "1",
        "unit": "mg",
        "label_source": LABEL,
        **extra,
    }
    r = client.post(f"{PRODUCTS}{a}/ingredients/", body, format="json")
    assert r.status_code == 400
    assert not ProductIngredient.objects.exists()


def test_ingredient_without_label_source_key_is_refused(client, substance):
    a = _product(client)
    r = client.post(
        f"{PRODUCTS}{a}/ingredients/", {"substance": substance.pk}, format="json"
    )
    assert r.status_code == 400 and "label_source" in r.json()


def test_same_substance_twice_in_a_product_is_refused(client, substance):
    a = _product(client)
    assert _ingredient(client, a, substance.pk).status_code == 201
    assert _ingredient(client, a, substance.pk).status_code == 400


def test_database_refuses_rows_without_label_source_or_unit(db, substance):
    owner = User.objects.create_user(email="d@example.com", password="correct-horse-9")
    for kw in ({"label_source": ""}, {"name": ""}):
        with pytest.raises(IntegrityError), transaction.atomic():
            Product.objects.create(
                owner=owner,
                **{
                    "name": "P",
                    "label_source": "s",
                    "label_fetched_on": "2026-01-02",
                    **kw,
                },
            )
    product = Product.objects.create(
        owner=owner, name="P", label_source="s", label_fetched_on="2026-01-02"
    )
    for kw in ({"label_source": ""}, {"amount_per_unit": Decimal(1), "unit": None}):
        with pytest.raises(IntegrityError), transaction.atomic():
            ProductIngredient.objects.create(
                product=product, substance=substance, **{"label_source": "s", **kw}
            )


def test_product_api_is_owner_only_and_patch_needs_a_new_fetch_date(client, substance):
    mine = _product(client)
    other = _user("o@example.com")
    assert other.get(f"{PRODUCTS}{mine}/").status_code == 404
    assert (
        other.post(f"{PRODUCTS}{mine}/ingredients/", {}, format="json").status_code
        == 404
    )
    assert other.get(PRODUCTS).json() == []
    assert APIClient().get(PRODUCTS).status_code in (401, 403)
    assert (
        client.patch(
            f"{PRODUCTS}{mine}/", {"label_source": "new"}, format="json"
        ).status_code
        == 400
    )
    ok = client.patch(
        f"{PRODUCTS}{mine}/",
        {"label_source": "new", "label_fetched_on": "2026-02-02"},
        format="json",
    )
    assert ok.status_code == 200 and ok.json()["label_source"] == "new"
    ing = _ingredient(client, mine, substance.pk).json()["id"]
    assert other.delete(f"{PRODUCTS}{mine}/ingredients/{ing}/").status_code == 404
    assert client.delete(f"{PRODUCTS}{mine}/ingredients/{ing}/").status_code == 204


def test_nothing_is_seeded_and_migrations_are_clean(db):
    assert not Product.objects.exists() and not ProductIngredient.objects.exists()
    assert not Substance.objects.exists()
    call_command("makemigrations", "--check", "--dry-run")
