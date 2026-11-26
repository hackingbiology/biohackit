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
  `validation_state` (`entered`), `aggregation_eligible` (true only with laboratory,
  method and a confirmed state, see below), `normalised_value` / `normalised_unit` (empty unless a stored conversion
  exists) and `plausibility`.
- `400` if any result is invalid (unknown LOINC code, more than 6 decimals, DEXA or
  microbiome without laboratory and method, naive time, ...). The body names the result
  index and field, e.g. `{"results": {"1": {"reported_value": ["..."]}}}`; nothing is stored.
- `401` when not logged in.

### Input limits

- `reported_value` is at most **40 characters** (after trimming); longer gives a 400 naming
  `reported_value` and the result index.
- A report holds at most **200 results**; more gives a 400 naming `results`, before anything is stored.

These are abuse protection, not scientific limits: a 20-digit value with 6 decimals needs far
fewer than 40 characters. In both cases nothing is stored. Defaults are open in Q70.

## `GET /api/labs/reports/<id>/`

The report with its results. `404` for a report owned by someone else.

## `GET /api/labs/reports/<id>/fhir/`

The report as a FHIR R4 `collection` Bundle (`application/fhir+json`): one DiagnosticReport whose
`result` references one Observation per result, plus an Organization (name only) per distinct
laboratory. Each Observation has the LOINC code and the value as reported (a JSON number, not
rounded). `valueQuantity` has `system` `http://unitsofmeasure.org` and `code` only when the
reported unit exactly equals a stored `Unit.ucum_code`; otherwise only `unit` text. `method`,
`performer` (laboratory), `effectiveDateTime` (collected) and `issued` (reported) appear only
when stored. `status` is `unknown` and no patient is referenced (Q73). `404` for another user's
report; `401`/`403` when not signed in. Element sources: docs/fhir/lab-report-mapping.md.

## Plausibility

`plausibility = {"status": "within" | "outside" | "not_checked", "range_source": {...} | null}`.
It compares the value only with a stored, cited `ReferenceRange` of the same analyte whose
unit equals the reported unit (or the normalised unit). Only a single range without age,
sex, ancestry or population strata, and whose lab and method are empty or equal to the result's, is used; otherwise the status is `not_checked`. It is a flag: the
value is stored in every case. No range is invented or seeded (Q70).

## CSV import (two steps)

Header (UTF-8, comma-separated): `loinc_code,value,unit,collected_at,reported_at,laboratory,method`.
The first three columns are required; the last four are optional. Any other or duplicate column
rejects the whole file with a `400` naming the header. Empty cells are treated as absent.
Rows go through the same rules as manual entry. Nothing is guessed (Q71).

### `POST /api/labs/imports/csv/preview/`

Multipart field `file`. Stores nothing. Returns
`{"rows": [{"row": 1, "status": "recognised" | "not_recognised", "reason": "", "loinc_code", "value", "unit", "plausibility"}]}`
with `row` the 1-based data line. `not_recognised` carries a reason naming the column (unknown
LOINC code, empty unit, bad number, time without UTC offset, ...) and `plausibility` null. The
status `inferred` exists in the review vocabulary but this parser never emits it.

### `POST /api/labs/imports/csv/confirm/`

Same file again, plus an optional `laboratory` form field for the report. If any row is
`not_recognised` the answer is `400` with `detail` and the `rows`, and nothing is stored.
Otherwise one `LabReport` (`origin = import`, `import_name` = file name) and its results are
stored in one transaction, with `validation_state = user_confirmed` (you checked every row in
the preview); `201` with the report and results.

The report JSON (confirm, `GET /api/labs/reports/<id>/`) carries `original_retained` (bool),
`original_sha256` and `original_size` (bytes). The uploaded CSV is kept exactly as sent, in a
private store under a generated name (never your file name), with no automatic expiry (Q57).
It is never served, published or put into OpenData: no endpoint returns the file, a path or a
URL. `DELETE /api/labs/reports/<id>/` removes the file after the rollback commits (Q65). If you
send `redact_terms`, the original is **not** kept (it would defeat the redaction): the confirm
answer has `original_retained: false` and `original_not_retained_reason` (Q76). The preview
never stores a file; a refused confirm leaves none.

### Validation states and `PATCH /api/labs/results/<id>/validation/`

| State | Meaning |
|---|---|
| `entered` | typed or imported, not yet checked (typed entries start here) |
| `user_confirmed` | the user checked it against their own report |
| `source_verified` | the original document is attached and the value matches it (deterministic extraction or a second person) |
| `disputed` | flagged as possibly wrong |
| `retracted` | withdrawn by the user, excluded from statistics, kept for audit |

A result is `aggregation_eligible` only with a laboratory, a method **and** the state
`user_confirmed` or `source_verified`. The owner changes the state with
`{"validation_state": "<state>"}`: `user_confirmed`, `disputed` or `retracted` give `200`
with the result as in `GET /api/labs/reports/<id>/`. `entered` and `source_verified` (no
attached-original check exists yet), and any change away from `retracted`, give `400` naming
`validation_state`. Another user's or a missing result gives `404`. Nothing changes on `400`/`404`.

### PII redaction (opt-in)

Off by default. Both import endpoints accept an optional `redact_terms`: the exact strings to
remove (your name, IDs), as repeated multipart fields, one JSON list, or a JSON array. At most
20 terms, each 1..200 characters and not blank; a breach gives `400` naming `redact_terms` and
nothing is stored. Matching is exact and case-insensitive. Overlapping or adjacent matches merge into one
removal (one placeholder) naming the term with the longest match, so no part of a longer
match is kept. There are no built-in patterns (Q72). Each removal becomes `[REDACTED]`. The
terms may match at most 1000 places in a file, otherwise `400` naming `redact_terms`. Row
count and field lengths are checked on the raw file before redaction runs (`400` naming `file`).
If a cell only exceeds its limit because `[REDACTED]` is longer than the term, the `400` names
`redact_terms`. Cells are trimmed before they are checked and redacted, so offsets are relative to the trimmed cell.

Redaction is applied cell by cell to the data rows, to the file name (`import_name`) and to the
`laboratory` form field, before the rows are evaluated; the header is not touched. The preview
answers `redaction: {"applied": bool, "removals": [{"row", "column", "term_index", "start",
"end", "line", "replacement"}]}`. `row` is the data line (null for the file name and form
field), `start`/`end`/`line` locate the match inside that field, and `term_index` is the
position in your list. The removed text is never echoed back. Confirm re-applies the same terms,
so only the placeholder is stored. A term that hits `loinc_code`, `value`, `unit`, `collected_at`
or `reported_at` makes that row `not_recognised` naming the column (a value is never silently
changed), so confirm refuses. Without `redact_terms`, `applied` is `false` and nothing changes.

### Limits (`400` naming the limit, nothing stored)

File at most 1 MiB; at most 200 data rows; each field at most its model length (`value` 40
characters); the file must be UTF-8.

### `DELETE /api/labs/reports/<id>/`

Rolls back an import: removes the report and its results, nothing else. `204`; `404` for another
user's report; `409` for a manual report. The retained original file is not stored yet (TG-g).
