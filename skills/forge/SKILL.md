---
name: forge
description: >-
  Take a tracked issue from wherever it lives — Linear, GitHub Issues, or an
  in-repo document — through implementation, a pull request, and a self-driving
  review-and-rectify loop, stopping at a verified ready-to-merge state without
  merging. The reviewer is local, Cursor, or Codex. Use when the user
  asks to ship, land, or implement an issue end to end, to shepherd or babysit
  a pull request through review, to keep resolving review comments until a PR
  is clean, or invokes "/forge" or "/ship-issue". With --tranches, the run
  splits the work into an approved plan. Each tranche waits uncommitted for
  the user's review, and the run fixes what they flag before asking to commit.
  Review findings get the same gate: the user agrees each proposed resolution
  before any edit, then signs off the fixes before any commit.
---

# Forge

Own one issue from its tracker to a pull request that a fresh review reports as
clean, then hand it back. One invocation covers every cycle; the user should not
have to re-prompt between review rounds. Under `--tranches` the opposite is the
contract: the run pauses at every checkpoint and waits for feedback, in the
review rounds as much as in the build.

## Invariants

These hold for the whole run. Breaking one is a failure, not a judgement call.

1. **Never merge.** The terminal state is a clean PR reported as ready to merge.
   Merging is the user's decision, even when every gate is green.
   Report ready to merge only on a `clean` verdict — never infer it from an
   absence of findings, which an unreviewed pull request also has.
2. **Never stop at "PR opened."** Opening the PR is the midpoint. Remain
   responsible until the loop terminates or a stop condition fires.
   Keep going while each round makes progress. Rounds are not rationed — a
   review that keeps finding real defects is the loop working, not failing.
   Under `--tranches`, a checkpoint stop is this invariant working, not
   breaking it: the stop is scheduled, announced, and hands back on purpose.
3. **Never close the issue.** Advance its status to in-review at most.
4. **Stay inside the issue's scope.** Unrelated improvements belong to other
   issues, however tempting.
5. **Report honestly.** A skipped check, an unreviewed area, or an unresolved
   thread goes in the final report in plain words.
6. **Under `--tranches`, never cross a checkpoint.** The checkpoints are the
   plan, before any code; each tranche, before its commit and push and before
   the next tranche begins; and two stops in every review round. Those two are
   the proposed resolutions, before any edit, and the finished fixes, before
   any commit, push, reply, or resolved thread. The gate does not lift when the
   PR leaves draft. Silence is never confirmation.

## Arguments

```text
/forge <issue-ref> [--reviewer local|cursor|codex] [--pr <number>] [--cycles <n>] [--tranches]
```

- `issue-ref` — a Linear key, GitHub issue number, document path, or plain
  description. Omit it when resuming an existing PR.
- `--reviewer` — who reads the diff:

  | Mode | Reviewer |
  | --- | --- |
  | `local` (default) | the `pr-review` skill, run by a subagent started with fresh context |
  | `cursor` | `cursor-agent` running the same method, out of process |
  | `codex` | `@codex` on GitHub |

  One reviewer per run. Every posted review from `local` or `cursor` opens
  with a note naming who read the diff, as harness/model — `Claude/Opus-5`,
  `Cursor/Grok-4.7` — so the PR's history says which model said what.

- `--pr` — resume the loop on an existing PR and skip implementation.
- `--cycles` — hard cap on rectification rounds. Unset by default: the loop runs
  until it converges or stalls, not until a counter expires.
- `--tranches` — plan first, then gate: split the work into tranches, get the
  plan approved before any code, and keep each tranche uncommitted until the
  user reviews and confirms it. Once the PR is under review, every round stops
  twice more: the proposed resolutions before any edit, and the fixes before
  any commit. See phases 2a and 6.

In the commands below, `<skill>` is the directory containing this file.

## 1. Resolve the target and the source

If `--pr` is given, or the current branch already has an open PR, announce that
you are resuming. A tranche checklist on the issue or in the PR body, ticked or
not, means the run is under `--tranches` even if the flag was not passed
again; say so. When that checklist has an unchecked tranche (phase 2a), continue
there; otherwise skip to phase 4, still gated.

Otherwise detect where the issue lives and read it. Follow
[references/issue-sources.md](references/issue-sources.md) — the source is a
property of the repository, and guessing wrong means implementing the wrong
thing.

Open the run by stating: the issue, its source, the acceptance criteria, the
scope boundary, and the reviewer mode. This is the contract the rest of the run
is judged against.

## 2. Implement

Create a semantic branch from the current checkout, named for the issue
(`feat/NAV-123-tenant-scoped-lookup`).

