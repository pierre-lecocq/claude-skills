# Makefile rules

Conventions for authoring a project's `Makefile`. The `help`/`.PHONY`/`all` conventions are
language-agnostic; the tool-invocation guidance leans Go-specific since that's this collection's
primary use case.

## Target ordering

- Group targets in this order, top to bottom: the `.PHONY` line, `.DEFAULT_GOAL`, `all`, `help`,
  then build targets, then test/quality targets (`test`, `lint`, `vuln`, `deadcode`, ...), then
  dev-loop targets (`dev`, `run`, ...), then `clean` last.

## The `help` target

- The `help` target is mandatory and used to self document the Makefile targets

```makefile
help: ## Display this help
	@echo "### Makefile Targets"
	@grep -E '^[\/a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
```

- The `/` in the grep character class (`[\/a-zA-Z_-]+`) is intentional, not an oversight — it's
  what lets slash-named targets like `build/linux` show up in the listing. Don't "simplify" it
  away.

## Targets documentation

- The Makefile file must self document all targets.
- All targets must include a comment on the same line, starting with `##`
- This comment will be listed in the `help` target

Example:

```makefile
build: ## Build binary
	my-command
```

## The `all` target and default goal

- Always add an `all` target that calls `help`, and pin the default goal explicitly with
  `.DEFAULT_GOAL := help` — don't rely on `all`/`help` merely being declared first in the file.
  Make's default-goal rule is "first target in the file," so a later reordering (e.g. inserting a
  new target above `all`) would silently change what a bare `make` does. Declaring
  `.DEFAULT_GOAL` makes that goal explicit and reorder-proof.

```makefile
.DEFAULT_GOAL := help

all: help
```

## .PHONY section

- The Makefile file must have a `.PHONY` line near the top that lists every target, including
  `help` and `all` themselves — a target missing from `.PHONY` still works most of the time, but
  breaks silently the moment a file or directory with that same name appears in the project root.

## Tool invocation

- For Go-based CLI tools, prefer `go run <module>@<version> ...` inside the target's recipe over
  assuming the binary is pre-installed globally (e.g. `vuln: govulncheck` uses
  `go run golang.org/x/vuln/cmd/govulncheck@<version> ./...`) — this needs no separate install
  step and stays reproducible across machines and CI.
- Pin an actual version (e.g. `@v1.2.3`), not `@latest` — `@latest` means the exact same `make
  lint`/`make vuln` invocation can behave differently next month with no change to the repo,
  which defeats the point of having the check in a Makefile at all.
- Only fall back to assuming a globally-installed binary (documented as a prerequisite in the
  target's `##` comment) for tools that can't run via `go run` — e.g. long-running/daemon or
  watch-mode tools like `air`, which don't fit the one-shot `go run` model.

## Recipe correctness

- Recipe lines must be indented with a literal tab character, not spaces — Make errors out
  otherwise, and this is invisible in most editors' default rendering.
- A multi-line recipe runs each line in its own subshell by default, so a failing command on one
  line does NOT stop the target unless lines are chained with `&&`/`; \` continuations, or the
  target uses `.ONESHELL:` to run the whole recipe in a single shell.

## Format checking

- If the project's language rules mandate a formatter (e.g. `gofmt` for Go), the Makefile must
  expose it as its own target (e.g. `fmt` or `check-fmt`) rather than only relying on it being
  bundled inside a linter step — keeps "is this formatted" independently runnable and scriptable
  in CI.
