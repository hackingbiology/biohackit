# [review] Residual medium findings on m02-tgb-manual-lab-entry-api

Labels: autodev

[
 {
  "file": "backend/core/views.py",
  "line": 159,
  "severity": "medium",
  "claim": "reported_value has no length cap, so a huge string reaches LabResult._exact_reported_value, whose trailing-zero loop is quadratic. One authenticated request can tie up a worker's CPU.",
  "fix": "In _create_result, reject a reported_value longer than a small bound (about 40 characters) with a 400 on reported_value, and cap len(results). In the model, replace the slicing loop with a single O(n) count of trailing zeros followed by one slice.",
  "confirmed": true,
  "reason": "Read the code. views.py:158-171 only checks that the value is a non-empty string and passes value.strip() to LabResult with no length limit. core/models.py:299-300 runs `while len(digits) > 1 and digits[-1] == 0: digits = digits[:-1]`, and each slice copies the whole tuple. A value like '1' followed by N zeros therefore costs O(N\u00b2). I did not time it, but the code matches the finding as stated."
 }
]