Build only what the acceptance criteria require. Read the authority documents
the issue defers to, plus `AGENTS.md` and `CLAUDE.md`, before writing code.
Follow existing patterns in the files you touch.

Then, using the repository's own commands:

1. Add or update the tests the issue demands.
2. Run tests, lint, type check, format check, and build.
3. Perform any validation the repository requires for the surfaces you changed.
4. Commit in coherent units with messages that say why.

Do not proceed to a PR with a failing gate. Fix it, or stop and report it.

## 2a. Tranches (`--tranches` only)

Without the flag, skip this section.

**Plan first.** Before writing any code, derive the tranches from the
acceptance criteria: each tranche independently implementable, testable, and
committable, naming the criteria it covers. Post the plan as a Markdown
checklist comment on the issue — move it into the PR body once the PR exists —
so it survives a lost session, then stop and ask for approval. Never implement
an unapproved plan.

**One tranche at a time.** Implement and test the tranche, but do not commit or
push it. End the turn with:

1. What changed and the checks run.
2. The remaining checklist.
3. One question: confirm the tranche, or name the corrections.

**Feedback is binding.** A correction becomes a standing constraint for every
remaining tranche. Fix it in the current uncommitted tranche, re-check earlier
work for the same problem, rerun the affected checks, and present the updated
result. Then wait for confirmation again. Silence is not confirmation, and an
open correction blocks the commit.

**Commit only on confirmation.** Once the user confirms the tranche, commit and
push it, then tick its checkbox. Report the commit hash and wait before starting
the next tranche. Confirming one tranche approves that tranche and nothing after
it.

**The PR stays a draft** from its first push until the final tranche is
approved — the one exception to phase 3. External reviewers ignoring drafts is
exactly what a half-finished plan wants. When the last tranche is approved,
mark the PR ready for review and run phases 4–7. The review runs on its own;
what it finds does not. Every rectification round has the two checkpoints in
phase 6, and the final tranche's approval does not pre-approve any of them.

## 3. Open the pull request

Push the branch and open a PR that is **ready for review, not a draft** —
external reviewers ignore drafts, which stalls the loop silently. (Under
`--tranches` the PR is deliberately a draft until the final tranche is
approved — phase 2a.)

The body carries the issue reference, a summary of the implementation, each
acceptance criterion mapped to where it is satisfied, the validation performed,
and any known limitation. Use `Closes #<n>` only when the merge should close a
GitHub issue.

**The body also carries the review boundary.** Add a `## Scope` section with
two lists:

```markdown
## Scope

In scope:
- <each acceptance criterion, one line>

Out of scope:
- <exclusions the issue names>
- <behaviour in the touched files that this change does not alter>
```

It is the one thing every reviewer reads: `pr-review` stages it for `local`
and `cursor`, and Codex reads the PR description. A comment that asks for
work outside it is answered from it (phase 6), so write it as the contract
you are prepared to hold the review to. It never excuses a defect the
diff introduces: a bug in an "out of scope" file that this change caused or
newly exposed is in scope by definition.

## 4. Trigger a review

**`local`** — start a subagent with fresh context and have it run the
`pr-review` skill against this PR. Use the Agent tool with a general-purpose
agent, never a fork: a fork inherits this conversation, and the reviewer must
begin with no memory of writing the code. Do not read the diff in this context,
and do not review it here if the subagent fails; start another subagent.

Give the subagent:

- the repository and PR number;
- the path to the `pr-review` skill, to follow end to end including the post;
- the instruction to sign as `Claude/<model>` with the model the subagent
  itself is running on, `Claude/Opus-5` for example, never a label handed
  down from here;
- the instruction to return the review URL that `pr_review.py post` prints,
  or the exit code and reason when the post did not land.

Its last command is the post:

```bash
python3 <pr-review>/scripts/pr_review.py post --workdir <workdir> \
  --findings-file findings.json \
  --signed-by 'Claude/<the model the subagent is running on, e.g. Opus-5>'
```

The subagent posts its outcome to GitHub, which is what the next phase reads.
A return without a review URL is no review at all.

**`cursor`** — invoke the `pr-review` skill with `--reviewer cursor`. It runs the
same method through `cursor-agent`, out of process and read-only, then posts
from here as usual. It uses automatic model selection (`--model auto`) unless
`--model` says otherwise. The default `signed_by` label is `Cursor/Auto`,
which names the selection mode rather than claiming a specific underlying
model. An explicit model override changes the label. Driven directly:

```bash
python3 <pr-review>/scripts/pr_review.py gather <number> --repo <owner/name>
python3 <pr-review>/scripts/cursor_review.py --workdir <workdir>
python3 <pr-review>/scripts/pr_review.py post --workdir <workdir> \
  --findings-file <workdir>/findings.json \
  --suspicions-file <workdir>/suspicions.json \
  --signed-by '<the signed_by value cursor_review.py printed, e.g. Cursor/Auto>'
```

