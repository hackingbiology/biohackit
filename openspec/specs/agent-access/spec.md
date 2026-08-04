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

### Requirement: Genomics excluded from agent access
The system SHALL exclude genomic-derived data from anything returned through agent access.

#### Scenario: Genomics not exposed to agents
- **WHEN** an agent queries a profile that has genomic data
- **THEN** the response contains no genomic-derived fields
