# SPDX-License-Identifier: AGPL-3.0-or-later
"""Constrained-column validator (M03 TG-c): the gate any extractor goes through.

The schema is read from the Django model fields. A proposed value is written only when
it is an exact member of a closed enum (`choices`) or fits `max_length`. Free text goes
to the notes field. Anything else is returned as ambiguous with its full original value;
no value is ever truncated, coerced or guessed, and the other fields are still kept.
"""

import json
from dataclasses import dataclass, field
from typing import Any, cast

from django.db import models

from .models import AmbiguityReason

NOTES_KEY = "notes"


@dataclass(frozen=True)
class Ambiguous:
    field: str
    value: str  # the full original value (JSON text when it was not a string)
    reason: str


@dataclass(frozen=True)
class Validated:
    accepted: dict[str, str] = field(default_factory=dict)
    notes: str = ""
    ambiguous: list[Ambiguous] = field(default_factory=list)


@dataclass(frozen=True)
class Rule:
    choices: frozenset[str] | None
    max_length: int | None


def schema_for(model: type[models.Model], allowed: tuple[str, ...]) -> dict[str, Rule]:
    """Read the closed-enum / max_length rule of each allowed field from the model."""
    schema: dict[str, Rule] = {}
    for name in allowed:
        model_field = cast("models.Field[Any, Any]", model._meta.get_field(name))
        if model_field.choices:
            keys = frozenset(str(k) for k, _ in model_field.flatchoices)
            schema[name] = Rule(keys, None)
        elif isinstance(model_field, models.CharField) and model_field.max_length:
            schema[name] = Rule(None, model_field.max_length)
        else:
            raise ValueError(f"{name} is neither an enum nor a bounded CharField")
    return schema


def _original(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def validate_proposal(
    model: type[models.Model], proposed: dict[str, Any], allowed: tuple[str, ...]
) -> Validated:
    """Route each proposed value: write it, keep it as notes, or mark it ambiguous."""
    schema = schema_for(model, allowed)
    accepted: dict[str, str] = {}
    notes = ""
    ambiguous: list[Ambiguous] = []
    for name, value in proposed.items():
        reason: str | None = None
        if name != NOTES_KEY and name not in schema:
            reason = AmbiguityReason.UNKNOWN_FIELD
        elif not isinstance(value, str):
            reason = AmbiguityReason.NOT_TEXT
        elif name == NOTES_KEY:
            notes = value
        else:
            rule = schema[name]
            if rule.choices is not None and value not in rule.choices:
                reason = AmbiguityReason.NOT_IN_ENUM
            elif rule.max_length is not None and len(value) > rule.max_length:
                reason = AmbiguityReason.TOO_LONG
            else:
                accepted[name] = value
        if reason is not None:
            ambiguous.append(Ambiguous(name, _original(value), reason))
    return Validated(accepted, notes, ambiguous)
