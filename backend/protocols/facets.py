# SPDX-License-Identifier: AGPL-3.0-or-later
"""Validated shape of the protocol facets. Names and units are kept as entered (no catalog or
UCUM lookup until M03 TG-a/TG-b); amounts are exact decimal strings, never floats."""

from decimal import Decimal, InvalidOperation
from typing import Any

from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs

FACETS = ("interventions", "cycles", "measures", "goals")
PURPOSES = ("efficacy", "safety", "baseline")
MAX_ITEMS = 100
MAX_TEXT = 500
AMOUNT_HINT = 'must be a decimal string such as "6" or "0.5".'


def _text(raw: Any, where: str, required: bool = True) -> str:
    if raw is None and not required:
        return ""
    if not isinstance(raw, str):
        raise ValidationError({where: "must be text."})
    text = raw.strip()
    if "\x00" in text or len(text) > MAX_TEXT:
        raise ValidationError(
            {where: f"must be at most {MAX_TEXT} characters, without NUL."}
        )
    if required and not text:
        raise ValidationError({where: "must not be blank."})
    return text


def _amount(raw: Any, where: str) -> str:
    if raw is None or raw == "":
        return ""
    if not isinstance(raw, str):
        raise ValidationError({where: AMOUNT_HINT})
    text = raw.strip()
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise ValidationError({where: AMOUNT_HINT}) from None
    if not value.is_finite() or value < 0:
        raise ValidationError({where: "must be a finite number, zero or more."})
    return text


def _days(raw: Any, where: str) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        raise ValidationError({where: "must be a whole number of days, zero or more."})
    return raw


def _items(raw: Any, facet: str) -> list[Any]:
    if not isinstance(raw, list) or len(raw) > MAX_ITEMS:
        raise ValidationError({facet: f"must be a list of at most {MAX_ITEMS} items."})
    return raw


def _object(raw: Any, where: str, keys: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValidationError({where: "must be an object."})
    unknown = sorted(set(raw) - keys)
    if unknown:
        raise ValidationError({where: f"unknown field(s): {', '.join(unknown)}."})
    missing = sorted(required - set(raw))
    if missing:
        raise ValidationError({where: f"missing field(s): {', '.join(missing)}."})
    return raw


def _intervention(raw: Any, where: str) -> dict[str, str]:
    item = _object(raw, where, {"name", "amount", "unit", "schedule"}, {"name"})
    out = {
        "name": _text(item["name"], f"{where}.name"),
        "amount": _amount(item.get("amount"), f"{where}.amount"),
        "unit": _text(item.get("unit"), f"{where}.unit", required=False),
        "schedule": _text(item.get("schedule"), f"{where}.schedule", required=False),
    }
    if out["amount"] and not out["unit"]:
        raise ValidationError({f"{where}.unit": "is required when an amount is given."})
    return out


def _cycle(raw: Any, where: str) -> dict[str, Any]:
    keys = {"label", "on_days", "off_days"}
    item = _object(raw, where, keys, keys)
    return {
        "label": _text(item["label"], f"{where}.label"),
        "on_days": _days(item["on_days"], f"{where}.on_days"),
        "off_days": _days(item["off_days"], f"{where}.off_days"),
    }


def _measure(raw: Any, where: str) -> dict[str, str]:
    keys = {"loinc_code", "purpose"}
    item = _object(raw, where, keys, keys)
    if item["purpose"] not in PURPOSES:
        raise ValidationError(
            {f"{where}.purpose": f"must be one of {', '.join(PURPOSES)}."}
        )
    return {
        "loinc_code": _text(item["loinc_code"], f"{where}.loinc_code"),
        "purpose": item["purpose"],
    }


def clean_facet(facet: str, raw: Any) -> list[Any]:
    """Return the facet in canonical form, or raise a 400 naming the offending path."""
    items = _items(raw, facet)
    if facet == "goals":
        return [_text(g, f"goals[{i}]") for i, g in enumerate(items)]
    clean = {"interventions": _intervention, "cycles": _cycle, "measures": _measure}[
        facet
    ]
    return [clean(item, f"{facet}[{i}]") for i, item in enumerate(items)]


def missing_in_draft(
    interventions: list[Any], goals: list[Any], measures: list[Any], level: str
) -> list[str]:
    """What a draft still lacks, in plain words, from fixed rules. Never blocks a save."""
    purposes = {m["purpose"] for m in measures}
    rules = [
        (not interventions, "No interventions yet."),
        (not goals, "No goal yet."),
        ("efficacy" not in purposes, "No efficacy markers yet."),
        ("safety" not in purposes, "No safety markers yet."),
        (not level, "No level chosen yet (medical or research)."),
    ]
    return [text for lacking, text in rules if lacking]
