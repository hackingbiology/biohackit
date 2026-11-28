# [M03] TG-f part 2a: fork a published protocol, and fix the public throttle proxy bypass
Labels: autodev, feature
Milestone: M03 Interventions catalog and protocols
Parent:

Goal: a logged-in user copies a published protocol into their own Draft that records the source protocol and the exact published version; editing the copy never changes the source. Also `REST_FRAMEWORK["NUM_PROXIES"]` now comes from `DRF_NUM_PROXIES` (default 0) so a spoofed X-Forwarded-For cannot dodge the anonymous throttle.

Spec: openspec/changes/m03-interventions-protocols (TG-f part 2a); protocols ("Forking preserves lineage and safety", "Fork then diverge", "A fork copies only what the source shows publicly").

Acceptance: see tasks.md TG-f part 2a; tests in backend/tests/test_protocol_fork.py. Part 2b (measurement binding, Paused overdue) stays open.
