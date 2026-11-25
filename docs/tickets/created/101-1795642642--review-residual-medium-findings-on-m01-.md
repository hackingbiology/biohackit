# [review] Residual medium findings on m01-tg-loinc-b-search-api

Labels: autodev

[
 {
  "file": "backend/terminology/views.py",
  "line": 53,
  "severity": "medium",
  "claim": "The search query `q` has no length limit and no DRF throttling is configured, so an authenticated user can send a very large `q` and force expensive trigram and full-text work.",
  "fix": "Reject `q` longer than about 200 characters with HTTP 400 and a plain-language message, add a test for it, and consider a throttle scope on LoincSearchView.",
  "confirmed": true,
  "reason": "views.py:53-56 only checks that q is non-empty. I found no length cap on q and no THROTTLE setting in the backend Python files. The cost on a full LOINC release is an inference from how the query is built. I did not measure it, but the missing bound is real."
 },
 {
  "file": "backend/biohackit/settings.py",
  "line": 107,
  "severity": "medium",
  "claim": "The line assigns OPTIONS['options'] outright, so it overwrites any `options` value that DATABASE_URL already supplied, such as a search_path setting.",
  "fix": "Append to any existing `options` value instead of replacing it. Better, make the threshold explicit in search_loinc so correctness does not depend on the connection setup.",
  "confirmed": true,
  "reason": "settings.py:107-109 uses setdefault only on the OPTIONS dict and then assigns the `options` key directly, discarding anything env.db() parsed from the URL query string. The search relies on this per-connection threshold, as the comment at lines 104-106 says."
 }
]
