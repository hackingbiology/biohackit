# [review] Residual medium findings on m02-tga1-labreport-labresult-models

Labels: autodev

[
 {
  "file": "backend/core/models.py",
  "line": 205,
  "severity": "medium",
  "claim": "A reported value with more than 6 decimals is silently quantized to 6 places and stored as the as-reported value, so the stored value can differ from what the lab reported.",
  "fix": "Do not round silently. Raise ValidationError when the value has more than 6 decimals or too many integer digits, or widen the column. Alternatively, keep the original text of the value. Change test_reported_value_is_rounded_before_normalising to match.",
  "confirmed": true,
  "reason": "I read backend/core/models.py. Line 159 declares reported_value as DecimalField(max_digits=20, decimal_places=6). Line 205 runs `Decimal(self.reported_value).quantize(Decimal(\"0.000001\"))` in save and overwrites the field with no warning or flag. The line is 205, not the cited 207. I did not open the test file; the report says the test pins the rounding. Even without line 205, the 6-place column would round the value at the database. So the loss of precision is real, but this code makes it deliberate and silent. It conflicts with the scenario that the as-reported value is stored. It is low-frequency, which is why it stays medium."
 }
]
