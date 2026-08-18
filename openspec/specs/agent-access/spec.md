# Agent Access (MCP)

## Purpose

Lets a biohacker query their own data with their own agent through a revocable, read-only token and a lightweight MCP gateway. Low cost, high cultural impact for the hacker audience, and something no commercial competitor will ship.

## Requirements

### Requirement: Revocable read-only token
The system SHALL issue per-profile, read-only, revocable tokens for agent access, and SHALL never grant write access through this path.

#### Scenario: Token queried then revoked
- **WHEN** a user issues an agent token and later revokes it
- **THEN** queries succeed before revocation and fail immediately after
- **AND** the token can never mutate data

### Requirement: MCP gateway over encrypted context
The system SHALL expose a lightweight MCP endpoint returning the profile's data context, queryable by external agents (e.g. Claude, Cursor, a Nostr bot).

#### Scenario: External agent reads biomarkers
- **WHEN** an authorised agent queries via MCP
- **THEN** it receives the read-only biomarker/protocol context for that profile

### Requirement: Agent access respects per-item visibility
The system SHALL return through agent access only data consistent with the profile's visibility settings — withheld items are never returned; public data (including public genomics, where the user made it public) follows those settings. There is no special genomics carve-out.

#### Scenario: Withheld items not exposed
- **WHEN** an agent queries a profile
- **THEN** withheld items are not returned
- **AND** public data follows the profile's visibility settings
