#!/usr/bin/env python3
"""Plumbing for the pr-review skill.

Subcommands:
  gather   Resolve the review target (PR URL, PR number, branch name, or the
           current branch), then stage everything the review needs in a temp
           workdir: state.json, diff.patch, threads.json (existing review
           threads with resolution state, via GraphQL), pr_body.md, and — when
           a local clone with a matching remote exists — a detached read-only
           worktree of the PR head at head/.
  post     Render findings.json into Codex-style inline comments plus a
           summary body, then post the review. The reviews endpoint is atomic:
           one comment anchored to a line outside the PR diff fails the whole
           POST with a 422, so every anchor is validated against the live diff
           first and misses are reported with the nearest commentable line.
  cleanup  Remove the worktree gather created.

Requires only the Python stdlib and an authenticated `gh` CLI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
PR_URL_RE = re.compile(r"github\.[\w.-]+/([^/\s]+)/([^/\s]+)/pull/(\d+)")

SEVERITIES = ("P1", "P2", "P3", "P4")
BADGE_COLORS = {"P1": "orange", "P2": "yellow", "P3": "lightgrey", "P4": "lightgrey"}

THREADS_QUERY = """\
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          path
          line
          comments(first: 1) {
            totalCount
            nodes { author { login } body }
          }
        }
      }
    }
  }
}
"""


def run(cmd: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, input=input_text, text=True, capture_output=True)


def run_gh(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return run(["gh", *args], input_text=input_text)


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


# ---------------------------------------------------------------- target resolution


def default_repo() -> str | None:
    p = run_gh(["repo", "view", "--json", "nameWithOwner"])
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)["nameWithOwner"]
    except (json.JSONDecodeError, KeyError):
        return None


def resolve_target(target: str, repo_flag: str | None) -> tuple[str, int]:
    """Turn a PR URL / number / branch / nothing into (owner/name, pr_number)."""
    target = (target or "").strip()

    m = PR_URL_RE.search(target)
    if m:
        return f"{m.group(1)}/{m.group(2)}", int(m.group(3))

    if re.fullmatch(r"#?\d+", target):
        repo = repo_flag or default_repo()
        if not repo:
            die("got a PR number but no repo — pass --repo owner/name or run inside a clone")
        return repo, int(target.lstrip("#"))

    branch = target
    if not branch:
        p = run(["git", "branch", "--show-current"])
        branch = (p.stdout or "").strip()
        if not branch:
            die("no target given and no current branch — pass a PR URL, number, or branch")

    repo = repo_flag or default_repo()
    listing = ["pr", "list", "--head", branch, "--state", "open", "--json", "number", "--limit", "1"]
    if repo:
        listing += ["--repo", repo]
    p = run_gh(listing)
    if p.returncode != 0:
        die(f"could not list PRs for branch '{branch}':\n{p.stderr.strip()}")
    rows = json.loads(p.stdout or "[]")
    if not rows:
        die(f"no open PR found for branch '{branch}'", code=2)
    if not repo:
        repo = default_repo()
        if not repo:
            die("resolved a PR but not the repo — pass --repo owner/name")
    return repo, rows[0]["number"]


# ---------------------------------------------------------------- gather


def fetch_threads(repo: str, number: int) -> tuple[list[dict], str | None]:
    """Existing review threads with resolution state (GraphQL-only information)."""
    owner, name = repo.split("/", 1)
    threads: list[dict] = []
    cursor: str | None = None
    while True:
        gh_args = [
            "api", "graphql",
            "-F", f"owner={owner}", "-F", f"name={name}", "-F", f"number={number}",
            "-f", f"query={THREADS_QUERY}",
        ]
        if cursor:
            gh_args += ["-F", f"cursor={cursor}"]
        p = run_gh(gh_args)
        if p.returncode != 0:
            return threads, f"could not fetch review threads: {(p.stderr or '').strip()[:200]}"
        try:
            page = json.loads(p.stdout)["data"]["repository"]["pullRequest"]["reviewThreads"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return threads, "unexpected reviewThreads response; existing-thread dedup may be incomplete"
        for node in page["nodes"]:
            first = (node["comments"]["nodes"] or [{}])[0]
            threads.append({
                "path": node["path"],
                "line": node["line"],
                "is_resolved": node["isResolved"],
                "is_outdated": node["isOutdated"],
                "author": (first.get("author") or {}).get("login"),
                "excerpt": (first.get("body") or "")[:300],
                "comment_count": node["comments"]["totalCount"],
            })
        if not page["pageInfo"]["hasNextPage"]:
            return threads, None
        cursor = page["pageInfo"]["endCursor"]


def url_matches(url: str, repo: str) -> bool:
    """True if a git remote URL points at owner/name (ssh or https, ±.git)."""
    url = url.lower()
    if url.endswith(".git"):
        url = url[:-4]
    return url.replace(":", "/").endswith("/" + repo.lower())


def matching_remote(repo: str) -> str | None:
    p = run(["git", "remote", "-v"])
    if p.returncode != 0:
        return None
    for line in p.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and url_matches(parts[1], repo):
            return parts[0]
    return None


def make_worktree(repo: str, number: int, head_sha: str, workdir: Path) -> tuple[str | None, str | None, str | None]:
    """Detached worktree of the PR head; never touches the user's checkout.

    Returns (worktree_path, repo_root, note)."""
    p = run(["git", "rev-parse", "--show-toplevel"])
    if p.returncode != 0:
        return None, None, "not inside a git repo; read files via gh api at the head SHA"
    root = p.stdout.strip()
    remote = matching_remote(repo)
    if not remote:
        return None, root, f"no git remote here matches {repo}; read files via gh api at the head SHA"
    f = run(["git", "fetch", "--quiet", remote, f"pull/{number}/head"])
    if f.returncode != 0:
        return None, root, f"git fetch {remote} pull/{number}/head failed: {(f.stderr or '').strip()[:200]}"
    path = str(workdir / "head")
    w = run(["git", "worktree", "add", "--detach", path, head_sha])
    if w.returncode == 0:
        return path, root, None
    w2 = run(["git", "worktree", "add", "--detach", path, "FETCH_HEAD"])
    if w2.returncode == 0:
        return path, root, f"worktree is at FETCH_HEAD, which may differ from recorded head {head_sha[:10]}"
    return None, root, f"could not create worktree: {(w.stderr or '').strip()[:200]}"


def cmd_gather(args: argparse.Namespace) -> int:
    repo, number = resolve_target(args.target, args.repo)
    meta_p = run_gh(["pr", "view", str(number), "--repo", repo, "--json",
                     "number,title,body,baseRefName,headRefOid,url,changedFiles,additions,deletions,files"])
    if meta_p.returncode != 0:
        die(f"could not read PR {repo}#{number}:\n{meta_p.stderr.strip()}")
    meta = json.loads(meta_p.stdout)
    head_sha = meta["headRefOid"]
    workdir = Path(tempfile.mkdtemp(prefix=f"pr-review-{number}-"))
    notes: list[str] = []

    diff_p = run_gh(["pr", "diff", str(number), "--repo", repo])
    diff_file: Path | None = None
    if diff_p.returncode == 0:
        diff_file = workdir / "diff.patch"
        diff_file.write_text(diff_p.stdout, encoding="utf-8")
    else:
        notes.append(f"could not fetch the diff ({(diff_p.stderr or '').strip()[:200]}); read files individually")

    (workdir / "pr_body.md").write_text(meta.get("body") or "", encoding="utf-8")

    threads, threads_note = fetch_threads(repo, number)
    (workdir / "threads.json").write_text(json.dumps(threads, indent=2), encoding="utf-8")
    if threads_note:
        notes.append(threads_note)

    worktree = repo_root = None
    if args.no_worktree:
        notes.append("worktree skipped (--no-worktree)")
    else:
        worktree, repo_root, wt_note = make_worktree(repo, number, head_sha, workdir)
        if wt_note:
            notes.append(wt_note)

    state = {
        "repo": repo, "pr": number, "head_sha": head_sha, "base": meta["baseRefName"],
        "url": meta["url"], "workdir": str(workdir), "worktree": worktree, "repo_root": repo_root,
    }
    (workdir / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    print(json.dumps({
        "repo": repo,
        "pr": number,
        "title": meta["title"],
        "url": meta["url"],
        "base": meta["baseRefName"],
        "head_sha": head_sha,
        "changed_files": meta.get("changedFiles"),
        "additions": meta.get("additions"),
        "deletions": meta.get("deletions"),
        "files": [{"path": f["path"], "additions": f["additions"], "deletions": f["deletions"]}
                  for f in meta.get("files") or []],
        "threads_open": sum(1 for t in threads if not t["is_resolved"]),
        "threads_resolved": sum(1 for t in threads if t["is_resolved"]),
        "workdir": str(workdir),
        "diff": str(diff_file) if diff_file else None,
        "threads": str(workdir / "threads.json"),
        "pr_body": str(workdir / "pr_body.md"),
        "worktree": worktree,
        "notes": notes,
    }, indent=2))
    return 0


# ---------------------------------------------------------------- findings → review


def validate_findings(findings: object) -> list[str]:
    if not isinstance(findings, list):
        return ["findings file must be a JSON array"]
    errors: list[str] = []
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"finding {i}: must be an object")
            continue
        for key in ("path", "severity", "title", "body"):
            if not f.get(key):
                errors.append(f"finding {i}: missing '{key}'")
        if f.get("severity") and f["severity"] not in SEVERITIES:
            errors.append(f"finding {i}: severity must be one of {', '.join(SEVERITIES)}")
        if isinstance(f.get("title"), str) and len(f["title"].strip()) > 120:
            errors.append(f"finding {i}: 'title' must be at most 120 characters")
        if isinstance(f.get("body"), str) and len(f["body"].split()) > 120:
            errors.append(f"finding {i}: 'body' must be at most 120 words")
        if "line" in f and not isinstance(f["line"], int):
            errors.append(f"finding {i}: 'line' must be an integer")
        if "start_line" in f:
            if "line" not in f:
                errors.append(f"finding {i}: 'start_line' requires 'line'")
            elif isinstance(f.get("start_line"), int) and isinstance(f.get("line"), int) and f["start_line"] >= f["line"]:
                errors.append(f"finding {i}: 'start_line' must be less than 'line'")
    return errors


def validate_suspicions(rows: object) -> list[str]:
    """Severe-but-unproved rows. Schema is small on purpose: where, what it would
    cost, and the single check that would settle it."""
    if not isinstance(rows, list):
        return ["suspicions file must be a JSON array"]
    errors = []
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            errors.append(f"suspicion {i}: must be an object")
            continue
        for key in ("path", "consequence", "check"):
            if not isinstance(r.get(key), str) or not r[key].strip():
                errors.append(f"suspicion {i}: missing required non-empty '{key}'")
        if "line" in r and not isinstance(r["line"], int):
            errors.append(f"suspicion {i}: 'line' must be an integer")
    return errors


def drop_low_priority(findings: list[dict]) -> tuple[list[dict], list[dict]]:
    """Default posting policy: only P1/P2 reach the pull request. Returns
    (posted, dropped); --include-low bypasses this."""
    posted = [f for f in findings if f["severity"] in ("P1", "P2")]
    low = [f for f in findings if f["severity"] in ("P3", "P4")]
    return posted, low


def split_findings(findings: list[dict], max_inline: int) -> tuple[list[dict], list[dict]]:
    """Keep every P1/P2 inline; apply the cap only to lower-priority findings."""
    ordered = sorted(findings, key=lambda f: SEVERITIES.index(f["severity"]))
    blocking = [f for f in ordered if f["severity"] in ("P1", "P2")]
    lower = [f for f in ordered if f["severity"] in ("P3", "P4")]
    lower_slots = max(max_inline - len(blocking), 0)
    return blocking + lower[:lower_slots], lower[lower_slots:]


def render_comment_body(finding: dict) -> str:
    sev = finding["severity"]
    badge = f"![{sev} Badge](https://img.shields.io/badge/{sev}-{BADGE_COLORS[sev]}?style=flat)"
    return f"**<sub><sub>{badge}</sub></sub>  {finding['title'].strip()}**\n\n{finding['body'].strip()}"


def finding_to_comment(finding: dict) -> dict:
    comment: dict = {"path": finding["path"], "body": render_comment_body(finding)}
    if "line" in finding:
        comment["line"] = finding["line"]
        comment["side"] = finding.get("side", "RIGHT")
        if "start_line" in finding:
            comment["start_line"] = finding["start_line"]
            comment["start_side"] = finding.get("start_side", comment["side"])
    return comment


# Stable identifier proving a review was posted by this skill rather than typed
# by hand. forge/scripts/pr_watch.py requires this exact string by default;
# changing it here without changing it there breaks the clean verdict.
SIGNATURE = "rehanhaider/pr-review-skill"


def render_summary(
    head_sha: str,
    findings: list[dict],
    folded: list[dict],
    signature: str | None = None,
    suspicions: list[dict] | None = None,
) -> str:
    counts = Counter(f["severity"] for f in findings)
    parts = [f"{counts[s]} {s}" for s in SEVERITIES if counts[s]]
    if findings:
        noun = "finding" if len(findings) == 1 else "findings"
        lines = [
            f"Reviewed `{head_sha[:10]}` — {len(findings)} {noun} ({', '.join(parts)})."
        ]
    elif suspicions:
        # Never the all-clear sentence while a severe candidate is unresolved:
        # automation reads that phrase as ready-to-merge.
        n = len(suspicions)
        lines = [f"Reviewed `{head_sha[:10]}` — no findings, "
                 f"{n} unverified."]
    else:
        # Exact wording: automation treats this phrase as the all-clear signal.
        lines = [f"Reviewed `{head_sha[:10]}` — no new issues found."]
    if folded:
        lines += ["", "Additional low-priority findings:", ""]
        for f in folded:
            loc = f"`{f['path']}:{f['line']}`" if "line" in f else f"`{f['path']}`"
            lines.append(f"- **{f['severity']}** {loc} — {f['title'].strip()}")
    if suspicions:
        # Severe candidates that could not be proved. They belong on the pull
        # request, not in a chat nobody reads: an automated loop can only act on
        # what GitHub shows it.
        lines += ["", "Unverified — severe if real, could not be proved:", ""]
        for s_ in suspicions:
            loc = f"`{s_['path']}:{s_['line']}`" if s_.get("line") else f"`{s_['path']}`"
            lines.append(f"- {loc} — {s_['consequence'].strip()} "
                         f"Check: {s_['check'].strip()}")
    if signature:
        # Trailer, never the first line: the all-clear sentence must stay first
        # so automation reading only line one is unaffected.
        lines += ["", f"— {signature}"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- anchor validation


def commentable_lines(diff_text: str) -> dict[str, dict[str, set[int]]]:
    """Map path -> {"RIGHT": new-file lines in hunks, "LEFT": old-file lines}.

    GitHub accepts inline comments only on lines that appear in a diff hunk:
    added and context lines on RIGHT (new-file numbering), deleted and context
    lines on LEFT (old-file numbering).
    """
    files: dict[str, dict[str, set[int]]] = {}
    current: dict[str, set[int]] | None = None
    old_path: str | None = None
    old_no = new_no = 0
    in_hunk = False

    def parse_path(header: str, prefix: str) -> str | None:
        target = header[4:].split("\t")[0]
        if target == "/dev/null":
            return None
        return target[len(prefix):] if target.startswith(prefix) else target

    for raw in diff_text.splitlines():
        if raw.startswith("diff --git"):
            in_hunk = False
            current = None
            old_path = None
            continue
        m = HUNK_RE.match(raw)
        if m:
            old_no, new_no = int(m.group(1)), int(m.group(3))
            in_hunk = current is not None
            continue
        if in_hunk:
            if raw.startswith("+"):
                current["RIGHT"].add(new_no)
                new_no += 1
            elif raw.startswith("-"):
                current["LEFT"].add(old_no)
                old_no += 1
            elif raw.startswith("\\"):
                pass  # "\ No newline at end of file"
            else:  # context line (" " prefix, or "" if trailing whitespace was stripped)
                current["RIGHT"].add(new_no)
                current["LEFT"].add(old_no)
                new_no += 1
                old_no += 1
        else:
            if raw.startswith("--- "):
                old_path = parse_path(raw, "a/")
            elif raw.startswith("+++ "):
                new_path = parse_path(raw, "b/")
                path = new_path or old_path  # deleted files keep their old path
                current = files.setdefault(path, {"RIGHT": set(), "LEFT": set()}) if path else None
    return files


def validate_comments(comments: list[dict], diff_text: str) -> list[str]:
    lines_map = commentable_lines(diff_text)
    errors: list[str] = []
    for i, c in enumerate(comments):
        path = c.get("path")
        if not path or not c.get("body"):
            errors.append(f"comment {i}: missing required 'path' or 'body'")
            continue
        if "line" not in c:
            continue  # file-level comment
        for line_key, side_key, default_side in (("line", "side", "RIGHT"), ("start_line", "start_side", c.get("side", "RIGHT"))):
            if line_key not in c:
                continue
            side = c.get(side_key, default_side)
            valid = lines_map.get(path, {}).get(side, set())
            if c[line_key] in valid:
                continue
            if not lines_map.get(path):
                errors.append(f"comment {i} ({path}:{c[line_key]}): file is not in the PR diff")
            elif not valid:
                errors.append(f"comment {i} ({path}:{c[line_key]}): no commentable {side} lines in this file's hunks")
            else:
                nearest = min(valid, key=lambda n: abs(n - c[line_key]))
                errors.append(
                    f"comment {i} ({path}:{c[line_key]}, {side}): line is not part of the diff; "
                    f"nearest commentable {side} line is {nearest}"
                )
    return errors


# ---------------------------------------------------------------- post


def cmd_post(args: argparse.Namespace) -> int:
    repo, pr, commit = args.repo, args.pr, args.commit
    if args.workdir:
        state = json.loads((Path(args.workdir) / "state.json").read_text(encoding="utf-8"))
        repo = repo or state.get("repo")
        pr = pr or state.get("pr")
        commit = commit or state.get("head_sha")
    if not (repo and pr and commit):
        die("post needs --workdir (from gather) or all of --repo, --pr, --commit")

    findings = json.loads(args.findings_file.read_text(encoding="utf-8"))
    errors = validate_findings(findings)
    if errors:
        print("Refusing to post: invalid findings:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if not args.include_low:
        findings, low = drop_low_priority(findings)
        if low:
            print(f"note: {len(low)} P3/P4 finding(s) suppressed — only P1/P2 "
                  "are posted by default; pass --include-low to post them",
                  file=sys.stderr)

    inline, folded = split_findings(findings, args.max_inline)
    comments = [finding_to_comment(f) for f in inline]
    if folded:
        print(f"note: {len(folded)} lower-priority finding(s) beyond "
              f"--max-inline={args.max_inline} were folded into the summary body",
              file=sys.stderr)
    suspicions: list[dict] = []
    if args.suspicions_file:
        suspicions = json.loads(args.suspicions_file.read_text(encoding="utf-8"))
        bad = validate_suspicions(suspicions)
        if bad:
            print("Refusing to post: invalid suspicions file:", file=sys.stderr)
            for e in bad:
                print(f"  - {e}", file=sys.stderr)
            return 1

    body = render_summary(commit, findings, folded, args.signed_by, suspicions)

    if comments and not args.no_validate:
        diff = run_gh(["pr", "diff", str(pr), "--repo", repo])
        if diff.returncode != 0:
            print(f"warning: could not fetch diff for validation:\n{diff.stderr}", file=sys.stderr)
        else:
            anchor_errors = validate_comments(comments, diff.stdout)
            if anchor_errors:
                print("Refusing to post: invalid comment anchors (the whole review would 422):", file=sys.stderr)
                for e in anchor_errors:
                    print(f"  - {e}", file=sys.stderr)
                return 1

    head = run_gh(["pr", "view", str(pr), "--repo", repo, "--json", "headRefOid"])
    if head.returncode == 0:
        live_sha = json.loads(head.stdout).get("headRefOid", "")
        if live_sha and live_sha != commit:
            moved = (
                f"PR head is now {live_sha[:10]} but the reviewed commit is "
                f"{commit[:10]} (new commits were pushed)"
            )
            if args.dry_run or args.allow_moved_head:
                print(
                    f"warning: {moved}; re-check that findings still apply",
                    file=sys.stderr,
                )
            else:
                # Posting now would attach findings derived from the old code to
                # a commit nobody reviewed. Re-review instead of re-anchoring.
                print(
                    f"Refusing to post: {moved}.\n"
                    "Re-run gather and review the new head; pass "
                    "--allow-moved-head only if the findings provably still apply.",
                    file=sys.stderr,
                )
                return 3

    payload: dict[str, object] = {"commit_id": commit, "event": args.event, "body": body}
    if comments:
        payload["comments"] = comments

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        print("dry run: validation passed, nothing posted", file=sys.stderr)
        return 0

    proc = run_gh(
        ["api", "--method", "POST", f"repos/{repo}/pulls/{pr}/reviews", "--input", "-"],
        input_text=json.dumps(payload),
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode

    try:
        print(json.loads(proc.stdout).get("html_url", proc.stdout))
    except (json.JSONDecodeError, AttributeError):
        print(proc.stdout)
    return 0


# ---------------------------------------------------------------- cleanup


def cmd_cleanup(args: argparse.Namespace) -> int:
    state_file = Path(args.workdir) / "state.json"
    if not state_file.is_file():
        die(f"no state.json in {args.workdir} — was this workdir created by gather?")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    worktree, root = state.get("worktree"), state.get("repo_root")
    if not worktree:
        print("no worktree to remove")
        return 0
    git = ["git", "-C", root] if root else ["git"]
    p = run([*git, "worktree", "remove", worktree])
    if p.returncode != 0:
        if not Path(worktree).exists():
            run([*git, "worktree", "prune"])
            print("worktree already gone; pruned stale entries")
            return 0
        print(f"git worktree remove failed: {(p.stderr or '').strip()}", file=sys.stderr)
        return 1
    print(f"removed worktree {worktree}")
    return 0


# ---------------------------------------------------------------- entry point


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    g = sub.add_parser("gather", help="resolve the PR and stage review context in a temp workdir")
    g.add_argument("target", nargs="?", default="",
                   help="PR URL, PR number, or branch name (default: current branch)")
    g.add_argument("--repo", help="owner/name (default: repo of the current directory)")
    g.add_argument("--no-worktree", action="store_true", help="skip creating the read-only worktree")
    g.set_defaults(func=cmd_gather)

    p = sub.add_parser("post", help="render findings.json and post the review")
    p.add_argument("--workdir", help="workdir from gather (supplies --repo/--pr/--commit)")
    p.add_argument("--repo", help="owner/name (overrides workdir state)")
    p.add_argument("--pr", type=int, help="PR number (overrides workdir state)")
    p.add_argument("--commit", help="reviewed commit SHA (overrides workdir state)")
    p.add_argument("--findings-file", type=Path, required=True)
    p.add_argument("--suspicions-file", type=Path,
                   help="JSON array of {path, line?, consequence, check} for severe "
                        "candidates that could not be proved; rendered into the summary")
    p.add_argument("--event", default="COMMENT", choices=["COMMENT", "REQUEST_CHANGES", "APPROVE"])
    p.add_argument("--include-low", action="store_true",
                   help="also post P3/P4 findings; by default only P1/P2 reach "
                        "the pull request and lower tiers are dropped")
    p.add_argument("--max-inline", type=int, default=10,
                   help="P3/P4 inline cap when --include-low is set; P1/P2 always stay inline")
    p.add_argument("--no-validate", action="store_true", help="skip diff-anchor validation")
    p.add_argument("--dry-run", action="store_true", help="validate and print the payload without posting")
    p.add_argument("--allow-moved-head", action="store_true",
                   help="post even though the PR head moved since the review (exit 3 otherwise)")
    p.add_argument("--signed-by", default=SIGNATURE,
                   help=f"trailer identifying who produced the review (default: {SIGNATURE!r}); "
                        f"append the model, e.g. '{SIGNATURE} · Claude Opus 5'. Pass '' to omit")
    p.set_defaults(func=cmd_post)

    c = sub.add_parser("cleanup", help="remove the worktree gather created")
    c.add_argument("--workdir", required=True)
    c.set_defaults(func=cmd_cleanup)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
