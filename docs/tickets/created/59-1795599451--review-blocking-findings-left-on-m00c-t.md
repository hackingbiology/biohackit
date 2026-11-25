# [review] Blocking findings left on m00c-tg2-gates-b-pnpm-audit

Labels: autodev

[
 {
  "file": "tools/audit/ignore.toml",
  "line": 17,
  "severity": "high",
  "claim": "The change waives high and critical advisories that already have patched versions. That breaks the task rule to add an ignore entry only if no patched version exists. One of them is a critical Next.js authorization bypass.",
  "fix": "Bump `next` in frontend/package.json to a patched release, regenerate the lockfile, run lint, type-check and test:ci, then remove the ignore entries. If that can't be done in this task, don't waive the critical advisories that have a fix. Leave the gate failing and escalate.",
  "confirmed": true,
  "reason": "I read tools/audit/ignore.toml and frontend/package.json:15. The file has `next` waivers, including critical GHSA-9qr9-h5gf-34mp and GHSA-f82v-jwr5-mffw. Each reason says `fixed in >=...`, so a patched version exists. frontend/package.json pins `next` at `15.1.0`. The waivers contradict task step 5, which allows an ignore entry only when no patched version exists. The stated reason is that the upgrade is deferred and tracked in Q33, not that no fix exists. I did not re-check the claim about frontend/src/middleware.ts, and it isn't needed to confirm the rule violation."
 }
]
