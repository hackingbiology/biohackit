# [S01] Account erasure part 1: delete-everything API (Q57)

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: owner-only GET/POST /api/auth/me/erase/: states the clones notice, deletes the account, data and retained originals; keep-for-research refused until M12.

Spec refs: s01-spec-discovery accounts-and-profiles "Personal data erasure"; Q57; Q85.

Acceptance: scenarios erasure-on-request, clones-are-disclosed and erasure-offers-a-research-retention-choice have tests; gates pass.
