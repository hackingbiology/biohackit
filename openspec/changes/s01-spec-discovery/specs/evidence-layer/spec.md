## ADDED Requirements

### Requirement: Claims Validator
The system SHALL let a visitor paste the URL of a product page and SHALL check the claims on that page against the evidence layer, without requiring an account or storing personal data. (Source: docs/hackingbiology-project-spec.md § 6 M12, phase 2.)

#### Scenario: Claims checked against evidence
- **WHEN** a visitor submits a product page URL
- **THEN** each claim found is shown with the matching evidence claims and their confidence, or marked as not found in the evidence layer
- **AND** any verdict text is labelled as AI-generated per `ai-uses-and-attribution`

#### Scenario: No personal data
- **WHEN** a visitor uses the validator
- **THEN** no personal data is required or stored

#### Scenario: Only public web pages are fetched
- **WHEN** a submitted URL is not http or https, or resolves to a private, loopback or link-local address, including after a redirect
- **THEN** the system refuses to fetch it and says why

#### Scenario: Fetch is bounded
- **WHEN** the system fetches a page
- **THEN** configured size and time limits apply and a fetch exceeding them is aborted with a clear message

#### Scenario: Anonymous use is rate-limited
- **WHEN** an anonymous client submits URLs faster than the configured rate
- **THEN** further requests are refused until the rate allows

#### Scenario: Page text is untrusted
- **WHEN** a fetched page is processed
- **THEN** the LLM only extracts candidate claims from it
- **AND** matching against evidence and confidence come from deterministic code, never from page or LLM text
