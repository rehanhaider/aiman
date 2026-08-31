#!/usr/bin/env python3
"""Report or wait for review information on a pull request.

Subcommands:
  state  print the PR's current review state as JSON and exit
  wait   block until new review activity lands, then print that state as JSON

Both emit one JSON object on stdout. Progress goes to stderr. Requires an
authenticated `gh` CLI.

Exit codes: 0 state resolved (read `verdict`), 2 wait timed out, 1 error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Any

THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          originalLine
          comments(first: 50) {
            totalCount
            nodes {
              databaseId
              url
              body
              createdAt
              author { login }
            }
          }
        }
      }
    }
  }
}
"""

PR_FIELDS = (
    "number,url,title,state,isDraft,headRefName,headRefOid,baseRefName,"
    "author,reviewDecision,mergeable,mergeStateStatus"
)


def die(msg: str, code: int = 1) -> None:
    print(f"pr_watch: {msg}", file=sys.stderr)
    raise SystemExit(code)


def note(msg: str) -> None:
    print(f"pr_watch: {msg}", file=sys.stderr, flush=True)


def run_gh(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8"
    )
    if check and proc.returncode != 0:
        die(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def gh_json_lines(args: list[str]) -> list[dict]:
    """Run a paginated `gh api ... --jq '.[]'` call and parse NDJSON output."""
    proc = run_gh(args, check=False)
    if proc.returncode != 0:
        note(f"warning: gh {' '.join(args)} failed: {proc.stderr.strip()}")
        return []
    items: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            note("warning: skipped an unparsable API line")
    return items


def resolve_pr(target: str | None, repo: str | None) -> dict:
    args = ["pr", "view"]
    if target:
        args.append(target)
    if repo:
        args += ["--repo", repo]
    args += ["--json", PR_FIELDS]
    proc = run_gh(args, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip()
        die(
            "could not resolve a pull request"
            + (f" for '{target}'" if target else " for the current branch")
            + f": {detail}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        die("gh pr view returned unparsable JSON")
        raise  # unreachable, keeps type checkers quiet


def repo_slug(target: str | None, repo: str | None) -> str:
    if repo:
        return repo
    proc = run_gh(["repo", "view", "--json", "nameWithOwner"], check=False)
    if proc.returncode == 0:
        try:
            return json.loads(proc.stdout)["nameWithOwner"]
        except (json.JSONDecodeError, KeyError):
            pass
    die("could not determine the repository; pass --repo owner/name")
    raise  # unreachable


_VIEWER: str | None = None


def viewer_login() -> str:
    """The authenticated gh account, used to tell our replies from theirs."""
    global _VIEWER
    if _VIEWER is None:
        proc = run_gh(["api", "user", "--jq", ".login"], check=False)
        _VIEWER = proc.stdout.strip() if proc.returncode == 0 else ""
    return _VIEWER


def parse_review_id(value: str | None) -> int | None:
    """Accept a bare review id or the html_url `pr_review.py post` prints."""
    if not value:
        return None
    match = re.search(r"pullrequestreview-(\d+)", value)
    if match:
        return int(match.group(1))
    if value.strip().isdigit():
        return int(value.strip())
    die(f"could not read a review id from '{value}'")
    raise  # unreachable


def fetch_threads(repo: str, number: int) -> tuple[list[dict], str | None]:
    owner, _, name = repo.partition("/")
    viewer = viewer_login()
    threads: list[dict] = []
    cursor: str | None = None
    while True:
        args = [
            "api",
            "graphql",
            "-f",
            f"query={THREADS_QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={number}",
        ]
        if cursor:
            args += ["-F", f"cursor={cursor}"]
        proc = run_gh(args, check=False)
        if proc.returncode != 0:
            return threads, f"reviewThreads query failed: {proc.stderr.strip()}"
        try:
            page = json.loads(proc.stdout)["data"]["repository"]["pullRequest"][
                "reviewThreads"
            ]
        except (json.JSONDecodeError, KeyError, TypeError):
            return threads, "unexpected reviewThreads response"
        for node in page.get("nodes") or []:
            block = node.get("comments") or {}
            comments = block.get("nodes") or []
            first = comments[0] if comments else {}
            last = comments[-1] if comments else {}
            author = (first.get("author") or {}).get("login")
            last_author = (last.get("author") or {}).get("login")
            threads.append(
                {
                    "thread_id": node["id"],
                    "comment_id": first.get("databaseId"),
                    "is_resolved": bool(node.get("isResolved")),
                    "is_outdated": bool(node.get("isOutdated")),
                    "path": node.get("path"),
                    "line": node.get("line"),
                    "original_line": node.get("originalLine"),
                    "author": author,
                    "url": first.get("url"),
                    "created_at": first.get("createdAt"),
                    "body": first.get("body") or "",
                    "comment_count": block.get("totalCount", len(comments)),
                    "last_comment": {
                        "author": last_author,
                        "created_at": last.get("createdAt"),
                        "body": last.get("body") or "",
                    }
                    if comments
                    else None,
                    # True when the newest word in the thread is not ours, i.e.
                    # the reviewer said something we have not answered yet.
                    "needs_reply": bool(last_author and last_author != viewer),
                }
            )
        info = page.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            return threads, None
        cursor = info.get("endCursor")


def fetch_reviews(repo: str, number: int) -> list[dict]:
    raw = gh_json_lines(
        ["api", f"repos/{repo}/pulls/{number}/reviews", "--paginate", "--jq", ".[]"]
    )
    reviews = [
        {
            "id": r.get("id"),
            "author": (r.get("user") or {}).get("login"),
            "state": r.get("state"),
            "submitted_at": r.get("submitted_at"),
            "commit_id": r.get("commit_id"),
            "url": r.get("html_url"),
            "body": r.get("body") or "",
        }
        for r in raw
        # PENDING reviews are drafts only the author can see; they are not signal.
        if r.get("state") != "PENDING"
    ]
    reviews.sort(key=lambda r: (r.get("submitted_at") or "", r.get("id") or 0))
    return reviews


def fetch_comments(repo: str, number: int) -> list[dict]:
    raw = gh_json_lines(
        ["api", f"repos/{repo}/issues/{number}/comments", "--paginate", "--jq", ".[]"]
    )
    comments = [
        {
            "id": c.get("id"),
            "author": (c.get("user") or {}).get("login"),
            "created_at": c.get("created_at"),
            "url": c.get("html_url"),
            "body": c.get("body") or "",
        }
        for c in raw
    ]
    comments.sort(key=lambda c: (c.get("created_at") or "", c.get("id") or 0))
    return comments


def collect(repo: str, number: int, ignore: set[str]) -> dict:
    threads, thread_warning = fetch_threads(repo, number)
    reviews = fetch_reviews(repo, number)
    comments = fetch_comments(repo, number)

    def kept(author: str | None) -> bool:
        return (author or "").lower() not in ignore

    return {
        "threads": [t for t in threads if kept(t["author"])],
        "reviews": [r for r in reviews if kept(r["author"])],
        "comments": [c for c in comments if kept(c["author"])],
        "warning": thread_warning,
    }


# The exact sentence pr_review.py posts when it finds nothing. Matched against
# the first line only, anchored: prose such as "no major issues, but ..." is an
# objection, not an all-clear, and substring matching cannot tell them apart.
# Must match pr-review/scripts/pr_review.py SIGNATURE. Required by default so a
# review typed by hand cannot pass as an automated one; external reviewers such
# as codex sign differently and need --allow-unsigned.
DEFAULT_SIGNATURE = "rehanhaider/pr-review-skill"

CLEAN_MARKER_RE = re.compile(
    r"^reviewed\s+`?(?P<sha>[0-9a-f]{7,40})`?\s*[—–-]\s*"
    r"no new issues found\.?$"
)


def clean_marker_sha(body: str) -> str | None:
    """Return the reviewed SHA when the body's first line is the exact all-clear."""
    lines = (body or "").strip().splitlines()
    if not lines:
        return None
    match = CLEAN_MARKER_RE.match(" ".join(lines[0].lower().split()))
    return match.group("sha") if match else None


def is_author_reply_shell(review: dict, pr_author: str | None) -> bool:
    """True for the empty COMMENTED review GitHub fabricates when the PR author
    replies inside a review thread over the REST API. It is conversation
    plumbing, not an attestation: it must not make a head look reviewed, and it
    must not turn an otherwise clean head into "unclear"."""
    return bool(
        pr_author
        and review.get("author") == pr_author
        and review.get("state") == "COMMENTED"
        and not (review.get("body") or "").strip()
    )


# External reviewers do not post pr-review's marker sentence, and several do
# not post a review object at all. Codex answers a no-findings round with an
# issue comment ("Codex Review: Didn't find any major issues. ... Reviewed
# commit `<sha>`") or with only a +1 reaction on the trigger comment; only its
# has-findings round arrives as a real PR review. A profile names the login,
# how its text anchors the reviewed commit, and the exact all-clear line.
# Only a profile with both sha_re and clean_re can ever grade clean; every
# other recognized reviewer response wakes the wait and grades unclear, which
# forces a read instead of a silent pass.
EXTERNAL_REVIEWER_PROFILES: list[dict[str, str]] = [
    {
        "name": "codex",
        "login_re": r"^chatgpt-codex-connector(\[bot\])?$",
        "sha_re": r"reviewed commit:?[\s*]*`?([0-9a-f]{7,40})`?",
        "clean_re": r"^codex review: didn'?t find any major issues",
    },
    # Recognized so their responses wake `wait` and force an explicit read;
    # never auto-clean, because their all-clear formats are unverified here.
    {"name": "cursor-bugbot", "login_re": r"^cursor(\[bot\])?$"},
    {"name": "coderabbit", "login_re": r"^coderabbitai(\[bot\])?$"},
    {"name": "gemini", "login_re": r"^gemini-code-assist(\[bot\])?$"},
    {"name": "copilot", "login_re": r"^copilot-pull-request-reviewer(\[bot\])?$"},
]


def reviewer_profiles(args: argparse.Namespace) -> list[dict[str, str]]:
    profiles = list(EXTERNAL_REVIEWER_PROFILES)
    for spec in getattr(args, "attest_profile", None) or []:
        parts = spec.split(":::")
        if len(parts) != 3 or not all(parts):
            die("--attest-profile needs LOGIN_RE:::SHA_RE:::CLEAN_RE")
        profiles.append(
            {
                "name": f"custom:{parts[0]}",
                "login_re": parts[0],
                "sha_re": parts[1],
                "clean_re": parts[2],
            }
        )
    for pattern in getattr(args, "reviewer_bot", None) or []:
        profiles.append({"name": f"custom:{pattern}", "login_re": pattern})
    return profiles


def profile_for(
    login: str | None, profiles: list[dict[str, str]]
) -> dict[str, str] | None:
    """The reviewer profile for a login. Unknown `[bot]` accounts get a
    nameless profile: enough to wake the wait, never enough to grade clean."""
    if not login:
        return None
    for profile in profiles:
        if profile.get("login_re") and re.search(
            profile["login_re"], login, re.IGNORECASE
        ):
            return profile
    if login.endswith("[bot]"):
        return {"name": login}
    return None


def comment_attestation(
    comment: dict,
    head_sha: str,
    profiles: list[dict[str, str]],
    signature: str | None,
) -> dict | None:
    """Grade one issue comment as an external reviewer's review-equivalent.

    A clean grade requires the profile's exact all-clear line AND a commit
    reference matching the current head — a statement that does not name what
    it reviewed cannot attest anything. A signature requirement (local/cursor
    modes) keeps unsigned bot prose out of "clean" entirely."""
    profile = profile_for(comment.get("author"), profiles)
    if profile is None:
        return None
    body = comment.get("body") or ""
    attestation: dict[str, Any] = {
        "kind": "comment",
        "author": comment.get("author"),
        "reviewer": profile.get("name"),
        "url": comment.get("url"),
        "created_at": comment.get("created_at"),
        "sha": None,
        "grade": "unclear",
    }
    sha_re = profile.get("sha_re")
    if sha_re:
        match = re.search(sha_re, body, re.IGNORECASE)
        if match:
            attestation["sha"] = match.group(1).lower()
    sha = attestation["sha"]
    if sha and not head_sha.lower().startswith(sha):
        attestation["grade"] = "stale"
        return attestation
    clean_re = profile.get("clean_re")
    lines = (
        " ".join(raw.lower().split())
        for raw in body.strip().splitlines()
        if raw.strip()
    )
    if sha and clean_re and any(re.search(clean_re, line) for line in lines):
        attestation["grade"] = "clean" if signature is None else "unsigned"
    return attestation


def external_attestations(
    comments: list[dict],
    head_sha: str,
    profiles: list[dict[str, str]],
    signature: str | None,
) -> list[dict]:
    """Newest attestation per reviewer login; input is sorted oldest first."""
    latest: dict[str | None, dict] = {}
    for comment in comments:
        attestation = comment_attestation(comment, head_sha, profiles, signature)
        if attestation is not None:
            latest[attestation["author"]] = attestation
    return list(latest.values())


def parse_comment_id(value: str | None) -> int | None:
    """Accept a bare comment id or the html_url `gh pr comment` prints."""
    if not value:
        return None
    match = re.search(r"issuecomment-(\d+)", value)
    if match:
        return int(match.group(1))
    if value.strip().isdigit():
        return int(value.strip())
    die(f"could not read a comment id from '{value}'")
    raise  # unreachable


def detect_trigger_comment(comments: list[dict], viewer: str) -> dict | None:
    """The newest '@<reviewer> review' comment we posted — where a reviewer
    that answers with only an emoji reaction will put it."""
    for comment in reversed(comments):
        if comment.get("author") == viewer and re.search(
            r"@\S+\s+review\b", comment.get("body") or ""
        ):
            return comment
    return None


def resolve_trigger(
    repo: str, comments: list[dict], explicit_id: int | None
) -> dict | None:
    if explicit_id is not None:
        for comment in comments:
            if comment.get("id") == explicit_id:
                return comment
        raw = gh_json_lines(
            ["api", f"repos/{repo}/issues/comments/{explicit_id}", "--jq", "."]
        )
        if raw:
            c = raw[0]
            return {
                "id": c.get("id"),
                "author": (c.get("user") or {}).get("login"),
                "created_at": c.get("created_at"),
                "url": c.get("html_url"),
                "body": c.get("body") or "",
            }
        return {"id": explicit_id}
    return detect_trigger_comment(comments, viewer_login())


def fetch_reactions(repo: str, comment_id: int) -> list[dict]:
    raw = gh_json_lines(
        [
            "api",
            f"repos/{repo}/issues/comments/{comment_id}/reactions",
            "--paginate",
            "--jq",
            ".[]",
        ]
    )
    return [
        {
            "author": (r.get("user") or {}).get("login"),
            "content": r.get("content"),
            "created_at": r.get("created_at"),
        }
        for r in raw
    ]


_COMMITTED_AT: dict[str, str | None] = {}


def head_committed_at(repo: str, sha: str) -> str | None:
    """When the head commit reached its final form, to anchor reaction-only
    attestations: a +1 on a trigger older than the head answers an older ask."""
    if sha not in _COMMITTED_AT:
        proc = run_gh(
            ["api", f"repos/{repo}/commits/{sha}", "--jq", ".commit.committer.date"],
            check=False,
        )
        _COMMITTED_AT[sha] = (
            proc.stdout.strip()
            if proc.returncode == 0 and proc.stdout.strip()
            else None
        )
    return _COMMITTED_AT[sha]


def reaction_attestation(
    repo: str,
    head_sha: str,
    trigger: dict | None,
    profiles: list[dict[str, str]],
    signature: str | None,
) -> dict | None:
    """A recognized reviewer's +1 on the trigger comment — codex's documented
    no-findings reply when it posts nothing at all. Valid only when the trigger
    was posted after the head commit existed, so the ask it answers is this
    head and not an earlier one."""
    if trigger is None or trigger.get("id") is None:
        return None
    for reaction in fetch_reactions(repo, trigger["id"]):
        profile = profile_for(reaction.get("author"), profiles)
        if profile is None or reaction.get("content") != "+1":
            continue
        committed = head_committed_at(repo, head_sha)
        anchored = bool(committed and (trigger.get("created_at") or "") > committed)
        if anchored:
            grade = "clean" if signature is None else "unsigned"
        else:
            grade = "unanchored"
        return {
            "kind": "reaction",
            "author": reaction.get("author"),
            "reviewer": profile.get("name"),
            "sha": head_sha.lower() if anchored else None,
            "grade": grade,
            "trigger_comment": trigger.get("url"),
            "created_at": reaction.get("created_at"),
        }
    return None


def reviews_missing_marker(
    at_head: list[dict], head_sha: str, signature: str | None = None
) -> list[dict]:
    """Reviews of this head that do not carry an all-clear for this head.

    One review per author, newest first, so that an earlier objection cannot be
    outvoted by a later reviewer simply because it was posted first. When a
    signature is required, a review must also carry it — a human typing the
    all-clear sentence by hand then cannot satisfy the automation.
    """
    latest_by_author: dict[str | None, dict] = {}
    for review in at_head:
        latest_by_author[review.get("author")] = review
    missing = []
    for review in latest_by_author.values():
        body = review.get("body") or ""
        sha = clean_marker_sha(body)
        if sha is None or not head_sha.lower().startswith(sha):
            missing.append(review)
        elif signature and signature.lower() not in body.lower():
            missing.append(review)
    return missing


def verdict_for(
    snapshot: dict,
    unresolved: list[dict],
    head_sha: str,
    review_decision: str | None,
    required_review_id: int | None = None,
    required_signature: str | None = None,
    attestations: list[dict] | None = None,
    pr_author: str | None = None,
) -> str:
    """Unresolved conversations decide first; attestations only break a tie.

    Absence of findings is not evidence of a review: a pull request nobody has
    looked at also has zero unresolved threads. Only an explicit all-clear for
    this exact head — a marker review, an external reviewer's no-findings
    statement naming the head, or its anchored +1 reaction — from every
    reviewer that spoke of this head returns "clean".
    """
    if snapshot.get("warning"):
        # A partial fetch undercounts threads, which biases toward "clean".
        return "unknown"
    if unresolved:
        return "findings"
    if review_decision == "CHANGES_REQUESTED":
        # Nothing to rectify, and only the reviewer can clear the decision.
        return "blocked"

    attestations = attestations or []
    reviews = [
        r for r in snapshot["reviews"] if not is_author_reply_shell(r, pr_author)
    ]
    if not reviews and not attestations:
        return "unreviewed"

    at_head = [r for r in reviews if r.get("commit_id") == head_sha]
    at_head_attestations = [
        a
        for a in attestations
        if a.get("sha") and head_sha.lower().startswith(a["sha"])
    ]
    if not at_head and not at_head_attestations:
        return "stale"

    if required_review_id is not None and not any(
        r.get("id") == required_review_id for r in at_head
    ):
        # The review we commissioned never landed. Whatever else is here, the
        # work we asked for did not happen.
        return "unreviewed"

    if reviews_missing_marker(at_head, head_sha, required_signature):
        return "unclear"
    if any(a.get("grade") != "clean" for a in at_head_attestations):
        return "unclear"
    return "clean"


def resolve_verdict(
    pr: dict,
    snapshot: dict,
    unresolved: list[dict],
    head_sha: str,
    timed_out: bool,
    required_review_id: int | None = None,
    required_signature: str | None = None,
    attestations: list[dict] | None = None,
) -> str:
    """Terminal pull-request states outrank any review signal."""
    if pr["state"] != "OPEN":
        return "closed"
    if pr.get("isDraft"):
        # Reviewers skip drafts, so the loop would stall with no signal at all.
        return "draft"
    if timed_out:
        return "timeout"
    return verdict_for(
        snapshot,
        unresolved,
        head_sha,
        pr.get("reviewDecision") or None,
        required_review_id,
        required_signature,
        attestations,
        (pr.get("author") or {}).get("login"),
    )


def build_state(
    pr: dict,
    repo: str,
    snapshot: dict,
    *,
    baseline: dict | None = None,
    waited: float | None = None,
    timed_out: bool = False,
    required_review_id: int | None = None,
    required_signature: str | None = None,
    profiles: list[dict[str, str]] | None = None,
    trigger_comment: dict | None = None,
) -> dict:
    # Outdated means the anchor line moved, not that the concern was addressed —
    # an unrelated edit in the same file outdates a thread. Counting these as
    # resolved would silently drop live findings.
    unresolved = [t for t in snapshot["threads"] if not t["is_resolved"]]
    outdated_unresolved = [t for t in unresolved if t["is_outdated"]]
    head_sha = pr["headRefOid"]
    pr_author = (pr.get("author") or {}).get("login")
    profiles = profiles if profiles is not None else EXTERNAL_REVIEWER_PROFILES
    attestations = external_attestations(
        snapshot["comments"], head_sha, profiles, required_signature
    )
    from_reaction = reaction_attestation(
        repo, head_sha, trigger_comment, profiles, required_signature
    )
    if from_reaction is not None:
        attestations.append(from_reaction)
    shells = [
        r for r in snapshot["reviews"] if is_author_reply_shell(r, pr_author)
    ]
    reviews = [r for r in snapshot["reviews"] if not is_author_reply_shell(r, pr_author)]
    at_head = [r for r in reviews if r.get("commit_id") == head_sha]
    attestations_at_head = [
        a
        for a in attestations
        if a.get("sha") and head_sha.lower().startswith(a["sha"])
    ]
    state: dict[str, Any] = {
        "repo": repo,
        "number": pr["number"],
        "url": pr["url"],
        "title": pr["title"],
        "pr_state": pr["state"],
        "is_draft": pr["isDraft"],
        "branch": pr["headRefName"],
        "base": pr["baseRefName"],
        "head_sha": pr["headRefOid"],
        "author": (pr.get("author") or {}).get("login"),
        "review_decision": pr.get("reviewDecision"),
        "mergeable": pr.get("mergeable"),
        "merge_state": pr.get("mergeStateStatus"),
        "verdict": resolve_verdict(
            pr,
            snapshot,
            unresolved,
            head_sha,
            timed_out,
            required_review_id,
            required_signature,
            attestations,
        ),
        "required_review_id": required_review_id,
        "required_review_present": None
        if required_review_id is None
        else any(r.get("id") == required_review_id for r in at_head),
        "unresolved_count": len(unresolved),
        "unresolved_threads": unresolved,
        "outdated_unresolved_count": len(outdated_unresolved),
        "resolved_count": len(snapshot["threads"]) - len(unresolved),
        "latest_review": reviews[-1] if reviews else None,
        "latest_review_at_head": at_head[-1] if at_head else None,
        "reviews_at_head": len(at_head),
        "reviews_at_head_without_marker": [
            {"author": r.get("author"), "state": r.get("state"), "url": r.get("url")}
            for r in reviews_missing_marker(at_head, head_sha, required_signature)
        ],
        "review_count": len(reviews),
        # Review-equivalents from external reviewers that answer outside the
        # review channel (codex comments / reactions). Grades: clean, unsigned
        # (clean text but a signature is required), unclear, stale, unanchored.
        "external_attestations": attestations,
        "attestations_at_head": len(attestations_at_head),
        "author_reply_shell_reviews": len(shells),
        "trigger_comment": (trigger_comment or {}).get("url"),
    }
    if snapshot.get("warning"):
        state["warning"] = snapshot["warning"]
    if waited is not None:
        state["waited_seconds"] = round(waited, 1)
    if baseline is not None:
        seen_reviews = {r["id"] for r in baseline["reviews"]}
        seen_threads = {t["thread_id"] for t in baseline["threads"]}
        seen_comments = {c["id"] for c in baseline["comments"]}
        state["new_since_baseline"] = {
            "reviews": [r for r in reviews if r["id"] not in seen_reviews],
            "threads": [
                t for t in snapshot["threads"] if t["thread_id"] not in seen_threads
            ],
            "comments": [
                c for c in snapshot["comments"] if c["id"] not in seen_comments
            ],
        }
        state["head_moved"] = baseline["head_sha"] != pr["headRefOid"]
    return state


def required_signature(args: argparse.Namespace) -> str | None:
    """The signature a review must carry, or None when unsigned is acceptable."""
    if args.allow_unsigned:
        return None
    return args.require_signature or None


def cmd_state(args: argparse.Namespace) -> int:
    repo = repo_slug(args.target, args.repo)
    pr = resolve_pr(args.target, repo)
    ignore = {a.lower() for a in args.ignore_author}
    snapshot = collect(repo, pr["number"], ignore)
    profiles = reviewer_profiles(args)
    trigger = resolve_trigger(
        repo, snapshot["comments"], parse_comment_id(args.trigger_comment)
    )
    print(
        json.dumps(
            build_state(
                pr,
                repo,
                snapshot,
                required_review_id=parse_review_id(args.require_review),
                required_signature=required_signature(args),
                profiles=profiles,
                trigger_comment=trigger,
            ),
            indent=2,
        )
    )
    return 0


def cmd_wait(args: argparse.Namespace) -> int:
    repo = repo_slug(args.target, args.repo)
    pr = resolve_pr(args.target, repo)
    number = pr["number"]
    ignore = {a.lower() for a in args.ignore_author}
    wake_on = {w.strip() for w in args.wake_on.split(",") if w.strip()}
    required_review_id = parse_review_id(args.require_review)
    profiles = reviewer_profiles(args)
    expect_sha = args.expect_review_of
    if expect_sha == "head":
        expect_sha = pr["headRefOid"]

    baseline = collect(repo, number, ignore)
    baseline["head_sha"] = pr["headRefOid"]
    trigger = resolve_trigger(
        repo, baseline["comments"], parse_comment_id(args.trigger_comment)
    )
    baseline_reactions: set[tuple[str | None, str | None]] = set()
    if trigger is not None and trigger.get("id") is not None:
        baseline_reactions = {
            (r.get("author"), r.get("content"))
            for r in fetch_reactions(repo, trigger["id"])
        }
    note(
        f"watching {repo}#{number} at {pr['headRefOid'][:10]} — "
        f"{len(baseline['reviews'])} reviews, {len(baseline['threads'])} threads; "
        f"waking on {', '.join(sorted(wake_on))}"
        + (
            f"; reactions on comment {trigger['id']}"
            if trigger is not None and trigger.get("id") is not None
            else ""
        )
        + f"; timeout {args.timeout}s"
    )

    seen_reviews = {r["id"] for r in baseline["reviews"]}
    seen_threads = {t["thread_id"] for t in baseline["threads"]}
    seen_comments = {c["id"] for c in baseline["comments"]}

    started = time.monotonic()
    while True:
        elapsed = time.monotonic() - started
        remaining = args.timeout - elapsed
        if remaining <= 0:
            pr = resolve_pr(str(number), repo)
            snapshot = collect(repo, number, ignore)
            print(
                json.dumps(
                    build_state(
                        pr,
                        repo,
                        snapshot,
                        baseline=baseline,
                        waited=elapsed,
                        timed_out=True,
                        required_review_id=required_review_id,
                        required_signature=required_signature(args),
                        profiles=profiles,
                        trigger_comment=trigger,
                    ),
                    indent=2,
                )
            )
            note("timed out with no new review information")
            return 2

        time.sleep(min(args.interval, remaining))
        elapsed = time.monotonic() - started

        pr = resolve_pr(str(number), repo)
        if pr["state"] != "OPEN":
            snapshot = collect(repo, number, ignore)
            print(
                json.dumps(
                    build_state(
                        pr,
                        repo,
                        snapshot,
                        baseline=baseline,
                        waited=elapsed,
                        required_review_id=required_review_id,
                        required_signature=required_signature(args),
                        profiles=profiles,
                        trigger_comment=trigger,
                    ),
                    indent=2,
                )
            )
            note(f"pull request is {pr['state']}; stopping")
            return 0

        if pr["headRefOid"] != baseline["head_sha"]:
            # Someone pushed. Any review still in flight describes dead code.
            snapshot = collect(repo, number, ignore)
            print(
                json.dumps(
                    build_state(
                        pr,
                        repo,
                        snapshot,
                        baseline=baseline,
                        waited=elapsed,
                        required_review_id=required_review_id,
                        required_signature=required_signature(args),
                        profiles=profiles,
                        trigger_comment=trigger,
                    ),
                    indent=2,
                )
            )
            note(
                f"head moved to {pr['headRefOid'][:10]} during the wait; "
                "the awaited review would describe the old commit"
            )
            return 0

        snapshot = collect(repo, number, ignore)
        fresh_reviews = [r for r in snapshot["reviews"] if r["id"] not in seen_reviews]
        fresh_threads = [
            t for t in snapshot["threads"] if t["thread_id"] not in seen_threads
        ]
        fresh_comments = [
            c for c in snapshot["comments"] if c["id"] not in seen_comments
        ]

        wake_reason: str | None = None
        if expect_sha:
            # The commissioned review ends the wait — and so does any response
            # from a recognized external reviewer, because several of them
            # answer a no-findings round outside the review channel entirely
            # (codex: an issue comment, or only a +1 on the trigger comment).
            # A passing human comment still does not end the wait.
            if any(r.get("commit_id") == expect_sha for r in fresh_reviews):
                wake_reason = "review-at-expected-commit"
            if wake_reason is None:
                for comment in fresh_comments:
                    if profile_for(comment.get("author"), profiles) is not None:
                        wake_reason = "external-reviewer-comment"
                        break
            if (
                wake_reason is None
                and trigger is not None
                and trigger.get("id") is not None
            ):
                current_reactions = {
                    (r.get("author"), r.get("content"))
                    for r in fetch_reactions(repo, trigger["id"])
                }
                for author, content in current_reactions - baseline_reactions:
                    if content in ("+1", "-1") and profile_for(author, profiles):
                        wake_reason = "external-reviewer-reaction"
                        break
            if wake_reason is None and (
                fresh_reviews or fresh_threads or fresh_comments
            ):
                note(
                    f"activity landed but no reviewer response for "
                    f"{expect_sha[:10]} yet ({len(fresh_reviews)} reviews, "
                    f"{len(fresh_threads)} threads, {len(fresh_comments)} "
                    f"comments); still waiting"
                )
        else:
            triggered_plain = bool(
                ("reviews" in wake_on and fresh_reviews)
                or ("threads" in wake_on and fresh_threads)
                or ("comments" in wake_on and fresh_comments)
            )
            if triggered_plain:
                wake_reason = "activity"
        if wake_reason is not None:
            state = build_state(
                pr,
                repo,
                snapshot,
                baseline=baseline,
                waited=elapsed,
                required_review_id=required_review_id,
                required_signature=required_signature(args),
                profiles=profiles,
                trigger_comment=trigger,
            )
            state["wake_reason"] = wake_reason
            print(json.dumps(state, indent=2))
            note(
                f"new review information after {elapsed:.0f}s "
                f"({wake_reason}): {len(fresh_reviews)} reviews, "
                f"{len(fresh_threads)} threads, {len(fresh_comments)} comments "
                f"-> {state['verdict']}"
            )
            return 0

        note(
            f"no new review information after {elapsed:.0f}s "
            f"(head {pr['headRefOid'][:10]}); polling again"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "target",
            nargs="?",
            help="PR number, URL, or branch; omit to use the current branch",
        )
        p.add_argument("--repo", help="owner/name; inferred from the checkout if unset")
        p.add_argument(
            "--ignore-author",
            action="append",
            default=[],
            metavar="LOGIN",
            help="drop activity from this login; repeatable",
        )
        p.add_argument(
            "--require-signature",
            metavar="TEXT",
            default=DEFAULT_SIGNATURE,
            help=f"text a review body must contain to count as clean "
            f"(default: {DEFAULT_SIGNATURE!r})",
        )
        p.add_argument(
            "--allow-unsigned",
            action="store_true",
            help="accept reviews without the signature; needed for external "
            "reviewers such as codex, which sign their own way",
        )
        p.add_argument(
            "--require-review",
            metavar="ID_OR_URL",
            help="refuse a clean verdict unless this review is present at the "
            "head; accepts the html_url that `pr_review.py post` prints",
        )
        p.add_argument(
            "--trigger-comment",
            metavar="ID_OR_URL",
            help="the '@<reviewer> review' comment whose emoji reactions count "
            "as reviewer responses; accepts the html_url `gh pr comment` "
            "prints; auto-detected from our newest trigger comment when unset",
        )
        p.add_argument(
            "--reviewer-bot",
            action="append",
            default=[],
            metavar="LOGIN_RE",
            help="recognize this login (regex) as an external reviewer for "
            "waking and unclear-grading; repeatable; never grades clean",
        )
        p.add_argument(
            "--attest-profile",
            action="append",
            default=[],
            metavar="LOGIN_RE:::SHA_RE:::CLEAN_RE",
            help="full external-reviewer profile whose matching no-findings "
            "comment (naming the head via SHA_RE group 1) may grade clean; "
            "repeatable",
        )

    s = sub.add_parser("state", help="print the current review state and exit")
    add_common(s)
    s.set_defaults(func=cmd_state)

    w = sub.add_parser("wait", help="block until new review information lands")
    add_common(w)
    w.add_argument(
        "--timeout", type=int, default=1800, help="seconds before giving up (1800)"
    )
    w.add_argument(
        "--interval", type=int, default=30, help="seconds between polls (30)"
    )
    w.add_argument(
        "--wake-on",
        default="reviews,threads",
        help="comma-separated triggers: reviews, threads, comments",
    )
    w.add_argument(
        "--expect-review-of",
        metavar="SHA",
        help="wake for a review of this commit ('head' for the current head), "
        "for any recognized external reviewer's comment, or for its emoji "
        "reaction on the trigger comment; other activity is logged but does "
        "not end the wait",
    )
    w.set_defaults(func=cmd_wait)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
