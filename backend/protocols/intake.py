# SPDX-License-Identifier: AGPL-3.0-or-later
"""Intake events (M04 TG-b): generated stateless; only the owner sets a state, by explicit action."""

import re
from datetime import date
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.utils import timezone

from core.cadence import Cadence, due_events

from .facets import AMOUNT_HINT, MAX_AMOUNT, PLAIN_AMOUNT
from .models import IntakeEvent, IntakeState, ProtocolVersion

MAX_UNIT = 100
AMOUNT_FRACTION_DIGITS = 10  # matches IntakeEvent.entered_amount decimal_places
AMOUNT_WHOLE_DIGITS = 20  # max_digits 30 minus decimal_places
CANONICAL_KEY = re.compile(r"0|[1-9][0-9]*")
WITH_AMOUNT = (IntakeState.DONE, IntakeState.PARTIAL)


def generate_intake_events(
    protocol_version: ProtocolVersion,
    intervention_key: str,
    cadence: Cadence,
    start: date,
    window_start: date,
    window_end: date,
) -> list[IntakeEvent]:
    """Create the missing events of the window, all pending; existing rows are left untouched."""
    interventions = protocol_version.snapshot["interventions"]
    if not CANONICAL_KEY.fullmatch(intervention_key):
        raise ValueError("intervention_key must be an index into the snapshot")
    if int(intervention_key) >= len(interventions):
        raise ValueError("intervention_key is not in this version's snapshot")
    pairs = due_events(cadence, start, window_start, window_end)
    with transaction.atomic():
        IntakeEvent.objects.bulk_create(
            [
                IntakeEvent(
                    owner_id=protocol_version.protocol.owner_id,
                    protocol_id=protocol_version.protocol_id,
                    version=protocol_version,
                    intervention_key=intervention_key,
                    due_date=day,
                    occurrence_index=index,
                )
                for day, index in pairs
            ],
            ignore_conflicts=True,
        )
    return list(
        IntakeEvent.objects.filter(
            version=protocol_version,
            intervention_key=intervention_key,
            due_date__in={day for day, _ in pairs},
        )
    )


def _clean_amount(amount: Any, unit: Any, state: str) -> tuple[Decimal | None, str]:
    if amount is None:
        if unit not in (None, ""):
            raise ValueError("a unit needs an amount")
        return None, ""
    if state not in WITH_AMOUNT:
        raise ValueError("an amount is allowed only with state done or partial")
    if not isinstance(unit, str) or not unit.strip():
        raise ValueError("an amount needs a UCUM unit")
    unit = unit.strip()
    if len(unit) > MAX_UNIT or "\x00" in unit:
        raise ValueError(f"unit must be at most {MAX_UNIT} characters, without NUL")
    if not isinstance(amount, str):
        raise ValueError(f"amount {AMOUNT_HINT}")
    text = amount.strip()
    if len(text) > MAX_AMOUNT or not PLAIN_AMOUNT.fullmatch(text):
        raise ValueError(f"amount {AMOUNT_HINT}")
    whole, _, fraction = text.partition(".")
    if len(whole) > AMOUNT_WHOLE_DIGITS or len(fraction) > AMOUNT_FRACTION_DIGITS:
        raise ValueError(f"amount {AMOUNT_HINT}")
    return Decimal(text), unit


def set_intake_state(
    event: IntakeEvent,
    actor: AbstractBaseUser,
    state: str,
    entered_amount: str | None = None,
    entered_unit: str | None = None,
) -> IntakeEvent:
    """The only write path for `IntakeEvent.state`: the owner, explicitly."""
    if actor.pk != event.owner_id:
        raise PermissionError("only the owner can set an intake state")
    if state not in IntakeState.values:
        raise ValueError(f"state must be one of {', '.join(IntakeState.values)}")
    amount, unit = _clean_amount(entered_amount, entered_unit, state)
    event.state = state
    event.state_set_by = actor  # type: ignore[assignment]
    event.state_set_at = timezone.now()
    event.entered_amount = amount
    event.entered_unit = unit
    event.save()
    return event
