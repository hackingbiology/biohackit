# get-based: strategy watch (2026-11-26)

Source: GitHub API on elkimek/get-based (releases, commits since 2026-09-01, issues and PRs). Facts only. Interpretation is marked as such.

## Status
- **Licence and size:** AGPL-3.0, 168 stars, 34 forks.
- **Maintainers:** essentially a single maintainer (elkimek, about 2,370 commits; the next contributor has 18).
- **Pace:** 142 commits since September (56 in September, 53 in October, 33 in November). Releases v1.19 to v1.27, the last three on 2026-11-02.

## Last three months
- **v1.19:** CLI agent providers, chat workspace and dashboard.
- **v1.20:** reports that are easier to share.
- **v1.21:** Biology Scores upgrade.
- **v1.22:** correlations.
- **v1.23 and v1.24:** migration to TypeScript 7 and a stronger foundation.
- **v1.25:** waist measurements and cycle guidance.
- **v1.26:** personal baselines and immune markers.
- **v1.27:** updating health records through chat.
- **Smaller work:**
  - meals, nutrition and WHOOP;
  - a UVB light-device program;
  - hardening of Routstr wallet, backup and proxy, including 136 regression cases;
  - local AI reasoning for Biology Scores (2026-11-26).

## AI model policy and LingSante
- **Provider-agnostic:** get-based works with OpenRouter, the privacy providers PPQ, Routstr (with Tinfoil enclaves) and Venice, a custom API, and local models.
- **Current recommendations** (#1724 on 2026-11-16, #1727 on 2026-11-18):
  - Claude Fable 5.2, GPT-6.1 Sol, Gemini 4 Carbon/Hydrogen and Qwen4-Max;
  - DeepSeek V4.1 Flash, Kimi K3.1 Pro and GLM 5.3 for the private providers.
  
  Chinese general-purpose models are recommended without reservation.
- **Specialized derivatives excluded:** #1724 explicitly "exclude[s] specialized derivatives of the new general-purpose identities" from the recommendations.
- **No sign of LingSante:** nothing in commits, issues or PRs. LingSante was released on 2026-11-19, after that policy. It could still be used through the custom API or local runtimes.
- **Interpretation:** there is no current plan to integrate LingSante. Their policy favours general frontier models plus privacy-preserving routing over medical fine-tunes.

## Strategic direction: a big change ahead
- **#1719** (2026-11-12, owner review, not merged or announced) plans to move personal use from the hosted app to **self-hosted get-based**:
  - a password-protected migration archive;
  - a loopback npm server, accessed through Tailscale HTTPS;
  - the hosted origin becomes **recovery-only 30 days after the announcement**;
  - the encrypted Sync relay and a fictional-data demo remain.
- **#1736:** nutrition import with FoodData Central first and AI only as fallback. This is the same deterministic-first philosophy as ours.
- **#1717:** a community member is asking to fork for German and French UI and contribute back. **#9:** CGM/CKM integration request.

The export, backup and planned migration-archive formats, read from source with citations, are in [getbased-archive-format.md](getbased-archive-format.md).

## Implications for biohack.it (interpretation, for Fabio)
1. **Non-technical users may lose their home.** If the hosted app goes recovery-only, users who cannot self-host with Tailscale need an alternative. biohack.it is server-hosted, so an **importer for the get-based migration archive or export** becomes high-value and is a natural collaboration point, to be proposed to the maintainer through GIVEBACK and not posted without Fabio's OK.
2. **Converging data needs.** Biology Scores, baselines and immune markers overlap with M02/M06. Reuse candidates for Q56 (PhenoAge and Bortz): check their implementation and cite it, but never use it as a number source.
3. **Shared nutrition data.** FoodData Central first matches M04; we can share mappings.
4. **LingSante.** Their choice (general models plus privacy routing) is a useful reference point for our ai02 governance analysis.
