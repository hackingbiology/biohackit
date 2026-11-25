# [review] Residual medium findings on m00c-tg2-gates-g-mutmut

Labels: autodev

[
 {
  "file": "tools/mutmut/mutmut_gate.py",
  "line": 32,
  "severity": "medium",
  "claim": "The gate counts mutmut's `timeout` status as caught, so a surviving mutant that comes back as `timeout` passes the gate. The result then depends on timing, not only on the tests.",
  "fix": "Don't count `timeout` as killed. Either put it in its own bucket that fails closed, or re-run those mutants once and fail if they still time out. Print the timeout count per target. Add an offline test that a timeout-only result does not count as killed without a retry.",
  "confirmed": true,
  "reason": "mutmut_gate.py:32 sets `CAUGHT = frozenset({\"killed\", \"timeout\"})`, and lines 181-183 tally anything in CAUGHT as killed. docs/STATE.md:9 says '43 or 44 of 44 killed depending on the run'. The accepted mutant `x_normalize_value__mutmut_22` is documented as equivalent and therefore unkillable. The 44/44 runs can only have happened if that mutant was scored as timeout, so the gate result varies from run to run. I did not open mutmut's own source, so the exit-code mapping for timeout is not checked."
 },
 {
  "file": "tools/mutmut/mutmut_gate.py",
  "line": 216,
  "severity": "medium",
  "claim": "The allowlist matches survivors only by mutmut's position-based id. Nothing checks that an accepted id is still the same mutation, or that it still exists and still survives. A different survivor can take over an accepted id and pass, and stale entries go unreported.",
  "fix": "Pin each accepted entry to a hash of its normalised `mutmut show` diff (`<id> <sha256> # <reason>`). Fail with exit 2 if the hash does not match. Also warn or fail when an accepted id is not among the survivors. Add offline tests for both cases.",
  "confirmed": true,
  "reason": "mutmut_gate.py:210 is `pending = [m for m in survivors if m not in accepted]`, and the only check is id membership. read_accepted (lines 89-99) stores only id\u2192reason. The entry in tools/mutmut/accepted_survivors.txt is the bare id `terminology.services.x_normalize_value__mutmut_22` plus a prose reason. The gate never compares the reason with the actual mutation. Nothing flags an accepted id that is absent from the survivors."
 }
]
