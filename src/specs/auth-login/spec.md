# Capability: auth-login

Authenticate a registered OrangeHRM user through the login form, enforcing the
`POST /api/v1/auth/login` contract at the UI level. The success oracle is the
**observable effect** of each HTTP response, verified through Selenium — not the
HTTP response itself.

## Requirements

### Requirement: Successful authentication with valid credentials
The system SHALL grant access and redirect the user to the Dashboard when valid
credentials are submitted.
_Traces: SDD-01 · contract `responses.200` (Direct)._

#### Scenario: Valid credentials redirect to the Dashboard
- **GIVEN** the user is on the login page
- **WHEN** the user submits username "Admin" and password "admin123"
- **THEN** the browser redirects to a URL containing "/dashboard"
- **AND** the Dashboard renders

### Requirement: Rejection of invalid credentials
The system SHALL deny access and display the "Invalid credentials" alert when
invalid credentials are submitted.
_Traces: SDD-02 · contract `responses.401` (Direct)._

#### Scenario: Invalid credentials are rejected
- **GIVEN** the user is on the login page
- **WHEN** the user submits username "Admin" and password "wrong_password"
- **THEN** the user remains on "/auth/login"
- **AND** the alert "Invalid credentials" is shown

### Requirement: Required-field validation for username
The system SHALL block submission and show the "Required" validation error on the
username field when the username is empty. Client-side validation is the contract's
first line of defense for `schema.required`.
_Traces: SDD-03 · contract `schema.required` (Derived)._

#### Scenario: Missing username is blocked client-side
- **GIVEN** the user is on the login page
- **WHEN** the user submits an empty username and password "admin123"
- **THEN** the username field shows the "Required" validation error
- **AND** no request is sent to the backend

### Requirement: Required-field validation for password
The system SHALL block submission and show the "Required" validation error on the
password field when the password is empty.
_Traces: SDD-04 · contract `schema.required` (Derived)._

#### Scenario: Missing password is blocked client-side
- **GIVEN** the user is on the login page
- **WHEN** the user submits username "Admin" and an empty password
- **THEN** the password field shows the "Required" validation error
- **AND** no request is sent to the backend

## Notes

- **Literal strings.** "Invalid credentials", "Required", "username", and "password"
  are rendered by OrangeHRM (or are HTML attribute names). They are asserted verbatim.
  If the instance changes locale, update them only in the Page Object locators
  (`locators.md`), the single source of truth (rule P1).
- **Why the UI is the oracle.** The contract is a JSON API, but the user flow goes
  through the form. Selenium verifies the observable effect of each response code,
  not the HTTP contract directly.
- **`.feature` mapping.** SDD-03 and SDD-04 share one `Scenario Outline` in the
  generated `authentication.feature` (parametrized by an `Examples` table), so adding
  an edge case is adding a row, not a scenario.
