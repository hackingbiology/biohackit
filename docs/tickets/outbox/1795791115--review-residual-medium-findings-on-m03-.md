# [review] Residual medium findings on m03-tga-substance-codes-and-omop-pause-fix

Labels: autodev

[
 {
  "file": "backend/substances/services.py",
  "line": 155,
  "severity": "medium",
  "claim": "PATCH of a code's code/system/source without fetched_on keeps the old fetch date, so the new value is stored with a date never recorded for it.",
  "fix": "In update_code, require fetched_on in the data whenever code, system or source is sent (400 otherwise). Do the same in update_substance for the class fields and class_fetched_on. Add a test.",
  "confirmed": true,
  "reason": "Read services.py:155-171. `merged` seeds fetched_on from the stored row and then applies `**data`, so a body with only `source` or `code` passes clean_code and keeps the old date. update_substance and clean_class (lines 56-73, 120-136) merge with `current` in the same way, so the class fields have the same problem. The fetch date then no longer matches the changed code or source, which weakens the provenance the spec requires."
 },
 {
  "file": "backend/substances/services.py",
  "line": 31,
  "severity": "medium",
  "claim": "_text does not refuse NUL characters, so a staff request with \\x00 in a text field reaches PostgreSQL and fails as a 500 instead of a 400.",
  "fix": "In _text, raise SubstanceError({key: 'Enter text.'}) when '\\x00' is in the value, and add a test case that expects 400.",
  "confirmed": true,
  "reason": "Read _text at services.py:31-40, which has no NUL check. grep for x00 in backend/substances returns nothing, while backend/protocols/services.py:47, :66 and :76 guard against it on purpose. Only SubstanceError is mapped to a 400. PostgreSQL cannot store NUL in text, so the database error would escape. I did not run the request, so the 500 itself is inferred from PostgreSQL behaviour."
 }
]
