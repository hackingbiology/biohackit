# Tasks — ai02 LingSante evaluation
- [ ] Ecosystem entry for LingSante (air-VL, flash, Pulse) in docs/ecosystem/integrations.md, facts fetched from the model cards
- [ ] Extraction-proposal interface (provider-agnostic) + verbatim verification gate + tests (scenarios above)
- [ ] Evaluation harness + synthetic sample reports (it/en/zh, clearly fictitious, no real persons) + results file; runnable against any OpenAI-compatible endpoint
- [ ] AI surfaces map entry (status: under evaluation, not enabled)
- [ ] Fabio decides deployment option A/B/C (QUESTIONS)

## Governance and political assessment (Fabio 2026-11-26: "it may be a political choice")
- [ ] `docs/research/model-governance/README.md`: method and template, applicable to every model including Claude
- [ ] LingSante governance record, each item from cited sources:
  - **Origin:** Ant Group / inclusionAI.
  - **Jurisdiction:** PRC laws relevant to a self-hosted open-weight model versus a hosted service (generative-AI service rules, data-export rules).
  - **EU AI Act:** GPAI and open-source provisions, and how they apply to deployers like us.
  - **GDPR:** hosted versus self-hosted data flows.
  - **Training-data and benchmark transparency** declared on the cards and in the papers.
  - **Supply chain:** safetensors only, no `trust_remote_code`, hash pinning.
- [ ] Behavioural audit harness and probe set in it/en/zh. Compare against at least one EU-origin open model and one US model. Report differences, with no editorialising beyond the evidence.
- [ ] Stakeholder and positioning analysis for Fabio's decision, kept factual with each option's pros and cons:
  - how EU funders (NLnet/NGI), the rapamycin.news community and Chinese users (WeChat, zh-CN) may perceive the choice;
  - the open-weights sovereignty argument: self-hosting means no dependency on a foreign service;
  - the reputational risks either way.
- [ ] Decision record proposed to Fabio in the digest. **No enablement without his explicit decision.**
