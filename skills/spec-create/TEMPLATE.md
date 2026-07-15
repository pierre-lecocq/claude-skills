# [Feature name]

<!--
One file = one feature spec. This file lives in specs/<short-feature-slug>.md and should be
filled in before asking for implementation. Delete these HTML comments as you fill in each
section; leave a section's placeholder text if it genuinely doesn't apply (e.g. "N/A — no data
model changes"), rather than deleting the section itself.
-->

| | |
|---|---|
| **Status** | Draft \| Approved \| In progress \| Done \| Abandoned |
| **Owner** | [who is asking for / accountable for this] |
| **Date** | [YYYY-MM-DD created/last updated] |
| **Related specs** | [links to other files in specs/, or "none"] |

## What

<!-- One or two sentences. The feature in plain language, as if explaining it to a teammate who
has never seen this request before. No implementation detail yet. -->

## Why

<!-- The problem being solved or the opportunity being taken. Why does this matter now? What
happens if it's *not* built? Prefer a concrete incident, request, or metric over "it would be
nice to have". -->

## Who

<!-- Who asked for this, who consumes it once built (end users, other services, internal
tooling), and who needs to review/approve it before it ships. -->

## Context

<!-- Background needed to understand the request: how the relevant part of the system works
today, prior discussions or decisions, links to tickets/conversations. Assume the reader knows
the codebase but not this specific request. -->

## Goals

<!-- Bullet list of what this feature must achieve. Specific and testable — each goal should be
checkable as done/not-done. -->

-

## Non-goals

<!-- Explicitly out of scope, especially anything adjacent that someone might assume is included.
Prevents scope creep and mismatched expectations during review. -->

-

## Constraints

<!-- Anything that limits the solution space: deadlines, backwards-compatibility requirements,
performance/scale expectations, dependencies on other in-flight work, technical limits (e.g.
SQLite, net/http-only per CLAUDE.md), regulatory/data constraints. -->

-

## Requirements

### Functional

<!-- What the system must do, from the caller's/user's point of view. Written as behavior, not
as code — e.g. "Given an unknown esport short name, the API returns 404" rather than "add an
if-statement". -->

-

### Non-functional

<!-- Performance, security, observability, error-handling expectations that apply regardless of
the specific endpoint/feature — only list ones that matter beyond the project's existing
defaults. -->

-

## Proposed approach

<!-- The shape of the implementation, following this project's layout (see CLAUDE.md):
handlers -> services -> models. Fill in only the subsections that apply; delete the rest. -->

### API surface

<!-- New/changed endpoints: method, path, path/query params, request body, response shape,
status codes and error cases. This is the source the gen-docs skill will regenerate
docs/openapi.yml from once implemented. -->

### Data model

<!-- New/changed tables or model structs under internal/models/<name>/, and which of
find/list/create/update/delete are needed. Note any migration needed for the SQLite schema. -->

### Services / business logic

<!-- New/changed functions in internal/services/, what they orchestrate, and any non-obvious
business rules or edge cases they must encode. -->

### Out-of-repo dependencies

<!-- Any new third-party package this would require — note that CLAUDE.md restricts the HTTP
layer to net/http and test dependencies to testify/assert and go-cmp/cmp, so anything beyond
stdlib should be justified here explicitly. -->

## Alternatives considered

<!-- Other approaches that were considered and why they were rejected. Keeps future readers
(and future you) from re-litigating a decision that was already made deliberately. -->

-

## Open questions

<!-- Anything still unresolved that needs an answer before or during implementation. Remove
this section once everything is resolved, or mark each question with its resolution. -->

-

## Testing plan

<!-- How this will be verified: which layers need tests per CLAUDE.md's testing rules
(handlers via httptest, services/models against a throwaway SQLite db), and any manual/
end-to-end check beyond automated tests. The /gen-tests skill can generate the automated
tests once the code exists. -->

## Acceptance criteria

<!-- The checklist that defines "done". Should be directly derived from Goals + Requirements,
concrete enough that anyone (not just the author) can verify each item. -->

- [ ]

## Rollout notes

<!-- Anything relevant to shipping this safely: env vars to add (update .env.example and
docs/environment.md), config flags, ordering dependencies with other work, whether docs/
architecture.md needs regenerating (new layer/package/dependency) — see the gen-docs skill. -->
