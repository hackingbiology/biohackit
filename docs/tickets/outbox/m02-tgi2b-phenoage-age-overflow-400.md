# [M02] TG-i part 2b: PhenoAge age_years too large for a float is a 400
Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: fix the confirmed medium review finding (docs/tickets/outbox/1795694970--review-residual-medium-findings-on-m02-.md).
Spec refs: m02-blood-layer TG-i; scenario biomarkers-and-labs::phenoage-from-routine-bloods.
Acceptance: age_years=1e400 / -1e400 gives 400 naming `age_years`; age_years=40 still 200; no dependency, no migration.
