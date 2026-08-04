# Procurement & Inventory (M4)

## Purpose

Turns a protocol into a supply plan and a daily intake schedule, optimising bioavailability and avoiding interactions and toxicity summation. Phase 3. No commercial integration with suppliers in the initial phase — the main conflict-of-interest surface to keep clean.

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

### Requirement: Day-schedule optimisation
The system SHALL allocate intakes into day slots optimising bioavailability and avoiding interference and toxicity summation (e.g. mineral separation, food/fasting, hepatic load), using a constraint solver rather than an LLM.

#### Scenario: Competing compounds separated
- **WHEN** two compounds should not be co-administered
- **THEN** the schedule places them in separated slots with a stated reason

### Requirement: No monetised procurement initially
The system SHALL NOT monetise procurement or embed supplier affiliations in the initial phase.

#### Scenario: Neutral sourcing
- **WHEN** sourcing information is shown
- **THEN** it carries no paid placement or affiliate incentive
