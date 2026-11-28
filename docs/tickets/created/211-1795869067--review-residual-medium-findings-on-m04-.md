# [review] Residual medium findings on m04-tgc-deterministic-daily-allocation

Labels: autodev

[
 {
  "file": "backend/protocols/allocation.py",
  "line": 164,
  "severity": "medium",
  "claim": "If one intake can never be placed, `_solve` runs in time exponential in the number of other, unrelated intakes, so `allocate` can hang on a realistic daily list.",
  "fix": "Apply the unary food rules (`substance_b is None`) when building `cands` in `allocate`, so slots that fail `_meal_distance_ok` are dropped. If an intake has no candidates left, flag a conflict naming those constraint ids and leave that intake out of the search. Order the search so intakes that share pairwise rules come first, or solve each group of rule-sharing intakes separately. Add a test with about 15 intakes and one unsatisfiable food rule that must finish quickly.",
  "confirmed": true,
  "reason": "I read allocation.py:158-195. `step()` is plain chronological backtracking over intakes in key order. The food rule is checked only inside `fits()` when that intake's turn comes, and there is no pruning, memo or backjumping. An intake with no feasible slot, such as key 'z' with a sourced food rule whose minutes exceed the largest circular distance of 720, makes the search enumerate every placement of the unrelated earlier intakes first. That is roughly slots^n. `_minimal_conflict` (lines 198-210) calls `_solve` again once per rule, which multiplies the cost. I did not run it. The defect follows directly from the code."
 }
]
