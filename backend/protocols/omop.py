# SPDX-License-Identifier: AGPL-3.0-or-later
"""Protocol intervention -> OMOP CDM v5.4 DRUG_EXPOSURE row (pure, no DB writes).

An export target, not a storage schema. Columns and order are those of the official
v5.4.0 DDL; see docs/omop/drug-exposure-mapping.md for the source of every column.
A column with no stored value is None: no concept id and no default is ever guessed.
"""

from datetime import UTC, date
from typing import Any

from .models import ProtocolVersion

OMOP_CDM_VERSION = "5.4"  # docs/omop/drug-exposure-mapping.md, tag v5.4.0

DRUG_EXPOSURE_COLUMNS: tuple[str, ...] = (
    "drug_exposure_id",
    "person_id",
    "drug_concept_id",
    "drug_exposure_start_date",
    "drug_exposure_start_datetime",
    "drug_exposure_end_date",
    "drug_exposure_end_datetime",
    "verbatim_end_date",
    "drug_type_concept_id",
    "stop_reason",
    "refills",
    "quantity",
    "days_supply",
    "sig",
    "route_concept_id",
    "lot_number",
    "provider_id",
    "visit_occurrence_id",
    "visit_detail_id",
    "drug_source_value",
    "drug_source_concept_id",
    "route_source_value",
    "dose_unit_source_value",
)


def _start_date(version: ProtocolVersion, item: dict[str, Any]) -> date:
    """Date of the first version of the unbroken run, up to `version`, holding `item`.

    The item is identified by equality of its stored fields. An item that is in version 1
    starts at `in_effect_since` when set and not after v1's creation date; every other first version contributes its own
    `created_at` (UTC date). A later version that merely repeats the item moves nothing.
    """
    first = version
    earlier = version.protocol.versions.filter(number__lt=version.number)
    for prior in earlier.order_by("-number"):
        if item not in prior.snapshot["interventions"]:
            break
        first = prior
    created = first.created_at.astimezone(UTC).date()
    since = version.protocol.in_effect_since
    # A Draft edit does not check the date, so a future one is never trusted.
    if first.number == 1 and since is not None and since <= created:
        return since
    return created


def intervention_to_omop_drug_exposure(
    version: ProtocolVersion, index: int
) -> dict[str, Any]:
    """Map intervention `index` of a stored version to a DRUG_EXPOSURE-shaped dict.

    `drug_source_value` and `dose_unit_source_value` are the stored text unchanged.
    The amount and the schedule go to no column (see the mapping document).
    """
    item = version.snapshot["interventions"][index]
    row: dict[str, Any] = dict.fromkeys(DRUG_EXPOSURE_COLUMNS)
    row["drug_exposure_start_date"] = _start_date(version, item)
    row["drug_source_value"] = item["name"]
    row["dose_unit_source_value"] = item["unit"] or None
    return row
