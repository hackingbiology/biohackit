# LabResult → OMOP CDM MEASUREMENT mapping

Implemented by `lab_result_to_omop_measurement` in `backend/core/omop.py` (pure function, no DB writes).

## DDL source

- File: `inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql`, table `MEASUREMENT` (lines 161–184)
- URL: https://raw.githubusercontent.com/OHDSI/CommonDataModel/v5.4.0/inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql
- Tag `v5.4.0`, commit `dd85c0d30bb3dd4bd16c5dbef7dbf9dd93075fa2` (api.github.com/repos/OHDSI/CommonDataModel/git/ref/tags/v5.4.0)
- Fetched 2026-11-26 with `curl -s`. Licence Apache-2.0 (docs/ecosystem/m02-blood-layer.md).
- The latest release is v5.5.0 (CDM v5.5), which adds `value_as_source_concept_id` to MEASUREMENT. We target v5.4 as specified; that column is not exported.

## Rules

- No OMOP vocabulary content is stored in git, so no integer `*_concept_id` is ever produced (Q69). The LOINC code and the reported unit go to the `*_source_value` columns instead.
- A column without a stored, cited source is `None`. This includes the NOT NULL columns `person_id`, `measurement_concept_id` and `measurement_type_concept_id`: the mapper returns `None` and never a default; the exporter that fills them (TG-j) must supply them from a cited source or refuse the row.
- Date and time come from `collected_at` only, converted to UTC. `reported_at` is never used. With no `collected_at`, `measurement_date` (NOT NULL in the DDL) is `None`.
- `value_as_number` is the normalised value and `unit_source_value` is then `LabResult.normalised_unit`, so the number and its unit always agree. When the result is not normalised, `value_as_number` is `None` and `unit_source_value` is the as-reported unit (the as-reported number is in `value_source_value`).
- `value_source_value` is the stored `reported_value` as plain decimal text. The column is `numeric(20,6)`, so a row read from the database has scale 6 (e.g. `5.500000` for a reported `5.500`); the value is exact, only trailing zeros are added.
- No truncation: `*_source_value` columns are `varchar(50)`; an exporter must handle a longer value (e.g. a unit up to 64 characters).

## Columns (DDL order)

| Column | DDL type | Source field |
|---|---|---|
| `measurement_id` | integer NOT NULL | `LabResult.pk` (None if unsaved) |
| `person_id` | integer NOT NULL | none (left empty) |
| `measurement_concept_id` | integer NOT NULL | none (left empty) |
| `measurement_date` | date NOT NULL | `LabResult.collected_at` (UTC date); none if no collected time |
| `measurement_datetime` | TIMESTAMP NULL | `LabResult.collected_at` (UTC, naive); none if no collected time |
| `measurement_time` | varchar(10) NULL | `LabResult.collected_at` (UTC, `HH:MM:SS`) |
| `measurement_type_concept_id` | integer NOT NULL | none (left empty) |
| `operator_concept_id` | integer NULL | none (left empty) |
| `value_as_number` | NUMERIC NULL | `LabResult.normalised_value`; none if not normalised |
| `value_as_concept_id` | integer NULL | none (left empty) |
| `unit_concept_id` | integer NULL | none (left empty) |
| `range_low` | NUMERIC NULL | none (left empty) |
| `range_high` | NUMERIC NULL | none (left empty) |
| `provider_id` | integer NULL | none (left empty) |
| `visit_occurrence_id` | integer NULL | none (left empty) |
| `visit_detail_id` | integer NULL | none (left empty) |
| `measurement_source_value` | varchar(50) NULL | `LabResult.biomarker.loinc_code` |
| `measurement_source_concept_id` | integer NULL | none (left empty) |
| `unit_source_value` | varchar(50) NULL | `LabResult.normalised_unit` when normalised, else `LabResult.reported_unit` |
| `unit_source_concept_id` | integer NULL | none (left empty) |
| `value_source_value` | varchar(50) NULL | `LabResult.reported_value` as plain decimal text (stored scale 6) |
| `measurement_event_id` | bigint NULL | none (left empty) |
| `meas_event_field_concept_id` | integer NULL | none (left empty) |

## Export endpoint

`GET /api/labs/reports/<id>/omop/` (owner only) returns the mapper output of every non-retracted result of a report, in result id order, with `omop_cdm_version` `5.4` and the column list above. It adds nothing to the mapper: the NOT NULL columns `person_id`, `measurement_concept_id` and `measurement_type_concept_id` stay `null`, so the rows are not loadable into an OMOP database until a cited source for them exists (Q69, Q80). See docs/api-labs.md.
