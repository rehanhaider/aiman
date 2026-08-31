---
name: ship-issue
description: >-
  Take a tracked issue from wherever it lives — Linear, GitHub Issues, or an
  in-repo document — through implementation, a pull request, and a self-driving
  review-and-rectify loop, stopping at a verified ready-to-merge state without
  merging. Use when the user asks to ship, land, or implement an issue end to
  end, to shepherd or babysit a pull request through review, to keep resolving
  review comments until a PR is clean, or invokes "/ship-issue". With
  --tranches, the work is split into an approved plan and the run pauses for
  the user's feedback after every tranche.
---

# Ship Issue

Own one issue from its tracker to a pull request that a fresh review reports as
clean, then hand it back. One invocation covers every cycle; the user should not
have to re-prompt between review rounds. Under `--tranches` the opposite is the
contract: the run pauses at every checkpoint and waits for feedback.

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
6. **Under `--tranches`, never cross a checkpoint.** No code before the plan is
   approved, and no tranche begins while the previous one awaits feedback.

## Arguments

```text
/ship-issue <issue-ref> [--reviewer local|cursor|codex] [--pr <number>] [--cycles <n>] [--tranches]
```

- `issue-ref` — a Linear key, GitHub issue number, document path, or plain
  description. Omit it when resuming an existing PR.
- `--reviewer` — who reads the diff:

  | Mode | Reviewer | Independent of the author? |
  | --- | --- | --- |
  | `local` (default) | the `pr-review` skill, in this context | No — same model, same context, same account |
  | `cursor` | `cursor-agent` running the same method, out of process | In judgement, yes; the review still posts under your account |
  | `codex` | `@codex` on GitHub | Yes, in judgement and identity |

- `--pr` — resume the loop on an existing PR and skip implementation.
- `--cycles` — hard cap on rectification rounds. Unset by default: the loop runs
  until it converges or stalls, not until a counter expires.
- `--tranches` — plan first, then gate: split the work into tranches, get the
  plan approved before any code, and end the turn after each finished tranche
  to wait for feedback. See phase 2a.

In the commands below, `<skill>` is the directory containing this file.

## 1. Resolve the target and the source

If `--pr` is given, or the current branch already has an open PR, announce that
you are resuming. When the issue or PR carries an unfinished tranche checklist
(phase 2a), continue at the first unchecked tranche; otherwise skip to phase 4.

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

**One tranche per turn.** A tranche runs under the phase-2 rules: build, test,
commit, push. Then tick its checkbox and end the turn with:

1. What changed, the checks run, and the commit hash.
2. The remaining checklist.
3. One question: continue, or correct.

**Feedback is binding.** A correction becomes a standing constraint for every
remaining tranche. Before continuing, re-check the tranches already built for
the same problem and fix them in the next commit.

**The PR stays a draft** from its first push until the final tranche is
approved — the one exception to phase 3. External reviewers ignoring drafts is
exactly what a half-finished plan wants. When the last tranche is approved,
mark the PR ready for review and run phases 4–7 unchanged.

## 3. Open the pull request

Push the branch and open a PR that is **ready for review, not a draft** —
external reviewers ignore drafts, which stalls the loop silently. (Under
`--tranches` the PR is deliberately a draft until the final tranche is
approved — phase 2a.)

The body carries the issue reference, a summary of the implementation, each
acceptance criterion mapped to where it is satisfied, the validation performed,
and any known limitation. Use `Closes #<n>` only when the merge should close a
GitHub issue.

## 4. Trigger a review

**`local`** — invoke the `pr-review` skill against this PR. It posts its outcome
to GitHub, which is what the next phase reads. Review the diff as unfamiliar
code; run it in a fresh context or subagent where the harness allows, since the
author of a change is the worst judge of it.

```bash
python3 <pr-review>/scripts/pr_review.py post --workdir <workdir> \
  --findings-file findings.json \
  --signed-by 'rehanhaider/pr-review-skill · <your model>'
```

