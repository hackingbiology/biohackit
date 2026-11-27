# [M03] TG-c: input-output diff, constrained-column validator and resolve fixes

Labels: autodev, feature
Milestone: M03 Interventions catalog and protocols
Parent: 

Goal: a batch resolve that ends with "N submitted, M recognised, K not understood" and a staged commit; closed enums written only by code after validation, free text to notes, anything else `ambiguous` and never truncated. Also throttle `/resolve/` and stop an erased-reviewer synonym from resolving.

Spec refs: interventions-and-catalog "Input↔output diff at end of extraction", "LLM never writes into constrained columns".

Acceptance: see openspec/changes/m03-interventions-protocols/tasks.md (TG-c) and backend/tests/test_substance_extraction.py.

Refs docs/tickets/outbox/1795799375--review-residual-medium-findings-on-m03-.md
