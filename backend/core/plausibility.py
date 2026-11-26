# SPDX-License-Identifier: AGPL-3.0-or-later
"""Plausibility of a typed lab value against stored, cited reference ranges (M02 TG-b, Q70).

Pure and deterministic: no range is invented, nothing is ever rejected. Only
unstratified ranges are used, because the user has not supplied age, sex or ancestry
and guessing a stratum would be inventing data."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from terminology.services import range_status

Plausibility = Literal["within", "outside", "not_checked"]


@dataclass(frozen=True)
class RangeCandidate:
    """The fields of a stored ReferenceRange that the check needs."""

    low: Decimal | None
    high: Decimal | None
    unit: str  # UCUM code of the range's unit
    source_id: int
    stratified: bool  # any of age/sex/ancestry is set


@dataclass(frozen=True)
class PlausibilityOutcome:
    status: Plausibility
    source_id: int | None


NOT_CHECKED = PlausibilityOutcome("not_checked", None)


def check_plausibility(
    reported_value: Decimal,
    reported_unit: str,
    normalised_value: Decimal | None,
    normalised_unit: str | None,
    candidates: list[RangeCandidate],
) -> PlausibilityOutcome:
    """`within` or `outside` only when exactly one unstratified range exists whose unit
    equals the reported unit or the normalised unit; otherwise `not_checked`."""
    usable = [
        c
        for c in candidates
        if not c.stratified
        and (
            c.unit == reported_unit
            or (normalised_value is not None and c.unit == normalised_unit)
        )
    ]
    if len(usable) != 1:
        return NOT_CHECKED
    rng = usable[0]
    value = reported_value if rng.unit == reported_unit else normalised_value
    if value is None:
        return NOT_CHECKED
    status = range_status(value, rng.low, rng.high)
    return PlausibilityOutcome(
        "within" if status == "within" else "outside", rng.source_id
    )
