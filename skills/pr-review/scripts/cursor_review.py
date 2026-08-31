#!/usr/bin/env python3
"""Run a pull-request review through the `cursor-agent` CLI.

Drives cursor-agent over the context `pr_review.py gather` staged, then writes
`findings.json` and `suspicions.json` in the schema `pr_review.py post` expects.
This script never posts: the caller posts, so the review carries the same
signature and URL-verification path as an in-context review.

The agent runs read-only (`--mode ask`), so it can read the repository and run
`git`/`rg` but cannot edit, commit, or touch GitHub.

Exit codes: 0 review produced, 1 error, 3 the agent could not complete a review.

The distinction between 1/3 and an empty findings array matters more here than
anywhere else in this skill: an empty array means "reviewed, nothing to
publish", and any failure that silently produced one would read downstream as an
all-clear.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Opus 4.6 at maximum reasoning effort with Max Mode off. Cursor has no
# `max_mode` parameter — the mode is expressed through `context`, where 200k is
# the non-Max window and 1m is Max Mode. `--list-models` does not show this base
# id; it lists only the pre-baked `claude-4.6-opus-*` variants, which are all 1m.
DEFAULT_MODEL = "claude-opus-4-6[thinking=true,context=200k,effort=max]"

# Must contain pr_review.py's SIGNATURE, because pr_watch.py requires that exact
# substring before it will call a review clean. The suffix records which agent
# and model actually did the reading.
SIGNATURE = "rehanhaider/pr-review-skill"
SIGNED_BY = f"{SIGNATURE} · cursor-agent claude-opus-4-6"

SEVERITIES = ("P1", "P2", "P3", "P4")
SIDES = ("RIGHT", "LEFT")


def die(msg: str, code: int = 1) -> None:
    print(f"cursor_review: {msg}", file=sys.stderr)
    raise SystemExit(code)


def note(msg: str) -> None:
    print(f"cursor_review: {msg}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------- prompt


OUTPUT_CONTRACT = """
## Output contract for this run

This replaces step 7's `findings.json`. You have no write access, so report by
printing instead.

