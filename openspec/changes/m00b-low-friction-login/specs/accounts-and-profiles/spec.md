## ADDED Requirements

### Requirement: Low-friction sign-in
The system SHALL let a person register and sign in with an existing identity — rapamycin.news (DiscourseConnect), Google, Microsoft, Apple, Facebook/Meta, WeChat — or passwordless (email code, passkey), in addition to email + password, using django-allauth as the single authentication library.

#### Scenario: Sign up with the rapamycin.news forum account
- **WHEN** a visitor chooses "Continue with rapamycin.news" and approves on the forum
- **THEN** the system verifies the DiscourseConnect payload signature (HMAC-SHA256) and nonce, and creates or signs in the account
- **AND** the profile gets a `rapamycin_news` social handle with the forum username and profile URL
- **AND** a tampered signature or a reused nonce is rejected

#### Scenario: Only configured providers are shown
- **WHEN** an instance has credentials for some providers only
- **THEN** the sign-in page shows exactly those providers, and works with none configured

#### Scenario: Passwordless sign-in
- **WHEN** a user requests an email login code, or uses a registered passkey
- **THEN** they are signed in without a password

#### Scenario: Linking does not hijack accounts
- **WHEN** a social login returns an email that matches an existing account
- **THEN** the accounts are connected automatically only if the provider marks the email verified; otherwise the user must sign in to the existing account first

#### Scenario: Minimal scopes
- **WHEN** any provider is configured
- **THEN** only identity scopes (openid/email/profile or the provider equivalent) are requested
