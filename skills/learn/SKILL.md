---
name: learn
description: One-shot skill - given a topic to learn, interview the user (why, time available, current level), research the topic, then generate a self-contained local HTML/JS learning website with chapters and quizzes in a new folder named after the topic.
disable-model-invocation: true
argument-hint: "<topic to learn>"
---

# Learn

The user has named a topic they want to learn. This is a **one-shot** pipeline: Interview → Plan → Research → Build. Unlike the `teach` skill (a long-running, multi-session workspace), `/learn` produces one finished, self-contained website per topic and hands it over.

## Step 1 — Interview (do this first, before any research or files)

Ask whatever of the following the user hasn't already told you. Don't re-ask what's already answered in their initial message. Use `AskUserQuestion` for the structured parts.

- **Why**: the concrete real-world reason they want this. Push past abstract framing ("understand Rust") toward the underlying outcome ("ship a CLI tool at work").
- **Time**: both total budget and cadence — "3 hours this weekend" implies a different shape than "15 minutes a day for a month."
- **Current level**: complete beginner, some exposure, or refreshing something half-forgotten.
- **Depth vs. breadth**: a broad tour vs. going deep on a narrower slice.
- **Anything out of scope**: adjacent things they explicitly don't want to chase right now.

Skip straight to planning only if the user has already answered all of this up front or explicitly says to just proceed.

## Step 2 — Plan the curriculum

Based on the interview, decide the chapter breakdown and size it to the stated time budget — each chapter should be completable in one sitting (roughly 10-20 minutes of reading plus its quiz). Order chapters so each one scaffolds the next, building toward the stated goal.

Show the user the planned chapter list in one short message before doing deep research, so they can redirect if the shape is wrong. Don't write a lengthy plan document — this is a quick check-in, not a deliverable.

## Step 3 — Research

Use web search/fetch tools — don't rely purely on parametric knowledge, especially for anything fast-moving or niche. Prefer high-trust, primary sources (official docs, respected books/courses, standards bodies) over SEO content farms. Track which source(s) back each chapter — every chapter in the final site must cite/link at least one primary source.

## Step 4 — Build the site

**Folder**: a dash-case slug of the topic, created directly under the current directory, e.g. `./rust-ownership/`. If that folder already exists, stop and ask the user whether to overwrite it, version it (`-2` suffix), or pick a different topic — never overwrite silently.

**Structure**:

```
<topic-slug>/
  index.html          landing page: title, the "why", chapter list
  chapters/
    01-<name>.html
    02-<name>.html
    ...
  assets/
    style.css          copied from this skill's templates/style.css
    quiz.js             copied from this skill's templates/quiz.js
```

Copy `templates/style.css` and `templates/quiz.js` from this skill's directory into the new `assets/` folder as the starting point. Reuse the quiz widget mechanics as-is (the `.quiz[data-quiz]` JSON contract, the immediate per-question feedback) — don't reinvent that part per topic.

### Visual design — mandatory, every time

Before treating the site as done, invoke the `frontend-design` skill (`frontend-design:frontend-design`) and give this topic a bespoke visual identity — never ship the plain copied template as the final look. Ground every choice in the topic's own real-world subject matter (its materials, vernacular, iconic colors/objects/diagrams), not a generic default:

- Pick a 4-6 color token system and a type pairing (display + body, plus a mono/utility face if the topic has notation, code, or figures worth calling out) that are specific to this subject — e.g. a driving-test topic borrows the actual road-signage palette; a puzzle topic borrows the object's own official colors; a programming topic might lean on its language's own brand/terminal aesthetic. Self-host any webfonts (download the woff2 files once via `curl`, store them in `assets/fonts/`, reference locally) — no CDN dependency at runtime.
- Design one genuine signature element the whole site is built around (a distinctive nav treatment, a way of rendering the domain's key artifacts — formulas, notation, diagrams, timelines) — something that couldn't be copy-pasted onto an unrelated topic without looking wrong.
- Reuse the existing sidebar markup (`nav.sidebar > ol > li > a`, with `class="current"` on the active chapter's link) — a modern `:has()`-based CSS selector (`li:has(a.current)`, `li:has(a.current) ~ li`) can restyle it into whatever nav concept fits the topic without touching any chapter HTML.
- If a component needs DOM changes that would otherwise mean editing every chapter file (e.g. turning inline code into styled tokens, auto-highlighting figures), write a small `assets/site.js` that does it on `DOMContentLoaded` instead of hand-editing each chapter.
- Keep quiz correctness/feedback semantics intact (immediate right/wrong feedback) — restyle freely, don't remove the mechanic.
- Self-critique before opening the site: re-read it against the brief once — if any choice reads as one of the generic AI-design defaults (cream + serif + terracotta; near-black + one neon accent; broadsheet hairlines) rather than something this specific topic earned, revise it.
- Validate before opening: check CSS brace/paren balance, run any new JS through `node --check`, and re-verify the quiz JSON still parses after any markup changes.

**Every chapter page** includes:
- A concise recap of the material — no walls of text, this is a summary a learner returns to, not the full research.
- A link to the primary source(s) it's based on.
- A quiz block using the shared widget (see rules below).
- Prev/next chapter navigation, and a link back to `index.html`.
- A short reminder that the agent is available for follow-up questions on anything unclear.

**`index.html`** recaps the mission (why + time budget) in 1-2 sentences and links every chapter in order.

**Constraints**: no external CDN dependencies — everything must work opening `index.html` directly from disk (`file://`), no build step, no server required.

Once built, open `index.html` for the user (`open ./<topic-slug>/index.html` on macOS).

## Quiz rules

Use the shared `quiz.js` widget: a `<div class="quiz" data-quiz='[...]'></div>` populated with a JSON array of objects: `{"q": "...", "choices": ["...", "..."], "answer": 0, "explain": "..."}`. It renders immediate per-question feedback with no page reload or server.

- Make every choice roughly the same length and register — never let the correct answer be identifiable just from being conspicuously longer or more specific than the distractors.
- Favor retrieval practice: test recall of what was just explained, not verbatim recognition of the same sentence used in the recap.
- 3-5 questions per chapter is enough; this is a check, not an exam.

## Keep it lean

This is a one-shot deliverable, not the stateful multi-session workspace that `teach` builds (`MISSION.md`, `RESOURCES.md`, learning records, a growing glossary). Don't create any of that here — the interview answers just inform the plan and get folded into `index.html`'s intro copy.

If the user later returns and says "keep going" or "add a chapter on X" for a topic folder that already exists: read the existing chapters first for continuity and style, then add new chapter(s) and update `index.html`'s list and the neighboring chapters' prev/next links.
