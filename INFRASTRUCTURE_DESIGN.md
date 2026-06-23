# INFRASTRUCTURE_DESIGN.md

> **Project:** AI Orchestration — E2E automation suite for OrangeHRM authentication
> **Approach:** Specification-Driven Development (SDD)
> **Stack:** Python · Selenium · Behave (BDD) · Ponytail (minimalist code philosophy) · OpenSpec 1.0.0
> **Source contract:** `POST /api/v1/auth/login` (OrangeHRM Authentication API v1.0.0)

---

## 0. Context & Traceability

This document translates a **declarative contract** (OpenSpec) into **executable behavior** (Behave) under the SDD philosophy: the specification is the single source of truth, and every test artifact is derived from — and traceable back to — it.

Traceability chain:

```
OpenSpec (contract)  ──►  SDD Matrix (mapping)  ──►  Gherkin (.feature)  ──►  Steps + POM (Selenium)
     contract                traceability             behavior                implementation
```

Minimal project layout (Ponytail: one responsibility per file):

```
project/
├── features/
│   ├── authentication.feature        # Official Gherkin (section 2)
│   ├── environment.py                # driver lifecycle
│   └── steps/
│       └── auth_steps.py             # glue layer / steps (section 3)
├── pages/
│   └── login_page.py                 # simplified Page Object (section 3)
└── INFRASTRUCTURE_DESIGN.md
```

---

## 1. Contract-to-BDD Mapping (SDD Matrix)

The matrix decomposes each clause of the OpenSpec JSON into its expected behavior at the **API** level (contract) and its observable manifestation at the **UI/Selenium** level (E2E verification).

| ID | Method + Path | Payload / Field | HTTP Code | API behavior (contract) | Expected UI behavior (Selenium) | BDD Scenario | Origin |
|----|---------------|-----------------|:---------:|-------------------------|---------------------------------|--------------|--------|
| **SDD-01** | `POST /api/v1/auth/login` | `{username:"Admin", password:"admin123"}` | `200` | Successful login; returns token and redirect to Dashboard | Browser redirects to a URL containing `/dashboard`; the Dashboard header renders | `Successful login with valid credentials` | **Direct** (spec `responses.200`) |
| **SDD-02** | `POST /api/v1/auth/login` | invalid `{username, password}` | `401` | Invalid credentials; access denied | Stays on `/auth/login`; the `Invalid credentials` alert is shown | `Failed login with invalid credentials` | **Direct** (spec `responses.401`) |
| **SDD-03** | `POST /api/v1/auth/login` | `username` missing | *(validation)* | Violates `required: ["username"]`; the request must not be built | The *username* field shows the `Required` validation error; no submit to the backend | `Required-field validation` | **Derived** (spec `schema.required`) |
| **SDD-04** | `POST /api/v1/auth/login` | `password` missing | *(validation)* | Violates `required: ["password"]`; the request must not be built | The *password* field shows the `Required` validation error | `Required-field validation` | **Derived** (spec `schema.required`) |

**SDD derivation notes**

- Rows marked **Direct** map 1:1 to a response code declared in `paths./api/v1/auth/login.post.responses`.
- Rows marked **Derived** are not response codes but **contract preconditions** inferred from the `schema.required` array. SDD requires testing them because the contract asserts both fields are mandatory: client-side validation is the contract's first line of defense.
- The contract describes a JSON API, but verification happens over the **UI** because the real user flow goes through the form. The *API behavior* column preserves the conceptual link; the *UI behavior* column defines Selenium's observable oracle.
- **On literal strings:** `Invalid credentials`, `Required`, `username`, and `password` are literal strings rendered by OrangeHRM (or HTML attribute names). They are asserted verbatim; changing them would break the tests. If the instance is reconfigured to another locale, update these strings in a single location (section 3.2).

---

## 2. Official Gherkin Specification (BDD)

