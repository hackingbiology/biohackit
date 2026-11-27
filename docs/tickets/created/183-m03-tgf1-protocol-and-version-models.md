# [M03] TG-f part 1: Protocol and ProtocolVersion models with an owner-only API

Labels: autodev, feature
Milestone: M03 Interventions catalog and protocols
Parent: unknown (no M03 issue found in docs/tickets/created)

Goal: a Draft is edited in place; leaving Draft or any later change creates an immutable version with change events and a mandatory reason; two versions can be diffed with stdlib difflib. Plain model (Q109), no new dependency.

Spec refs: openspec/changes/m03-interventions-protocols (protocols: Versioning and change tracking, A protocol version is immutable); openspec/specs/protocols (Create a protocol from scratch, Import an already-running protocol); docs/QUESTIONS.md Q114.

Acceptance: the nine listed scenarios are covered in backend/tests/test_protocols.py; routes documented in docs/api-protocols.md; part 2 (fork, measurement binding) stays open in tasks.md.
