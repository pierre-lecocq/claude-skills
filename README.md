# Claude skills

## /grill

Inspired by Matt Pocock [`/grill-me`](https://www.aihero.dev/skills-grill-me) skill, and adapted to the specs workflow.

Run a "grill-me"-style HITL interview — one question at a time, each with a recommended answer, grounded in the current codebase — to pressure-test and close gaps in either a freeform idea or an existing `specs/*.md` file. Use when asked to "grill this idea", "grill me on X", "/grill", or as the mandatory first step of `/spec-plan` before drafting any implementation plan.

**Install skill with**:

```sh
npx skills add pierre-lecocq/claude-skills --skill=grill -y
```

## /spec-create

Create a new feature spec file under specs/ from the bundled [template](./skills/spec-create/TEMPLATE.md) (one file = one feature) — either blank, or pre-filled from a just-completed /grill idea-mode session. Use when asked to "create a new spec", "start a spec for X", "/spec-create", or to scaffold a specs/*.md file before planning/implementing a feature.

**Install skill with**:

```sh
npx skills add pierre-lecocq/claude-skills --skill=spec-create -y
```

## /spec-plan

Turn a chosen feature spec under `specs/` (one file = one feature, scaffolded by `/spec-create`) into a concrete implementation plan for this repo, opening with the `/grill` skill's HITL interview to close spec gaps before planning. Use when asked to "plan a spec", "plan the next feature", "/spec-plan", or to turn a `specs/*.md` file into an implementation plan.

**Install skill with**:

```sh
npx skills add pierre-lecocq/claude-skills --skill=spec-plan -y
```

## /spec-audit

Scan every `specs/*.md` file and report a status dashboard plus staleness/drift findings (specs claiming Done whose code doesn't exist, specs whose code already exists but are still marked Draft, broken Related-specs links, never-filled-in template stubs, unresolved Open questions). Read-only — never edits spec files. Use when asked to "audit specs", "check spec status", "which specs are stale", or "/spec-audit".

**Install skill with**:

```sh
npx skills add pierre-lecocq/claude-skills --skill=spec-audit -y
```

## /todo-list

Scan the codebase for actionable comment markers (`@TODO`, `@FIXME`, `@BUG`, `@HACK`, `@XXX`, `@OPTIMIZE`, `@REFACTOR`, `@DEPRECATED`) and regenerate `docs/todo-list.md` — a table of tasks grouped by theme, each with a stable numeric ID and every file:line reference for that task. Use when asked to "list TODOs", "audit TODO comments", "what's left to fix in the code", or "/todo-list".

**Install skill with**:

```sh
npx skills add pierre-lecocq/claude-skills --skill=todo-list -y
```

## /reviews-list

List pull requests across configured GitHub repos relevant to a set of teams and users (authored by a configured team member, a configured team requested as reviewer, assigned to a configured user, or authored by a configured user), as a single markdown table sorted by most recently updated.

- **config file**: a user managed config file must be added in `.claude/skills/reviews-list/config.json` based on the example file from the same directory
- **argument-hint**: `[state: open|closed|merged|all]` (default open)

**Install skill with**:

```sh
npx skills add pierre-lecocq/claude-skills --skill=reviews-list -y
```
