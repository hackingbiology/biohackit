# [review] Residual medium findings on x01-tg4-integration-anchor-scans

Labels: autodev

[
 {
  "file": "docs/ecosystem/GIVEBACK.md",
  "line": 13,
  "severity": "medium",
  "claim": "The fhir.resources give-back row asserts the LICENSE is the 3-clause BSD text and proposes BSD-3-Clause metadata. Both scans say the clause count was not determined.",
  "fix": "Reword the row so it claims no SPDX id or clause count. For example: 'Propose declaring an SPDX licence expression in package metadata: GitHub reports NOASSERTION and PyPI says only \"BSD license\"'. Alternatively, fetch the LICENSE, count the clauses, and update integrations.md, m01-terminology.md and Q9 to match.",
  "confirmed": true,
  "reason": "GIVEBACK.md:13 says 'license_expression BSD-3-Clause' and 'the LICENSE file is the 3-clause text'. integrations.md:46 and m01-terminology.md:116 both say the clause count was not determined and no SPDX id is claimed. This is an unverified licence fact in text meant for upstream, and it contradicts the scans. The two reviewer findings are duplicates of each other."
 }
]
