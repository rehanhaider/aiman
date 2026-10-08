# Replay evaluation

`../recall` measures whether a review finds defects that were posted on a
pull request by anyone, scored against the whole PR. This evaluation is
narrower and harder: it replays a single historical commit where one
reviewer posted defects the owner then fixed and the other reviewer posted
"no new issues found", with everything after that moment hidden, and asks
how many of the accepted defects the method posts in one round.

It was built on 2026-10-08 to test the single-reader method that now stands
in `SKILL.md` steps 2 to 7. The method it replaced ran six role "lenses", one
verifier subagent per candidate with a 0-100 score and a drop-below-80 gate,
a stricter severity ladder, and posted only its P1 and P2.

## Commits

Four targets, where Codex's GitHub reviewer posted findings the owner
accepted and the skill posted nothing at the same SHA, and two holdouts,
where the skill posted findings the owner accepted. `build_bundles.py` lists
them with their base commits and review cutoffs.

| Commit | Role | Owner-accepted reference |
| --- | --- | ---: |
| rehanhaider/naqid#137 `5ce3656760` | target | 6 |
| rehanhaider/naqid#144 `20b4eed550` | target | 3 |
| rehanhaider/naqid#146 `e50604afa8` | target | 7 |
| Mizanic/Qaleening#53 `e58238fb9d` | target | 9, plus 1 partial |
| rehanhaider/naqid#181 `11f2849f5d` | holdout | 7 |
| Mizanic/Qaleening#60 `954da55d6b` | holdout | 6 |

The reference is read from the owner's replies by hand, not by regex
(`reference.md`). A regex classifier had counted 11 accepted target findings;
reading the replies gives 25, because "Confirmed and fixed in 3c8bafb" and
"**Accepted** — fixed in b5ff2da" are acceptances.

## Running it

```bash
python3 build_bundles.py --root /tmp/pr-review-replay
```

For each target this writes a workdir shaped like `pr_review.py gather`
output (`diff.patch`, `pr_body.md`, `issue.md`, `threads.json`, `state.json`,
a detached `head/` worktree at the reviewed SHA) and a `METHOD.md` made of
`replay-wrapper.md`, steps 2 to 7 of `SKILL.md`, and `references/severity.md`.
The PR body, issue, and threads are the versions that existed before the
review cutoff, taken from GitHub's edit history. The wrapper forbids the
network, `gh`, and reads outside the workdir.

Then run one reviewer per workdir with the prompt "read `<workdir>/METHOD.md`
in full, then follow it", and let it write `findings.json` and `record.md`.
Score by root cause against `reference.md`, not by line: a finding counts
when it names the same trigger and consequence, whatever anchor it chose.
Record every judgment in a ledger like `score-ledger.md`. Measure cost from
the reviewer transcripts with `measure.py`. Remove the worktrees afterwards.

Pass conditions: post at least 18 of the 25 target findings with at least one
per commit; nothing posted that the owner would reject; at least as many of
the 13 holdout findings as the previous method; and the cost per run logged.

## Results on 2026-10-08

Reviewer: one Claude Opus 5.5 agent per commit. v1 is the single-reader
method as first drafted; v2 is the text now in `SKILL.md`.

| Commit | Reference | v1 posted | v2 posted | Live skill at that SHA |
| --- | ---: | ---: | ---: | ---: |
| naqid#137 | 6 | 0 | 3 | 0 |
| naqid#144 | 3 | 0 | 2 | 0 |
| naqid#146 | 7 | 2 | 6 | 0 |
| Qaleening#53 | 9 (+1) | 0 | 5 (+1) | 0 |
| **Targets** | **25** | **2** | **16** | **0** |
| naqid#181 (holdout) | 7 | 3 | 6 | 7 |
| Qaleening#60 (holdout) | 6 | 3 | 4 | 6 |
| **Holdouts** | **13** | **6** | **10** | **13** |

v2 also posted 4 defects on the targets and 8 on the holdouts that the other
reviewer found only at a later SHA of the same PR and the owner accepted. On
my read nothing v2 posted is something the owner would reject; eight v2
findings have no later-round validation and are marked in the ledger.

What v1 showed: it raised 17 of the 25 target defects as candidates and then
dropped 11 at its admission step and priced 4 at P3. Its disproof rule, "if a
decisive link is unknown, exclude the candidate", turned the absence of a
test, a fixture that never rejects, a document silent on the exact case, or a
constant the author chose into a drop. A control run of Codex gpt-6-astra on
the same v1 text dropped the exact finding Codex's own GitHub reviewer had
posted on naqid#144, so the text and not the model caused it. The eight
defects v1 never raised were hunk-level: a comment promising a check the code
lacks, a cap the product's data violates, a response root the client schema
does not parse, a drift test comparing a copy with a copy.

What v2 changed, each tied to a miss in the ledger: drops need named contrary
evidence and eight non-disproofs are listed; P2 is the floor for an admitted
defect; and the read step gained the hunk audit, invariant sweep, contract
parity, fixture parity, tests-versus-claims, production-adapter rejection
traces, route-parameter remounts, copy and projection tracing, and cost
shape without a measurement.

Strict pass conditions: recall 16 of 18 (failed by two), holdout 10 of 13
(failed), precision not yet judged by the owner, cost failed on every run.
The method was adopted because on every measured axis except cost it
dominates what it replaced, and cost is level.

### Cost

| Run (one Opus 5.5 agent) | v1 | v2 | Diff lines |
| --- | ---: | ---: | ---: |
| Qaleening#53 | $21.20 | $21.17 | 1,030 |
| Qaleening#60 | $16.52 | $25.26 | 1,398 |
| naqid#146 | $17.87 | $23.28 | 3,673 |
| naqid#144 | $28.61 | $28.74 | 3,623 |
| naqid#137 | $19.85 | $29.41 | 3,599 |
| naqid#181 | $41.39 | $49.47 | 7,356 |

The replaced method's first reviews in the local session logs cost a $19.47
median on 1,000 to 3,000-line diffs. The single reader is at cost parity, not
cheaper. The transcripts show 24 to 62 tool calls over a prefix of 160,000 to
300,000 tokens and 60,000 to 125,000 output tokens per run, most of it
reasoning; file reads are 50,000 to 110,000 tokens of the prefix.

### Known gaps

Two reference defects were missed by every run, including the Codex control,
and are the next targets: comparing a response root with the client schema
that parses it (Qaleening#53, "Return the mosque at the documented response
root"), and fixture parity on validation sentences (naqid#181, "Give a
client-side contract rejection a field and a sentence"). Single findings also
vary run to run; the totals are the signal.

## Why the method is shaped this way

From the study that preceded this test (GitHub history since 2026-07-01 on
eleven repositories, 3,118 Codex findings and 666 skill findings, and 210
skill runs in the session logs):

- Precision was a tie: the owner accepted 94.1% of Codex's findings and 93.5%
  of the skill's, by hand-labelled replies.
- Recall was the gap: Codex posted a median of 3 findings per round, the
  skill a median of 1; at nine identical commits the skill said "no new
  issues found" at eight while Codex posted 37 findings, 12 of them accepted.
  Of 187 Codex findings the skill lacked on dual-reviewed PRs, 106 needed
  nothing beyond the diff and the changed file.
- Cost was structural: 210 runs cost $3,879, a $10 median, with the six lens
  agents at 49.8% of spend and re-review rounds at 67%.
- Codex's own review prompt admits a finding when the author would fix it,
  has no disproof step, and uses the P0 to P3 scale. That scale and those
  rules are now this skill's.
