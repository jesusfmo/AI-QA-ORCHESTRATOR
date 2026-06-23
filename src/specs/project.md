# Project: AI Orchestration — OrangeHRM Authentication Suite

> Read this first. It is the global overview an AI client should load before any task.

## Goal

A minimal, fully traceable end-to-end automation suite for the **OrangeHRM**
authentication flow, generated under Specification-Driven Development (SDD) using a
**local** AI model. The specification is the single source of truth; every test
artifact is derived from — and traceable back to — it.

## Stack

- **Language:** Python
- **Browser automation:** Selenium
- **BDD runner:** Behave
- **Code philosophy:** Ponytail (maximum efficiency, zero redundancy)
- **Spec format:** OpenSpec 1.0.0
- **Target:** OrangeHRM demo — `https://opensource-demo.orangehrmlive.com`
- **Source contract:** `POST /api/v1/auth/login` (OrangeHRM Authentication API v1.0.0)

## Traceability chain

```
OpenSpec (contract) ──► SDD Matrix (mapping) ──► Gherkin (.feature) ──► Steps + POM (Selenium)
     contract              traceability            behavior              implementation
```

Each behavior carries an `SDD-0x` ID from contract through to the assertion, so a
change in the contract propagates traceably: contract → spec → scenario → step → POM.

## Target project layout (Ponytail: one responsibility per file)

```
project/
├── features/
│   ├── authentication.feature    # generated from specs/auth-login/spec.md
│   ├── environment.py            # driver lifecycle
│   └── steps/
│       └── auth_steps.py         # glue layer (Gherkin → POM verbs)
├── pages/
│   └── login_page.py             # Page Object (selectors live here only)
└── openspec/                     # this spec layer
```

## Capabilities

| Capability   | Folder                  | Status   |
|--------------|-------------------------|----------|
| `auth-login` | `specs/auth-login/`     | Specified |

Future capabilities (dashboard, PIM, leave, …) each get their own folder.
