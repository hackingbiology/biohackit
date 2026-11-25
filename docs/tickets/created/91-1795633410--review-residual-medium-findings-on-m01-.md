# [review] Residual medium findings on m01-tg3-coded-analyte-registry

Labels: autodev

[
 {
  "file": "backend/core/models.py",
  "line": 58,
  "severity": "medium",
  "claim": "Biomarker.save() and Measurement.save() accept a whitespace-only LOINC code, so an uncoded analyte can be stored and treated as coded. Migration 0004 has the same gap.",
  "fix": "Use `if not (self.loinc_code or '').strip():` in Biomarker.save, Measurement.save and the 0004 map_units check. Add a test with loinc_code='  '. The suggested CheckConstraint is optional hardening.",
  "confirmed": true,
  "reason": "models.py:58 uses `if not self.loinc_code`, models.py:85 uses `not analyte.loinc_code`, and 0004:25 uses `not r.loinc_code`. None of them strip, so '   ' counts as coded. 0005 only makes the field non-null and unique, with no blank constraint."
 },
 {
  "file": "backend/core/migrations/0004_coded_biomarker_data.py",
  "line": 26,
  "severity": "medium",
  "claim": "The data step does not check for duplicate legacy LOINC codes. Migration 0005 then adds UNIQUE, so the operator gets a raw IntegrityError with no row ids instead of the loud row-naming error the task requires.",
  "fix": "In map_units, group rows by loinc_code and add a problem entry such as `duplicate loinc_code: ids [...]` before raising. Add a unit test with two rows sharing a code that asserts both ids appear in the error message.",
  "confirmed": true,
  "reason": "0001_initial.py:56 defines loinc_code as nullable with no unique constraint, so legacy duplicates are possible. 0004 only checks for empty codes (line 25) and unknown units, and 0005 makes the field unique. A duplicate would fail at the DB with no row ids."
 }
]
