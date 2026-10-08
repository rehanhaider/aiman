#!/usr/bin/env python3
"""Build replay bundles: one workdir per target commit, mirroring `pr_review.py gather`,
with everything after the review cutoff removed, plus a METHOD.md the reviewer follows.

The reviewer prompt is replay-wrapper.md + steps 2-7 of SKILL.md + severity.md, so the
replay always measures the skill text as it stands.

Usage:
  python3 build_bundles.py [--root /tmp/pr-review-replay]

Needs: gh (authenticated, read-only), and a local clone of each target repo (CLONES).
Creates detached worktrees in those clones; remove them afterwards with
`git worktree remove --force <workdir>/head`.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
CLONES = {
    "rehanhaider/naqid": Path.home() / "Projects/naqid",
    "Mizanic/Qaleening": Path.home() / "Projects/Qaleening",
}
# role=target: Codex posted findings at this SHA and the skill posted "no new issues found".
# role=holdout: the skill posted accepted findings at this SHA; checks that strengths stay.
TARGETS = [
    dict(name="naqid-137", repo="rehanhaider/naqid", pr=137, sha="5ce3656760ed92d7734f127a9707111d04f2c706",
         base="de09cc5b3c", cutoff="2026-08-10T16:50:20Z", role="target"),
    dict(name="naqid-144", repo="rehanhaider/naqid", pr=144, sha="20b4eed550a23d3296a3e962f4d21cde5dbf9719",
         base="4e63b92a2b", cutoff="2026-08-11T22:25:21Z", role="target"),
    dict(name="naqid-146", repo="rehanhaider/naqid", pr=146, sha="e50604afa8b96c85044813fb5e2a7a4329332e8d",
         base="fd7f05633b", cutoff="2026-08-12T19:31:04Z", role="target"),
    dict(name="qaleening-53", repo="Mizanic/Qaleening", pr=53, sha="e58238fb9dd8479307e4b033b3888d48505c6896",
         base="c791fb0450", cutoff="2026-07-26T19:42:23Z", role="target"),
    dict(name="naqid-181", repo="rehanhaider/naqid", pr=181, sha="11f2849f5d6cb945aea6f2ffa2155631e8add1c0",
         base="a2003bed37", cutoff="2026-09-06T17:28:46Z", role="holdout"),
    dict(name="qaleening-60", repo="Mizanic/Qaleening", pr=60, sha="954da55d6b4a565047b42c22cf7ff1015fb6d8e2",
         base="28a98d9089", cutoff="2026-07-28T14:25:47Z", role="holdout"),
]

Q = """
query($owner:String!,$name:String!,$number:Int!){
  repository(owner:$owner,name:$name){
    pullRequest(number:$number){
      title url baseRefName body createdAt
      userContentEdits(last:20){ nodes{ editedAt diff } }
      closingIssuesReferences(first:3){ nodes{ number title body userContentEdits(last:20){ nodes{ editedAt diff } } } }
      reviewThreads(first:100){ nodes{ path line isResolved isOutdated
        comments(first:10){ totalCount nodes{ author{login} createdAt body } } } }
    }
  }
}"""


def sh(args, cwd=None):
    p = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if p.returncode != 0:
        sys.exit(f"FAILED {' '.join(map(str, args))}\n{p.stderr}")
    return p.stdout


def version_at(edits, current, cutoff):
    """Body text as it stood at the cutoff: the latest edit at or before it that carries text."""
    cands = [e for e in edits if e.get("editedAt") and e["editedAt"] <= cutoff and e.get("diff")]
    if cands:
        best = max(cands, key=lambda e: e["editedAt"])
        return best["diff"], best["editedAt"]
    return current, "current (no pre-cutoff edit version available)"


def method_text(workdir: Path) -> str:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    steps = skill[skill.index("## 2. Establish the contract"):skill.index("## 8. Dry-run, then post")]
    severity = (SKILL / "references" / "severity.md").read_text(encoding="utf-8")
    wrapper = (Path(__file__).parent / "replay-wrapper.md").read_text(encoding="utf-8")
    return (wrapper + steps.rstrip() + "\n\n---\n\n" + severity).replace("{WORKDIR}", str(workdir))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("/tmp/pr-review-replay"))
    args = ap.parse_args()
    summary = []
    for t in TARGETS:
        clone = CLONES[t["repo"]]
        wd = args.root / t["name"]
        wd.mkdir(parents=True, exist_ok=True)
        owner, name = t["repo"].split("/")
        data = json.loads(sh(["gh", "api", "graphql", "-F", f"owner={owner}", "-F", f"name={name}",
                              "-F", f"number={t['pr']}", "-f", f"query={Q}"]))
        pr = data["data"]["repository"]["pullRequest"]
        body, body_ver = version_at(pr["userContentEdits"]["nodes"], pr["body"] or "", t["cutoff"])
        (wd / "pr_body.md").write_text(f"# {pr['title']}\n\n{body}\n", encoding="utf-8")
        issues = []
        for iss in pr["closingIssuesReferences"]["nodes"]:
            ib, _ = version_at(iss["userContentEdits"]["nodes"], iss["body"] or "", t["cutoff"])
            issues.append(f"# Issue #{iss['number']}: {iss['title']}\n\n{ib}\n")
        if issues:
            (wd / "issue.md").write_text("\n\n---\n\n".join(issues), encoding="utf-8")
        threads = []
        for n in pr["reviewThreads"]["nodes"]:
            cs = [c for c in n["comments"]["nodes"] if c["createdAt"] < t["cutoff"]]
            if not cs:
                continue
            threads.append({"path": n["path"], "line": n["line"], "is_resolved": n["isResolved"],
                            "is_outdated": n["isOutdated"], "author": (cs[0].get("author") or {}).get("login"),
                            "excerpt": (cs[0]["body"] or "")[:300], "comment_count": len(cs)})
        (wd / "threads.json").write_text(json.dumps(threads, indent=2), encoding="utf-8")
        sh(["git", "fetch", "--quiet", "origin", f"pull/{t['pr']}/head"], cwd=clone)
        full_base = sh(["git", "rev-parse", t["base"]], cwd=clone).strip()
        mb = sh(["git", "merge-base", t["base"], t["sha"]], cwd=clone).strip()
        assert mb == full_base, f"{t['name']}: merge-base {mb[:10]} != base {full_base[:10]}"
        diff = sh(["git", "diff", f"{t['base']}..{t['sha']}"], cwd=clone)
        (wd / "diff.patch").write_text(diff, encoding="utf-8")
        head = wd / "head"
        if not head.exists():
            sh(["git", "worktree", "add", "--detach", str(head), t["sha"]], cwd=clone)
        state = {"repo": t["repo"], "pr": t["pr"], "head_sha": t["sha"], "base": pr["baseRefName"],
                 "base_sha": full_base, "url": pr["url"], "workdir": str(wd), "worktree": str(head),
                 "replay_cutoff": t["cutoff"], "role": t["role"], "pr_body_version": body_ver}
        (wd / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        (wd / "METHOD.md").write_text(method_text(wd), encoding="utf-8")
        summary.append({"name": t["name"], "diff_lines": diff.count("\n"), "threads_before_cutoff": len(threads),
                        "body_version": body_ver})
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
