# [review] Residual medium findings on m00c-tg2-docs-a-ai-surfaces-map

Labels: autodev

[
 {
  "file": "docs/ai-surfaces.md",
  "line": 17,
  "severity": "medium",
  "claim": "The 'Safety threshold' row cites only 'Dose sanity check'. The spec's safety threshold is a measured-value limit that triggers critical-value alerts, so it is missing from the deterministic table.",
  "fix": "Rename the row to 'Dose plausibility check' and add a separate row 'Safety threshold (critical-value alert) | deterministic | openspec/specs/safety-guardrails/spec.md: Interaction and critical-value alerts | specified'. Regenerate the JSON.",
  "confirmed": true,
  "reason": "docs/ai-surfaces.md:17 maps 'Safety threshold' only to 'Dose sanity check'. In openspec, 'safety threshold' is a per-analyte range (domain-model/spec.md:55, biomarkers-and-labs/spec.md:18). safety-guardrails/spec.md:51 uses it under 'Interaction and critical-value alerts' (line 40). ai-uses-and-attribution/spec.md:13 lists 'safety threshold' as a computed value. The mapping therefore points at the wrong requirement."
 }
]
