#!/usr/bin/env python3
"""Rebuild the recall corpus from real pull requests.

Every finding here was posted to a real PR and accepted by the repository owner,
so it is a defect a competent review should have found. The corpus exists to
measure recall — whether the skill finds defects nobody pointed out to it —
which the prompt-and-expected-output evals structurally cannot do.

Usage:  python3 build_ground_truth.py > ground-truth.json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

# PRs reviewed independently by both the pr-review skill and the Codex bot.
# Add rows as more dual-reviewed PRs accumulate; more sources make the corpus
# less likely to encode one reviewer's blind spots.
SOURCES = [
    ("Magnolia-Impact/navinier-app", 39),
    ("Mizanic/Qaleening", 50),
    ("rehanhaider/naqid", 31),
]

BADGE_RE = re.compile(r"badge/(P[0-9])-")
TITLE_RE = re.compile(r"</sub></sub>\s+(.+?)\*\*", re.S)


def gh(args: list[str]) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"gh {' '.join(args)} failed: {proc.stderr.strip()}", file=sys.stderr)
        return ""
    return proc.stdout


def main() -> int:
    findings = []
    for repo, number in SOURCES:
        out = gh(
            [
                "api",
                f"repos/{repo}/pulls/{number}/comments",
                "--paginate",
                "--jq",
                # Top-level comments only: replies are the rectification loop
                # answering a finding, not a finding.
                ".[] | select(.in_reply_to_id == null) | "
                "{path, line, original_line, sha: .original_commit_id, "
                "author: .user.login, body, url: .html_url}",
            ]
        )
        for raw in out.splitlines():
            raw = raw.strip()
            if not raw:
                continue
            row = json.loads(raw)
            badge = BADGE_RE.search(row.get("body") or "")
            if not badge:
                continue  # unbadged prose, not a filed finding
            title = TITLE_RE.search(row["body"])
            findings.append(
                {
                    "repo": repo,
                    "pr": number,
                    "sha": row.get("sha"),
                    "path": row.get("path"),
                    "line": row.get("line") or row.get("original_line"),
                    "severity": badge.group(1),
                    "reviewer": "codex"
                    if "codex" in (row.get("author") or "")
                    else "pr-review",
                    "title": (title.group(1).strip() if title else "")[:120],
                    "url": row.get("url"),
                }
            )

    findings.sort(key=lambda f: (f["repo"], f["pr"], f["path"] or "", f["line"] or 0))
    json.dump(
        {
            "note": "Findings posted to real PRs and accepted by the owner. "
            "Recall corpus for the pr-review skill; see README.md.",
            "sources": [{"repo": r, "pr": n} for r, n in SOURCES],
            "count": len(findings),
            "findings": findings,
        },
        sys.stdout,
        indent=1,
    )
    print()
    print(f"{len(findings)} findings from {len(SOURCES)} PRs", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
