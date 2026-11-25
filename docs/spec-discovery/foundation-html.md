# Spec discovery register — part D2b3: foundation page

Source compared with `openspec/specs/**`: `docs/foundation.html` (8 `<h2>` sections). It is the HTML version of `docs/foundation.md`, so every row is first matched against the part A register `docs/spec-discovery/whitepaper.md` and reuses its status and requirement. Legal, governance and funding facts that describe no product behaviour are `out-of-scope`. Open items are in `docs/QUESTIONS.md` (Q39), not requirements.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour, or a decision not taken; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/foundation.html § 1. Why two names, one mission | Software (biohack.it) and non-profit steward (Hacking Biology Foundation) are separate; the steward is the guarantor of the mission | added | community-and-social/Stewardship and mission lock are published | Same as part A foundation.md § 1 |
| docs/foundation.html § 2. Incorporation & ownership | Incorporation seat (Roatán, Próspera ZEDE) and Foundation ownership of software, brand, trademark and copyright | out-of-scope | — | Legal structure; the user-visible part is the published stewardship statement. Same as part A foundation.md § 2 |
| docs/foundation.html § 2. Incorporation & ownership | Incorporation is separate from data hosting; data-protection duties are met at the hosting layer | out-of-scope | — | Hosting jurisdiction is still open in the source and no behaviour is stated. Same as part A foundation.md § 2; see Q39 |
| docs/foundation.html § 3. What the Foundation guarantees (the mission lock) | Never commercial, never sold, never a walled garden | added | community-and-social/Knowledge is not for sale | Same as part A foundation.md § 3 |
| docs/foundation.html § 3. What the Foundation guarantees (the mission lock) | Software under AGPL-3.0; anyone can run their own instance | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | Same as part A foundation.md § 3 |
| docs/foundation.html § 3. What the Foundation guarantees (the mission lock) | Public dataset released as a clonable snapshot; content under open licences | added | analytics-and-open-data/Open licences declared on published data and content | Same as part A foundation.md § 3 |
| docs/foundation.html § 3. What the Foundation guarantees (the mission lock) | Harm reduction first; safety guardrails non-optional; describes, never prescribes | added | safety-guardrails/Platform describes and never prescribes | Same as part A foundation.md § 3 |
| docs/foundation.html § 3. What the Foundation guarantees (the mission lock) | Where AI is and is not used is published (AI surfaces map) | covered | ai-uses-and-attribution/Published AI surfaces map — "what is AI, what is NOT AI" | Same as part A foundation.md § 3 |
| docs/foundation.html § 3. What the Foundation guarantees (the mission lock) | Every reused upstream is attributed and notified | covered | ai-uses-and-attribution/Notify upstreams of their inclusion | Same as part A foundation.md § 3 |
| docs/foundation.html § 3. What the Foundation guarantees (the mission lock) | Full export always; the individual owns the record | added | accounts-and-profiles/Full personal data export | Same as part A foundation.md § 3 |
| docs/foundation.html § 4. Governance | Foundation holds domain, trademark, copyright and canonical instance; cannot relicense away from AGPL | out-of-scope | — | Legal and organisational. Same as part A foundation.md § 4 |
| docs/foundation.html § 4. Governance | Board is a basket of biohackers and software hackers | out-of-scope | — | Organisational. Same as part A foundation.md § 4; first members open, see Q39 |
| docs/foundation.html § 4. Governance | ADRs and specs are public from day one | added | community-and-social/Specification is publicly browsable | Same as part A foundation.md § 4 |
| docs/foundation.html § 4. Governance | Community governance attaches to Rapamycin News, not a cold-launched forum | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | Same as part A foundation.md § 4 |
| docs/foundation.html § 4. Governance | Contested claims are public and discussed | covered | community-and-social/Public claim review | Same as part A foundation.md § 4 |
| docs/foundation.html § 4. Governance | Study proposals are public and discussed | covered | community-and-social/Host study proposals for comment and consensus | Same as part A foundation.md § 4 |
| docs/foundation.html § 5. Sustainability | Funded only by public grants; possible equity in aligned startups | out-of-scope | — | Funding model. Same as part A foundation.md § 5; grant programmes open, see Q39 |
| docs/foundation.html § 5. Sustainability | Knowledge never for sale; no supplier can buy influence over which protocols emerge | added | community-and-social/Knowledge is not for sale | Same as part A foundation.md § 5 |
| docs/foundation.html § 6. Public presence — two sites, two jobs | biohack.it is the product site and hackingbiology.com the organisation site; About links to the Foundation | added | community-and-social/Stewardship and mission lock are published | Same as part A foundation.md § 6. hackingbiology.com is rebuilt outside this repository |
| docs/foundation.html § 7. Risks & mitigations | Mission drift, funding pressure, regulatory qualification and jurisdiction risks mitigated by charter, grants, mixed board and hosting-layer data protection | out-of-scope | — | Organisational mitigations. Same as part A foundation.md § 7 |
| docs/foundation.html § 7. Risks & mitigations | Capture of the canonical instance is countered by full clonability and self-hosting | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | Same as part A foundation.md § 7 |
| docs/foundation.html § 7. Risks & mitigations | Descriptive-not-prescriptive posture by design to avoid medical-device qualification | added | safety-guardrails/Platform describes and never prescribes | Same as part A foundation.md § 7. The legal review before launch is a process step, not software |
| docs/foundation.html § Resolved (Fabio) & still open | Resolved decisions (seat, ownership, board, grants; no conflict-of-interest charter) and open items (hosting jurisdiction, first board members, grant programmes) | out-of-scope | — | Status log of organisational decisions. Same as part A foundation.md § Resolved and still open; open items go to Q39 |
