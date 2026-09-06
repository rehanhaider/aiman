# Rectifying review comments

A review comment is a hypothesis, not an instruction. Judge each one against
the requirements and the code, then act on the judgement. Under `--tranches`
the judgement goes to the user before any action; see the section of that name
below.

## Per comment

1. **Read before deciding.** Open the cited code, the surrounding
   implementation, the PR description, the issue, the linked requirements, and
   the repository conventions in `AGENTS.md` or `CLAUDE.md`.
2. **Name the underlying concern.** Reviewers frequently propose a fix for a
   real problem they have described imprecisely. Separate the concern from the
   proposed patch.
3. **Decide, with the requirements as the arbiter.** Ask whether acting on it
   would match the stated behaviour, and whether it improves correctness,
   security, maintainability, performance, reliability, or usability — or
   instead adds complexity, scope creep, or a regression.

| Decision | Action |
| --- | --- |
| Accept | Fix the underlying issue. Prefer the correct fix over the reviewer's literal suggestion when they differ. |
| Partially accept | Implement the valid part. Say plainly which part you did not implement and why. |
| Reject | Change nothing. Justify from requirements, architecture, existing behaviour, tests, or a stated trade-off. |

Never edit code solely to silence a comment. An unjustified change is worse
than an open disagreement, because it ships.

## Scope discipline

Fix what the comment identifies. Do not refactor adjacent code, rename beyond
the fix, or fold in unrelated improvements — a growing diff invalidates the
review that has already happened and restarts the loop.

The PR body's `## Scope` section is the arbiter. A comment is out of scope when
acting on it would change no line the diff touches and no acceptance criterion
depends on it — a request to harden code the change did not alter, a
pre-existing defect the diff neither caused nor exposed, a feature the issue
did not ask for. Reject it in one reply that names the section, resolve the
thread, and record it for a follow-up issue. Do not debate it and do not
build it.

The boundary never covers a defect the diff introduced or newly made
reachable, whatever file it lives in. That is in scope by definition; fix it.

If a comment is correct but properly belongs to separate work, say so, record it
for a follow-up issue, and reject it for this PR.

## Under `--tranches`

Judging is read-only. Do the reading and deciding above for every finding,
then stop before changing anything. The round has two checkpoints, and the
turn ends at each one.

**Checkpoint 1: the proposed resolutions.** One row per finding:

| # | Finding | Proposed decision | Proposed change | Why |
| --- | --- | --- | --- | --- |
| 1 | `path:line` — one-line gist | accept / partial / reject | what will change, or "nothing" | one sentence, from the requirements |

Rejections and out-of-scope calls are rows too, because the reply that refuses
them is external state the user has not seen yet. End the turn with one
question: agree to every row, or name the rows to change. Edit nothing until
the answer arrives. A correction rewrites that row. Re-check it against the
other rows, and it holds as a standing constraint for the rest of the run. Then
ask again. Silence is not agreement.

**Checkpoint 2: the finished fixes.** Apply only the agreed rows, run steps 1
to 4 of "After the fixes", and end the turn with: the files changed, the checks
with their results, and each row's outcome against what the user agreed. One
question: sign off, or name the corrections. Do not commit, push, reply to a
thread, or resolve one until the sign-off arrives. Fix a correction in the
uncommitted work, re-check it, and present it again.

**After sign-off**, and only then: commit, push, reply, resolve, and report the
hash. Return to phase 4 with the new head; the next round starts again at
checkpoint 1.

## After the fixes

1. Add or update tests that would fail without the fix.
2. Run the relevant suite, lint, type check, format check, and build. Use the
   repository's own commands.
3. Re-read the complete diff for regressions, unintended changes, duplicated
   logic, and inconsistency with the rest of the file.
4. Confirm every accepted comment is fully addressed, not partially.
5. Commit with a message that names what changed and why. Push to the existing
   PR branch — never force-push over review history unless the user asks.
   Under `--tranches`, this step waits for the sign-off at checkpoint 2.

## Replying and resolving

Under `--tranches`, nothing in this section happens before the sign-off at
checkpoint 2. The replies and the resolved threads are part of what the user
signed off.

Reply to each thread with a short account of what changed or why nothing did.
Two or three sentences. No transcripts, no restating the reviewer's comment.

Reply only where `needs_reply` is true. When it is false the newest message in
that thread is already yours, so replying again just talks over yourself. Read
`last_comment` first: on a thread you have answered before, the reviewer may
have come back with a follow-up that changes the decision.

```bash
# reply in an existing review thread
gh api repos/<owner/name>/pulls/<number>/comments/<comment_id>/replies \
  -f body='Fixed in <sha>. The fallback now carries tenantId, matching the primary path.'
```

Resolve a thread only once the concern is genuinely addressed or reasonably
refused. Leave it open when it needs the user's clarification or a decision you
are not entitled to make.

```bash
# resolve a thread by its GraphQL node id, from pr_watch.py's unresolved_threads
gh api graphql -f query='
  mutation($id: ID!) {
    resolveReviewThread(input: {threadId: $id}) { thread { isResolved } }
  }' -F id='<thread_id>'
```

Resolving a thread you disagreed with is legitimate — the justification is in
the reply, and leaving it open blocks the loop for no reason. Escalate instead
when the disagreement is about intended behaviour rather than implementation.

## Reporting each cycle

After every rectification cycle, report a compact table plus the mechanics:

| Comment | Decision | Reasoning |
| --- | --- | --- |
| `path:line` — one-line gist | accepted / partial / rejected | one sentence |

Then: files changed, checks run with their results, threads left unresolved and
why, the commit hash, and confirmation that the branch was pushed.

Under `--tranches` the table appears twice: as the proposal at checkpoint 1,
with the decision column marked proposed, and as the result after sign-off.
