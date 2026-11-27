# Protocol intervention → OMOP CDM DRUG_EXPOSURE mapping

Implemented by `intervention_to_omop_drug_exposure(version, index)` in `backend/protocols/omop.py` (pure function, no DB writes, no HTTP route). This is an **export target, not a storage schema**: protocols keep their interventions as validated facet items of an immutable `ProtocolVersion` (docs/ecosystem/m03-interventions-protocols.md, section (c)); nothing here is stored in DRUG_EXPOSURE form.

## DDL source

- File: `inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql`, table `DRUG_EXPOSURE` (lines 94–117)
- URL: https://raw.githubusercontent.com/OHDSI/CommonDataModel/v5.4.0/inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql
- Tag `v5.4.0`, commit `dd85c0d30bb3dd4bd16c5dbef7dbf9dd93075fa2` (api.github.com/repos/OHDSI/CommonDataModel/git/ref/tags/v5.4.0)
- Fetched 2026-11-27 with `curl -s`. Licence Apache-2.0 (docs/ecosystem/m02-blood-layer.md). Same pinned commit as docs/omop/measurement-mapping.md.

## Rules

- No OMOP vocabulary is loaded, so no integer `*_concept_id` is ever produced: `drug_concept_id`, `drug_source_concept_id`, `drug_type_concept_id` and `route_concept_id` are `None`. The stored name and unit go to the `*_source_value` columns, exactly as stored (no trimming beyond what the API stored, no case change, no truncation).
- A column without a stored value is `None`, also when the DDL says NOT NULL (`person_id`, `drug_concept_id`, `drug_exposure_end_date`, `drug_type_concept_id`). The function never takes a default; a row is not loadable into an OMOP database until a cited source for those exists (Q115).
- Start date: found from the first version of the unbroken run (up to the exported version) whose snapshot holds an identical intervention (same name, amount, unit, schedule). If that first version is version 1 and `Protocol.in_effect_since` is set and not after that version's creation date, it is `in_effect_since` (a Draft edit does not check the date, so a future one is ignored); otherwise it is the UTC date of that first version's `created_at`. An intervention added or edited in a later version therefore starts at that version, never at the protocol-level date, and a later version that repeats it unchanged moves nothing. The run also ends where an active version follows a non-active one (a resume): if an intervention runs active, is paused, then resumes, the exported version of the resumed run is dated from the version that resumed it, not from before the pause. A version in any state may be exported (a default, Q115, not a decision); a paused version, or several paused versions in a row, are dated from the start of the active run before the pause. Nothing else is used. `drug_exposure_start_datetime` is `None` because no start time is stored.
- End date: not stored, so `drug_exposure_end_date` and `drug_exposure_end_datetime` are `None`. It is not derived from cycles or from the schedule.
- Amount: goes to no column. `quantity` is the quantity dispensed and `days_supply` the supply in days, which are not the amount of one dose; the DDL has no dose-amount column. The amount stays in the stored version.
- Schedule: goes to no column. `sig` holds the directions printed on a prescription, and a free-text self-experiment schedule is not that. It stays in the stored version.
- `dose_unit_source_value` is `None` when no unit is stored (an intervention without an amount may have none).
- `*_source_value` columns are `varchar(50)` while a stored name or unit may be up to 500 characters: an exporter must handle a longer value; the function does not truncate.

## Columns (DDL order)

| Column | DDL type | Source |
|---|---|---|
| `drug_exposure_id` | integer NOT NULL | empty: no stored value |
| `person_id` | integer NOT NULL | empty: no stored value |
| `drug_concept_id` | integer NOT NULL | empty: no vocabulary loaded |
| `drug_exposure_start_date` | date NOT NULL | first version of the unbroken active run (a pause ends it): `in_effect_since` if it is v1, set and not after v1's creation date (a Draft edit does not check it, so a future date is ignored), else that version's UTC `created_at` date (see Rules) |
| `drug_exposure_start_datetime` | TIMESTAMP NULL | empty: no stored value |
| `drug_exposure_end_date` | date NOT NULL | empty: no stored value |
| `drug_exposure_end_datetime` | TIMESTAMP NULL | empty: no stored value |
| `verbatim_end_date` | date NULL | empty: no stored value |
| `drug_type_concept_id` | integer NOT NULL | empty: no vocabulary loaded |
| `stop_reason` | varchar(20) NULL | empty: no stored value |
| `refills` | integer NULL | empty: no stored value |
| `quantity` | NUMERIC NULL | empty: no stored value (the amount is not a dispensed quantity) |
| `days_supply` | integer NULL | empty: no stored value |
| `sig` | TEXT NULL | empty: no stored value (the schedule is not prescription directions) |
| `route_concept_id` | integer NULL | empty: no vocabulary loaded |
| `lot_number` | varchar(50) NULL | empty: no stored value |
| `provider_id` | integer NULL | empty: no stored value |
| `visit_occurrence_id` | integer NULL | empty: no stored value |
| `visit_detail_id` | integer NULL | empty: no stored value |
| `drug_source_value` | varchar(50) NULL | intervention `name`, as stored |
| `drug_source_concept_id` | integer NULL | empty: no vocabulary loaded |
| `route_source_value` | varchar(50) NULL | empty: no stored value |
| `dose_unit_source_value` | varchar(50) NULL | intervention `unit`, as stored; empty if none |
