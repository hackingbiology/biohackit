# SPDX-License-Identifier: AGPL-3.0-or-later
"""LabReport -> FHIR R4 collection Bundle (hand-written, pure apart from reading rows).

Element names and the source field of each are listed in
docs/fhir/lab-report-mapping.md. An element with no stored source is not emitted;
no placeholder and no default is ever invented. Values stay `Decimal` here so that
nothing is rounded; `render_fhir_json` writes them as exact JSON numbers.
"""

import json
import re
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from core.models import LabReport, LabResult

LOINC_SYSTEM = "http://loinc.org"
UCUM_SYSTEM = "http://unitsofmeasure.org"
REPORT_LABEL = "Laboratory report"
# Stable namespace so the same stored row always gives the same urn:uuid.
_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://biohack.it/fhir/lab-report")
_DECIMAL_MARK = "\x00dec:"  # NUL is refused in every stored text field


def _urn(kind: str, key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(_NAMESPACE, f'{kind}/{key}')}"


def _instant(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def _quantity(result: LabResult) -> dict[str, Any]:
    quantity: dict[str, Any] = {"value": result.reported_value}
    if result.reported_unit_ref is not None:
        quantity["system"] = UCUM_SYSTEM
        quantity["code"] = result.reported_unit_ref.ucum_code
    else:
        quantity["unit"] = result.reported_unit
    return quantity


def _observation(
    result: LabResult, organization_urns: dict[str, str]
) -> dict[str, Any]:
    observation: dict[str, Any] = {
        "resourceType": "Observation",
        "status": "unknown",
        "code": {
            "coding": [{"system": LOINC_SYSTEM, "code": result.biomarker.loinc_code}]
        },
        "valueQuantity": _quantity(result),
    }
    if result.collected_at is not None:
        observation["effectiveDateTime"] = _instant(result.collected_at)
    if result.reported_at is not None:
        observation["issued"] = _instant(result.reported_at)
    if result.method:
        observation["method"] = {"text": result.method}
    if result.laboratory:
        observation["performer"] = [{"reference": organization_urns[result.laboratory]}]
    return observation


def lab_report_to_fhir_bundle(report: LabReport) -> dict[str, Any]:
    """One DiagnosticReport whose `result` references one Observation per LabResult,
    plus an Organization (name only) per distinct laboratory, in a collection Bundle."""
    results = list(
        LabResult.objects.filter(report=report)
        .select_related("biomarker", "reported_unit_ref")
        .order_by("pk")
    )
    organization_urns: dict[str, str] = {}
    for result in results:
        if result.laboratory and result.laboratory not in organization_urns:
            organization_urns[result.laboratory] = _urn(
                "organization", f"{report.pk}/{result.laboratory}"
            )
    observation_urns = [_urn("observation", str(r.pk)) for r in results]
    entries: list[dict[str, Any]] = [
        {
            "fullUrl": _urn("diagnosticreport", str(report.pk)),
            "resource": {
                "resourceType": "DiagnosticReport",
                "status": "unknown",
                "code": {"text": REPORT_LABEL},
                "result": [{"reference": urn} for urn in observation_urns],
            },
        }
    ]
    entries.extend(
        {"fullUrl": urn, "resource": _observation(r, organization_urns)}
        for urn, r in zip(observation_urns, results, strict=True)
    )
    entries.extend(
        {
            "fullUrl": urn,
            "resource": {"resourceType": "Organization", "name": name},
        }
        for name, urn in organization_urns.items()
    )
    return {"resourceType": "Bundle", "type": "collection", "entry": entries}


def _without_padding(value: Decimal) -> Decimal:
    """Drop trailing zeros on the digit tuple (as LabResult does): the column pads to
    6 decimals and FHIR counts decimal digits as significant. Not `normalize()`,
    which can round."""
    sign, digits, exponent = value.as_tuple()
    if not isinstance(exponent, int):
        return value
    if not any(digits):
        return Decimal(0)
    trailing = next((i for i, d in enumerate(reversed(digits)) if d), 0)
    if trailing and exponent < 0:
        keep = min(trailing, -exponent)
        return Decimal((sign, digits[:-keep], exponent + keep))
    return value


def _encode(value: Any) -> Any:
    if isinstance(value, Decimal):
        return f"{_DECIMAL_MARK}{_without_padding(value):f}"
    raise TypeError(f"not JSON serialisable: {type(value).__name__}")


def render_fhir_json(bundle: dict[str, Any]) -> str:
    """JSON text of the bundle with every Decimal written as an exact number."""
    text = json.dumps(bundle, default=_encode, sort_keys=True)
    return re.sub(r'"\\u0000dec:(-?[0-9.]+)"', r"\1", text)
