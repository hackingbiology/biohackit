# [review] Residual medium findings on m03-tgj1-omop-drug-exposure-and-amount-fix

Labels: autodev

[
 {
  "file": "backend/protocols/omop.py",
  "line": 51,
  "severity": "medium",
  "claim": "The 'unbroken run' walk in _start_date only checks whether the item is in each earlier snapshot. It ignores the protocol state, so a pause does not break the run and a resumed exposure is dated from before the pause.",
  "fix": "In _start_date, also stop the walk when prior.snapshot['state'] is not 'active'. Document in the mapping doc and Q115 whether a version that is not active may be exported at all. Add a test: v1 active, v2 paused, v3 active, and exporting from v3 gives v3's created_at date.",
  "confirmed": true,
  "reason": "backend/protocols/omop.py:52-55 walks back through earlier versions and breaks only when `item not in prior.snapshot['interventions']`; it never reads state. services.py:25-26 allows ACTIVE->PAUSED and PAUSED->ACTIVE. services.py:21 puts `state` in TRACKED and services.py:32 shows the snapshot includes it. A pause is therefore a version whose snapshot lists the same interventions, so v1 active, v2 paused, v3 active makes the walk return v1's date (or in_effect_since). The task says only to document the start-date choice, not to handle pauses, so this is a correctness gap in the exported date, not a spec violation. The v2/in_effect_since tests I saw in the commit log do not cover pauses. I did not open the test files or the mapping doc."
 }
]
