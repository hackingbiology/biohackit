# SPDX-License-Identifier: AGPL-3.0-or-later
"""Validated shape of the protocol facets. Names and units are kept as entered (no catalog or
UCUM lookup until M03 TG-a/TG-b); amounts are exact decimal strings, never floats."""

import re
from decimal import Decimal
from typing import Any

from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs

FACETS = ("interventions", "cycles", "measures", "goals")
PURPOSES = ("efficacy", "safety", "baseline")
MAX_ITEMS = 100
MAX_TEXT = 500
MAX_AMOUNT = 30
BASES = ("absolute", "per_body_weight")
PROVENANCES = ("human-derived", "animal-derived")
PER_WEIGHT = "per_body_weight"
# Plain labels, not SNOMED/EDQM/FHIR codes (Q130, a default, not a cited list).
ROUTES = (
    "oral",
    "sublingual",
    "topical",
    "intranasal",
    "inhaled",
    "subcutaneous",
    "intramuscular",
    "other",
)
MAX_FORMULATION = 100
AMOUNT_HINT = (
    'must be a plain decimal string such as "6" or "0.5" '
    f"(ASCII digits only, at most {MAX_AMOUNT} characters)."
)
PLAIN_AMOUNT = re.compile(r"[0-9]+(\.[0-9]+)?", re.ASCII)


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
    if len(text) > MAX_AMOUNT or not PLAIN_AMOUNT.fullmatch(text):
        raise ValidationError({where: AMOUNT_HINT})
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


def _enum(raw: Any, choices: tuple[str, ...], where: str) -> str:
    if not isinstance(raw, str) or raw not in choices:
        raise ValidationError({where: f"must be one of {', '.join(choices)}."})
    return raw


def _posology(item: dict[str, Any], where: str) -> dict[str, str]:
    """The optional basis and provenance keys, written only when not at their default,
    so a stored item without them stays identical (absolute, no provenance)."""
    out: dict[str, str] = {}
    if item.get("basis") is not None:
        basis = _enum(item["basis"], BASES, f"{where}.basis")
        if basis != "absolute":
            out["basis"] = basis
    raw = item.get("provenance")
    source = _text(item.get("provenance_source"), f"{where}.provenance_source", False)
    if raw in (None, ""):
        if source:
            raise ValidationError(
                {f"{where}.provenance": "is required when a source is given."}
            )
        return out
    out["provenance"] = _enum(raw, PROVENANCES, f"{where}.provenance")
    if not source:
        raise ValidationError(
            {f"{where}.provenance_source": "is required with a provenance."}
        )
    out["provenance_source"] = source
    return out


def _formulation(raw: Any, where: str) -> str:
    text = _text(raw, where, False)
    if len(text) > MAX_FORMULATION:
        raise ValidationError(
            {where: f"must be at most {MAX_FORMULATION} characters; it is never cut."}
        )
    return text


def _product_use(item: dict[str, Any], where: str) -> dict[str, Any]:
    """Optional `product_id` and `units_per_day`, written only when set. Neither sets or
    changes the amount: they only feed the label-contents total."""
    out: dict[str, Any] = {}
    raw = item.get("product_id")
    if raw is not None:
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
            raise ValidationError(
                {f"{where}.product_id": "must be the id of one of your products."}
            )
        out["product_id"] = raw
    units = _amount(item.get("units_per_day"), f"{where}.units_per_day")
    if units:
        if Decimal(units) <= 0:
            raise ValidationError(
                {f"{where}.units_per_day": "must be greater than zero."}
            )
        if "product_id" not in out:
            raise ValidationError(
                {f"{where}.product_id": "is required with units_per_day."}
            )
        out["units_per_day"] = units
    return out


def _genomic(item: dict[str, Any], where: str) -> dict[str, bool]:
    """Optional `genomic` flag, written only when true. A genomic item is never published
    (no genomics heightened consent exists yet)."""
    raw = item.get("genomic")
    if raw is None or raw is False:
        return {}
    if raw is not True:
        raise ValidationError({f"{where}.genomic": "must be true or false."})
    return {"genomic": True}


def _intervention(raw: Any, where: str) -> dict[str, Any]:
    keys = {"name", "amount", "unit", "schedule", "basis", "provenance"}
    extra = {"provenance_source", "route", "formulation", "product_id", "units_per_day"}
    item = _object(raw, where, {*keys, *extra, "genomic"}, {"name"})
    out = {
        "name": _text(item["name"], f"{where}.name"),
        "amount": _amount(item.get("amount"), f"{where}.amount"),
        "unit": _text(item.get("unit"), f"{where}.unit", required=False),
        "schedule": _text(item.get("schedule"), f"{where}.schedule", required=False),
    }
    if out["amount"] and not out["unit"]:
        raise ValidationError({f"{where}.unit": "is required when an amount is given."})
    if item.get("route") is not None:
        out["route"] = _enum(item["route"], ROUTES, f"{where}.route")
    formulation = _formulation(item.get("formulation"), f"{where}.formulation")
    if formulation:
        out["formulation"] = formulation
    return {
        **out,
        **_posology(item, where),
        **_product_use(item, where),
        **_genomic(item, where),
    }


def is_per_weight(item: dict[str, Any]) -> bool:
    return item.get("basis") == PER_WEIGHT


def untagged_per_weight(interventions: list[Any]) -> list[str]:
    """Names of per-weight items with no provenance: not accepted as a dose."""
    return [
        i["name"] for i in interventions if is_per_weight(i) and not i.get("provenance")
    ]


def animal_derived(interventions: list[Any]) -> list[str]:
    return [i["name"] for i in interventions if i.get("provenance") == "animal-derived"]


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
    item = _object(raw, where, {*keys, "genomic"}, keys)
    if item["purpose"] not in PURPOSES:
        raise ValidationError(
            {f"{where}.purpose": f"must be one of {', '.join(PURPOSES)}."}
        )
    return {
        "loinc_code": _text(item["loinc_code"], f"{where}.loinc_code"),
        "purpose": item["purpose"],
        **_genomic(item, where),
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
    lines = [text for lacking, text in rules if lacking]
    lines += [
        f"{name}: this dose is per body weight. Say whether it comes from human or "
        "animal data, and give the source."
        for name in untagged_per_weight(interventions)
    ]
    return lines
