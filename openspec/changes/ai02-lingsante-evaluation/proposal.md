# Change: ai02 — Evaluate Ant Group's LingSante open medical models

## Why
Fabio (2026-11-26) asked for an analysis of whether and how to integrate LingSante, the medical models that Ant Group (inclusionAI) open-sourced from its 150-million-user health app.

Facts verified from the Hugging Face model cards on 2026-11-26:
- **Licence:** MIT for all models, so they are AGPL-compatible.
- **`LingSante-3.1-air-VL`:** a multimodal MoE with 124B total parameters, of which 5.5B are active per token. It covers medical imaging reports, report interpretation, skin, and dietary and nutritional analysis from images. Community GGUF and MXFP4 quantizations exist.
- **`LingSante-3.1-flash`:** a MoE with 560B total and 25B active parameters and a 1M-token context, aimed at medical reasoning and deep research.
- **`LingSante-Pulse-1.0`:** an encoder for physiological signals.
- **Medical status:** both cards say "research model, not a medical device".
- **Hardware:** the recommended serving is SGLang on 4× 141 GB-class GPUs. The project server has 8 CPUs, 31 GB of RAM and no GPU, so it cannot run them.

## Candidate uses, in order of value and compatible with the frozen criteria
1. **Lab-report extraction proposals (M02):**
   - air-VL reads photos and scans of reports in IT, EN or ZH and *proposes* structured rows (analyte name, LOINC candidate, value string, unit string, reference interval string).
   - Criterion 4 still holds, so the LLM never decides a number. Every proposed value and unit must be found **verbatim** in the document text (PDF text layer, or a deterministic OCR such as the local deepseek-ocr) by deterministic code; otherwise it is rejected.
   - Each row enters as `entered` (Q63) and becomes `user_confirmed` only after the user checks it.
   - The model is listed in the AI surfaces map.
2. **Plain-language explanation** of a user's own report, in words only, labelled as AI and cached (AI4L). This is especially useful for zh-CN users.
3. **Second model in multi-LLM research** (R1 optimal ranges, Q56 clock coefficients) as a source *finder* next to Evipedia/AI4L. Numbers always come from the cited papers.
4. **Meal-photo nutrition hints** (M04 nutrition), as words or proposals only.
5. **Pulse-1.0** for wearable signals (M05/M09): evaluate only in that module's ecosystem scan.

## Explicitly out of scope
- Diagnosis, skin-disease assessment and dosing.
- GUI agents that book appointments or buy medicines.

Each of these would make biohack.it a medical device (EU MDR rule 11) and breaks the harm-reduction posture.

## Deployment options, a decision for Fabio
- **A. Hosted API**, if a provider offers it: quick and cheap to test, but health data leaves our servers. It is allowed only with explicit consent, after de-identification, and with a GDPR transfer assessment if the provider is outside the EU.
- **B. GPU rented on demand** with a quantized air-VL, for batch evaluation only.
- **C. Self-hosted** on owned hardware: for a quantized air-VL, roughly one ≥96 GB GPU or a 128 GB unified-memory machine (to be verified in the evaluation).
- **Default until Fabio decides:** no runtime integration. Build a **provider-agnostic interface** (the extraction-proposal contract and its verbatim-verification gate) plus an **evaluation harness** on synthetic, non-personal sample reports, so that LingSante, Claude and others can be compared on the same data once a runtime exists.
