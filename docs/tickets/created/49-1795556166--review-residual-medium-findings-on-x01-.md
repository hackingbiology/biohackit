# [review] Residual medium findings on x01-tg1-ecosystem-readme-giveback-m00-scan

Labels: autodev

[
 {
  "file": "backend/tests/test_ecosystem_docs.py",
  "line": 83,
  "severity": "medium",
  "claim": "The test never checks an entry's AGPL-compatible verdict against its Licence or the README licence table. An entry with a GPL-3.0 or CC-BY-SA licence can claim `yes` and still pass.",
  "fix": "Parse the README licence table into a map from SPDX id to verdict. Allow a `yes` verdict only when the Licence maps to `yes`. For any other or missing licence, require a compat value starting with `unknown` or `no`.",
  "confirmed": true,
  "reason": "Lines 83-96 only reject `yes` when the Licence is `unknown`, and require QUESTIONS.md and Provisional when the verdict contains 'unknown'. README.md:55 and :59 mark GPL-3.0 and CC-BY-SA as `unknown`. An entry with `Licence: GPL-3.0`, `AGPL-compatible: yes` and `adopt as dependency` passes every assertion. This is also the substance of the first and third findings, which duplicate each other, so I count them as one."
 },
 {
  "file": "backend/tests/test_ecosystem_docs.py",
  "line": 70,
  "severity": "medium",
  "claim": "Duplicate of the finding at line 83: the test does not cross-check the compat verdict against the README licence table.",
  "fix": "Same fix as the finding at line 83. Keep one finding.",
  "confirmed": true,
  "reason": "The code is the same as in the line-83 finding. Confirmed as a real defect, but it is the same issue and should be merged into that one."
 },
 {
  "file": "docs/ecosystem/m00-foundations.md",
  "line": 41,
  "severity": "medium",
  "claim": "The scan has a psycopg entry but no entry for `psycopg-binary`. The project installs `psycopg[binary]`, which pulls in that separate distribution.",
  "fix": "Add a `psycopg-binary` entry, with licence and last activity fetched from pypi.org/pypi/psycopg-binary/json. If the fetch fails, mark the fields `unknown`.",
  "confirmed": true,
  "reason": "backend/pyproject.toml:14 requires `psycopg[binary]>=3.1`. backend/uv.lock:505 lists `psycopg-binary` as a dependency, and lock line 509 is its own package block. The only psycopg entry in the scan is at line 41 (the Python wrapper, licence LGPL-3.0). The binary wheel runs in-process and has no entry. I did not check the claim about what the wheel bundles."
 }
]
