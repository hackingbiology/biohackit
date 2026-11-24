# Ecosystem reuse

biohack.it prefers maintained open-source projects, upstream schemas (FHIR, OMOP CDM, OHDSI vocabularies) and open datasets over custom designs, even with some overhead (OpenSpec change `x01-ecosystem-reuse`). This folder holds one **scan** per module (`m00-foundations.md`, later `m01-terminology.md`, …) and the [give-back register](GIVEBACK.md).

## Method

1. Before a module's OpenSpec change is written, list every external project, schema or dataset the module uses or considered.
2. For each, **fetch** the facts from the source. Never fill a field from memory:
   - GitHub: `curl -s https://api.github.com/repos/<owner>/<repo>` → `license.spdx_id`, `pushed_at`
   - PyPI: `curl -s https://pypi.org/pypi/<pkg>/json` → `info.license_expression`, `info.project_urls`
   - npm: `curl -s https://registry.npmjs.org/<pkg>` → `license`, `repository`, `time`
   - When GitHub reports `NOASSERTION` for the licence, use the package registry or the licence file and say so in the entry.
3. Anything that cannot be fetched is the literal word `unknown`.
4. Record the decision (categories below) and link the scan from the module's `proposal.md`.
5. Concrete contributions we could make upstream go into [GIVEBACK.md](GIVEBACK.md). Nothing is posted externally without Fabio's approval.

`backend/tests/test_ecosystem_docs.py` enforces the entry format and the proposal link.

## Decision categories

| Decision | Meaning |
|---|---|
| `adopt as dependency` | We install it and depend on it as published. |
| `reuse schema or dataset` | We take an upstream schema, vocabulary or dataset (with its licence recorded), not code. |
| `learn-from only` | We read it for design ideas; no code, schema or data is imported. |
| `reject` | Considered and not used (reason given in the entry). |

## Entry format

Each project is a `### <Name>` heading followed by these mandatory fields (all as `- **Field:** value`):

| Field | Content |
|---|---|
| Name | The heading text. |
| URL | Canonical source URL, starting `https://`. |
| Licence | SPDX id as fetched, or `unknown`. |
| AGPL-compatible | `yes`, `no`, or `unknown` plus a short reason (see table). |
| Last activity | `YYYY-MM-DD` as fetched (GitHub `pushed_at`, or release date), or `unknown`. |
| Decision | One of the four categories above. |
| Verified | Source(s) fetched and a `YYYY-MM-DD` date, e.g. `api.github.com + pypi.org, 2026-11-24`, or exactly `unknown`. |
| Licence note | Optional free text. The `Licence` field itself is an SPDX id or the word `unknown`; prose goes here. |
| Provisional | Optional; `yes, ...` when the decision waits on an open question (see below). |

## Licence compatibility with AGPL-3.0

Grounded in the GNU list <https://www.gnu.org/licenses/license-list.html>, fetched 2026-11-24. That page states compatibility with the GNU GPL, and describes AGPLv3 as the GPLv3 terms plus a network-use paragraph; where the page does not speak to AGPL itself the verdict is `unknown`.

| Licence | AGPL-3.0 verdict | Ground |
|---|---|---|
| MIT (Expat) | yes | GNU list: Expat is permissive and GPL-compatible |
| BSD-2-Clause (FreeBSD) | yes | GNU list: permissive, GPL-compatible |
| BSD-3-Clause (Modified BSD) | yes | GNU list: permissive, GPL-compatible |
| Apache-2.0 | yes | GNU list: compatible with GPLv3 (not GPLv2) |
| LGPL-3.0 | yes | GNU list: compatible with GPLv3 |
| GPL-3.0 | unknown — question in docs/QUESTIONS.md | GPLv3 entry on the list was not parsed; the combining rule lives in the licence text, which was not fetched |
| AGPL-3.0 | yes | Same licence |
| MPL-2.0 | yes | GNU list: §3.3 gives indirect compatibility with AGPLv3 |
| CC-BY (data, docs) | yes for data/docs only | GNU list: GPL-compatible, "should not be used on software" |
| CC-BY-SA | unknown — question in docs/QUESTIONS.md | GNU list: one-way compatible with GPLv3; AGPL not stated in the part fetched |
| CC0 | yes | GNU list: public-domain dedication, GPL-compatible |
| Proprietary / source-available / unknown | no | GNU list: nonfree licences are incompatible with the GPL; `unknown` licence is treated as not usable until resolved |

**Separate-process servers.** If the verdict is `unknown` for a server we only talk to over a network or socket (e.g. a database), the entry may keep `adopt as dependency` only with a `- **Provisional:** yes, ...` line naming the exact images/builds and the open question; the question must be in docs/QUESTIONS.md. Code we link or bundle gets no such exception.

A licence not in this table is `unknown` until it is looked up and added.
