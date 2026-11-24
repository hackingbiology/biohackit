## ADDED Requirements

### Requirement: Quick actions on the dashboard
The system SHALL show on the dashboard a column of quick actions, each with a title and an explanatory subtitle. (Source: docs/hackingbiology-project-spec.md § 8.5ter.)

#### Scenario: Each action explains itself
- **WHEN** a user opens the dashboard
- **THEN** every quick action shows a title and a subtitle saying what it does

### Requirement: Trend alerts
The system SHALL raise an alert when a biomarker series shows a sustained slope, a sudden jump or a critical out-of-range value, using a regression with thresholds on slope and goodness of fit, and SHALL NOT raise a trend alert from insufficient data. (Source: docs/getbased-reuse-analysis.md § A4. The source gives no thresholds; see QUESTIONS.md Q25.)

#### Scenario: Sustained trend
- **WHEN** a series has enough points and its fitted slope and fit exceed the declared thresholds
- **THEN** a trend alert is raised stating the slope, the fit and the points used

#### Scenario: Sudden jump
- **WHEN** a new value departs abruptly from the preceding series
- **THEN** a jump alert is raised naming the two values and their dates

#### Scenario: Too few points
- **WHEN** a series has fewer points than the declared minimum
- **THEN** no trend alert is raised and the chart says the data is insufficient

### Requirement: Intervention timeline overlaid on biomarker chart
The system SHALL draw the person's interventions (supplements, drugs, therapies) as a timeline over each biomarker chart, together with the reference and optimal range bands. (Source: docs/getbased-reuse-analysis.md § A5, "intervento × biomarcatore".)

#### Scenario: Chart shows when an intervention was active
- **WHEN** a user opens a biomarker chart
- **THEN** each intervention appears as a span from its start to its end, labelled with its protocol version
- **AND** the reference and optimal bands are drawn with their sources

#### Scenario: Accessible alternative
- **WHEN** a user cannot see the chart
- **THEN** a table lists each measurement with the interventions active on that date

### Requirement: Time-limited password-protected sharing link
The system SHALL let a user create a sharing link for their profile or doctor sheet that expires and is protected by a password, usable without an account for the recipient, and revocable at any time. (Source: docs/getbased-reuse-analysis.md § B8. The source gives no lifetime; see QUESTIONS.md Q27.)

#### Scenario: Recipient opens the link
- **WHEN** a recipient opens a valid link and enters the password
- **THEN** they see the shared view without registering

#### Scenario: Link expired or revoked
- **WHEN** a link has expired or was revoked
- **THEN** it shows nothing of the shared data

#### Scenario: Wrong password
- **WHEN** a wrong password is entered
- **THEN** no shared data is shown

#### Scenario: Repeated wrong passwords are throttled
- **WHEN** wrong passwords are entered repeatedly for one link
- **THEN** further attempts are delayed or the link is locked, and the owner can see that attempts failed
- **AND** the number of attempts allowed is not fixed by this requirement; see QUESTIONS.md Q31

#### Scenario: Link shows only selected items
- **WHEN** a recipient opens a valid link
- **THEN** only the items the owner selected for sharing are shown
- **AND** no withheld item is shown or can be reached from the link
