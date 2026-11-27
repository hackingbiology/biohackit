# [review] Blocking findings left on x01-getbased-archive-format-and-import-spec

Labels: autodev

[
 {
  "file": "openspec/changes/x01-ecosystem-reuse/specs/biomarkers-and-labs/spec.md",
  "line": 4,
  "severity": "high",
  "claim": "The requirement ignores get-based's per-value provenance (`markerSources`, `importedWith`, `derivedFrom`, `manuallyEdited`). AI-extracted or calculated values would be stored as ordinary lab results.",
  "fix": "Add scenarios that keep `importedWith` and `markerSources` as provenance and flag AI-extracted values in the preview. Add a scenario that lists results with `derivedFrom` as not recognised (calculated, not measured). Add a scenario that labels `manuallyEdited` results.",
  "confirmed": true,
  "reason": "The doc (lines 48 and 52) lists `markerSources` with `reported`, `manuallyEdited` and `derivedFrom`, and `importedWith` as `{modelId, provider}`. Spec lines 4-56 contain none of these fields. Origin records only \"get-based\" and `version`, so provenance is lost on every stored value (frozen criteria 2 and 4)."
 }
]
