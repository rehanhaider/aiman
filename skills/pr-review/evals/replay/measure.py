#!/usr/bin/env python3
"""Token and cost measurement for replay reviewers run as Claude Code subagents.

Usage:
  python3 measure.py --subagents-dir ~/.claude/projects/<project>/<session>/subagents --since <epoch>

Sums the usage fields of every agent transcript modified after --since, prices them at
Opus rates, and tags each by the replay workdir named in its prompt.
"""
import argparse
import glob
import json
import os
import re

PRICE = {"input": 15.0, "cache_write": 18.75, "cache_read": 1.5, "output": 75.0}  # USD per million tokens


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subagents-dir", required=True)
    ap.add_argument("--since", type=float, required=True, help="unix epoch; transcripts modified before it are ignored")
    args = ap.parse_args()
    rows = []
    for meta in glob.glob(os.path.join(os.path.expanduser(args.subagents_dir), "agent-*.meta.json")):
        if os.path.getmtime(meta) < args.since:
            continue
        jl = meta.replace(".meta.json", ".jsonl")
        if not os.path.exists(jl):
            continue
        turns = tool_calls = max_prefix = 0
        u = dict(input_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0, output_tokens=0)
        target = None
        for line in open(jl):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            msg = o.get("message") or {}
            if o.get("type") == "user" and target is None:
                c = msg.get("content")
                txt = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                mm = re.search(r"replay/([\w-]+)", txt or "")
                if mm:
                    target = mm.group(1)
            if o.get("type") == "assistant" and isinstance(msg, dict) and msg.get("usage"):
                turns += 1
                us = msg["usage"]
                for k in u:
                    u[k] += us.get(k, 0)
                max_prefix = max(max_prefix, sum(us.get(k, 0) for k in
                                                 ("cache_read_input_tokens", "cache_creation_input_tokens", "input_tokens")))
                tool_calls += sum(1 for b in msg.get("content") or [] if isinstance(b, dict) and b.get("type") == "tool_use")
        cost = (u["input_tokens"] * PRICE["input"] + u["cache_creation_input_tokens"] * PRICE["cache_write"]
                + u["cache_read_input_tokens"] * PRICE["cache_read"] + u["output_tokens"] * PRICE["output"]) / 1e6
        rows.append(dict(target=target, turns=turns, tool_calls=tool_calls, max_prefix_tokens=max_prefix,
                         cost_usd=round(cost, 2), **u))
    rows.sort(key=lambda r: r["target"] or "")
    print(f"{'target':16} {'turns':>5} {'calls':>5} {'prefix':>8} {'cache_w':>9} {'cache_r':>11} {'out':>7} {'usd':>7}")
    for r in rows:
        print(f"{str(r['target']):16} {r['turns']:>5} {r['tool_calls']:>5} {r['max_prefix_tokens']:>8} "
              f"{r['cache_creation_input_tokens']:>9} {r['cache_read_input_tokens']:>11} {r['output_tokens']:>7} {r['cost_usd']:>7.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