Omit `--suspicions-file` when `suspicions.json` is an empty array.

`cursor_review.py` exits 3 when the agent reports it could not finish. **Treat
that as no review at all** — re-run it, or fall back to `local`. Never post an
empty `findings.json` that came from a run which exited non-zero: that publishes
the all-clear sentence over a review that never happened.

**`--signed-by` is the visible label, not the machine signature.** `post`
renders it as a note at the top of the review (`🤖 Reviewed by Claude/Opus-5`)
and always adds the hidden marker `pr_watch.py` keys on as an HTML comment, so
no label can leave the loop stuck. Name the harness and the model that actually
read the diff; a review signed as a model that did not run is a false record.
Keep the review URL that `post` prints on success — phase 5 uses it to prove
this specific review landed.

If `pr_review.py post` exits 3, whether the subagent reports it or `cursor`
hits it, the head moved while the review was being written. Do not retry the
post — review the new head from the beginning. After two consecutive head
moves, stop and tell the user something keeps pushing to the branch.

**`codex`** — post the trigger comment and hand off:

```bash
gh pr comment <number> --repo <owner/name> --body '@codex review'
```

Never trigger a review against a head that has uncommitted or unpushed changes.
The review would describe code that no longer exists.

## 5. Wait for new information

For `codex`, block until the reviewer responds **to the current head**. The
response channel varies by outcome: findings arrive as a real PR review, but a
clean round arrives as an issue comment (`Codex Review: Didn't find any major
issues … Reviewed commit \`<sha>\``) or as only a 👍 reaction on the trigger
comment. The wait ends on any of the three; an unrelated human comment does not
end it. Pass the trigger-comment URL that `gh pr comment` printed so the
reaction channel is watched (auto-detected from the newest `@… review` comment
when omitted):

```bash
python3 <skill>/scripts/pr_watch.py wait <number> --repo <owner/name> \
  --expect-review-of head --allow-unsigned --trigger-comment '<comment url>' \
  --timeout 1800 --interval 30
```

`wake_reason` in the output says which channel ended the wait.

Reviewers other than Codex: known bots (coderabbit, gemini, copilot) and any
`[bot]` account also wake the wait but never grade clean on their own; extend
recognition with `--reviewer-bot` or a full `--attest-profile`.

For `local` and `cursor`, the review is already posted, so read the state —
passing the URL from phase 4, so that a silently failed review cannot read as
clean:

```bash
python3 <skill>/scripts/pr_watch.py state <number> --repo <owner/name> \
  --require-review '<review url from pr_review.py post>'
```

The signature is required by default, so nothing extra to pass here. An
external reviewer that answers in text signs its own way, which is why the
`codex` command above carries `--allow-unsigned`; never add that flag on the
`local` or `cursor` paths, as it removes the only thing separating an automated
review from a typed comment. Both of those post through `pr_review.py`, so both
are already signed — the marker is a hidden HTML comment, so its absence from
the rendered page means nothing.

Both print one JSON object. The fields that drive the decision:

| Field | Meaning |
| --- | --- |
| `verdict` | see the table below |
| `unresolved_count` | unresolved conversations — the primary signal |
| `unresolved_threads` | the threads to judge, with `thread_id`, `comment_id`, `path`, `line`, `body` |
| `needs_reply` (per thread) | the reviewer spoke last — you have not answered yet |
| `last_comment` (per thread) | the newest message, so you do not answer twice |
| `required_review_present` | whether the review you commissioned actually landed |
| `latest_review_at_head` | the newest review **of the current commit**, or `null` |
| `head_moved` | whether someone pushed while you were waiting |
| `new_since_baseline` | what arrived during the wait |

### How the verdict is decided

Unresolved conversations decide on their own. The newest review body is read
**only** when there are none — it is a tiebreaker, never an override.

1. Any unresolved conversation → `findings`. A thread marked outdated still
   counts: outdated means the anchor line moved, not that the concern was
   addressed.
2. Otherwise, take every review of the current head commit, newest per author.
   The PR author's empty reply-shell reviews — fabricated by GitHub when a
   thread is answered over the API — are not reviews and are ignored.
3. All of them must carry the exact all-clear sentence `pr-review` posts —
   `Reviewed \`<sha>\` — no new issues found.` — for this same commit. A
   recognized external reviewer's attestation counts the same way: its
   no-findings comment naming this commit, or its 👍 on the trigger comment,
   accepted only under `--allow-unsigned` (`external_attestations` in the
   output shows each one and its grade).

