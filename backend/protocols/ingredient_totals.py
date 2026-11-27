# SPDX-License-Identifier: AGPL-3.0-or-later
"""Per-day total of label contents across the products of a protocol (M03 TG-e).

Pure arithmetic on declared label amounts with `Decimal`: amount per unit x units per day,
added only where the unit string is exactly the same. Nothing is converted, estimated or
read from anywhere else, and the result is a total of label contents, never a posology.
"""

from decimal import Decimal, localcontext
from typing import Any

from django.contrib.auth.models import AbstractBaseUser

from substances.models import Product

KIND = "label-contents-total"
NOTE = (
    "This is a total of what the product labels declare. It is not a recommended "
    "dose or a posology."
)
PRECISION = 120  # exact for every amount the API accepts (18 + 12 digits per factor)


def _text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _contribution(
    product: Product, index: int, units: Decimal, amount: Decimal
) -> dict[str, Any]:
    return {
        "product": product.pk,
        "product_name": product.name,
        "intervention_index": index,
        "units_per_day": _text(units),
        "per_day": _text(amount),
        "label_source": product.label_source,
    }


def ingredient_totals(
    owner: AbstractBaseUser, interventions: list[dict[str, Any]]
) -> dict[str, Any]:
    ids = {i["product_id"] for i in interventions if "product_id" in i}
    products = {
        p.pk: p
        for p in Product.objects.filter(owner=owner, pk__in=ids).prefetch_related(
            "ingredients__substance"
        )
    }
    by_substance: dict[int, dict[str, Any]] = {}
    sums: dict[tuple[int, str], dict[str, Any]] = {}
    without_units: list[dict[str, Any]] = []
    with localcontext() as ctx:
        ctx.prec = PRECISION
        for index, item in enumerate(interventions):
            product = products.get(item.get("product_id", 0))
            if product is None:
                continue
            raw_units = item.get("units_per_day")
            if raw_units is None:
                without_units.append(
                    {"intervention_index": index, "product": product.pk}
                )
                continue
            units = Decimal(raw_units)
            for ing in product.ingredients.all():
                entry = by_substance.setdefault(
                    ing.substance_id,
                    {
                        "substance": ing.substance_id,
                        "name": ing.substance.name,
                        "totals": [],
                        "without_amount": [],
                    },
                )
                if ing.amount_per_unit is None or not ing.unit:
                    entry["without_amount"].append(
                        {
                            "product": product.pk,
                            "product_name": product.name,
                            "intervention_index": index,
                            "amount": None,
                            "label_source": ing.label_source,
                        }
                    )
                    continue
                per_day = ing.amount_per_unit * units
                key = (ing.substance_id, ing.unit)
                if key not in sums:
                    sums[key] = {
                        "unit": ing.unit,
                        "_sum": Decimal(0),
                        "contributions": [],
                    }
                    entry["totals"].append(sums[key])
                sums[key]["_sum"] += per_day
                sums[key]["contributions"].append(
                    {
                        **_contribution(product, index, units, per_day),
                        "amount_per_unit": _text(ing.amount_per_unit),
                        "ingredient_label_source": ing.label_source,
                    }
                )
    for bucket in sums.values():
        bucket["amount"] = _text(bucket.pop("_sum"))
    return {
        "kind": KIND,
        "note": NOTE,
        "substances": list(by_substance.values()),
        "items_without_units_per_day": without_units,
    }
