# Seed files

`manage.py seed_reference [--dir PATH]` loads every `*.json` file in this directory
(sorted by name). No data file is committed yet: UCUM units arrive in M01 TG5 part B,
once the UCUM licence (Q9) is verified from the source.

## Format

```json
{"rows": [
  {"model": "unit",
   "source": {"name": "...", "version": "", "licence": "...", "url": "...", "retrieved_at": "2026-11-25"},
   "fields": {"ucum_code": "...", "display": "..."}},
  {"model": "unit_conversion",
   "source": {"...": "..."},
   "fields": {"from_unit": "<ucum_code>", "to_unit": "<ucum_code>", "factor": "0.01", "biomarker": null}}
]}
```

- `model` is `unit`, `unit_conversion` or `getbased_marker_mapping`; unknown models, unknown or missing fields are errors.
- `source.name`, `licence`, `url`, `retrieved_at` (ISO date) are mandatory and non-blank;
  `version` is optional (stored as `""`).
- `factor` is a string, parsed as `Decimal`, never as a float. It must be > 0, have at most
  12 decimal places and at most 18 integer digits (the column limits); nothing is rounded.
- `ucum_code`, `display`, `from_unit`, `to_unit` and a non-null `biomarker` must be non-blank
  strings within the column length limits. `source.version` must be a string if present.
- `from_unit`/`to_unit` must already exist (earlier row or earlier file); `biomarker` is a
  `loinc_code` that must already exist, or `null`. Nothing is auto-created.

## get-based marker mapping rows

No mapping rows are committed (Q91): no LOINC code can be verified here. Each row must
cite the get-based catalogue file at a pinned commit (see
`docs/ecosystem/getbased-archive-format.md`). Placeholders only:

```json
{"model": "getbased_marker_mapping",
 "source": {"...": "..."},
 "fields": {"getbased_key": "<getbased marker key>", "kind": "measured",
            "biomarker": "<loinc_code>", "unit": "<ucum_code>",
            "unit_source_path": "<catalogue file path>",
            "unit_source_commit": "<40-hex commit>"}},
{"model": "getbased_marker_mapping",
 "source": {"...": "..."},
 "fields": {"getbased_key": "calculatedRatios.<name>", "kind": "calculated",
            "biomarker": null, "unit": null,
            "unit_source_path": null, "unit_source_commit": null}}
```

- Same rules as `core.GetbasedMarkerMapping`: `measured` needs an existing `biomarker`
  (`loinc_code`) and may not use a `calculatedRatios.` key; `calculated` has null
  biomarker, unit, path and commit. The unit, path and commit are all set or all null;
  the commit is 40 lowercase hex. `unit` is the `ucum_code` of an existing Unit.
- A measured row without a unit citation loads as is (the preview shows it as "not
  recognised: unit not verified"); `inspect_seed_dir` reports it as a warning.
- Upsert by `getbased_key`.

## Behaviour

- Upsert by natural key: Source `(name, version)`, Unit `ucum_code`, UnitConversion
  `(from_unit, to_unit, biomarker)`. Running twice changes nothing.
- A file is validated completely before writing, then written in one transaction: a bad
  row means nothing from that file is committed. Files processed earlier in the same run
  stay committed. A database error is reported with the file and row too.
- A Source `(name, version)` that already exists (in the DB or earlier in the run) is never
  modified: a row whose licence, url or retrieved_at differs is refused. Change provenance
  by using a new `version`.
- A restricted filename (see below) in the directory aborts the run before any write.
  Errors read like `units.json row 3: missing source.licence`.

## Licence rule

Only openly licensed or explicitly permitted content, with the licence recorded in each
row's Source. Never SNOMED or the full LOINC table (Q9, Q10); `inspect_seed_dir`
(used by the command's tests) flags `Loinc.csv`, `LoincTable*`, `*Snomed*`, `sct2_*`, `der2_*`.
