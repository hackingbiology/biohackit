# [M03] TG-b: synonyms with language, source and reviewer, and an ambiguous review queue

Labels: autodev, feature
Milestone: M03 Interventions catalog and protocols
Parent: unknown

Goal: a SubstanceSynonym table (language, source, reviewer) and `resolve_name`: exact match after case and whitespace normalisation on reviewed synonyms only; any other outcome is an open `ambiguous` review item, never dropped, never attached. No synonym seeded. Also fixes the two residual medium findings on backend/substances/services.py (new fetch date needed when a code or class changes; NUL gives 400).

Spec refs: M03 "Synonyms carry provenance and resolve only by exact match"; main-IC "Substance resolution on codes, not English strings".

Acceptance: scenarios italian-input-resolves, unresolved-substance-is-surfaced-not-dropped, a-synonym-without-a-reviewer-does-not-resolve, a-near-match-is-proposed-not-resolved covered; docs/api-substances.md; gates pass.
