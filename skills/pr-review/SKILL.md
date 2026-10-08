---
name: pr-review
description: >-
  Review a GitHub pull request, branch, or open changes for concrete defects
  introduced by the change; prioritize findings by user and system impact; and
  post a concise GitHub review outcome, including when no issues are found. Use
  when the user asks for a PR review, branch review, code review of open
  changes, prioritized findings, posted review comments, or invokes
  "/pr-review".
---

# PR Review

Find every defect this change introduces that its author would fix if they
knew about it, and post the ones that matter.

One reader does the whole review. It reads the diff and what the diff
touches, records every candidate as it goes, admits or drops each one on
evidence it read, and prices what survives on the P0 to P3 scale. There are
no separate lenses and no second verifier. A candidate is dropped only on
contrary evidence, never on the absence of a test, a document, or a
measurement: that is how a review that read the right code still posts "no
new issues found".

Keep source code read-only. Do not edit code, commit, push, or resolve threads.
For a GitHub PR review, posting the review outcome is the deliverable. Post it
whether findings exist or not, unless the user explicitly says not to post or
asks to see the review first.

Use `scripts/pr_review.py` from this skill directory for GitHub PR plumbing.
In commands below, `<skill>` is the directory containing this file. The script
requires an authenticated `gh` CLI.

## Arguments

```text
/pr-review [target] [--reviewer local|cursor|opencode]
```

- `target` — a PR URL, PR number, or branch; omit it to use the current branch.
- `--reviewer` — who reads the diff. `local` (default) is you, running steps 2–7
  in this context. `cursor` and `opencode` hand those steps to `cursor-agent` or
  `opencode` running this same method out of process, then return here for
  step 8.

All modes post identically, so the choice is about who does the reading, not
about what lands on GitHub.

## 1. Gather the review

Run:

```bash
python3 <skill>/scripts/pr_review.py gather [target] [--repo owner/name]
```

`target` may be a PR URL, PR number, or branch; omission means the current
branch. The command prints the reviewed SHA and creates a temporary directory
containing:

- `state.json`: repository, PR, base, head SHA, and cleanup state
- `diff.patch`: full PR diff
- `threads.json`: existing review threads and resolution state
- `pr_body.md`: PR description
- `head/`: detached worktree at the PR head when a matching clone is available

If `head/` is absent, read a file at the reviewed SHA with:

```bash
gh api "repos/<owner/repo>/contents/<path>?ref=<head_sha>" \
  --jq .content | base64 -d
```

If there is no open PR, stop unless the user explicitly requested a pre-PR
review. For a pre-PR review, inspect the merge-base diff locally and do not
post.

### When `--reviewer` is cursor or opencode

Hand steps 2–7 to the agent CLI and pick this up again at step 8:

```bash
python3 <skill>/scripts/cursor_review.py --workdir <workdir>     # cursor
python3 <skill>/scripts/opencode_review.py --workdir <workdir>   # opencode
```

`cursor_review.py` uses Cursor's automatic model selection (`--model auto`).
`opencode_review.py` uses Muse Spark 1.3, free tier, on OpenCode Zen
(`--model opencode/muse-spark-1.3-contributor-free`), and runs under a
permission config that denies edits and allows only read-only shell commands.
Either takes `--model` to override. Both run read-only over the context
gathered above, with this same method as its prompt.
Each writes `findings.json` and `suspicions.json` into the workdir in the schema
step 8 validates, and prints a summary whose `signed_by` is the harness/model
label to post under (`Cursor/Auto` or `OpenCode/Muse-Spark-1.3-Contributor` by
default). `Auto` names the selection mode; it does not identify the underlying
model Cursor chose.

Exit 3 means the agent said it could not complete the review. **That is not an
empty review.** Re-run it, or fall back to `--reviewer local` and read the diff
yourself. Never post findings from a run that exited non-zero: an empty
`findings.json` publishes the all-clear sentence, and automation reads that
phrase as ready to merge.

Read what comes back before posting it. You own step 8 either way, so a finding
that is wrong, out of scope, or anchored off the diff is yours to drop — arriving
from a subprocess does not exempt it from the admission criteria in step 5.

## 2. Establish the contract

Read `AGENTS.md`, `CLAUDE.md`, and the documents they defer to for the
directories the diff touches. For each record type or contract the change
writes or reshapes, list every invariant, decision, and acceptance criterion
that names it; each write path is checked against each of them in step 4.
Read the PR title, body, linked issue, and the `## Scope` section if present.
Read `threads.json`: do not duplicate an unresolved finding; re-raise a
resolved one only if the defect is still present at the reviewed SHA. Treat
the reviewed SHA as fixed evidence; if the head moves, re-check findings
against the new head before posting.

