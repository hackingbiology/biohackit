# SPDX-License-Identifier: AGPL-3.0-or-later
"""Products and the ingredients their label declares (M03 TG-e). Amounts come only from a
cited label: a missing amount stays null and is never estimated, a value that does not fit
the column is refused and never rounded or truncated."""

import re
from decimal import Decimal
from typing import Any

from django.db import transaction

from accounts.models import User

from .models import Product, ProductIngredient, Substance
from .services import NAME_MAX, SOURCE_MAX, SubstanceError, _date, _text

UNIT_MAX = 50
INTEGER_DIGITS = 18
DECIMAL_PLACES = 12
AMOUNT_HINT = (
    'must be a plain decimal string such as "500" or "0.25" (ASCII digits only, at '
    f"most {INTEGER_DIGITS} before and {DECIMAL_PLACES} after the point)."
)
PLAIN_AMOUNT = re.compile(
    rf"[0-9]{{1,{INTEGER_DIGITS}}}(\.[0-9]{{1,{DECIMAL_PLACES}}})?", re.ASCII
)
PRODUCT_KEYS = {"name", "label_source", "label_fetched_on"}
INGREDIENT_KEYS = {"substance", "amount_per_unit", "unit", "label_source"}


def _only(data: dict[str, Any], keys: set[str]) -> None:
    unknown = sorted(set(data) - keys)
    if unknown:
        raise SubstanceError({"detail": f"Not accepted here: {', '.join(unknown)}."})


def _amount(raw: Any) -> Decimal | None:
    if raw is None or raw == "":
        return None
    if not isinstance(raw, str) or not PLAIN_AMOUNT.fullmatch(raw.strip()):
        raise SubstanceError({"amount_per_unit": f"Send it as text: it {AMOUNT_HINT}"})
    return Decimal(raw.strip())


def _unit(data: dict[str, Any]) -> str | None:
    if data.get("unit") is None:
        return None
    value = _text(data, "unit", UNIT_MAX, required=False)
    return value or None


def create_product(owner: User, data: dict[str, Any]) -> Product:
    _only(data, PRODUCT_KEYS)
    return Product.objects.create(
        owner=owner,
        name=_text(data, "name", NAME_MAX, required=True),
        label_source=_text(data, "label_source", SOURCE_MAX, required=True),
        label_fetched_on=_date(data.get("label_fetched_on"), "label_fetched_on"),
    )


def update_product(product: Product, data: dict[str, Any]) -> Product:
    """Changing the label source needs a new fetch date in the same request."""
    _only(data, PRODUCT_KEYS)
    if "label_source" in data and "label_fetched_on" not in data:
        raise SubstanceError(
            {"label_fetched_on": "Enter the fetch date when you change the label."}
        )
    if "name" in data:
        product.name = _text(data, "name", NAME_MAX, required=True)
    if "label_source" in data:
        product.label_source = _text(data, "label_source", SOURCE_MAX, required=True)
    if "label_fetched_on" in data:
        product.label_fetched_on = _date(data["label_fetched_on"], "label_fetched_on")
    product.save()
    return product


def _substance(raw: Any) -> Substance:
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise SubstanceError({"substance": "Send the id of an existing substance."})
    found = Substance.objects.filter(pk=raw).first()
    if found is None:
        raise SubstanceError({"substance": "Send the id of an existing substance."})
    return found


def _check_amount_unit(amount: Decimal | None, unit: str | None) -> None:
    if amount is not None and not unit:
        raise SubstanceError({"unit": "is required when an amount is given."})


def add_ingredient(product: Product, data: dict[str, Any]) -> ProductIngredient:
    _only(data, INGREDIENT_KEYS)
    substance = _substance(data.get("substance"))
    amount = _amount(data.get("amount_per_unit"))
    unit = _unit(data)
    _check_amount_unit(amount, unit)
    source = _text(data, "label_source", SOURCE_MAX, required=True)
    with transaction.atomic():
        if product.ingredients.filter(substance=substance).exists():
            raise SubstanceError(
                {"substance": "This product already lists that substance."}
            )
        return ProductIngredient.objects.create(
            product=product,
            substance=substance,
            amount_per_unit=amount,
            unit=unit,
            label_source=source,
        )


def update_ingredient(
    ingredient: ProductIngredient, data: dict[str, Any]
) -> ProductIngredient:
    """The substance cannot change: remove the row and add another. `amount_per_unit:
    null` and `unit: null` record that the label gives no amount."""
    _only(data, INGREDIENT_KEYS - {"substance"})
    if "amount_per_unit" in data:
        ingredient.amount_per_unit = _amount(data["amount_per_unit"])
    if "unit" in data:
        ingredient.unit = _unit(data)
    if "label_source" in data:
        ingredient.label_source = _text(data, "label_source", SOURCE_MAX, required=True)
    _check_amount_unit(ingredient.amount_per_unit, ingredient.unit)
    ingredient.save()
    return ingredient
