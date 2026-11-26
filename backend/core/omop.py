# SPDX-License-Identifier: AGPL-3.0-or-later
"""LabResult -> OMOP CDM v5.4 MEASUREMENT row (pure, no DB access).

Columns and order are those of the official v5.4.0 DDL; see
docs/omop/measurement-mapping.md for the source of every column. A column with
no stored, cited source is None: no concept id and no default is ever guessed.
"""

from datetime import UTC
from typing import Any

from core.models import LabResult

OMOP_CDM_VERSION = "5.4"  # docs/omop/measurement-mapping.md, tag v5.4.0

MEASUREMENT_COLUMNS: tuple[str, ...] = (
    "measurement_id",
    "person_id",
    "measurement_concept_id",
    "measurement_date",
    "measurement_datetime",
    "measurement_time",
    "measurement_type_concept_id",
    "operator_concept_id",
    "value_as_number",
    "value_as_concept_id",
    "unit_concept_id",
    "range_low",
    "range_high",
    "provider_id",
    "visit_occurrence_id",
    "visit_detail_id",
    "measurement_source_value",
    "measurement_source_concept_id",
    "unit_source_value",
    "unit_source_concept_id",
    "value_source_value",
    "measurement_event_id",
    "meas_event_field_concept_id",
)


def lab_result_to_omop_measurement(result: LabResult) -> dict[str, Any]:
    """Map a stored LabResult to an OMOP MEASUREMENT-shaped dict (DDL order).

    Date and time come from `collected_at` only (UTC), never from `reported_at`.
    """
    row: dict[str, Any] = dict.fromkeys(MEASUREMENT_COLUMNS)
    row["measurement_id"] = result.pk
    collected = result.collected_at
    if collected is not None:
        utc = collected.astimezone(UTC)
        row["measurement_date"] = utc.date()
        row["measurement_datetime"] = utc.replace(tzinfo=None)
        row["measurement_time"] = utc.strftime("%H:%M:%S")
    row["value_as_number"] = result.normalised_value
    row["measurement_source_value"] = result.biomarker.loinc_code
    # unit_source_value must be the unit of value_as_number when that is set.
    normalised = result.normalised_value is not None and result.normalised_unit
    row["unit_source_value"] = (
        result.normalised_unit if normalised else result.reported_unit
    )
    row["value_source_value"] = format(result.reported_value, "f")
    return row