File: `features/authentication.feature`. Default English Gherkin syntax. Each scenario references its SDD Matrix ID via tags to preserve traceability.

```gherkin
Feature: User authentication in OrangeHRM
  As a registered OrangeHRM user
  I want to authenticate with my credentials
  So that I can access the application Dashboard

  Background:
    Given the user is on the login page

  @smoke @happy_path @SDD-01
  Scenario: Successful login with valid credentials
    When the user enters username "Admin" and password "admin123"
    And submits the authentication form
    Then the system grants access
    And the user is redirected to the Dashboard

  @regression @alternate_path @SDD-02
  Scenario: Failed login with invalid credentials
    When the user enters username "Admin" and password "wrong_password"
    And submits the authentication form
    Then the system denies access
    And the error message "Invalid credentials" is shown

  @regression @validation @SDD-03 @SDD-04
  Scenario Outline: Required-field contract validation
    When the user enters username "<username>" and password "<password>"
    And submits the authentication form
    Then the validation message "Required" is shown on the "<field>" field

    Examples:
      | username | password | field    |
      |          | admin123 | username |
      | Admin    |          | password |
```

**BDD design decisions**

- **Contract coverage:** the happy path (`@SDD-01`) covers `responses.200`; the alternate path (`@SDD-02`) covers `responses.401`; the `Scenario Outline` covers the `required` clause (`@SDD-03`/`@SDD-04`) without duplicating steps.
- **Business language, not implementation:** steps describe *what* happens ("grants access", "denies access"), never *how* (selectors, waits). Technical detail lives in the step and POM layer (section 3).
- **Data outside behavior:** the `Examples` table parametrizes the validation; adding an edge case is adding a row, not a scenario.
- **Tags as a living contract:** `@SDD-0x` allows selective regression against a specific OpenSpec clause (`behave --tags=@SDD-02`).
- **String note:** quoted strings (`"Invalid credentials"`, `"Required"`) are literal UI text and are asserted verbatim (see note in section 1).

---

## 3. Ponytail Style Guide for the Steps

Ponytail applied to Selenium automation = **maximum efficiency, zero redundancy, and `# ponytail: [reason]` comments only when a technical decision is not self-evident**. Clean code is not commented; whatever departs from the obvious is.

### 3.1 Ponytail rules (style contract)

| # | Rule | Rationale |
|---|------|-----------|
| P1 | **Single selector:** each locator is declared exactly once, in the Page Object. No step contains a `By.*`. | Removes the most expensive duplication to maintain in E2E. |
| P2 | **Minimal public action:** the POM exposes business verbs (`authenticate`), not per-field micro-operations. | Steps orchestrate business, not widgets. |
| P3 | **Private helper for repeated patterns:** `find → clear → send_keys` lives once. | Zero redundancy. |
| P4 | **Explicit waits, never `sleep`:** deterministic synchronization via `WebDriverWait`. | Efficiency and stability; bans blind waiting. |
| P5 | **Comment only if it justifies:** `# ponytail: [reason]` exclusively when the *why* is not readable in the *what*. | The comment is a reasoned exception, not decoration. |
| P6 | **One assert, one oracle:** each `Then` step validates exactly one contract assertion. | Readable failures, traceable to the SDD Matrix. |

### 3.2 Simplified Page Object (POM) — `pages/login_page.py`

