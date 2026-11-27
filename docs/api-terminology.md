# Terminology API

Read-only endpoints under `/api/terminology/`. Source: `backend/terminology/views.py`, `backend/terminology/serializers.py`, `backend/terminology/urls.py`. Both use the default authentication of the API (JWT or the browser session cookie), so a request with no valid credentials is refused with `401`.

## `GET /api/terminology/loinc/?q=<text>`

Searches the imported LOINC terms by name words or by LOINC code. Throttled per scope `loinc_search` (default `60/min`, `LOINC_SEARCH_THROTTLE_RATE`); over the limit: `429`.

- `q` is required, at most 200 characters after trimming. A missing, empty or too long `q`: `400` with a message under `q`.
- Paginated: `page`, and `page_size` (default 20, at most 100).
- `200` lists terms, each with `loinc_num`, `long_common_name`, `short_name`, `component`, `system`, `property`, `scale_type`, `status` and `source` (`name`, `version`, `licence`, `url`, `retrieved_at`).

## `GET /api/terminology/biomarkers/<loinc_code>/ranges/`

Returns the ranges of one analyte, kept as three separate keys, each with its source: `reference`, `optimal` and `safety`, plus `biomarker` (`loinc_code`, `name`, `unit` as a UCUM code) and `value`. `optimal` is `null` unless its provenance is complete. Only `GET`, `HEAD` and `OPTIONS` are allowed.

- Optional `?value=<decimal>`: each range then carries a `status` computed in code. The value is taken to be in the analyte's unit; no unit conversion is done. A value that is not a finite decimal: `400` with a message under `value`.
- An unknown `loinc_code`: `404`.
