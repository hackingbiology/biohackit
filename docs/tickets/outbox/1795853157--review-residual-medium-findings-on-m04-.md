# [review] Residual medium findings on m04-tga-typed-cadence-and-unit-match-fix

Labels: autodev

[
 {
  "file": "backend/core/cadence.py",
  "line": 75,
  "severity": "medium",
  "claim": "from_dict silently ignores unknown keys, so a typo or a camelCase key such as timesPerDay is dropped and times_per_day falls back to 1.",
  "fix": "In from_dict, check that data is a dict and refuse any key outside {mode, times_per_day, days_of_week, interval_days} with a ValueError naming the key. Add a test for {\"mode\": \"daily\", \"timesPerDay\": 3}.",
  "confirmed": true,
  "reason": "Read cadence.py:74-84. from_dict reads only the four snake_case keys with data.get() and never checks for extra keys. times_per_day defaults to 1, so {\"mode\":\"daily\",\"timesPerDay\":3} gives times_per_day=1 with no error. There is also no isinstance(data, dict) check. This can silently undercount due_events. I did not check the get-based docstring or the tests."
 }
]
