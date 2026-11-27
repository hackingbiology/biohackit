# [M03] TG-e: route, formulation and multi-ingredient products
Labels: autodev, feature
Milestone: M03 Interventions catalog and protocols
Parent:

Goal: each protocol intervention records a route (closed plain-word list) and a formulation; a Product records the ingredients its label declares (each a Substance, amount per unit, label as source); a per-day total of one ingredient across products is computed only from declared amounts and labelled a total of label contents, never a posology; an ingredient without a label amount is listed, never summed or estimated.

Spec: openspec/changes/m03-interventions-protocols (TG-e); interventions-and-catalog ("Route and formulation are recorded per intake item", "Multi-ingredient products list their declared ingredients").

Acceptance: see tasks.md TG-e; tests in backend/tests/test_protocol_products.py.
