# Generation Tasks

Ordered, small, one-artifact-per-task. For each task, in your AI client (Continue,
Qwen Code, …) `@`-mention **only** the files listed — never the whole `openspec/`
folder. This keeps each prompt small enough to stay stable on a local model.

> Config (`config.yaml`) carries the Ponytail rules. Many tasks reference it; if your
> client auto-loads project context, you may not need to mention it every time.

---

## Task 1 — Gherkin feature

**Generate:** `features/authentication.feature`
**Mention:** `@specs/auth-login/spec.md`
**Prompt idea:**
> From this capability spec, write the Behave `.feature`. One scenario per Requirement.
> Merge SDD-03 and SDD-04 into a single `Scenario Outline` with an `Examples` table.
> Tag each scenario with its `@SDD-0x` ID plus `@smoke`/`@regression`/`@validation`.
> Business language only — no selectors, no waits.

**Acceptance:** four behaviors covered; tags present; no implementation detail in steps.

---

## Task 2 — Page Object (POM)

**Generate:** `pages/login_page.py`
**Mention:** `@specs/auth-login/spec.md` `@specs/auth-login/locators.md` `@config.yaml`
**Prompt idea:**
> Write the `LoginPage` Page Object. Locators from `locators.md`, declared once (P1).
> Expose `authenticate(username, password)` (P2). Put `find→clear→send_keys` in one
> private helper (P3). All reads via `WebDriverWait` (P4). Expose `alert_text()`,
> `field_error_text()`, `wait_for_dashboard()`. Add `# ponytail:` comments only where
> intent isn't obvious (P5).

**Acceptance:** no `By.*` outside this file; no `time.sleep`; business verbs only.

---

## Task 3 — Steps (glue layer)

**Generate:** `features/steps/auth_steps.py`
**Mention:** `@features/authentication.feature` `@pages/login_page.py` `@config.yaml`
**Prompt idea:**
> Write thin Behave steps that translate each Gherkin line into POM verbs. No UI logic,
> no selectors. Store credentials in `context` and submit at a single point. Each `Then`
> asserts exactly one oracle (P6), with the SDD-ID in the failure message.

**Acceptance:** steps contain zero selectors; one assert per `Then`.

---

## Task 4 — Lifecycle

**Generate:** `features/environment.py`
**Mention:** `@config.yaml`
**Prompt idea:**
> Write Behave `before_scenario` / `after_scenario`: one fresh Chrome driver per
> scenario (isolation, no shared state), maximized, quit on teardown.

**Acceptance:** one driver per scenario; clean teardown.

---

## Task 5 — Verify traceability (no generation)

**Mention:** `@specs/auth-login/spec.md` + the generated files
**Prompt idea:**
> Check that every Requirement has: a tagged scenario in the `.feature`, a step that
> implements it, and an observable oracle. List any SDD-ID missing a link.

**Acceptance:** every SDD-01..04 traces contract → spec → scenario → step → POM.

---

### Run order reference

```bash
behave                                  # full suite
behave --tags=@SDD-01                   # contract happy path (200)
behave --tags=@SDD-02,@SDD-03,@SDD-04   # error + validation regression
behave --tags=@smoke                    # deployment smoke
```
