# [review] Residual medium findings on m00c-tg2-docs-e-changelog

Labels: autodev

[
 {
  "file": "docs/CHANGELOG.md",
  "line": 3,
  "severity": "medium",
  "claim": "The changelog says it has one row per merged task, but it omits many merged task commits on the dates it covers, so the public page gives an incomplete account.",
  "fix": "Reword line 3 and the page intro to say the changelog is a selection of notable changes. Or add rows for every merged non-ticket task commit on the covered dates, and add a completeness test.",
  "confirmed": true,
  "reason": "docs/CHANGELOG.md:3 says \"one row per merged task\". `git log main` shows [M00c] task commits dated 2026-11-25 with no row: 90dabc2, 8d365ef, c76bf2e, 6a6601c, 598d2da, d42ce66, 0fe6a7c, 72ff5b6, 34c75b9 and 63f192b. The 2026-11-25 section has 10 rows. The 2026-11-24 section has only e512cc5 and 1787aa0. The claim is therefore false as written. Rewording the claim is the cheaper fix. I did not check whether the 2026-11-24 task commits cited in the finding exist. The spec only requires that cited entries resolve, so this is a misleading-wording defect, not a spec violation."
 }
]