Every pass reviews the whole pull request. `diff.patch` is the PR against its
base, and that is the scope on the first review and on every re-review.
Existing threads say what not to repeat; they never narrow what to read. A
file cleared at an earlier SHA can be broken by a later commit, and a file the
newest commit does not touch still ships. Dedup against prior findings; never
inherit their coverage.

## 3. Build the read plan

From `diff.patch`, list every changed behaviour (group hunks that implement one
thing, but keep initial load, manual retry, recovery, and each other entry
point as separate lines). For each, write one line naming: the changed
symbols, the callers, callees and data consumers you will open, the tests that
claim it, the rule section that governs it, and whether it holds state. Find
consumers by searching changed symbols, field names, storage keys and formats,
so copied records and caches appear. Prioritize writes, authorization, side
effects, recovery, and changed public contracts.

Keep one reviewer while the diff, contracts, code and thread history fit about
120,000 tokens of a 200,000-token window. Beyond that, split into the fewest
coherent slices that fit and run steps 4 to 6 once per slice in separate
agents given the same contract and this method. Assign every dependency that
crosses slices to one reviewer who reads both ends and their contract, and
check that list before merging findings. Never split by role.

Batch independent reads into one call and read ranges, not whole files. The
parent and every slice count against one budget. A budget never excuses an
all-clear with an unread dependency; if the evidence exceeds it, finish the
review and record the overrun.

## 4. Read and record

Walk the plan. For each behaviour read the hunk, then the surrounding
implementation, then the callers, callees and consumers named in the plan,
then the tests. Trace before and after. Record a candidate the moment you see
it, in a private ledger, as: anchor, trigger, actual result, expected result,
evidence read. Keep reading after each one. Use `git log` or `git blame` only
to answer a specific question a hunk raised.

Run these checks on every behaviour; each one recovered defects that a
behaviour-level read missed.

- **Hunk audit.** Read each hunk line by line. For every constant, bound,
  minimum, enum, default, regex, ordering of checks, and comment that promises
  a behaviour, ask what the governing document, the product data it names, or
  the code's own comment requires, and open that source. A limit the product's
  own data violates, a comment that promises a check the code lacks, a
  minimum nobody specified, and a 403 that a documented ordering says must be
  a 400 are all candidates.
- **Invariant sweep.** For each invariant listed in step 2, walk every write
  path in the diff that can violate it, including paths the invariant does not
  name. A document that states "at least one Operator" governs the Admin
  creation path even when it only mentions Operators.
- **Contract parity.** For each request or response shape the change produces
  or consumes, open the other side's parser, schema, or type (client schema,
  shared types, mobile types, a test that compares them) and compare root,
  field names, optionality, and clearing semantics. A test that compares a
  copy against a copy proves nothing; record it.
- **Fixture and mock parity.** When the change adds a durable or production
  implementation beside a fixture, mock, or earlier adapter, list every
  refusal, validation message, field attribution, and projection the earlier
  one made and confirm the new path makes the same decision. A refusal the
  fixture made and the durable path omits is a candidate.
- **Tests versus claims.** For each test behind a claimed behaviour, confirm
  its assertions execute and would fail on regression: no swallowed rejection
  before the assert, no assert inside a condition that can be false, no fake
  that ignores the conditions it says it honours. A test that cannot fail is
  a candidate anchored on the test, priced by what it leaves unproved.
- **Asynchronous operations.** For each one, open its callee and trace success
  and rejection through the caller to the visible or durable result. `void`
  and `finally` do not count as handling a rejection. Trace the specified
  production adapter even when today's only implementation is a fixture that
  never rejects.
- **State.** For anything that holds state, trace three more paths per entry
  point: the operation interrupted, a stale result arriving after the state
  moved, and two operations in flight at once; at each result write, check
  that its request and owner are still current. Include route parameter
  changes that keep the component mounted.
- **Stored fields and copies.** For each changed stored field or format, trace
  the write through copied records, summaries, caches and projections to
  their readers. A copy that a reader shows and the write does not update is
  a candidate even when the copy is a fixture.
- **Siblings.** For each claimed behaviour, enumerate the supported sibling
  cases and trace them; record a gap when the code and the applicable
  contract establish one.
- **Cost.** For a loop over user-sized data, state the shape and the scale at
  which it fails (quadratic over a Register of thousands); if the shape is
  clear, the lack of a measurement is not a reason to drop it.

