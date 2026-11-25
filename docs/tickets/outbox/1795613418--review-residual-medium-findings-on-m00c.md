# [review] Residual medium findings on m00c-tg2-gates-c-pip-audit-v2

Labels: autodev

[
 {
  "file": "tools/audit/pip_audit_gate.py",
  "line": 81,
  "severity": "medium",
  "claim": "The gate exits 0 with '0 packages, no fixable vulnerability' when the pip-audit report has no dependencies, so an audit that covered nothing passes.",
  "fix": "In check_all_audited (or run_audit), raise GateError when report.get('dependencies') is empty or missing. Optionally compare the audited count with the number of name==version lines in the exported requirements file. Add an offline test for {\"dependencies\": [], \"fixes\": []} that expects exit 2, tagged dev-process::backend-audit-cannot-run.",
  "confirmed": true,
  "reason": "I read the file. check_all_audited (lines 81-90) only iterates over entries that exist, and evaluate (lines 37-49) returns ([], []) for an empty or missing list. main (lines 111-114) then prints the 0-package summary and returns 0. Nothing checks for an empty report. The spec requires the gate to fail when the audit cannot run. Zero audited packages cannot be right for a backend with several direct runtime dependencies. I did not run the gate or confirm that pip-audit drops marker-mismatched requirements without reporting them."
 }
]
