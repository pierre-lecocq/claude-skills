---
name: grill
description: Run a "grill-me"-style HITL interview — one question at a time, each with a recommended answer, grounded in the current codebase — to pressure-test and close gaps in either a freeform idea or an existing specs/*.md file. Use when asked to "grill this idea", "grill me on X", "/grill", or as the mandatory first step of /spec-plan before drafting any implementation plan.
disable-model-invocation: false
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - AskUserQuestion
  - Agent
---

# grill

Pressure-tests a feature idea or an existing spec through a focused interview, modeled on the
["grill-me"](https://www.aihero.dev/skills-grill-me) pattern: adversarial validation, not a
rubber stamp. The goal is to surface every gap, contradiction, and unjustified assumption that
would otherwise force a silent guess later — whether "later" is a hand-written spec or an
implementation plan drafted by `/spec-plan`.

This skill only interviews and (in spec mode) records the resolved answers — it never drafts an
implementation plan itself; that's `/spec-plan`'s job, which calls this skill as its first step.

## 1. Determine what's being grilled

- If invoked with `args` naming an existing file (e.g. `specs/<slug>.md`), that's **spec mode** —
  the file is the input.
- If invoked with `args` containing free-form text, or the user describes an idea directly in
  chat with no file, that's **idea mode** — the described idea (held only in this conversation)
  is the input.
- If invoked with neither (bare `/grill`, no context), ask the user directly in chat (plain text,
  not `AskUserQuestion` — this is open-ended) whether they want to grill a written idea (and to
  describe it) or an existing spec. For the latter, `Glob specs/*.md`, present each as
  title + `Status` (same presentation as `/spec-plan`), and let them pick — offering the 4 most
  recently modified with a custom-path option if there are more.

## 2. Read the input in full

- **Spec mode**: read the entire file, not just the title/Goals. Note **Non-goals** and
  **Constraints** (they bound things as much as the goals do), every unresolved **Open
  questions** entry, and anything already sketched in **Proposed approach** — treat a prior
  sketch as a strong starting point to verify, not a rubber stamp.
- **Idea mode**: take the idea as given. There's no structured template to cross-check it
  against, so lean more heavily on codebase grounding (step 3) to find what's genuinely
  ambiguous versus already implied by existing conventions.

## 3. Ground it in the current codebase

Before asking anything:

- `Grep`/`Read` to confirm any endpoints, services, models, or env vars mentioned actually exist
  as described — specs go stale, and ideas can misremember existing code.
- For broad or unfamiliar scope, delegate the survey to the `Explore` agent rather than guessing.
- Note anywhere the input conflicts with what's actually in the code — surface it, don't silently
  reconcile it.
- This grounding is what lets step 4 skip any question that's already answerable from the code
  alone — never make the user restate something you could look up yourself.

## 4. Grill session (HITL)

- Ask **one question at a time** via `AskUserQuestion`, never a batch. Treat the questions as a
  decision tree, not a fixed checklist — let each answer determine whether/what to ask next,
  since design choices here are often interdependent (e.g. the answer about auth changes what's
  worth asking about rate limiting).
- For every question, propose a recommended answer as the first option, labeled `(Recommended)`,
  grounded in the input's own content, step 3's findings, and this repo's existing conventions
  (`CLAUDE.md`'s "Patterns") — never ask a bare open-ended question when a reasonable default
  exists to confirm or reject instead; that default is what makes this fast to get through.
- What to grill about, roughly in order of leverage (ask about whatever would most reshape the
  outcome first):
  - Contradictions or tension between stated goals and non-goals/constraints (spec mode:
    **Goals** vs **Non-goals**/**Constraints**; idea mode: whatever the idea implies about scope
    vs whatever it implies is out of scope).
  - Every item noted as unresolved in **Open questions** (spec mode) — this is where they get
    closed, not left for a plan to shrug at later.
  - Ambiguous or missing behavior that would change the API surface, data model, or error
    handling depending on the answer.
  - Assumptions baked into any proposed approach that aren't justified by context given so far —
    push back on them rather than accepting them at face value.
  - Any acceptance criterion (if one exists yet) that isn't concretely verifiable, or doesn't
    actually follow from the stated goals.
- Stop when the decision tree is resolved: no remaining question would materially change the
  outcome, or the user explicitly says to proceed with what's there. Don't manufacture questions
  once genuine ambiguity runs out — this is a gate, not a quota.

## 5. Record the outcome

- **Spec mode**: as each answer lands, record it back into the spec file (`Edit`) in the section
  it belongs to (e.g. resolve an **Open questions** entry, tighten a **Requirement**, add a
  **Non-goal**) rather than letting the resolution live only in this conversation — the spec is
  meant to stay the source of truth.
- **Idea mode**: there's no file to edit. Keep a running summary of resolved decisions in the
  conversation instead. Once the session ends, ask the user whether to persist it as a spec —
  don't force it; sometimes grilling an idea is just informal thinking-out-loud that ends there.
  If they want to persist it:
  1. Propose a short feature name for it (a few words capturing the core idea, the same way
     you'd title the spec's `# [Feature name]` heading) — don't just ask for a name with no
     suggestion; you already have enough context from the interview to suggest one.
  2. Invoke `Skill(skill: "spec-create", args: "<proposed name>")`. `spec-create` will confirm
     or let the user override that name, then generate `specs/<slug>.md` pre-filled from this
     grilled idea (see `spec-create`'s own instructions for how it pulls that content from this
     conversation) instead of a blank template.

## 6. Report

Summarize what was resolved and what (if anything) remains open, so whoever needs the result
next — a human, or `/spec-plan` continuing on to draft a plan — has a clear final state to act
on.