| Verdict | Meaning | What to do |
| --- | --- | --- |
| `findings` | unresolved conversations exist | Rectify — phase 6 |
| `clean` | every reviewer of this exact commit posted the all-clear | **Ready to merge** — phase 7 |
| `unreviewed` | no review exists at all | Go back to phase 4 and get one |
| `stale` | every review is of an older commit | Re-review the current head |
| `unclear` | reviewed at head, but some reviewer gave no all-clear | Read `reviews_at_head_without_marker`; never assume clean |
| `unclear` + "Unverified —" in the body | the reviewer found something severe it could not prove | Settle it: run the stated check, then re-review. Escalate if you cannot run it |
| `unreviewed` + a `failed` attestation | the external reviewer could not run | Read its `detail`; re-trigger once, then stop and report |
| `blocked` | changes requested with nothing to rectify | Only the reviewer can clear it — escalate |
| `unknown` | a GitHub fetch failed, so counts may be short | Never treat as clean; retry or escalate |
| `draft` | the PR is a draft, so reviewers will skip it | Mark it ready for review |
| `timeout` / `closed` | see phase 7 | |

Matching is deliberately strict and anchored to the first line. Prose such as
*"no major issues, but the retry loop needs a rethink"* is an objection, and
substring matching cannot tell it apart from an all-clear.

The distinction that matters: **a pull request nobody reviewed also has zero
findings.** Silence is not approval. Only `clean` may be reported as ready to
merge — `unreviewed`, `stale`, and `unclear` never may, however green the PR
looks.

Read `latest_review_at_head.body` even on `findings`: a reviewer can describe a
real problem in the summary without leaving an inline comment. Trust the prose
over the field when they disagree.

On `timeout`, do not loop blindly. Report that the review has not arrived and
tell the user the exact command to resume:
`/forge --pr <number> --reviewer codex`.

On `closed`, stop and report.

## 6. Judge and rectify

If `verdict` is `findings`, or the review body describes a real problem, work
through [references/rectify.md](references/rectify.md): judge each comment
against the requirements, fix what is justified, refuse what is not, test, reply
to every thread, resolve the ones genuinely addressed, commit, and push.

**Under `--tranches`, the round stops twice.** The section of the same name in
[rectify.md](references/rectify.md) says what each stop contains. First,
before touching a file: one row per finding with the proposed decision, the
proposed change, and the reason, then one question. Edit nothing until the
user agrees each row. A correction rewrites the row before any work starts.
Second, after the agreed fixes and their checks: what changed, the checks with
their results, and one question. Do not commit, push, reply, or resolve until
the user signs off. A round that edits before the first stop, or commits
before the second, has broken invariant 6, however small the finding.

Then return to phase 4 with the new head. A new head needs a new review — a
review of the previous commit says nothing about the current one.

## 7. Terminate

Stop and report when any of these fires:

| Condition | Outcome |
| --- | --- |
| `verdict` is `clean` | **Ready to merge** |
| `verdict` is `blocked`, `unknown`, or `draft` | Stop — say which, and what the user must do |
| `verdict` is `unreviewed`, `stale`, or `unclear` after a cycle | Say which, and that the PR is *not* confirmed clean |
| **Stalled** — a round ends with the same unresolved threads it started with, or a finding you already rectified comes back unchanged twice | Repeating the round will not help. Hand back with what is stuck and why |
| `--cycles` given and reached | Only when the user asked for a cap |
| A `--tranches` checkpoint is reached | Report the tranche, the proposed resolutions, or the uncommitted fixes, then wait — a scheduled stop, not a failure |
| A finding needs a decision about intended behaviour | Escalate with the specific question |
| Requirements ambiguous, credentials missing, or required validation impossible | Escalate before guessing |
| A destructive or irreversible operation is needed | Ask first |
| `timeout` or `closed` | Report the state and the resume command |

On the ready-to-merge path, state it plainly and stop:

> PR #42 is ready to merge — reviewed `31ded9d53a`, no findings, 0 unresolved
> threads, all checks green. Merge when you are ready.

Do not merge it, and do not offer to merge it as the obvious next step.

## Final report

Every run ends with:

1. The issue, its source, and the PR link.
2. Acceptance criteria mapped to how each is satisfied.
3. One row per review comment across all cycles: decision and reasoning.
4. Under `--tranches`: the approved plan, per tranche the feedback received
   and what it changed, and per review round the resolutions as agreed and
   the sign-off that released the commit.
5. Files changed and the final commit hash on the pushed branch.
6. Checks run and their results, including anything skipped.
7. Threads left unresolved and why.
8. Which reviewer produced the verdict and which model read the diff.
9. The terminal state: ready to merge, escalated, or not converged.

## References

- [Locating and reading the issue](references/issue-sources.md)
- [Judging and answering review comments](references/rectify.md)
