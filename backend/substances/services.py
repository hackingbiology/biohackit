# SPDX-License-Identifier: AGPL-3.0-or-later
"""Validation and writes for substances. A code without a source is refused here."""

from datetime import date
from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import CodeSystem, Substance, SubstanceCode

NAME_MAX = 200
CLASS_MAX = 200
CODE_MAX = 64
SOURCE_MAX = 300
EMPTY_CLASS: dict[str, Any] = {
    "substance_class": "",
    "class_source": "",
    "class_fetched_on": None,
}


class SubstanceError(ValueError):
    """Invalid input; `errors` maps a field name to a plain-language message."""

    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__(errors)
        self.errors = errors


def _text(data: dict[str, Any], key: str, maximum: int, *, required: bool) -> str:
    value = data.get(key, "")
    if not isinstance(value, str):
        raise SubstanceError({key: "Enter text."})
    if "\x00" in value:
        raise SubstanceError({key: "Enter text."})
    value = value.strip()
    if required and not value:
        raise SubstanceError({key: "This is required."})
    if len(value) > maximum:
        raise SubstanceError({key: f"Use at most {maximum} characters."})
    return value


def _date(raw: Any, key: str) -> date:
    message = "Enter the fetch date as YYYY-MM-DD."
    if not isinstance(raw, str):
        raise SubstanceError({key: message})
    try:
        value = date.fromisoformat(raw.strip())
    except ValueError:
        raise SubstanceError({key: message}) from None
    if value > timezone.now().date():
        raise SubstanceError({key: "The fetch date cannot be in the future."})
    return value


def clean_class(data: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Validate the class with its provenance; `current` fills fields not sent.

    A non-empty class needs a source and a fetch date; an empty class clears both.
    """
    merged = {**current, **{k: v for k, v in data.items() if k in current}}
    klass = _text(merged, "substance_class", CLASS_MAX, required=False)
    if not klass:
        return {"substance_class": "", "class_source": "", "class_fetched_on": None}
    source = _text(merged, "class_source", SOURCE_MAX, required=True)
    raw = merged.get("class_fetched_on")
    if raw is None or (
        ("substance_class" in data or "class_source" in data)
        and "class_fetched_on" not in data
    ):
        raise SubstanceError(
            {"class_fetched_on": "Enter the fetch date when you change the class."}
        )
    return {
        "substance_class": klass,
        "class_source": source,
        "class_fetched_on": _date(raw, "class_fetched_on"),
    }


def _system(data: dict[str, Any]) -> str:
    value = data.get("system")
    if value not in CodeSystem.values:
        raise SubstanceError({"system": f"Use one of: {', '.join(CodeSystem.values)}."})
    return str(value)


def _refuse_provisional(data: dict[str, Any]) -> None:
    """`provisional` is server-controlled: always true until Q105/Q106/Q116 are answered."""
    if "provisional" in data:
        raise SubstanceError({"provisional": "This field is set by the server."})


def clean_code(data: dict[str, Any]) -> dict[str, Any]:
    """Validate one code. The code string is kept as entered after a strip."""
    _refuse_provisional(data)
    return {
        "system": _system(data),
        "code": _text(data, "code", CODE_MAX, required=True),
        "source": _text(data, "source", SOURCE_MAX, required=True),
        "fetched_on": _date(data.get("fetched_on"), "fetched_on"),
        "provisional": True,
    }


def create_substance(data: dict[str, Any]) -> Substance:
    name = _text(data, "name", NAME_MAX, required=True)
    klass = clean_class(data, EMPTY_CLASS)
    raw_codes = data.get("codes", [])
    if not isinstance(raw_codes, list) or not all(
        isinstance(c, dict) for c in raw_codes
    ):
        raise SubstanceError({"codes": "Send a list of codes."})
    codes = [clean_code(c) for c in raw_codes]
    if len({(c["system"], c["code"]) for c in codes}) != len(codes):
        raise SubstanceError({"codes": "The same code is listed twice."})
    with transaction.atomic():
        substance = Substance.objects.create(name=name, **klass)
        SubstanceCode.objects.bulk_create(
            SubstanceCode(substance=substance, **c) for c in codes
        )
    return substance


def update_substance(substance: Substance, data: dict[str, Any]) -> Substance:
    if "name" in data:
        substance.name = _text(data, "name", NAME_MAX, required=True)
    if any(k in data for k in EMPTY_CLASS):
        current = {
            "substance_class": substance.substance_class,
            "class_source": substance.class_source,
            "class_fetched_on": (
                substance.class_fetched_on.isoformat()
                if substance.class_fetched_on
                else None
            ),
        }
        for field, value in clean_class(data, current).items():
            setattr(substance, field, value)
    substance.save()
    return substance


def _clashes(substance_id: int, cleaned: dict[str, Any], exclude: int | None) -> bool:
    rows = SubstanceCode.objects.filter(
        substance_id=substance_id, system=cleaned["system"], code=cleaned["code"]
    )
    if exclude is not None:
        rows = rows.exclude(pk=exclude)
    return rows.exists()


def add_code(substance: Substance, data: dict[str, Any]) -> SubstanceCode:
    cleaned = clean_code(data)
    if _clashes(substance.pk, cleaned, None):
        raise SubstanceError({"code": "This code is already recorded."})
    return SubstanceCode.objects.create(substance=substance, **cleaned)


def update_code(code: SubstanceCode, data: dict[str, Any]) -> SubstanceCode:
    """Correct a code; the result must still have a source and a fetch date.

    Changing the code, system or source needs a new fetch date, so an old date is
    never kept for a value fetched later.
    """
    changed = any(k in data for k in ("code", "system", "source"))
    if changed and "fetched_on" not in data:
        raise SubstanceError(
            {"fetched_on": "Enter the fetch date when you change the code."}
        )
    merged = {
        "system": code.system,
        "code": code.code,
        "source": code.source,
        "fetched_on": code.fetched_on.isoformat(),
        **data,
    }
    cleaned = clean_code(merged)
    cleaned["provisional"] = code.provisional
    if _clashes(code.substance_id, cleaned, code.pk):
        raise SubstanceError({"code": "This code is already recorded."})
    for field, value in cleaned.items():
        setattr(code, field, value)
    code.save()
    return code