## 5. Admit or drop each candidate

A candidate becomes a finding when all of these hold (Codex's rules, with the
Scope rule added):

1. It meaningfully impacts the accuracy, performance, security, or
   maintainability of the code.
2. It is discrete and actionable, not a general concern.
3. Fixing it does not demand rigor absent from the rest of the codebase.
4. Comparing the same supported scenario at base and head, the change creates
   it, worsens it, or newly makes it reachable. Unchanged code that this
   change calls for the first time counts as introduced. A broken specified
   use of new code counts. A touched line, a desired hardening, or a deferred
   feature alone does not.
5. The author would likely fix it if made aware of it. This is the test that
   decides; the others only shape it.
6. It does not rest on an unstated assumption about the code or the author's
   intent. "The author chose this constant or ordering on purpose" is itself
   an unstated assumption unless a document or the PR body records the
   choice.
7. You identified the code that is provably affected, not speculated that
   something might be.
8. The expected behaviour you are asserting agrees with the governing
   document section, its scope and exceptions, and recorded owner decisions.
   Quote that source for a rule-based finding. Do not flag behaviour it
   explicitly permits. A document that states an invariant governs every path
   that can violate it, even paths it does not name.
9. When the PR body carries a `## Scope` section, acting on it would change a
   line the diff touches or satisfy a listed criterion. A defect the diff
   introduces is always in scope, whatever file it lives in.

Drop a candidate only on contrary evidence that you read, and name it: an
upstream guard that blocks the trigger, a document section that permits the
outcome, base behaviour that is the same for the same scenario, a caller that
cannot produce the trigger, or a test that already proves the behaviour. These
are not contrary evidence and never justify a drop:

- no test exercises the path;
- today's only implementation is a fixture or mock that cannot fail; trace
  the specified production adapter and judge by its consequence;
- the author chose the constant, message, or ordering, when no document
  records that choice;
- the document is silent on the exact case while stating an invariant or a
  rule the outcome violates;
- the window is narrow, or the fixture resolves in a microtask;
- you could not measure it, when the mechanism and the failing scale are
  clear;
- the fix belongs to another issue, when the defect is in this diff;
- the defect is in unchanged code that this change reaches for the first
  time.

When two documents appear to conflict, the one that defines the contract
(data model, API conventions, product spec) governs over a status list of
what currently honours it; say which you applied. When the evidence is
incomplete, state in the body what you verified and what you assumed, and
admit the finding if the author would still fix it. Do not score; decide.
An unresolved P0 or P1-class candidate withholds the all-clear sentence:
carry it to step 8 as a suspicion, with the one check that would settle it.

Never a finding: a pre-existing problem the change does not worsen and does
not newly reach, a style preference, missing tests with no concrete regression
path, a design you prefer, or a diagnostic that a linter or type checker in CI
already reports.

## 6. Price and check coverage

Read [references/severity.md](references/severity.md). Assign once, from
consequence and exposure, using these definitions and no others. The script
posts P0, P1 and P2 and records P3.

- **P0** Drop everything to fix. Blocking release, operations, or major
  usage. Only for universal failures that do not depend on inputs.
- **P1** Urgent. Should be addressed in the next cycle.
- **P2** Normal. To be fixed eventually.
- **P3** Low. Nice to have.

P2 is the floor for any admitted defect: wrong output, lost input, an
unhandled rejection, a violated document or contract, a copy a reader shows
stale, a test that cannot fail. P3 is for wording, naming, stale comments, and
maintainability notes with no behaviour path. A consequence that is dev-only
today but inherited by the specified production adapter is priced by the
production consequence. Do not lower a priority because the window is narrow,
the fixture is instant, the fix is small, or the evidence is thin; resolve
the evidence or drop the finding. The P0 and P1 shapes in the severity reference
illustrate those tiers; they do not make every introduced defect a P1.

Then one bounded coverage check against the plan: a hunk not audited line by
line, an invariant not walked, a changed symbol whose consumers were not
opened, a contract without its other side compared, a fixture decision not
checked against the durable path, a test not checked for executing
assertions, an async operation without its rejection trace, a stateful entry
point without its three traces, a changed stored field not followed to its
readers. Close those gaps and stop. An empty result after a completed plan is
a result.

## 7. Write findings

`findings.json`:

```json
[
  {
    "path": "src/session.ts",
    "line": 84,
    "side": "RIGHT",
    "severity": "P1",
    "title": "Keep tenant scope on the fallback query",
    "body": "When the primary lookup misses, this fallback queries by email alone. A user in one tenant can therefore receive another tenant's record when both use the same email. Include `tenantId` in the fallback predicate, matching the primary path."
  }
]
```

