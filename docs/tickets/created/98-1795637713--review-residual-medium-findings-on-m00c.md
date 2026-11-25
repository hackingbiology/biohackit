# [review] Residual medium findings on m00c-tg2-gates-b2-pnpm-audit

Labels: autodev

[
 {
  "file": "tools/audit/pnpm_audit_gate.py",
  "line": 77,
  "severity": "medium",
  "claim": "A high or critical advisory with a missing or null patched_versions field is treated as 'unfixed' and the gate passes, instead of failing closed with exit 2.",
  "fix": "In evaluate, raise GateError when patched_versions is missing or not a string. Treat only '<0.0.0' (and an explicit empty string if pnpm really emits one) as unfixed. Add test cases with the key deleted and with the value None.",
  "confirmed": true,
  "reason": "Line 77 reads `str(advisory.get(\"patched_versions\") or \"\").strip()`, so a missing or null field becomes \"\". The `if patched in NO_PATCH` check on line 78 then files it as unfixed, which does not fail the gate. advisory_line (line 59) validates module_name, id and findings but not patched_versions. I did not check whether a test covers this case."
 },
 {
  "file": "openspec/changes/m00c-autodev-v2/tasks.md",
  "line": 15,
  "severity": "medium",
  "claim": "The acceptance criterion that lint, type-check, test:ci and build all exit 0 on the regenerated lockfile has not been verified.",
  "fix": "Run `pnpm --dir frontend install --frozen-lockfile`, then lint, type-check, test:ci and build in an isolated install or in CI before merging. Keep the B2 task unticked until they pass.",
  "confirmed": true,
  "reason": "Line 15 of tasks.md reads that the work is PARTIAL and states that lint, type-check, test:ci and build were not re-run against a fresh frozen install. It cites Q34 as the blocker. The task is correctly left unticked as `[ ]`. The acceptance criterion is still unmet, but the branch discloses this itself and does not claim it is done, so this is a merge-readiness gap and not a hidden defect."
 }
]
