#!/usr/bin/env python3
"""Run a pull-request review through the `opencode` CLI.

The OpenCode counterpart of `cursor_review.py`: it hands the context
`pr_review.py gather` staged to `opencode run`, then writes `findings.json` and
`suspicions.json` in the schema `pr_review.py post` expects. It never posts. The
printed `signed_by` is the harness/model label to pass to `pr_review.py post`.

OpenCode has no read-only switch that still allows a shell, so this script
supplies its own permission config: no edits, no web, no paths outside the
workspace and workdir, and only the shell commands a review reads with. Any
other command is denied, never asked, so a non-interactive run cannot hang on
an approval prompt.

Exit codes: 0 review produced, 1 error, 3 the agent could not complete a review.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from cursor_review import (
    build_prompt,
    die,
    extract_object,
    load_state,
    normalise,
    note,
    pretty_model,
    resolve_method_file,
)

# Muse Spark 1.3 on OpenCode Zen, free tier. An explicit --model overrides it.
DEFAULT_MODEL = "opencode/muse-spark-1.3-contributor-free"

HARNESS = "OpenCode"

# OpenCode evaluates rules in order and the last match wins, so the denials
# after the allowances carve the write forms back out of them.
READ_ONLY_BASH = {
    "*": "deny",
    "git log*": "allow",
    "git show*": "allow",
    "git blame*": "allow",
    "git diff*": "allow",
    "git status*": "allow",
    "git ls-files*": "allow",
    "git rev-parse*": "allow",
    "rg *": "allow",
    "grep *": "allow",
    "ls*": "allow",
    "cat *": "allow",
    "head *": "allow",
    "tail *": "allow",
    "wc *": "allow",
    "base64 -d*": "allow",
    "echo *": "allow",
    "gh api repos/*": "allow",
    'gh api "repos/*': "allow",
    "gh api 'repos/*": "allow",
    # Redirection and --output write files; rg --pre runs a program.
    "*>*": "deny",
    "*--output*": "deny",
    "rg *--pre*": "deny",
    # Any of these turns a gh api read into a write.
    "gh api * -X*": "deny",
    "gh api * --method*": "deny",
    "gh api * -f *": "deny",
    "gh api * -F *": "deny",
    "gh api * --field*": "deny",
    "gh api * --raw-field*": "deny",
    "gh api * --input*": "deny",
}


# Appended to the shared prompt. A denied read must not end in an empty review:
# a model that cannot see the code and reports nothing has produced a false clean.
SHELL_NOTE = """
## Shell in this run

The shell is restricted to read-only commands: `git log`, `git show`,
`git blame`, `git diff`, `git status`, `git ls-files`, `git rev-parse`, `rg`,
`grep`, `ls`, `cat`, `head`, `tail`, `wc`, `echo`, `base64 -d`, and
`gh api repos/...` reads. Pipes between them work. Anything else is denied, as are `;`, `&&`,
redirection, and any `gh api` write flag. Run one command per call.

If a denial leaves you unable to read code the review needs, retry with an
allowed form or with your read tool. If you still cannot read it, return
`{"error": "<what you could not read>"}`. Never return an empty review for code
you did not read.
"""


def permission_config(workdir: Path) -> dict:
    """The OpenCode config that makes the run read-only."""
    return {
        "permission": {
            "edit": "deny",
            "webfetch": "deny",
            "websearch": "deny",
            "external_directory": {"*": "deny", f"{workdir}/*": "allow"},
            "bash": READ_ONLY_BASH,
        }
    }


def reviewer_label(model: str) -> str:
    """What to pass as `--signed-by`: `OpenCode/Muse-Spark-1.3-Contributor`.

    The provider prefix and the `-free` tier suffix say where and how the model
    ran, not which model read the diff.
    """
    name = model.strip().split("/", 1)[-1]
    if name.endswith("-free"):
        name = name[: -len("-free")]
    return f"{HARNESS}/{pretty_model(name)}"


# ---------------------------------------------------------------- invocation


def run_agent(prompt: str, model: str, workspace: str, workdir: Path,
              timeout: int) -> str:
    """Return opencode's final message, or die."""
    if not shutil.which("opencode"):
        die("opencode is not on PATH; install it or use --reviewer local")
    argv = [
        "opencode", "run",
        # A private server, so the permission config below is the one in force
        # rather than whatever the background service loaded.
        "--standalone",
        "--model", model,
        "--format", "json",
    ]
    env = {**os.environ, "OPENCODE_CONFIG_CONTENT": json.dumps(permission_config(workdir))}
    note(f"running opencode ({model}) over {workspace}")
    try:
        proc = subprocess.run(
            argv, input=prompt, capture_output=True, text=True,
            encoding="utf-8", timeout=timeout, cwd=workspace, env=env,
        )
    except subprocess.TimeoutExpired:
        die(f"opencode did not finish within {timeout}s")
        raise  # unreachable
    if proc.returncode != 0:
        detail = event_error(proc.stdout) or (proc.stderr or proc.stdout).strip()
        die(f"opencode exited {proc.returncode}: {detail[:500]}")
    return agent_result(proc.stdout)


def events(stdout: str) -> list[dict]:
    """The JSON events `--format json` prints, one per line."""
    out = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            # Same rule as cursor: a bare line is a failure, never a review.
            die(f"opencode printed a line that is not a JSON event: {line[:500]}")
            raise  # unreachable
        if isinstance(event, dict):
            out.append(event)
    return out


def event_error(stdout: str) -> str | None:
    """The message of the first error event, if the stream has one."""
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("type") == "error":
            err = event.get("error")
            return str(err.get("message") if isinstance(err, dict) else err)
    return None


def agent_result(stdout: str) -> str:
    """The text of the last assistant message in the event stream.

    Earlier messages are narration between tool calls; only the final one
    carries the review object.
    """
    if not stdout.strip():
        die("opencode produced no output")
    stream = events(stdout)
    for event in stream:
        if event.get("type") == "error":
            err = event.get("error")
            msg = err.get("message") if isinstance(err, dict) else err
            die(f"opencode reported an error: {str(msg)[:500]}")
    texts: dict[str, list[str]] = {}
    last_message = None
    for event in stream:
        part = event.get("part")
        if event.get("type") != "text" or not isinstance(part, dict):
            continue
        message = part.get("messageID")
        texts.setdefault(message, []).append(str(part.get("text") or ""))
        last_message = message
    result = "".join(texts.get(last_message, [])) if last_message is not None else ""
    if not result.strip():
        die("opencode returned no final message")
    return result


# ---------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", required=True,
                        help="workdir created by `pr_review.py gather`")
    parser.add_argument("--method-file",
                        help="pr-review SKILL.md (default: the sibling pr-review skill)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"opencode provider/model (default: {DEFAULT_MODEL!r})")
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
    prompt = build_prompt(state, workdir, method, worktree, reviewer="opencode") + SHELL_NOTE

    if args.print_prompt:
        print(prompt)
        return 0

    reply = run_agent(prompt, args.model, workspace, workdir, args.timeout)
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
        "signed_by": reviewer_label(args.model),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