Include every admitted finding, P3 too: the script posts P0 to P2 and drops
P3, so a low tier in this file costs nothing on the pull request and an
inflated tier does. Keep P3 bodies to one sentence. Anchor on the changed line
closest to the defect; when the defect lives in an unchanged file, anchor on
the changed line that exposed it and name the real location in the body.

Title: imperative, at most 80 characters, naming the correction. Body: one
paragraph of two to four sentences, at most 120 words. First sentence states
the trigger ("When …", "If …", or the input that causes it). Second states the
incorrect outcome and who it reaches. Last names the fix boundary. When a rule
supports the finding, end with one reference line:
`AGENTS.md reference: <path>#L<start>-L<end>`. No code blocks over three
lines, no praise, no history. The script supplies badges and the summary; see
[references/codex-format.md](references/codex-format.md) for the rendered
output.

## 8. Dry-run, then post

Always render and validate first:

```bash
python3 <skill>/scripts/pr_review.py post --workdir <workdir> \
  --findings-file findings.json --suspicions-file suspicions.json --dry-run
```

Write `suspicions.json` from the step 5 candidates that are P0 or P1-class and
could not be resolved — omit the flag only when there are none:

```json
[
  {
    "path": "src/auth.ts",
    "line": 42,
    "consequence": "A quoted-JSON groups claim parses wrong, locking out every admin.",
    "check": "Log the raw claim from one deployed request."
  }
]
```

The script lists these under the summary and, while any exist, withholds the
`no new issues found` sentence — a pull request with an unresolved severe
candidate is not an all-clear, and automation keys on that phrase.

Inspect the payload for severity, concision, duplicate threads, and valid
anchors. The top-level GitHub review body is deliberately only a finding count
and reviewed SHA. Do not append “checked and fine” notes, resolved-thread
recaps, old findings, test output, or a narrative of the review process.

For a GitHub PR, rerun without `--dry-run` after validation. Do this even when
`findings.json` is empty: GitHub must receive the one-line “no findings” review
so the user does not have to search elsewhere for the result.

Skip posting only when the user explicitly says not to post, asks to see the
review first, or requested a local pre-PR review.

If the head moved while the review was being written, `post` exits 3 without
posting. Findings drawn from the old code must not be attached to a commit
nobody reviewed, so re-gather and review the new head rather than retrying the
post. Use `--allow-moved-head` only when the findings provably still apply.

If the PR moved or posting failed, do not silently lose the work: report the
findings with `path:line` and the reason posting was skipped.

`--signed-by` is required and names who read the diff, as harness/model, so a
reader can tell which one did:

```bash
--signed-by 'Claude/<the model running this session, e.g. Opus-5>'   # --reviewer local
--signed-by '<the signed_by that cursor_review.py printed>'          # --reviewer cursor
--signed-by '<the signed_by that opencode_review.py printed>'        # --reviewer opencode
```

`post` renders it as a note at the top of the review — `🤖 Reviewed by
Claude/Opus-5` — and adds the hidden marker `forge`'s watcher keys on as an
HTML comment on its own, whatever the label says. So the label is a record,
not a mechanism: name the model that actually ran, and nothing else about it
can jam the loop.

On success `post` prints the review's URL. Hand it back to the caller — for
automation it is the proof that this specific review landed.

## 9. Clean up and report

Run:

```bash
python3 <skill>/scripts/pr_review.py cleanup --workdir <workdir>
```

Then respond with:

1. The verdict, the reviewed SHA, and which reviewer read the diff.
2. Posted findings ordered P0 → P2, or “No findings.” Then any P3 findings,
   one line each, marked as recorded but not posted.
3. **Unproved severe suspicions** — confirmation of what you posted, not the
   delivery mechanism. They go on the pull request via `--suspicions-file`
   (step 8), because an automated loop can only act on what GitHub shows it.
   A suspicion left in chat is a suppressed P1 that nobody will ever read.
4. Coverage: the step 6 result. Name any hunk, invariant, consumer, contract
   side, fixture decision, test, async operation, state entry point, or stored
   field left unchecked, any budget overrun, and any unreviewed area.
5. The GitHub review link. If posting was explicitly suppressed or failed, say
   so instead.

Do not repeat inline-comment bodies or publish the private candidate ledger.

## References

- [Severity scale and the P0 and P1 shapes](references/severity.md)
- [Rendered GitHub comment format](references/codex-format.md)