**`cursor`** — invoke the `pr-review` skill with `--reviewer cursor`. It runs the
same method through `cursor-agent` on Opus 4.6, out of process and read-only,
then posts from here as usual. Driven directly:

```bash
python3 <pr-review>/scripts/pr_review.py gather <number> --repo <owner/name>
python3 <pr-review>/scripts/cursor_review.py --workdir <workdir>
python3 <pr-review>/scripts/pr_review.py post --workdir <workdir> \
  --findings-file <workdir>/findings.json \
  --suspicions-file <workdir>/suspicions.json \
  --signed-by 'rehanhaider/pr-review-skill · cursor-agent claude-opus-4-6'
```

Omit `--suspicions-file` when `suspicions.json` is an empty array.

`cursor_review.py` exits 3 when the agent reports it could not finish. **Treat
that as no review at all** — re-run it, or fall back to `local`. Never post an
empty `findings.json` that came from a run which exited non-zero: that publishes
the all-clear sentence over a review that never happened.

**Signing is not decoration.** `pr_watch.py` refuses a `clean` verdict unless the
review body contains the exact string `rehanhaider/pr-review-skill`, so a
`--signed-by` value that drops it leaves the loop stuck on `unclear` forever, no
matter how clean the PR is. Name the model in the suffix, never in place of the
signature. Keep the review URL that `post` prints on success — phase 5 uses it
to prove this specific review landed.

> **Neither local nor cursor is an independent attestation.** Both post under
> the GitHub account that authored the PR, so a clean result means "an agent
> working for the author found nothing", not that an outside reviewer agreed.
> `cursor` at least buys a different model reading with no memory of writing the
> code; `local` does not even buy that. Say which one ran in the final report.
> `--reviewer codex` is the genuinely independent path; prefer it when the
> change touches security, data, or money.

If `pr_review.py post` exits 3, the head moved while the review was being
written. Do not retry the post — review the new head from the beginning. After
two consecutive head moves, stop and tell the user something keeps pushing to
the branch.

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

`wake_reason` in the output says which channel ended the wait. Reviewers other
than codex: known bots (cursor, coderabbit, gemini, copilot) and any `[bot]`
account also wake the wait but never grade clean on their own; extend
recognition with `--reviewer-bot` or a full `--attest-profile`.

For `local` and `cursor`, the review is already posted, so read the state —
passing the URL from phase 4, so that a silently failed review cannot read as
clean:

```bash
python3 <skill>/scripts/pr_watch.py state <number> --repo <owner/name> \
  --require-review '<review url from pr_review.py post>'
```

The signature is required by default, so nothing extra to pass here. An
external reviewer signs its own way, which is why the `codex` command above
carries `--allow-unsigned`; never add that flag on the `local` or `cursor`
paths, as it removes the only thing separating an automated review from a typed
comment. Both of those post through `pr_review.py`, so both are already signed.

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
`/ship-issue --pr <number> --reviewer codex`.

On `closed`, stop and report.

## 6. Judge and rectify

If `verdict` is `findings`, or the review body describes a real problem, work
through [references/rectify.md](references/rectify.md): judge each comment
against the requirements, fix what is justified, refuse what is not, test, reply
to every thread, resolve the ones genuinely addressed, commit, and push.

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
| A `--tranches` checkpoint is reached | Report the tranche and wait — a scheduled stop, not a failure |
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
4. Under `--tranches`: the approved plan, and per tranche the feedback
   received and what it changed.
5. Files changed and the final commit hash on the pushed branch.
6. Checks run and their results, including anything skipped.
7. Threads left unresolved and why.
8. Which reviewer produced the verdict, and whether it was independent of the
   author. A `clean` from `local` or `cursor` is the author's own agent
   reporting on the author's own work.
9. The terminal state: ready to merge, escalated, or not converged.

## References

- [Locating and reading the issue](references/issue-sources.md)
- [Judging and answering review comments](references/rectify.md)
