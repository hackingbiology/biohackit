# [review] Blocking findings left on m00c-tg2-spec-discovery-d2b2-hb-protocol-structure

Labels: autodev

[
 {
  "file": "openspec/changes/s01-spec-discovery/specs/interventions-and-catalog/spec.md",
  "line": 47,
  "severity": "high",
  "claim": "The 'Weight-relative posology' requirement computes an absolute dose from the user's body weight without carrying the human/animal posology provenance. An animal per-kg dose could be scaled onto a human and shown as an absolute dose.",
  "fix": "Require the per-weight dose to carry the 'Posology provenance (human vs animal)' tag. Add a SHALL scenario: when the posology is animal-derived, no absolute human dose is computed. Alternatively, show it only with the animal-derived marking and the heightened acknowledgment, never as an established human dose.",
  "confirmed": true,
  "reason": "Lines 47-56 of the delta spec never mention provenance or animal-derived. The existing 'Posology provenance' requirement and safety-guardrails:55-56 (animal-derived heightened acknowledgment) are not tied to this requirement. The scenario computes the dose from weight with no provenance gate. This finding and the third are duplicates, and I am keeping this one."
 }
]
