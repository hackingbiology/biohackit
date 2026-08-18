# Procurement & Inventory (M4)

## Purpose

Turns a protocol into a supply plan — projected need, batch purchase, inventory, lots and expiry — and links to Pills Management for restock. Daily intake scheduling lives in `pills-management`. Phase 3. No commercial integration with suppliers in the initial phase — the main conflict-of-interest surface to keep clean.

## Requirements

### Requirement: Projected need from protocol
The system SHALL project consumption from the active protocol and derive batch purchase suggestions with lead time.

#### Scenario: Reorder before stock-out
- **WHEN** projected consumption will exhaust a stock before its lead time elapses
- **THEN** the system raises a reorder alert in time

### Requirement: Inventory with lots and expiry
The system SHALL track stock, lots, and expiry, and alert on expiring stock.

#### Scenario: Expiry alert
- **WHEN** a lot approaches expiry
- **THEN** the system alerts and reflects it in the projected need

### Requirement: No monetised procurement initially
The system SHALL NOT monetise procurement or embed supplier affiliations in the initial phase.

#### Scenario: Neutral sourcing
- **WHEN** sourcing information is shown
- **THEN** it carries no paid placement or affiliate incentive
