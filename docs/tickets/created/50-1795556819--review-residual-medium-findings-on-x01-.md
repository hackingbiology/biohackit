# [review] Residual medium findings on x01-tg2-m01-terminology-scan

Labels: autodev

[
 {
  "file": "docs/ecosystem/m01-terminology.md",
  "line": 135,
  "severity": "medium",
  "claim": "The decisions table cites TG2 as a changed M01 task for the ucumvert and OMOP-alignment decisions, but no TG2 line was changed.",
  "fix": "Change the 'M01 task changed' column to ucumvert \u2192 TG5, and OMOP column alignment \u2192 TG5 and TG-LOINC.",
  "confirmed": true,
  "reason": "m01-terminology.md:135 says 'TG2 (`Unit` validation) and TG5 (seed check)' and :136 says 'TG2, TG-LOINC'. In tasks.md, TG2 lines 6-9 are all `[x]` with no scan annotation. The ucumvert line sits only under TG5. I did not check whether the alignment note appears under TG-LOINC. So the table points at a TG2 change that does not exist."
 }
]
