# [review] Residual medium findings on x01-getbased-importer-p2b-confirm-provenance-undo

Labels: autodev

[
 {
  "file": "docs/api-labs.md",
  "line": 283,
  "severity": "medium",
  "claim": "The API doc says import_name is the upload's file name, but the code stores a fixed name and the spec says the upload name is not kept.",
  "fix": "Change the doc to say import_name is the fixed name `getbased-export.json` and the upload name is not kept (Q101 item 5).",
  "confirmed": true,
  "reason": "docs/api-labs.md:283 says `import_name` = the file name. backend/core/getbased_import.py:407 sets IMPORT_NAME = \"getbased-export.json\" and line 456 stores import_name=IMPORT_NAME. The latest commit message also says the upload name is not kept. I did not open the spec or the ticket outbox file, so the spec wording and the outbox repeat of the error are unchecked."
 }
]
