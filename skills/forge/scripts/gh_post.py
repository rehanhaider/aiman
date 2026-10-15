#!/usr/bin/env python3
"""forge's `gh` fallback for posting a review as the user.

forge posts reviews through mizcode-reviewer's `review.js post`, as the
`mizcode-reviewer[bot]` GitHub App. When the App is not configured or not
installed on the repository, forge posts the same findings with this script
instead, over the workdir `review.js gather` made.

It renders findings.json into Codex-style inline comments plus a summary body,
then posts the review. The reviews endpoint is atomic: one comment anchored to
a line outside the PR diff fails the whole POST with a 422, so every anchor is
validated against the live diff first and misses are reported with the nearest
commentable line.

Requires only the Python stdlib and an authenticated `gh` CLI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

SEVERITIES = ("P0", "P1", "P2", "P3")
BADGE_COLORS = {"P0": "red", "P1": "orange", "P2": "yellow", "P3": "lightgrey"}


def run(cmd: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, input=input_text, text=True, capture_output=True)


def run_gh(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return run(["gh", *args], input_text=input_text)


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


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
    """Default posting policy: P0, P1 and P2 reach the pull request; P3 is
    recorded only. Returns (posted, dropped); --include-low bypasses this."""
    posted = [f for f in findings if f["severity"] in ("P0", "P1", "P2")]
    low = [f for f in findings if f["severity"] == "P3"]
    return posted, low


def split_findings(findings: list[dict], max_inline: int) -> tuple[list[dict], list[dict]]:
    """Keep every P0-P2 finding inline; apply the cap only to P3."""
    ordered = sorted(findings, key=lambda f: SEVERITIES.index(f["severity"]))
    blocking = [f for f in ordered if f["severity"] in ("P0", "P1", "P2")]
    lower = [f for f in ordered if f["severity"] == "P3"]
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


# Stable identifier proving a review was posted by tooling rather than typed by
# hand. Rendered as an HTML comment: invisible on GitHub, returned verbatim by
# the API. pr_watch.py requires this exact string by default, and
# mizcode-reviewer's `review.js post` writes the same one; changing it here
# without changing it there breaks the clean verdict.
SIGNATURE = "rehanhaider/pr-review-skill"


def reviewer_note(reviewer: str) -> list[str]:
    """The visible attribution: a GitHub alert naming who read the diff, as
    harness/model — `Claude/Opus-5`, `Cursor/Grok-4.7`."""
    return ["> [!NOTE]", f"> 🤖 Reviewed by {reviewer.strip()}", ""]


def render_summary(
    head_sha: str,
    findings: list[dict],
    folded: list[dict],
    reviewer: str | None = None,
    suspicions: list[dict] | None = None,
    signature: str | None = SIGNATURE,
) -> str:
    lines: list[str] = []
    if reviewer and reviewer.strip():
        # Attribution leads, as an alert block. pr_watch.py skips a leading
        # alert before reading the verdict line, so the verdict still governs.
        lines += reviewer_note(reviewer)
    counts = Counter(f["severity"] for f in findings)
    parts = [f"{counts[s]} {s}" for s in SEVERITIES if counts[s]]
    if findings:
        noun = "finding" if len(findings) == 1 else "findings"
        lines.append(
            f"Reviewed `{head_sha[:10]}` — {len(findings)} {noun} ({', '.join(parts)})."
        )
    elif suspicions:
        # Never the all-clear sentence while a severe candidate is unresolved:
        # automation reads that phrase as ready-to-merge.
        n = len(suspicions)
        lines.append(f"Reviewed `{head_sha[:10]}` — no findings, "
                     f"{n} unverified.")
    else:
        # Exact wording: automation treats this phrase as the all-clear signal.
        lines.append(f"Reviewed `{head_sha[:10]}` — no new issues found.")
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
        # Last and invisible: a reader never sees it, and a person typing a
        # review by hand does not know to add it.
        lines += ["", f"<!-- {signature} -->"]
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
        die("needs --workdir (from review.js gather) or all of --repo, --pr, --commit")

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
            print(f"note: {len(low)} P3 finding(s) suppressed — only P0-P2 "
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

    if not args.signed_by.strip() or "\n" in args.signed_by:
        die("--signed-by needs a one-line harness/model label, e.g. 'Claude/Opus-5'")
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


# ---------------------------------------------------------------- entry point


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--workdir", help="workdir from `review.js gather` (supplies --repo/--pr/--commit)")
    p.add_argument("--repo", help="owner/name (overrides workdir state)")
    p.add_argument("--pr", type=int, help="PR number (overrides workdir state)")
    p.add_argument("--commit", help="reviewed commit SHA (overrides workdir state)")
    p.add_argument("--findings-file", type=Path, required=True)
    p.add_argument("--suspicions-file", type=Path,
                   help="JSON array of {path, line?, consequence, check} for severe "
                        "candidates that could not be proved; rendered into the summary")
    p.add_argument("--event", default="COMMENT", choices=["COMMENT", "REQUEST_CHANGES", "APPROVE"])
    p.add_argument("--include-low", action="store_true",
                   help="also post P3 findings; by default only P0-P2 reach "
                        "the pull request and P3 is dropped")
    p.add_argument("--max-inline", type=int, default=10,
                   help="P3 inline cap when --include-low is set; P0-P2 always stay inline")
    p.add_argument("--no-validate", action="store_true", help="skip diff-anchor validation")
    p.add_argument("--dry-run", action="store_true", help="validate and print the payload without posting")
    p.add_argument("--allow-moved-head", action="store_true",
                   help="post even though the PR head moved since the review (exit 3 otherwise)")
    p.add_argument("--signed-by", required=True, metavar="HARNESS/MODEL",
                   help="who read the diff, as harness/model, e.g. 'Claude/Opus-5' or "
                        "'Cursor/Grok-4.7'; rendered as a note at the top of the review. "
                        f"The machine signature {SIGNATURE!r} is always added as a "
                        "hidden HTML comment, whatever this says")

    args = p.parse_args()
    return cmd_post(args)


if __name__ == "__main__":
    raise SystemExit(main())
