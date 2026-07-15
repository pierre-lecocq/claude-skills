---
name: spec-create
description: Create a new feature spec file under specs/ from the bundled template (one file = one feature) — either blank, or pre-filled from a just-completed /grill idea-mode session. Use when asked to "create a new spec", "start a spec for X", "/spec-create", or to scaffold a specs/*.md file before planning/implementing a feature.
disable-model-invocation: false
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

# spec-create

Scaffolds a new `specs/<feature-slug>.md` file from the template bundled with this skill
(`TEMPLATE.md`, next to this file — not a copy living in `specs/`). `specs/` is user-owned
content: this skill only ever adds a new file to it, never overwrites the template into it.

This skill has two modes, distinguished by whether a just-completed `/grill` idea-mode session
is present earlier in this same conversation (i.e. this skill was invoked by `grill`'s step 5, or
the user asks to persist an idea they were just grilling):

- **Blank mode** (no grilled idea in context): scaffold the template untouched, as before.
- **Grilled mode** (a grilled idea is in context): pre-fill the sections that interview actually
  resolved instead of leaving them as placeholders — see step 4.

## 1. Ensure `specs/` exists

Check whether `specs/` exists at the repo root; create it if not (`mkdir -p specs`). Don't touch
anything else in it.

## 2. Get the feature name

- **Grilled mode**, or invoked with `args` carrying a proposed name (e.g. from `grill`'s
  `Skill(skill: "spec-create", args: "<proposed name>")`): state the proposed name in a normal
  chat message and ask the user to confirm it or give a different one — don't just ask blindly
  when you already have a reasonable suggestion from context.
- **Blank mode**, no proposal available: ask the user, in a normal chat message (not
  `AskUserQuestion` — this is free-form text, not a choice), what to name the new feature spec.

Either way, wait for their reply before continuing.

## 3. Derive the filename

Slugify the given name into `kebab-case` (lowercase, spaces/punctuation collapsed to single
hyphens, trimmed of leading/trailing hyphens) to get `specs/<slug>.md`.

If `specs/<slug>.md` already exists, stop and ask the user via `AskUserQuestion` whether to pick
a different name or overwrite the existing spec — never overwrite silently, since an existing
spec file may already hold in-progress work.

## 4. Generate the file

Read this skill's bundled `TEMPLATE.md` and write it to `specs/<slug>.md`, starting from these
two substitutions in every case:

- The `# [Feature name]` heading → `# <the confirmed feature name>`.
- The `**Date**` table cell's `[YYYY-MM-DD created/last updated]` placeholder → today's date
  (`date +%F`).

Leave `**Status**`, `**Owner**`, and `**Related specs**` as placeholders for the user to fill in,
in both modes.

- **Blank mode**: leave every other section exactly as the template has it (including the HTML
  comments guiding each section) — untouched.
- **Grilled mode**: additionally fill in each template section the grill session actually
  produced content for, replacing that section's placeholder/HTML comment with real prose drawn
  from the interview (not fabricated) — typically: **What** (the idea, restated concisely),
  **Why**, **Who** (if discussed), **Context** (relevant codebase grounding `grill` surfaced),
  **Goals**, **Non-goals** (anything explicitly ruled out during grilling), **Constraints** (if
  any surfaced), **Requirements** (functional/non-functional decisions resolved in the
  interview), **Proposed approach** subsections (only if the interview reached concrete
  API/data-model/service shape — often it won't, and that's fine), **Alternatives considered**
  (any rejected approaches discussed), and **Open questions** (either "None remaining" if the
  decision tree fully resolved, or whatever the user chose to leave open). Leave **Testing
  plan**, **Acceptance criteria**, and **Rollout notes** as placeholders unless the interview
  specifically covered them — don't invent detail an idea-level grill session wouldn't have
  produced.

## 5. Report

Tell the user the new file's path. In blank mode, mention it's now theirs to fill in
(What/Why/Who/Context/Goals/etc.) before planning. In grilled mode, mention which sections were
pre-filled from the interview and that the rest (if any) still needs their input. Either way —
`/spec-plan` can turn it into an implementation plan once it's ready.

## 6. Planning it later in this same conversation

If, later in this same conversation, the user asks to plan what they just wrote into this spec
(e.g. "plan this", "plan what I just wrote", "let's plan it") — without naming a different file —
invoke the `spec-plan` skill directly against the file created in step 4, passing its path as the
skill's `args` (e.g. `Skill(skill: "spec-plan", args: "specs/<slug>.md")`). This lets `spec-plan`
skip its own file-selection step and go straight to reading and grilling that spec, since which
file is meant is already unambiguous from context. If the user instead names a different or
unclear file, invoke `/spec-plan` plain so it asks as usual.
