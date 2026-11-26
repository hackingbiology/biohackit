# [review] Residual medium findings on m02-tgi2-phenoage-from-stored-results-api

Labels: autodev

[
 {
  "file": "backend/core/views.py",
  "line": 314,
  "severity": "medium",
  "claim": "A finite Decimal too large for a float (e.g. age_years=1e400) passes the 400 check, becomes inf, and yields a 200 engine refusal instead of a 400 naming age_years.",
  "fix": "Convert to float first, then raise the same 400 ValidationError when not math.isfinite(value). Add 1e400 and -1e400 to the bad-age test.",
  "confirmed": true,
  "reason": "Read views.py:308-316. The check is Decimal.is_finite() and float() is applied afterwards. Decimal('1e400') is finite but float() of it gives inf. The inf then reaches the engine and is refused as a 200, not a 400. I did not run the code."
 }
]
