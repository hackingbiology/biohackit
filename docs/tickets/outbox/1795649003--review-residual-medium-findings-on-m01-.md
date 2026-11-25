# [review] Residual medium findings on m01-tg-loinc-d2-panels-answerlists

Labels: autodev

[
 {
  "file": "backend/terminology/loinc_importer.py",
  "line": 368,
  "severity": "medium",
  "claim": "An AnswerListId longer than 100 characters is never length-checked and reaches the database, raising a raw DataError instead of a LoincImportError naming the file and line.",
  "fix": "In check_answer_rows, compare len(row.key) with char_limit(LoincAnswerList, 'answer_list_id') and raise LoincImportError(f\"{row.line}: answer_list_id is N characters, maximum M\"). Add a test with an overlong AnswerListId.",
  "confirmed": true,
  "reason": "parse_csv (loinc_importer.py:175) calls check_lengths only on the mapped values, not on the key. check_answer_rows (lines 332-357) checks only the ANSWER_LIST_FIELDS values and the answer fields, never row.key. models.py:370 sets answer_list_id max_length=100. import_answer_lists passes row.key straight to update_or_create (line 371). parse_term_rows (lines 200-204) has an explicit key-length check for loinc_num, and the new answer-list code has no equivalent. I did not run the import with an overlong id; the conclusion comes from reading the code."
 }
]
