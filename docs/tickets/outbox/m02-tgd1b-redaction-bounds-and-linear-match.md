# [M02] TG-d part 1b: redaction bounds error names redact_terms; linear-time term matching
Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: fix the two confirmed medium review findings (docs/tickets/outbox/1795671091--review-residual-medium-findings-on-m02-.md).
Spec refs: m02-blood-layer TG-d; scenario biomarkers-and-labs::user-opts-to-obfuscate.
Acceptance: overflow only after redaction gives 400 naming `redact_terms`; file overflow still names `file`; matching uses str.find; bounds and redaction see the stripped cell; no dependency, no migration.
