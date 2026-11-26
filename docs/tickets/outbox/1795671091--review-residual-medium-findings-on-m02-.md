# [review] Residual medium findings on m02-tgd1-deterministic-pii-redaction

Labels: autodev

[
 {
  "file": "backend/core/lab_import.py",
  "line": 205,
  "severity": "medium",
  "claim": "If redaction makes a laboratory or method cell longer than its limit, the 400 names `file` and blames the file, not `redact_terms`.",
  "fix": "After redaction, check lengths with a variant that raises `_terms_error` (a 400 naming `redact_terms`) and a message such as 'After redaction row N column is longer than L characters'. Add a test with a long laboratory cell and assert `redact_terms` is in the response and nothing is stored.",
  "confirmed": true,
  "reason": "I read lab_import.py:139-147 and 204-205. The second `_check_bounds(lines)` after redaction raises `_file_error`, so the 400 names `file`. `_prepare` (lines 300-304) uses `_terms_error` for the same overflow in import_name and the laboratory form field, so the cell path is inconsistent with it. The cause is the redaction, not the uploaded file."
 },
 {
  "file": "backend/core/redaction.py",
  "line": 33,
  "severity": "medium",
  "claim": "Matching costs O(len(text) \u00d7 number of terms \u00d7 term length), and the bounds check does not limit the text scanned, so a crafted file can cost a lot of CPU.",
  "fix": "Check bounds on unstripped cells, or redact the stripped cell. Find matches in linear time, for example with `str.find` on casefolded text per term, or with a single Aho\u2013Corasick-style pass.",
  "confirmed": true,
  "reason": "I read redaction.py:28-36. It runs `re.finditer` with a lookahead for each term over the full text, so every position is tried against every term. `_check_bounds` (lab_import.py:144) measures `.strip()`ped length, but `_redact_line` redacts the raw `cells[i]`. A cell of 'x' followed by about 1 MiB of spaces therefore passes the bounds check and is scanned in full. Terms made of leading spaces make each failed attempt compare up to about 199 characters. I did not time it. The cost is bounded by the 1 MiB file limit and by the endpoint being authenticated."
 }
]
