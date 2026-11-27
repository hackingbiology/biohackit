# [review] Residual medium findings on m03-tgb-synonyms-review-queue-and-substance-fixes

Labels: autodev

[
 {
  "file": "backend/substances/views.py",
  "line": 188,
  "severity": "medium",
  "claim": "POST /api/substances/resolve/ is open to any authenticated member with no throttle, so one account can add unbounded permanent review-queue rows and trigger a difflib scan per call.",
  "fix": "Add throttle_classes = [ScopedRateThrottle] and throttle_scope = 'substance_resolve' with an env-configurable rate in DEFAULT_THROTTLE_RATES; add a 429 test; record the default in docs/QUESTIONS.md.",
  "confirmed": true,
  "reason": "grep of backend/substances for 'throttle' returns no matches, so ResolveNameView has none. The finding says queue items are created via get_or_create and kept, and that the repo already throttles loinc_search. I did not open either of those."
 },
 {
  "file": "backend/substances/synonyms.py",
  "line": 96,
  "severity": "medium",
  "claim": "Resolution filters on reviewed_at, not on reviewer. A synonym whose reviewer was erased (SET_NULL) still resolves, which contradicts the SHALL scenario 'a synonym without a reviewer does not resolve'.",
  "fix": "Filter resolution (and the near-match known set at line 103) on reviewer__isnull=False, or keep a reviewer identity on erasure; add a test that erases the reviewer and expects ambiguous.",
  "confirmed": true,
  "reason": "synonyms.py:95 filters only on reviewed_at__isnull=False. models.py:85 sets reviewer as SET_NULL, and models.py:110-113 together with the migration constraint allow reviewer NULL when reviewed_at is set. A reviewer-less synonym can therefore resolve. I did not open the spec file for the scenario wording."
 }
]
