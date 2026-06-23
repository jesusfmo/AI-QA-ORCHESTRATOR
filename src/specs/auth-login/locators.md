# auth-login — Known UI locators (implementation reference)

> The AI model **cannot see the live DOM**, so it cannot guess selectors reliably.
> This file gives the verified locators for the OrangeHRM demo. Mention it (`@locators.md`)
> only when generating the Page Object. These are the single source of truth (rule P1);
> no step or feature file should ever contain a selector.

**Base URL**

```
https://opensource-demo.orangehrmlive.com/web/index.php/auth/login
```

**Locators (OrangeHRM demo, current markup)**

| Name        | Strategy            | Value                                | Used by                          |
|-------------|---------------------|--------------------------------------|----------------------------------|
| USERNAME    | `By.NAME`           | `username`                           | typing credentials               |
| PASSWORD    | `By.NAME`           | `password`                           | typing credentials               |
| SUBMIT      | `By.CSS_SELECTOR`   | `button[type='submit']`              | submitting the form              |
| ALERT       | `By.CSS_SELECTOR`   | `.oxd-alert-content-text`            | invalid-credentials oracle (401) |
| FIELD_ERROR | `By.CSS_SELECTOR`   | `.oxd-input-field-error-message`     | required-field validation        |

**Notes**

- OrangeHRM is an Angular app; element rendering is asynchronous → all reads must go
  through `WebDriverWait` (rule P4), never `time.sleep`.
- The success oracle is `EC.url_contains("/dashboard")`, not a token or the alert.
- These selectors are the most likely thing to drift if OrangeHRM updates its UI.
  If a test breaks on a selector, fix it here only.
