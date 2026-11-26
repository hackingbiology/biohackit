# M02 lab report API (manual entry)

Authenticated (JWT) endpoints under `/api/labs/`. A typed report uses the same
`LabReport` / `LabResult` models and `save` rules as an import, so a typed value gets the
same provenance fields, unit normalisation, validation state and aggregation
eligibility. Spec: `biomarkers-and-labs` "Manual entry of equal standing".

## `POST /api/labs/reports/`

Creates a report with `origin = manual`, owned by the caller, and all its results in one
transaction.

```json
{
  "laboratory": "optional, applies to results that name none",
  "results": [
    {
      "loinc_code": "required, must be a stored analyte",
      "reported_value": "required, decimal as a string, at most 6 decimals",
      "reported_unit": "required, as the lab reported it",
      "laboratory": "optional", "method": "optional", "device": "optional",
      "collected_at": "optional ISO 8601 with UTC offset",
      "reported_at": "optional ISO 8601 with UTC offset"
    }
  ]
}
```

- `201` with the report and its results. Each result has the stored fields,
  `validation_state` (`unreviewed`), `aggregation_eligible` (true only with laboratory
  and method), `normalised_value` / `normalised_unit` (empty unless a stored conversion
  exists) and `plausibility`.
- `400` if any result is invalid (unknown LOINC code, more than 6 decimals, DEXA or
  microbiome without laboratory and method, naive time, ...). The body names the result
  index and field, e.g. `{"results": {"1": {"reported_value": ["..."]}}}`; nothing is stored.
- `401` when not logged in.

## `GET /api/labs/reports/<id>/`

The report with its results. `404` for a report owned by someone else.

## Plausibility

`plausibility = {"status": "within" | "outside" | "not_checked", "range_source": {...} | null}`.
It compares the value only with a stored, cited `ReferenceRange` of the same analyte whose
unit equals the reported unit (or the normalised unit). Only a single range without age,
sex, ancestry or population strata, and whose lab and method are empty or equal to the result's, is used; otherwise the status is `not_checked`. It is a flag: the
value is stored in every case. No range is invented or seeded (Q70).