Your entire final message must be exactly one fenced ```json block and nothing
else — no preamble before it, no commentary after it. The block holds one
object:

```json
{
  "findings": [
    {"path": "src/session.ts", "line": 84, "side": "RIGHT", "severity": "P1",
     "title": "Keep tenant scope on the fallback query",
     "body": "2-4 sentences: trigger, incorrect outcome, fix boundary."}
  ],
  "suspicions": [
    {"path": "src/auth.ts", "line": 42,
     "consequence": "What it would cost if real.",
     "check": "The single check that would settle it."}
  ]
}
```

- `side` is "RIGHT" or "LEFT", uppercase. `severity` is one of P1, P2, P3, P4.
- Both arrays may be empty. An empty `findings` array is a positive claim: you
  completed the review and found nothing that clears step 4's bar. Never use it
  to mean you ran out of room or could not finish.
- If you cannot complete the review, return `{"error": "<what stopped you>"}`
  instead. A partial review reported as empty would be read downstream as an
  all-clear and merged.
"""


def build_prompt(state: dict, workdir: Path, method: str, worktree: str | None) -> str:
    repo, pr, head = state.get("repo"), state.get("pr"), state.get("head_sha", "")
    if worktree:
        source = f"    head/        — read-only worktree of the reviewed commit at {worktree}"
    else:
        source = (
            "    head/        — absent. Read files at the reviewed commit with:\n"
            f"                   gh api \"repos/{repo}/contents/<path>?ref={head}\" "
            "--jq .content | base64 -d"
        )
    return f"""You are reviewing GitHub pull request {repo}#{pr} at commit {head}.

Follow the review method reproduced below. It is the full text of the pr-review
skill, and it is the method for this review — not a summary to skim.

<review-method>
{method}
</review-method>

## How this run differs from that method

- **You are the reviewer.** The method's `--reviewer` argument has already been
  resolved — you are what `cursor` resolves to. Ignore that section, and do not
  delegate the reading to another agent.
- Steps 1 and 8 are already done for you. Do not run `pr_review.py`. Do not post
  anything to GitHub, and do not use `gh` for any write operation.
- The review context is staged at {workdir}:
    diff.patch   — the full PR diff against its base. This is the review scope.
    pr_body.md   — the PR description.
    threads.json — existing review threads with their resolution state.
{source}
- Everything you do is read-only. Do not edit files, commit, push, reply to
  threads, or resolve threads. Reading the repository and running `git log`,
  `git blame`, and `rg` is expected and encouraged.
- Step 9's chat report does not apply. The output contract below is the whole
  deliverable.
{OUTPUT_CONTRACT}"""


# ---------------------------------------------------------------- invocation


def run_agent(prompt: str, model: str, workspace: str, extra_dirs: list[str],
              timeout: int) -> str:
    """Return cursor-agent's final message, or die."""
    if not shutil.which("cursor-agent"):
        die("cursor-agent is not on PATH; install it or use --reviewer local")
    argv = [
        "cursor-agent",
        "--model", model,
        # Read-only: the agent may read and run shell, but cannot edit the branch
        # it is reviewing.
        "--mode", "ask",
        # Without this, a non-interactive run in an untrusted directory exits
        # asking to be run interactively instead of reviewing anything.
        "--trust",
        "--print",
        "--output-format", "json",
        "--workspace", workspace,
    ]
    for d in extra_dirs:
        argv += ["--add-dir", d]
    note(f"running cursor-agent ({model}) over {workspace}")
    try:
        proc = subprocess.run(
            argv, input=prompt, capture_output=True, text=True,
            encoding="utf-8", timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        die(f"cursor-agent did not finish within {timeout}s")
        raise  # unreachable
    if proc.returncode != 0:
        die(f"cursor-agent exited {proc.returncode}: "
            f"{(proc.stderr or proc.stdout).strip()[:500]}")
    return agent_result(proc.stdout)


def agent_result(stdout: str) -> str:
    """Pull the final message out of `--output-format json` output."""
    text = stdout.strip()
    if not text:
        die("cursor-agent produced no output")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        # An authentication or model-string failure prints a bare line instead
        # of the result envelope; surface it rather than parsing it as a review.
        die(f"cursor-agent did not return a JSON envelope: {text[:500]}")
        raise  # unreachable
    if not isinstance(payload, dict):
        die("cursor-agent returned an unexpected envelope")
    if payload.get("is_error"):
        die(f"cursor-agent reported an error: {str(payload.get('result'))[:500]}")
    result = payload.get("result")
    if not isinstance(result, str) or not result.strip():
        die("cursor-agent returned an empty result")
        raise  # unreachable
    return result


# ---------------------------------------------------------------- parsing


FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def extract_object(text: str) -> dict:
    """Find the review object in the agent's final message.

    Tries fenced blocks last-first: when a model restates the schema before
    answering, the real payload is the later block.
    """
    candidates = [m.group(1) for m in FENCE_RE.finditer(text)]
    candidates.reverse()
    candidates.append(text)
    for blob in candidates:
        try:
            value = json.loads(blob.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and (
            "findings" in value or "suspicions" in value or "error" in value
        ):
            return value
    die(f"could not find a review object in the agent's reply: {text[:500]}")
    raise  # unreachable


def coerce_line(value: object) -> int | None:
    """An anchor line as an int, or None when it is not one.

    Booleans are rejected outright: `True` is an `int` in Python and would sail
    through as line 1.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return None


def normalise(obj: dict) -> tuple[list[dict], list[dict]]:
    """Coerce the agent's object into the schema `pr_review.py post` validates.

    Only case and shape are repaired here. Anything missing stays missing so
    that `post` reports it, rather than being papered over into a valid-looking
    comment anchored at the wrong place.
    """
    if isinstance(obj.get("error"), str) and obj["error"].strip():
        die(f"the agent could not complete the review: {obj['error'].strip()}", 3)

    findings = obj.get("findings") or []
    suspicions = obj.get("suspicions") or []
    if not isinstance(findings, list) or not isinstance(suspicions, list):
        die("'findings' and 'suspicions' must both be arrays")

    problems: list[str] = []
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            problems.append(f"finding {i}: must be an object")
            continue
        sev = str(f.get("severity", "")).strip().upper()
        if sev not in SEVERITIES:
            problems.append(f"finding {i}: severity {f.get('severity')!r} "
                            f"is not one of {', '.join(SEVERITIES)}")
        else:
            f["severity"] = sev
        if "side" in f:
            side = str(f["side"]).strip().upper()
            if side not in SIDES:
                problems.append(f"finding {i}: side {f['side']!r} is not RIGHT or LEFT")
            else:
                # pr_review.py looks anchors up by exact case; a lowercase
                # "right" matches no hunk and fails the whole atomic POST.
                f["side"] = side
        if "line" in f:
            line = coerce_line(f["line"])
            if line is None:
                problems.append(f"finding {i}: line {f['line']!r} is not an integer")
            else:
                f["line"] = line
    for i, s in enumerate(suspicions):
        if not isinstance(s, dict):
            problems.append(f"suspicion {i}: must be an object")
            continue
        if s.get("line") is None:
            # `post` treats a missing line as a file-level anchor; an explicit
            # null would fail its integer check instead.
            s.pop("line", None)
        else:
            line = coerce_line(s["line"])
            if line is None:
                problems.append(f"suspicion {i}: line {s['line']!r} is not an integer")
            else:
                s["line"] = line
    if problems:
        die("the agent's review does not fit the schema:\n  " + "\n  ".join(problems))
    return findings, suspicions


# ---------------------------------------------------------------- main


def load_state(workdir: Path) -> dict:
    state_file = workdir / "state.json"
    if not state_file.is_file():
        die(f"no state.json in {workdir} — run `pr_review.py gather` first")
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        die(f"could not read {state_file}: {exc}")
        raise  # unreachable


def resolve_method_file(explicit: str | None) -> Path:
    """The review method to hand the agent: this skill's own SKILL.md."""
    path = Path(explicit) if explicit else Path(__file__).resolve().parent.parent / "SKILL.md"
    if not path.is_file():
        die(f"could not read the review method at {path}; pass --method-file")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", required=True,
                        help="workdir created by `pr_review.py gather`")
    parser.add_argument("--method-file",
                        help="pr-review SKILL.md (default: the sibling pr-review skill)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"cursor model string (default: {DEFAULT_MODEL!r})")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="seconds to allow the agent (1800)")
    parser.add_argument("--print-prompt", action="store_true",
                        help="print the prompt and exit without calling the agent")
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    state = load_state(workdir)
    method = resolve_method_file(args.method_file).read_text(encoding="utf-8")

    worktree = state.get("worktree")
    workspace = worktree or state.get("repo_root") or str(Path.cwd())
    prompt = build_prompt(state, workdir, method, worktree)

    if args.print_prompt:
        print(prompt)
        return 0

    # gather stages into a temp dir, so the agent needs it granted explicitly
    # unless it happens to sit inside the workspace already.
    extra_dirs = [] if workdir.is_relative_to(Path(workspace).resolve()) else [str(workdir)]
    reply = run_agent(prompt, args.model, workspace, extra_dirs, args.timeout)
    findings, suspicions = normalise(extract_object(reply))

    findings_file = workdir / "findings.json"
    suspicions_file = workdir / "suspicions.json"
    findings_file.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    suspicions_file.write_text(json.dumps(suspicions, indent=2), encoding="utf-8")

    note(f"{len(findings)} findings, {len(suspicions)} suspicions")
    print(json.dumps({
        "repo": state.get("repo"),
        "pr": state.get("pr"),
        "head_sha": state.get("head_sha"),
        "model": args.model,
        "findings_file": str(findings_file),
        "suspicions_file": str(suspicions_file),
        "findings_count": len(findings),
        "suspicions_count": len(suspicions),
        "signed_by": SIGNED_BY,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
