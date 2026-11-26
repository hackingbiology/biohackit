# [review] Residual medium findings on m02-tgo2-manual-entry-and-report-view-pages

Labels: autodev

[
 {
  "file": "frontend/src/lib/i18n.ts",
  "line": 508,
  "severity": "medium",
  "claim": "The /labs/new intro says a saved report can be undone, but a typed report cannot be undone (backend returns 409, report page hides Undo).",
  "fix": "Reword newIntro: \"Nothing is stored until you save. A report you type by hand cannot be undone after saving, so check each value first.\"",
  "confirmed": true,
  "reason": "i18n.ts:508 has the undo promise and page.tsx:200 renders it. backend/core/views.py:284-288 returns 409 for any non-import report, and i18n.ts:564 says a typed report cannot be undone. The page contradicts itself and the backend."
 },
 {
  "file": "frontend/src/app/labs/new/page.tsx",
  "line": 95,
  "severity": "medium",
  "claim": "Removing a result row deletes the focused button's fieldset and focus is not moved afterwards (WCAG 2.4.3).",
  "fix": "After removal, move focus to a stable target (the 'Add another result' button or the previous row's first input) using a ref and effect. Optionally announce the removal in a polite live region.",
  "confirmed": true,
  "reason": "page.tsx:95 removeRow only filters state and clears errors. A grep for focus( in the file finds nothing. The Remove button sits inside the removed fieldset, so focus is lost to body."
 }
]
