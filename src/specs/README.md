# openspec/

Spec layer for the **AI Orchestration** project: an E2E automation suite for
OrangeHRM authentication, built with Specification-Driven Development (SDD).

This folder is the decomposition of the original monolithic `INFRASTRUCTURE_DESIGN.md`
into small, load-on-demand artifacts. The point: a local 7B model (and a context-limited
GPU) can read **one small slice at a time** instead of a 13 KB monolith that overflows
the context window.

## Structure

```
openspec/
├── README.md                     # this file
├── project.md                    # project overview (read first)
├── config.yaml                   # stack context + Ponytail rules (conventions)
├── GENERATION_TASKS.md           # ordered generation tasks for the AI client
└── specs/
    └── auth-login/               # the single capability: authentication
        ├── spec.md               # behavior contract (Requirements + Scenarios)
        └── locators.md           # known OrangeHRM DOM locators (impl reference)
```

## The three concerns, kept separate

| Concern         | Lives in            | Nature                          |
|-----------------|---------------------|---------------------------------|
| Conventions     | `config.yaml`       | Ponytail style, applies to all  |
| Behavior (what) | `specs/.../spec.md` | The contract; source of truth   |
| Implementation  | generated code      | The how; output, not input      |

## Workflow with a local AI client (Continue / Qwen Code)

Never feed the whole folder. For each task, mention only the slice it needs:

1. Pick a task from `GENERATION_TASKS.md`.
2. In the chat, `@`-mention the small files that task lists (e.g. `@spec.md` `@config.yaml`).
3. Generate one artifact. Review against the Ponytail rules and the SDD-IDs.
4. Move to the next task.

One capability → one spec. When the project grows (dashboard, PIM, leave, …),
each new feature becomes a new capability folder under `specs/`.
