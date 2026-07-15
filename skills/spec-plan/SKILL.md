---
name: spec-plan
description: Turn a chosen feature spec under specs/ (one file = one feature, scaffolded by /spec-create) into a concrete implementation plan for this repo, opening with the /grill skill's HITL interview to close spec gaps before planning. Use when asked to "plan a spec", "plan the next feature", "/spec-plan", or to turn a specs/*.md file into an implementation plan.
disable-model-invocation: false
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - AskUserQuestion
  - EnterPlanMode
  - ExitPlanMode
  - Agent
---

# spec-plan

Plans a feature's implementation starting from one spec file in `specs/`, rather than from an
ad-hoc description. The spec is the primary source of truth for scope, constraints, and
acceptance criteria.

Before any plan gets drafted, this skill's first real action is delegating to the `grill` skill:
a focused, one-question-at-a-time HITL interview (the ["grill-me"](https://www.aihero.dev/skills-grill-me)
pattern) that pressure-tests the spec and closes its gaps rather than silently guessing through
them. Treat that phase as mandatory, not optional busywork — it's the whole reason to plan from a
written spec instead of an ad-hoc prompt.

## 0. Skip straight to a pre-selected spec, if there is one

If this invocation already names a specific spec file — passed as this skill's `args` (e.g.
`/spec-create` invoking `spec-plan specs/<slug>.md` right after scaffolding it) — skip steps 1
and 2 entirely and jump straight to step 3 with that file. Don't re-ask which spec to plan when
the caller already told you; that defeats the point of chaining the two skills.

Otherwise, continue with step 1.

## 1. Find the candidate specs

1. `Glob specs/*.md`.
2. If no spec files exist, say so and stop — suggest running `/spec-create` to scaffold one
   first. Don't invent a plan from nothing.
3. For each candidate file, peek at its title (first `#` heading) and its `Status` table row so
   the choice can be presented meaningfully, not just as bare file paths.

## 2. Ask which spec to plan

Always ask, via `AskUserQuestion`, which spec to plan — never guess from conversation context,
even if only one spec file exists. Offer each spec found as an option, labeled with its feature
title and status (e.g. `Add match reminders (Draft)`), description with a one-line summary from
its "What" section. If there are more than 4 specs, offer the 4 most recently modified and let
the user type another path as a custom answer.

## 3. Grill the chosen spec

Invoke the `grill` skill directly against the chosen file — e.g. `Skill(skill: "grill", args:
"specs/<slug>.md")` — as the first substantive step, before this skill does any reading, code
grounding, or plan drafting of its own. `grill` handles all of that itself: reading the spec in
full, grounding it in the current codebase, running the one-question-at-a-time interview, and
recording each resolved answer back into the spec file. Don't re-implement any part of that
here — by the time this step returns, the spec already reflects every resolved decision (and
any survived-unresolved open questions are visible in `grill`'s final report).

## 4. Draft the plan

Re-read the spec file first — `grill` likely edited it, and the plan must be drafted from the
final, resolved version, not whatever it looked like before step 3. Then call `EnterPlanMode`
before writing the plan. Structure the plan around this repo's layout (per `CLAUDE.md`'s
"Patterns" section), covering only the layers the spec actually touches:

- **Models** (`internal/models/<name>/{find,list,create,update,delete}.go`): new/changed structs
  and raw-SQL functions, and any schema change they imply.
- **Services** (`internal/services/*.go`): new/changed orchestration functions and the business
  rules/edge cases they must encode, per the spec's Requirements.
- **Handlers** (`internal/handlers/*.go`) and route registration: new/changed endpoints, request
  parsing, response/error shapes — matching the spec's "API surface" section.
- **Middleware**, if the spec calls for cross-cutting behavior.
- **Tests**: which layers need coverage and how, per the spec's "Testing plan" and this repo's
  testing rules (`httptest` for handlers, a throwaway SQLite db for services/models) — note that
  `/gen-tests` can generate these once the code exists, rather than planning to hand-write them.
  Independently, verify the spec's actual acceptance criteria are covered by the plan.
- **Docs**: call out that `docs/openapi.yml` (and `docs/environment.md`/`docs/architecture.md` if
  env vars or layers change) need regenerating once implemented — the `gen-docs` skill handles
  this, don't hand-draft the OpenAPI spec in the plan.
- **Sequencing**: order the steps bottom-up (models → services → handlers → tests → docs) unless
  the spec's constraints demand otherwise.

Call out any open questions that survived the grill step unresolved — because the user chose to
proceed without answering — and how the plan handles them (e.g. "assumed X, per the grill
session").

## 5. Get approval

Call `ExitPlanMode` with the drafted plan for the user's approval before writing any code.

## 6. After approval (optional bookkeeping)

If the user proceeds with implementation in the same session, offer to update the spec file's
`Status` row (e.g. `Draft` → `In progress`) once work begins, and to `Approved`/`Done` as it
completes — but only touch that one table cell, never rewrite the rest of the spec.
