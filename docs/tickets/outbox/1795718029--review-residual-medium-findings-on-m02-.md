# [review] Residual medium findings on m02-tgo1-csv-import-review-page

Labels: autodev

[
 {
  "file": "frontend/src/app/labs/import/page.tsx",
  "line": 219,
  "severity": "medium",
  "claim": "The review table never shows the plausibility flag, so users confirm values without seeing that a value is outside its cited reference range.",
  "fix": "Type `plausibility` as the documented shape. Add a 'Range check' column showing within / outside / not checked in words. Add a Jest test for an 'outside' row.",
  "confirmed": true,
  "reason": "grep for 'plausib' finds only frontend/src/lib/labs.ts:22, where it is typed `unknown`. page.tsx never reads it, so the table cannot show the flag. The finding's own evidence cites docs/api-labs.md:129 as saying preview rows carry it; I did not open that file."
 },
 {
  "file": "frontend/src/app/labs/import/page.tsx",
  "line": 64,
  "severity": "medium",
  "claim": "After a report is saved, 'Check file' stays enabled. Pressing it clears the saved report and its Undo button, and brings back an enabled Save for the same file, so the user can lose the Undo and save a duplicate.",
  "fix": "Disable or hide 'Check file' while a report is saved and not undone, or stop `onCheck` from clearing `report`. Say on screen that the earlier report is still saved, with its id.",
  "confirmed": true,
  "reason": "The 'Check file' button at line 174 is `disabled={busy}` only. `onCheck` calls `setReport(null)` and `setUndone(false)` at lines 64-65 with no guard on a saved report. The report id is discarded, so Undo is no longer reachable."
 },
 {
  "file": "docs/CHANGELOG.md",
  "line": 9,
  "severity": "medium",
  "claim": "The TG-o changelog row cites commit 04027e2, which is the TG-h completeness commit, not this task.",
  "fix": "Cite this task's commit (8b631df) in docs/CHANGELOG.md, then regenerate frontend/src/content/changelog.json with tools/docs/export_changelog.py.",
  "confirmed": true,
  "reason": "`git log -1 04027e2` is the 'TG-h part 1: completeness and freshness' commit, and docs/CHANGELOG.md:9 cites it for the TG-o import page. 8b631df is the TG-o part 1 commit. I did not open frontend/src/content/changelog.json, so the copied hash there is unchecked."
 }
]
