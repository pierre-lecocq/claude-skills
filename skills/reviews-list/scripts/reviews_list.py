#!/usr/bin/env python3
"""Fetch and categorize PRs across repos for the reviews-list skill.

Uses the `gh` CLI to pull team membership and pull request data, then prints
a markdown table.

Which GitHub host, repos, teams, and users to target is read from
config.json (next to this script, or --config), and can be extended per-run
with --repos/--team/--user. See config.json for the user-maintained list.
"""

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

DEFAULT_CONFIG_PATH = pathlib.Path(__file__).resolve().parent.parent / "config.json"
DEFAULT_GITHUB_HOST = "github.com"

PR_JSON_FIELDS = "number,title,url,author,assignees,reviewRequests,labels,createdAt,updatedAt"


def gh_json(args):
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"error running gh {' '.join(args)}: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def load_config(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def get_team_members(host, org, team):
    members = gh_json(["api", "--hostname", host, f"orgs/{org}/teams/{team}/members", "--paginate"])
    return {m["login"].lower() for m in members}


def get_current_user(host):
    return gh_json(["api", "--hostname", host, "user"])["login"].lower()


def get_prs(host, repo, state, limit):
    return gh_json(["pr", "list", "--repo", f"{host}/{repo}", "--state", state, "--limit", str(limit), "--json", PR_JSON_FIELDS])


def team_requested(review_requests, team):
    for r in review_requests or []:
        if r.get("__typename") != "Team":
            continue
        name = (r.get("name") or "").lower()
        slug = (r.get("slug") or "").lower()
        if name == team.lower() or slug.endswith(f"/{team.lower()}") or slug == team.lower():
            return True
    return False


def relative_time(iso_ts, now):
    dt = datetime.datetime.strptime(iso_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    delta = now - dt
    total_minutes = max(int(delta.total_seconds() // 60), 0)

    if total_minutes < 60:
        n = total_minutes
        return f"{n} minute{'s' if n != 1 else ''} ago"

    total_hours = total_minutes // 60
    if total_hours < 24:
        return f"{total_hours} hour{'s' if total_hours != 1 else ''} ago"

    days = total_hours // 24
    hours = total_hours % 24
    return f"{days} day{'s' if days != 1 else ''} and {hours} hour{'s' if hours != 1 else ''} ago"


def dedup(seq):
    seen = []
    for s in seq:
        if s.lower() not in [x.lower() for x in seen]:
            seen.append(s)
    return seen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config.json (default: config.json next to this script)")
    parser.add_argument("--github-host", default=None, help="GitHub hostname, e.g. github.com or an enterprise host")
    parser.add_argument("--repos", action="append", default=[], help="Additional OWNER/REPO to target (repeatable)")
    parser.add_argument("--org", default=None)
    parser.add_argument("--state", default=None, choices=["open", "closed", "merged", "all"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--team", action="append", default=[], help="Additional GitHub team slug to target (repeatable)")
    parser.add_argument("--user", action="append", default=[], help="Additional GitHub login to target (repeatable)")
    args = parser.parse_args()

    config = load_config(pathlib.Path(args.config))

    github_host = args.github_host or config.get("github_host") or DEFAULT_GITHUB_HOST
    repos = dedup(config.get("repos", []) + args.repos)
    org = args.org or config.get("org")
    state = args.state or config.get("state", "open")
    limit = args.limit or config.get("limit", 200)
    teams = dedup(config.get("teams", []) + args.team)
    users = dedup(config.get("users", []) + args.user)

    if not repos:
        print("no repos configured — edit config.json or pass --repos", file=sys.stderr)
        sys.exit(1)
    if not teams and not users:
        print("no teams or users configured — edit config.json or pass --team/--user", file=sys.stderr)
        sys.exit(1)
    if teams and not org:
        print("teams are configured but no org is set — edit config.json or pass --org", file=sys.stderr)
        sys.exit(1)

    team_members = {team: get_team_members(github_host, org, team) for team in teams}

    # Flatten team membership into the users list: assigned-to/authored-by
    # checks then apply to individual team members too, not just the
    # explicitly configured users.
    all_team_members = [login for members in team_members.values() for login in members]
    users = dedup(users + all_team_members)

    me = get_current_user(github_host)
    if me not in [u.lower() for u in users]:
        users.append(me)

    now = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for repo in repos:
        for pr in get_prs(github_host, repo, state, limit):
            author = pr.get("author") or {}
            author_login = (author.get("login") or "").lower()
            author_name = author.get("login") or "unknown"
            assignee_logins = {a["login"].lower() for a in (pr.get("assignees") or [])}

            matched = []
            for team in teams:
                if team_requested(pr.get("reviewRequests"), team):
                    matched.append(f"{team} reviewer")
            for user in users:
                if user.lower() in assignee_logins:
                    matched.append(f"assigned to {user}")
                if author_login == user.lower():
                    matched.append(f"authored by {user}")

            if not matched:
                continue

            labels = ", ".join(l["name"] for l in (pr.get("labels") or []))
            rows.append({
                "repo": repo,
                "number": pr["number"],
                "title": pr["title"],
                "url": pr["url"],
                "author": author_name,
                "labels": labels or "-",
                "matched": ", ".join(matched),
                "created": relative_time(pr["createdAt"], now),
                "updated": relative_time(pr["updatedAt"], now),
                "updated_at": pr["updatedAt"],
            })

    rows.sort(key=lambda r: r["updated_at"], reverse=True)

    print(f"Host: {github_host} | Repos: {', '.join(repos)} | Teams: {', '.join(teams) or '-'} | Users: {', '.join(users) or '-'} | State: {state} | Matches: {len(rows)}\n")
    print("| Repo | PR | Author | Matched criteria | Labels | Created | Updated |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        title = r["title"].replace("|", "\\|")
        print(f"| {r['repo']} | [#{r['number']}]({r['url']}) {title} | {r['author']} | {r['matched']} | {r['labels']} | {r['created']} | {r['updated']} |")


if __name__ == "__main__":
    main()
