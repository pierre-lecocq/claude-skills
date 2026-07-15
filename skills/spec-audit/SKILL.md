---
name: spec-audit
description: Scan every specs/*.md file and report a status dashboard plus staleness/drift findings (specs claiming Done whose code doesn't exist, specs whose code already exists but are still marked Draft, broken Related-specs links, never-filled-in template stubs, unresolved Open questions). Read-only — never edits spec files. Use when asked to "audit specs", "check spec status", "which specs are stale", or "/spec-audit".
disable-model-invocation: false
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
---

# spec-audit

Gives a point-in-time snapshot of every feature spec under `specs/` — not just their `Status`
field, but whether that status still matches reality. This is a reporting skill: it never edits
`specs/*.md` itself, even when it finds something to fix; it flags findings for the user to act
on (directly, or via `/spec-plan`'s own bookkeeping step).

## 1. Find the specs

`Glob specs/*.md`. If none exist, say so and stop — suggest `/spec-create` if the user seems to
want one, but don't invent findings from nothing.

## 2. Parse each spec's metadata

For each file, read it in full (not just the header) and extract:

- Title (first `#` heading).
- `Status`, `Owner`, `Date`, `Related specs` from the metadata table.
- Whether the body still contains unfilled template scaffolding — HTML comments (`<!-- ... -->`)
  left in place in required sections (What/Why/Goals/Requirements) with no actual prose added
  around them — meaning the spec was created but never actually authored.
- Whether **Open questions** still has unresolved content (anything beyond a "none remaining"
  statement).
- Every file path, function/type name, route, or package mentioned in **Proposed approach**
  (API surface / Data model / Services / business logic) — this is what step 3 checks against the
  real codebase.
- Every entry in **Related specs**, so step 3 can confirm those files still exist.

## 3. Cross-check against the current codebase

For each spec's extracted references:

- If a route/handler/service/model is named, `Grep`/`Read` to confirm it actually exists as
  described — don't assume the spec is accurate. If the codebase is large or the spec's scope is
  broad, delegate this survey to the `Explore` agent instead of guessing.
- **Status says `Done` or `Approved`, but the referenced code doesn't exist (or only partially
  does)** — flag as drift: either the work stalled after the status was bumped, or the status was
  updated prematurely.
- **Status says `Draft`/`In progress`, but the referenced code already fully exists and matches**
  — flag as a likely forgotten bookkeeping update (the feature shipped but the spec was never
  marked `Done`).
- **A `Related specs` entry points to a file that no longer exists** — flag as a broken link.
- Don't flag a mismatch on a spec with no concrete references yet (e.g. still in the "What/Why"
  stage with an empty Proposed approach) — there's nothing to drift from yet.

## 4. Detect other staleness signals

- Templated-but-never-authored specs from step 2 (a title and metadata table, but the rest is
  still HTML-comment placeholders) — flag as "never filled in."
- Unresolved **Open questions** left in place — flag as "grill session needed" (i.e. `/grill`
  hasn't been run to closure on this one yet, or was run and questions were left open on
  purpose).
- A `Draft`/`In progress` spec whose `Date` is old relative to the other specs in the directory
  (comparable staleness, not an arbitrary fixed threshold — a spec that's the oldest and still
  `Draft` while everything else has moved to `Done` is the signal, not a hardcoded day count).

## 5. Report

Present, don't silently fix:

1. A table: `File | Title | Status | Date | Findings` — one row per spec, `Findings` empty/"—"
   when clean.
2. A one-line count summary per status (`Draft`, `In progress`, `Approved`, `Done`, `Abandoned`).
3. A short "worth a look" list surfacing just the specs with findings, each with a one-line
   suggested next action (e.g. "run `/grill` to close its open questions," "code matches —
   consider bumping Status to Done," "referenced handler no longer exists — spec needs revising").

Never edit any spec file as part of this skill — if the user wants a finding fixed, that's a
separate, explicit follow-up action.
