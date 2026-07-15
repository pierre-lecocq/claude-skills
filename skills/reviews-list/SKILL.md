---
name: reviews-list
description: List pull requests across configured GitHub repos relevant to a set of teams and users (authored by a configured team member, a configured team requested as reviewer, assigned to a configured user, or authored by a configured user), as a single markdown table sorted by most recently updated.
argument-hint: [state: open|closed|merged|all] (default open)
allowed-tools:
  - Bash
---

# reviews-list

Lists pull requests on the configured GitHub repos (via the `gh` CLI) that match any of, for every team/user in `config.json`:

- **a)** a configured GitHub team is requested as a reviewer
- **b)** a configured user, or a member of a configured team, is assigned
- **c)** a configured user, or a member of a configured team, is the author

## Configuration

`config.json` (next to this file) is the user-maintained target list. `config.example.json` shows the shape with generic placeholders:

```json
{
  "github_host": "github.com",
  "repos": ["owner/repo"],
  "org": "your-org",
  "state": "open",
  "teams": ["your-team"],
  "users": ["your-username"]
}
```

Copy `config.example.json` to `config.json` and fill in your own host/repos/org/teams/users. Edit `repos`/`teams`/`users` directly to add or remove targets — no script changes needed. `github_host`/`org`/`state` are also editable defaults.

- `repos` is a list — every repo in it is queried and results are merged into one table (with a `Repo` column, since PR numbers aren't unique across repos).
- `github_host` is the GitHub hostname to query (e.g. a GitHub Enterprise host). If omitted from config, the script defaults to public `github.com` — set it explicitly for enterprise repos, since `gh` cannot reliably infer the host when run outside that repo's local checkout.
- `org` is the GitHub org that owns the configured `teams` (required whenever `teams` is non-empty).

**Team membership is merged into the effective users list.** Each configured team's members are fetched and added to the `users` list (deduplicated), so the "assigned"/"authored by" checks apply to individual team members too, not just the explicitly listed users. Example: if a team has members `user1, user2, user3` and `users` is `[user2, user4]`, the effective users targeted are `user1, user2, user3, user4`. The team itself is still checked separately for "requested as reviewer". The currently authenticated `gh` user is always included in the effective users list even if not listed anywhere in config.

## Pre-flight config check

Before running the script, validate `config.json` next to this file:

- The file exists (if not, it wasn't copied from `config.example.json` yet).
- `repos` is present and non-empty.
- At least one of `teams` or `users` is present and non-empty.
- If `teams` is non-empty, `org` is present and non-empty.

These are the same checks the script itself enforces (and will exit 1 on), so catching them first avoids a failed run.

- **If everything required is set:** proceed straight to running the script — do not ask for confirmation first.
- **If something is missing/empty:** don't run the script. Instead, tell the user exactly which key(s)/value(s) are missing or empty, show the current `config.json` contents (or note it doesn't exist yet), and offer to edit it directly — either by asking the user for the missing values and writing them in, or by pointing them to edit the file themselves. `github_host`/`state`/`limit` are optional (they have defaults), so don't flag those as missing.

## Usage

Run the bundled script from the repo root (or with an absolute path):

```bash
python3 .claude/skills/reviews-list/scripts/reviews_list.py [--state open|closed|merged|all] [--repos OWNER/REPO] [--github-host HOST] [--org ORG] [--team SLUG] [--user LOGIN] [--config PATH]
```

`--repos`/`--team`/`--user` are repeatable and add to (not replace) the lists from `config.json`, for one-off queries without editing the file. `--github-host`/`--org`/`--state`/`--limit` override the config values for a single run.

If the user asks for "all PRs" or mentions closed/merged ones, pass `--state all`.

The script:

1. Loads `config.json` for the target GitHub host, repos, org/state, and the teams/users lists.
2. Fetches each configured team's membership via `gh api --hostname {github_host} orgs/{org}/teams/{team}/members --paginate`, and merges those logins into the effective users list.
3. For each configured repo, fetches PRs via `gh pr list --repo {github_host}/{repo} --json ...` (author, assignees, reviewRequests, labels, createdAt, updatedAt).
4. Keeps a PR if it matches any of the criteria above, for any configured team/effective user (a PR can match more than one — all matches are listed in the "Matched criteria" column, naming which team/user matched).
5. Formats `createdAt`/`updatedAt` as relative time ("N minutes ago", "N hours ago", or "N days and M hours ago" — computed from wall-clock time, not guessed).
6. Sorts the combined result (across all repos) by `updatedAt` descending.
7. Prints a ready-to-use markdown table with columns: Repo, PR (number + title, linked), Author, Matched criteria, Labels, Created, Updated.

## Output

Run the script and present its markdown table output directly to the user — do not recompute the relative dates or re-sort by hand, the script already does both correctly. Do not truncate the table or paraphrase the rows; if the table is very large, still show all rows unless the user asks to narrow it down.