Abstract POM structure. Note how `# ponytail:` comments appear **only** where intent is not obvious:

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    # ponytail: locators grouped as the single source of truth (rule P1);
    #           no step re-declares a selector. The only place to touch if the
    #           instance changes locale or markup.
    _USERNAME   = (By.NAME, "username")
    _PASSWORD   = (By.NAME, "password")
    _SUBMIT     = (By.CSS_SELECTOR, "button[type='submit']")
    _ALERT      = (By.CSS_SELECTOR, ".oxd-alert-content-text")
    _FIELD_ERR  = (By.CSS_SELECTOR, ".oxd-input-field-error-message")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def authenticate(self, username, password):
        # Public business verb (P2): the step is unaware of individual fields.
        self._type(self._USERNAME, username)
        self._type(self._PASSWORD, password)
        self.driver.find_element(*self._SUBMIT).click()

    def alert_text(self):
        return self.wait.until(
            EC.visibility_of_element_located(self._ALERT)
        ).text

    def field_error_text(self):
        return self.wait.until(
            EC.visibility_of_element_located(self._FIELD_ERR)
        ).text

    def wait_for_dashboard(self):
        # ponytail: the success oracle is the Dashboard URL, not the token;
        #           Selenium verifies the observable effect of the 200, not the HTTP contract.
        return self.wait.until(EC.url_contains("/dashboard"))

    def _type(self, locator, value):
        # ponytail: private helper absorbing the find->clear->send_keys pattern (P3);
        #           empty value "" is allowed on purpose to trigger the Required validation.
        field = self.driver.find_element(*locator)
        field.clear()
        field.send_keys(value)
```

### 3.3 Steps (glue layer) — `features/steps/auth_steps.py`

Steps are thin: they translate Gherkin language into POM verbs. They contain no UI logic.

```python
from behave import given, when, then
from pages.login_page import LoginPage

BASE_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"


@given("the user is on the login page")
def step_open_login(context):
    context.driver.get(BASE_URL)
    context.login = LoginPage(context.driver)


@when('the user enters username "{username}" and password "{password}"')
def step_capture_credentials(context, username, password):
    # ponytail: credentials are stored in context and sent at a single point
    #           (submit step), avoiding re-typing the form.
    context.credentials = (username, password)


@when("submits the authentication form")
def step_submit(context):
    context.login.authenticate(*context.credentials)


@then("the system grants access")
def step_access_granted(context):
    assert context.login.wait_for_dashboard(), "Access was not granted (SDD-01)"


@then("the user is redirected to the Dashboard")
def step_redirect_dashboard(context):
    assert "/dashboard" in context.driver.current_url


@then("the system denies access")
def step_access_denied(context):
    assert "/auth/login" in context.driver.current_url, "Access was not denied (SDD-02)"


@then('the error message "{message}" is shown')
def step_validate_alert(context, message):
    assert context.login.alert_text() == message


@then('the validation message "{message}" is shown on the "{field}" field')
def step_validate_required_field(context, message, field):
    # ponytail: the contract requires username and password (schema.required); this step
    #           verifies the client blocks submission before reaching the backend.
    assert context.login.field_error_text() == message
```

### 3.4 Lifecycle — `features/environment.py`

```python
from selenium import webdriver


def before_scenario(context, scenario):
    # ponytail: one driver per scenario guarantees isolation; no shared state.
    context.driver = webdriver.Chrome()
    context.driver.maximize_window()


def after_scenario(context, scenario):
    context.driver.quit()
```

### 3.5 Ponytail anti-patterns (reject in code review)

- ❌ `time.sleep(3)` → violates **P4**. Use `WebDriverWait`.
- ❌ `By.NAME, "username"` inside a step → violates **P1**. The selector lives in the POM.
- ❌ A step that opens the field, clears it and types → violates **P2/P3**. That is `authenticate()`.
- ❌ A comment restating the code (`# click the button`) → violates **P5**. If the code reads, it is not commented.
- ❌ A `Then` with two or more asserts → violates **P6**. Split into atomic steps.

---

## 4. Execution & traceability verification

```bash
# Full suite
behave

# Contract happy path only (responses.200)
behave --tags=@SDD-01

# Contract error regression only (401 + required-field validations)
behave --tags=@SDD-02,@SDD-03,@SDD-04

# Deployment smoke tests
behave --tags=@smoke
```

Every row in the **SDD Matrix** has a homonymous tag in the `.feature`, a step that implements it, and an observable oracle. If an OpenSpec clause changes, the change propagates traceably: contract → matrix → scenario → step → POM.