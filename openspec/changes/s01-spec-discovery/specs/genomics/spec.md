## ADDED Requirements

### Requirement: Import of consumer DNA test files
The system SHALL import raw-data files from 23andMe, AncestryDNA, MyHeritage, FTDNA, Living DNA and Illumina and SHALL report any file it cannot parse. (Source: docs/getbased-reuse-analysis.md § A6. Whether parsing runs in the browser is an implementation choice; see QUESTIONS.md Q28.)

#### Scenario: Supported file
- **WHEN** a user uploads a file from a listed provider
- **THEN** its variants are read and the actionable ones are surfaced as in "Actionable interpretation focus"

#### Scenario: Unsupported file
- **WHEN** a file is not in a supported format
- **THEN** it is rejected with the reason and nothing is stored
