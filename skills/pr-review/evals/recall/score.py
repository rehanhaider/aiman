#!/usr/bin/env python3
"""Score a review's recall against defects known to be real.

Recall is the thing the prompt evals cannot see. They state the defect in the
prompt, so they measure labelling. This measures detection: run the skill on a
pull request in the corpus, then check how much of what is known to be there
came back.

Usage:
  python3 score.py --findings findings.json --repo OWNER/NAME --pr N [--sha SHA]
  python3 score.py --coverage          # what the corpus contains

Matching is deliberately generous — same file, and either a nearby line or
overlapping title wording. A generous matcher overstates recall, so a low score
is trustworthy and a high score still needs a human to confirm the matches are
really the same defect. Under-counting would be worse: it would send you
chasing findings the reviewer already made.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
STOPWORDS = {
    "the", "a", "an", "to", "for", "of", "in", "on", "and", "or", "not", "is",
    "it", "this", "that", "when", "with", "before", "after", "only", "its",
}
# Two distinct defects often sit within a few lines of each other, so proximity
# alone is weak evidence. Only a near-exact anchor matches on its own; anything
# further apart must also agree in wording.
LINE_SLACK = 0  # exact anchors only; see same_defect()
NEAR_SLACK = 40
MIN_WORD_OVERLAP = 3


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if w not in STOPWORDS and len(w) > 2}


def same_defect(known: dict, found: dict) -> tuple[bool, str]:
    if (known.get("path") or "") != (found.get("path") or ""):
        return False, ""
    k_line, f_line = known.get("line"), found.get("line")
    gap = (
        abs(int(k_line) - int(f_line))
        if k_line and f_line
        else None
    )
    # Only an exact anchor stands alone. Two unrelated defects a few lines apart
    # are common, so proximity without agreeing wording is not evidence.
    if gap == 0:
        return True, f"exact line {f_line}"

    overlap = words(known.get("title")) & words(
        f"{found.get('title', '')} {found.get('body', '')}"
    )
    if len(overlap) >= MIN_WORD_OVERLAP and (gap is None or gap <= NEAR_SLACK):
        near = f"line {f_line} vs {k_line}, " if gap is not None else ""
        return True, near + "wording: " + ", ".join(sorted(overlap)[:4])
    return False, ""


def load_corpus() -> dict:
    return json.loads((HERE / "ground-truth.json").read_text())


def cmd_coverage(corpus: dict) -> int:
    by_pr: dict[tuple, list] = {}
    for f in corpus["findings"]:
        by_pr.setdefault((f["repo"], f["pr"]), []).append(f)
    print(f"{corpus['count']} accepted findings across {len(by_pr)} pull requests\n")
    for (repo, pr), rows in sorted(by_pr.items()):
        sev = ", ".join(
            f"{n}× {s}"
            for s, n in sorted({r["severity"]: sum(1 for x in rows if x["severity"] == r["severity"]) for r in rows}.items())
        )
        print(f"  {repo}#{pr}: {len(rows)} findings ({sev})")
        for sha in sorted({r["sha"] for r in rows if r["sha"]}):
            n = sum(1 for r in rows if r["sha"] == sha)
            print(f"      {sha[:10]}  {n} finding(s)")
    return 0


def cmd_score(args: argparse.Namespace, corpus: dict) -> int:
    known = [
        f for f in corpus["findings"]
        if f["repo"] == args.repo and f["pr"] == args.pr
        and (not args.sha or f["sha"] == args.sha)
    ]
    if not known:
        print(f"no corpus entries for {args.repo}#{args.pr}"
              + (f" at {args.sha}" if args.sha else ""))
        return 1

    produced = json.loads(Path(args.findings).read_text())
    if isinstance(produced, dict):
        produced = produced.get("findings", [])

    hits, misses = [], []
    matched_produced: set[int] = set()
    for k in known:
        for i, p in enumerate(produced):
            ok, why = same_defect(k, p)
            if ok:
                hits.append((k, p, why))
                matched_produced.add(i)
                break
        else:
            misses.append(k)

    total = len(known)
    print(f"Recall on {args.repo}#{args.pr}"
          + (f" @ {args.sha[:10]}" if args.sha else " (all commits"
             f", {len({k['sha'] for k in known})} SHAs)"))
    print(f"  found {len(hits)}/{total} known defects\n")

    if misses:
        print("  MISSED:")
        for k in misses:
            print(f"    [{k['severity']}] {k['path']}:{k['line']} — {k['title']}")
            print(f"           found by {k['reviewer']} · {k['url']}")
    if hits:
        print("\n  FOUND (confirm these are really the same defect):")
        for k, _p, why in hits:
            print(f"    [{k['severity']}] {k['path']}:{k['line']} — {k['title']}")
            print(f"           matched on {why}")

    extra = [p for i, p in enumerate(produced) if i not in matched_produced]
    if extra:
        print(f"\n  NOT IN CORPUS ({len(extra)}) — new findings, or false positives; "
              "judge by hand:")
        for p in extra:
            print(f"    [{p.get('severity','?')}] {p.get('path')}:{p.get('line')}"
                  f" — {str(p.get('title',''))[:70]}")

    missed_severe = [k for k in misses if k["severity"] in ("P1", "P2")]
    if missed_severe:
        print(f"\n  {len(missed_severe)} missed finding(s) were P1/P2.")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--findings", help="findings.json the review produced")
    ap.add_argument("--repo", help="owner/name")
    ap.add_argument("--pr", type=int)
    ap.add_argument("--sha", help="score only findings from this reviewed commit")
    ap.add_argument("--coverage", action="store_true", help="describe the corpus and exit")
    args = ap.parse_args()

    corpus = load_corpus()
    if args.coverage:
        return cmd_coverage(corpus)
    if not (args.findings and args.repo and args.pr):
        ap.error("--findings, --repo and --pr are required unless --coverage")
    return cmd_score(args, corpus)


if __name__ == "__main__":
    raise SystemExit(main())
