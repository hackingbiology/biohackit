# M02 lab report API (manual entry)

Authenticated (JWT) endpoints under `/api/labs/`. A typed report uses the same
`LabReport` / `LabResult` models and `save` rules as an import, so a typed value gets the
same provenance fields, unit normalisation, validation state and aggregation
eligibility. Spec: `biomarkers-and-labs` "Manual entry of equal standing".

## Browser access

The API accepts either a JWT (`Authorization: Bearer ...`) or the browser sign-in session
cookie. A session request that changes data (POST, PATCH, DELETE) must also send the
`X-CSRFToken` header with the value of the `csrftoken` cookie, otherwise the answer is `403`
and nothing is stored. A request with no valid credentials is still refused with `401`.

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

## `GET /api/labs/reports/<id>/omop/`

The report's results as OMOP CDM v5.4 MEASUREMENT-shaped rows (JSON only, no CSV yet):
`{"omop_cdm_version": "5.4", "columns": [...], "rows": [...]}`. `columns` is the DDL order
(`core.omop.MEASUREMENT_COLUMNS`); there is one row per result, ordered by result id, each built
only by `lab_result_to_omop_measurement` with every column present. Retracted results are not
exported; disputed and entered ones are (the export is the owner's own data, Q80). Every
`*_concept_id`, `person_id` and other column without a stored, cited source is `null`: no
vocabulary content is stored, so none is invented (Q69). `404` for another user's report;
`401`/`403` when not signed in. Column sources: docs/omop/measurement-mapping.md.

## `GET /api/labs/results/<id>/convert/?unit=<ucum>`

Shows one of your results in the UCUM unit you name. The original value and unit are always
kept and always returned; nothing is written. `unit` is required, at most 64 characters, and
must be a stored UCUM code (otherwise `400` naming `unit`). Response:
`{result_id, reported_value, reported_unit, value, unit, converted, reason, conversion_source}`;
decimals are strings, not rounded.

- `converted: true`: a stored, sourced conversion exists (an analyte-specific one is preferred);
  `value` is `reported_value` times its factor, `unit` is the requested unit and
  `conversion_source` is the stored Source (`id, name, version, licence, url, retrieved_at`).
- `converted: false, reason: "same_unit"`: the requested unit is the reported one.
- `converted: false, reason: "no_conversion_known"`: no stored direct conversion (an inverse or
  a chain is never used) or the reported unit is not stored; `value`/`unit` are the reported
  ones.

Retracted results can still be viewed by their owner (Q81). `404` for another user's result;
`401`/`403` when not signed in.

## `GET /api/labs/results/<id>/ranges/`

Places one of your results against three separate ranges, never merged:
`{result_id, reported_value, reported_unit, reference_range, optimal_range, safety_threshold,
comparison_value, comparison_unit, converted, conversion_source}`. Each range object has `status` and, when a range applies,
`low`, `high` (decimal strings, `null` = open), `unit` and `source` (`name, version, url`).

- Comparison value: `reported_value` if reported in the analyte's unit, else the stored
  `normalised_value` (only when it is in that unit), else none. Nothing is converted on the fly. `converted` is `true` when the stored normalised
  value was used; `conversion_source` is then that stored Source (`name, version, url`), else `null`.
  A lab+method tier is chosen only among rows that apply to the subject, so a stratified
  lab-specific row never hides a generic row.
- Status rule: `below` if value < low, `above` if value > high, `inside` otherwise (bounds
  inclusive, a null bound is open); `no_range` if none applies (no bounds returned);
  `not_comparable` (`reason: "no_value_in_analyte_unit"`) when there is no comparison value.
- `reference_range` adds `lab, method, population, evidence_grade`. Only rows in the analyte's
  unit whose lab and method are empty or equal (trimmed, casefolded) to the result's apply;
  rows matching lab and method beat generic ones; a tie gives `no_range`.
- `optimal_range` is shown only if `displayable_optimal_range` passes (source, population,
  endpoint, evidence grade and last-reviewed date all present); it adds `population, endpoint,
  evidence_grade, last_reviewed`.
- `safety_threshold`: exactly one row is used; several give `no_range` with
  `reason: "ambiguous_several_thresholds"`.

The subject is unknown (no age, sex or ancestry stored), so only unstratified rows apply (Q82).
Retracted results can still be viewed by their owner. `404` for another user's result;
`401`/`403` when not signed in.

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

### `GET /api/labs/reports/<id>/phenoage/?age_years=<number>`

PhenoAge (Levine 2018) computed from the nine analytes of one of your reports (TG-i part 2).
`age_years` is a request parameter and is never stored (Q79); a missing value, or one that is not a
finite number or is too large to fit one (for example `1e400`), is `400` naming `age_years`. Another user's or a missing report is `404`; anonymous is 401/403.
Each analyte is found by the LOINC code of its biomarker; `retracted` and `disputed` results are
ignored. The value is used as is when its UCUM unit equals the PhenoAge unit, otherwise only a
stored unit conversion is applied. Nothing is written.

`200` with the result: `{"phenoage_years", "mortality_score", "xb", "constants_version",
"inputs": [{"field", "lab_result_id", "value", "unit", "converted"}], "method"}`; or `200` with
`{"refusal": {"reason", "field"}}`. Reasons: `analyte_not_mapped` (no verified LOINC code for
the analyte; **currently every analyte, see Q79**), `missing_input`, `ambiguous_analyte` (two
usable results for one analyte), `unit_not_convertible` (no stored conversion), and the engine's
`not_finite_input`, `crp_not_positive`, `mortality_score_out_of_range`.

### `GET /api/labs/reports/<id>/calculated/`

Calculated quotient markers for one of your reports (TG-n part 1). Each stored
`CalculatedRatioDefinition` (numerator and denominator analyte, the UCUM unit each input must be
in, and a cited Source) is computed in code with `Decimal` (28 digits, half-even, not rounded).
No definition is seeded (Q83), so until some are stored the answer is
`{"report_id", "markers": [], "note": "no_definitions_stored"}`. Another user's or a missing
report is `404`; anonymous is 401/403. Only this report's results are used; `retracted` and
`disputed` results are ignored; a value is used as reported when its unit matches, otherwise only
a stored unit conversion applies. Nothing is written.

Each marker has `name`, `calculated: true` and `source`. Computed: `status: "computed"`, `value`
(string), `unit_note` (the two input units; no unit is invented for the ratio) and `inputs`
(`role`, `lab_result_id`, `loinc_code`, `value_used`, `unit_used`, `reported_value`,
`reported_unit`, `collected_at`, `reported_at`, `converted`, `conversion_source` — the stored conversion's Source, null when not converted). Otherwise `status: "not_computable"`,
`value: null` and `reasons`: `missing_input:<role>`, `ambiguous_input:<role>`,
`unit_not_convertible:<role>`, `denominator_zero`.

### `GET /api/labs/completeness/`

Completeness and freshness per organ system (TG-h part 1). Each stored `OrganSystemPanel` (a name,
its expected analytes and a cited Source) is listed, ordered by name. No panel is seeded (Q84),
so until some are stored the answer is `{"panels": []}`. Anonymous is 401/403. Only your own
results count, across all of your reports; `retracted` and `disputed` results are ignored.
Nothing is written.

Each panel has `name`, `source`, `expected_count`, `present_count`, `present` and `missing`
(`biomarker_id`, `loinc_code`), `last_collected_at` (newest `collected_at`, else `reported_at`;
null when no present result has a date), `age_days` (whole days from that date to now, or null) and
`sparse` (true when `present_count < expected_count`). A panel with no expected analytes is 0/0,
not sparse, with a null date.

## `GET|POST /api/auth/me/erase/` (account erasure)

Owner-only (JWT). `GET` returns the plain-language notice (copies already cloned by others are outside the instance's control), what is deleted, and the two choices; `keep_for_research` is marked `available: false` with its reason.

`POST` with `choice` = `delete_everything` and `confirm` = `true` deletes the user, profile, lab reports, results, measurements and the retained original files in one transaction (files are removed once it commits). Without `confirm` true, or with an unknown choice: 400, nothing deleted. `keep_for_research`: 409 "de-identification not implemented yet", nothing deleted. Unauthenticated: 401. Defaults: Q85.

## `POST /api/labs/imports/getbased/preview/` (get-based archive preview)

Owner-only (JWT, then session with CSRF, as the CSV import). Multipart `file` (at most 5 MiB) and optional `profile_id`. Reads a plain-JSON get-based single-client export or all-clients bundle, both `version` 2 (`docs/ecosystem/getbased-archive-format.md`). **Stores nothing**: no report, no result, no retained original; the archive content is not logged.

A bundle with several profiles and no `profile_id` returns `{"status": "choose_profile", "profile_ids": [...]}` and no rows. Otherwise `{"status": "preview", "rows": [...], "summary": {...}, "can_confirm": bool}`. Each row: `marker`, `value` (exact text, `0.10` stays `0.10`), `date`, `status` (`matched` | `not_recognised` | `not_imported`), `reason`, and for a matched row `loinc_code`, `unit` (UCUM), `mapping_source`, `mapping_source_url` and `unit_source` (`path@sha` of the get-based catalogue unit), plus `flags` (AI-read, may be AI-read, origin not shown, origin unknown, edited in get-based after import; model and provider are entry-level and qualified). Matching is only through a stored `GetbasedMarkerMapping` row, never by name; with an empty table every marker is "not recognised". `can_confirm` is true only with no not recognised row and at least one matched row; left-out rows (deleted, calculated) are counted in `summary` and do not block.

400: not UTF-8, not JSON, `labcharts-backup`, `getbased-migration`, a version other than 2, an unknown `profile_id`, or a file over the bound; the message names the found format/version and the supported ones. Unauthenticated: 401. Defaults: Q100.
