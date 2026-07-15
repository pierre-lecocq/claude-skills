---
name: rest-api-audit
description: Audit the current REST API implementation against Postman's REST API best practices (https://blog.postman.com/rest-api-best-practices/) and report findings as a table with Severity, Priority, and a Complexity score to fix. Read-only — never edits code. Use when asked to "audit the API", "check REST best practices", "find API design issues", or "/rest-api-audit".
disable-model-invocation: false
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Write
  - Agent
---

# rest-api-audit

Audits this project's actual, current HTTP API — not a generic checklist recitation — against the
best practices in [Postman's REST API guide](https://blog.postman.com/rest-api-best-practices/).
This is a reporting skill: it finds and scores issues, it never fixes them itself.

## 1. Map the current API surface

Before checking anything against the checklist, know exactly what exists:

1. Find every registered route (route registration, e.g. `main.go`'s `mux.Handle` calls, or
   wherever routing lives) — method, path, and its handler.
2. For each route, read its handler → service → model chain in full: what it reads from the
   request (path/query params, body, headers), what status codes and response shapes it can
   produce (success and every error path), and what headers it sets.
3. If the codebase is large, delegate this survey to the `Explore` agent rather than sampling a
   few endpoints and generalizing.

Don't evaluate anything in step 2 until this map is complete — a finding based on half the
picture (e.g. "no endpoint sets Location on create" checked against only read endpoints) is
worse than no finding.

## 2. Check against the checklist

Evaluate the mapped surface against each of these (drawn from the Postman article) — only
report what you actually observe in the code, not what's merely undocumented or unverifiable:

- **Resource naming / URL design**: nouns not verbs, plural collections (`GET /users`), no more
  than ~2 levels of nesting, relationships expressed predictably (`/users/123/orders`).
- **HTTP methods**: GET never mutates state; POST creates (with `201` + `Location` header); PUT
  is a full idempotent replace; PATCH is partial; DELETE returns `204` or `200` with details.
- **Status codes**: correct use of `200/201/202/204` for success; `400/401/403/404/409/422/429`
  for client errors; `500/502/503/504` reserved for genuine server-side failure, not swallowed
  into a generic `500` for everything.
- **Error handling**: one consistent error shape across every endpoint, with a machine-readable
  error *code* distinct from the human-readable message (not just a message + status-text pair);
  validation errors report every failing field at once, with per-field detail, not just the
  first one found.
- **Versioning**: breaking changes (removed/renamed fields, changed types, changed auth) are
  versioned (URI or header); non-breaking additive changes aren't forced through a version bump.
- **Pagination**: any list endpoint that can return an unbounded number of rows has one of
  page/per_page, limit/offset, or cursor-based pagination — not an unbounded `SELECT *`.
- **Filtering / sorting / searching**: list endpoints expose query params for the filters/sort
  orders a client would actually need, rather than only supporting one hardcoded order/scope.
- **Auth & security**: HTTPS-only assumption is safe to state, not enforced in code; API
  key/bearer-token auth is present and correctly scoped where the API isn't meant to be fully
  public; rate limiting (if present) returns `429` **and** `X-RateLimit-Limit` /
  `X-RateLimit-Remaining` / `X-RateLimit-Reset` headers, not just a bare 429.
- **CORS**: `Access-Control-Allow-Origin`/`-Methods`/`-Headers` are set deliberately (explicit
  origins for a private API, not an unexamined wildcard for one that carries auth).
- **Content types**: `application/json` consistently in and out; no undeclared/implicit format.
- **Response design**: no field-selection support on payload-heavy endpoints is only a finding if
  payloads are actually heavy; responses stay reasonably flat and don't leak internal DB/model
  shape (column names, internal-only fields) into the public contract.
- **Idempotency**: GET/PUT/DELETE are actually idempotent in implementation, not just by
  convention; POST endpoints that create side-effecting resources support an idempotency key if
  retries are plausible for that client.
- **Observability**: every response (success and error) carries a request-correlation ID header;
  structured logging captures method, path, status, and latency per request.
- **Documentation**: every endpoint's method/path/params/request/response/status
  codes/auth requirements are documented somewhere real (e.g. `docs/openapi.yml` if this repo
  has one) and that doc actually matches the code — a stale doc is itself a finding.
- **Backward compatibility**: recent changes added fields/endpoints rather than removing/renaming
  in place; deprecated-but-still-present endpoints signal it (response field, header, or docs).
- **Testing**: endpoints have test coverage beyond the happy path — auth failures, validation
  errors, rate limiting, not-found, and other edge cases.
- **Common mistakes**: no GET that mutates state; no leaking of internal implementation details
  (table/column names) into URLs or JSON keys; consistent naming convention (no mixing
  `snake_case`/`camelCase`, no inconsistent pluralization) across every endpoint.

## 3. Score each finding

For every real, code-verified issue (cite the exact file(s)/line(s) it lives in — never a vague
"the API doesn't..." without a pointer):

- **Severity** — objective impact if left unaddressed: `Critical` (security/data-integrity risk,
  e.g. no auth on a mutating endpoint), `High` (breaks client expectations or causes real bugs,
  e.g. non-idempotent PUT, missing pagination on an unbounded list), `Medium` (inconsistency or
  missing ergonomics that cause friction but not breakage, e.g. no field-level validation detail),
  `Low` (polish/nice-to-have, e.g. no HATEOAS links, no deprecation headers).
- **Priority** — what order to actually act in, informed by severity *and* how cheap/disruptive
  the fix is: `P0` (fix now — typically Critical, or trivial-to-fix High), `P1` (next), `P2`
  (soon), `P3` (backlog). A Critical issue that's also cheap to fix is P0; a Medium issue that
  happens to be a one-line fix can reasonably outrank a High issue that requires a breaking
  change — use judgment, don't mechanically copy Severity into Priority.
- **Complexity** — effort to bring the current implementation in line with the recommendation, on
  a 1–5 scale:
  - `1` — trivial: one line, one file, no behavior risk (e.g. add a response header).
  - `2` — small: a few lines in one file, low risk (e.g. add a missing status-code branch).
  - `3` — moderate: spans handler/service/model for one endpoint, needs new tests (e.g. add
    pagination to one list endpoint).
  - `4` — large: cross-cutting across every endpoint (e.g. a unified machine-readable error-code
    scheme, or introducing versioning).
  - `5` — major: a breaking change requiring a migration/coordination with API consumers (e.g.
    reshaping the URL structure or changing the auth model).

## 4. Report

1. Write `docs/rest-api-audit.md`: an intro line (what was audited, against which guide, when),
   then a single table sorted by Severity (`Critical` → `Low`) and by Priority within each
   severity tier: `Finding | Severity | Priority | Complexity | Endpoint(s)/Reference(s) |
   Recommendation`. Overwrite whatever's currently there; create `docs/` if it doesn't exist.
2. In chat, summarize: total findings per severity tier, and the top 3–5 by priority with a
   one-line reason each — don't just say "see the file," give the user something to act on
   immediately.
3. If the audit finds nothing (the API already matches the guide's practices at the scope you
   checked), say so plainly — don't invent findings to pad the report.
