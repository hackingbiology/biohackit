# [review] Residual medium findings on m02-q56-clock-coefficient-research

Labels: autodev

[
 {
  "file": "docs/ecosystem/m02-blood-layer.md",
  "line": 137,
  "severity": "medium",
  "claim": "The get-based entry says its PhenoAge uses the original supplement's constants. The research document shows get-based uses a mix: S2's mortality-to-age pair together with the -19.907 intercept and 0.00188 ALP weight.",
  "fix": "Reword to say get-based uses S2's mortality-to-age constants with the -19.907 intercept and 0.00188 ALP weight (mixed, D1-D3), then regenerate frontend ecosystem.json.",
  "confirmed": true,
  "reason": "Line 137 says 'PhenoAge uses the original supplement's constants'. phenoage-coefficients.md line 187 lists get-based as 'S2 constants plus -19.907/0.00188 (mixed, D1-D3)'. Lines 53 and 61 give S2 as -19.9067 and 0.0019, against get-based's -19.907 and 0.00188 (S6 column). The two documents disagree. I did not re-check which sources S3/S4 are or whether the mortality-to-age pair is S2's. The finding's suggested rewording attributing the intercept and ALP weight to S3/S4 is a small extension: the research document shows S3/S4/S5/S8 print the same values, not that get-based took them from S3/S4."
 }
]
