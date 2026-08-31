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

Hunt for the ways this change breaks in production. Publish only what you can
demonstrate.

Those are two jobs with two different bars, and collapsing them is the main way
this review goes wrong. The search is exhaustive: assume a severe defect is
present and that your job is to find it. Publication is selective: an inline
comment must be proved. Never let the publication bar shrink the search.

The costs are not symmetric. A marginal comment costs the author half a minute
and a "won't fix". A missed P1 ships to users. So when a candidate would be
severe and you cannot yet prove it, spend more time — and if it is still
unproved, hand the user the suspicion in step 9. Never silence, and never a
relabel to P3 — P3s are not posted, so that relabel is silence wearing a badge.

Keep source code read-only. Do not edit code, commit, push, or resolve threads.
For a GitHub PR review, posting the review outcome is the deliverable. Post it
whether findings exist or not, unless the user explicitly says not to post or
asks to see the review first.

Use `scripts/pr_review.py` from this skill directory for GitHub PR plumbing.
In commands below, `<skill>` is the directory containing this file. The script
requires an authenticated `gh` CLI.

## Arguments

```text
/pr-review [target] [--reviewer local|cursor]
```

- `target` — a PR URL, PR number, or branch; omit it to use the current branch.
- `--reviewer` — who reads the diff. `local` (default) is you, running steps 2–7
  in this context. `cursor` hands those steps to `cursor-agent` running this
  same method out of process, then returns here for step 8.

Reach for `cursor` when you wrote the code under review, when a second model's
reading is worth the wall-clock, or when this context is already crowded with
the implementation you are about to judge. Both modes post identically, so the
choice is about who does the reading, not about what lands on GitHub.

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

### When `--reviewer` is cursor

Hand steps 2–7 to `cursor-agent` and pick this up again at step 8:

```bash
python3 <skill>/scripts/cursor_review.py --workdir <workdir>
```

It runs Opus 4.6 at maximum effort with Max Mode off, read-only, over the
context gathered above — this same method is its prompt. It writes
`findings.json` and `suspicions.json` into the workdir in the schema step 8
validates, and prints a summary naming the signature to post under.

Exit 3 means the agent said it could not complete the review. **That is not an
empty review.** Re-run it, or fall back to `--reviewer local` and read the diff
yourself. Never post findings from a run that exited non-zero: an empty
`findings.json` publishes the all-clear sentence, and automation reads that
phrase as ready to merge.

Read what comes back before posting it. You own step 8 either way, so a finding
that is wrong, out of scope, or anchored off the diff is yours to drop — arriving
from a subprocess does not exempt it from the admission criteria in step 4.

## 2. Establish the contract

Before judging code:

1. Read repository instructions such as `AGENTS.md` or `CLAUDE.md`.
2. Read the PR title, body, linked issue, and acceptance criteria.
3. Read existing threads. Do not duplicate an unresolved finding. Re-raise a
   resolved finding only when the defect still exists at the reviewed SHA.
4. Read the full diff, then the surrounding implementation, callers, callees,
   tests, configuration, and prior behavior needed to trace the change.

Treat the reviewed SHA as fixed evidence. If the head moves, re-check findings
against the new head before posting.

### Every pass reviews the whole pull request

`diff.patch` is the pull request against its base, not the newest commit, and
that is the review scope on every pass — the first and every re-review alike.

On a re-review, existing threads tell you what not to repeat. They do not narrow
what to read. Never scope a pass to "the commits since my last review": a file
you cleared at an earlier SHA can be broken by a later commit, and a file the
newest commit does not touch is still shipping in this pull request. Whatever
merges is the whole diff, so that is what must be reviewed.

Dedup against prior findings; never inherit their coverage.

For a large PR, make a private risk map and inspect high-risk surfaces first:
trust boundaries, writes, migrations, public interfaces, startup/configuration,
and concurrency. State any material unreviewed area in the final chat response;
do not pretend a skim was complete.

## 3. Fan out into independent lenses

One reviewer hunting for everything finds the obvious and stops. Run these
lenses **separately and blind to each other** — as subagents where the harness
provides them, otherwise as distinct passes that each start from the diff rather
than from the last pass's conclusions. A lens that inherits another lens's
reasoning stops being independent, and independence is the entire point.

| Lens | Job |
| --- | --- |
| **Repository rules** | Read `AGENTS.md`, `CLAUDE.md`, and the documents they defer to. Report every rule this change violates, quoting the rule with its file, line, **and the heading it sits under**. A violated written rule is a finding on its own; it does not also have to be a bug. A rule inherits the scope of its section — "encrypt everything at rest" under a cloud-infrastructure heading governs that infrastructure, not a phone's local store. |
| **Diff-only** | Read the changed hunks and nothing else. Report obvious defects. Deliberately shallow: this lens exists to catch what deep reading talks a reviewer out of. |
| **Blast radius** | For every symbol, route, table, config key, unit, encoding, or format the diff changes, find its other producers and consumers and read them. This lens owns the correct-diff/broken-system class and anything the change newly makes reachable. |
| **History** | `git log` and `git blame` the modified lines. What was the code being changed there to guard against? Has this been fixed before and re-broken? |
| **Prior review** | Earlier pull requests touching these files, and the comments left on them. A concern reviewers raised before usually applies again. |
| **Tests versus claims** | Does a test pin each behavior the PR claims, and would it fail if the claim broke? Weak assertions, timing-dependent passes, shared mutable state, and a mock that encodes the wrong behavior all count. |

Give the bug-hunting lenses this as their shared checklist:

| Dimension | Questions |
| --- | --- |
| Contract | Does every stated behavior and supported entry point work? |
| Data and state | Are writes atomic, ordered, idempotent, correctly scoped, and serialized with the right units? |
| Security and privacy | Is authentication, authorization, tenant isolation, validation, and secret handling enforced on every path? |
| Reliability | What happens on failure, retry, cancellation, timeout, duplicate delivery, or concurrent use? |
| Interfaces and release | Do callers, clients, schemas, migrations, configuration, and supported platforms remain compatible? |
| Performance and resources | Does realistic load cause unbounded work, N+1 access, leaks, or exhausted pools? |

Two search patterns worth naming, because they produce the most findings:

- **Claim gaps.** For each thing the PR claims — title, body, tests, comments,
  config — where does the diff fail to deliver it? Handling one form but missing
  an obvious sibling is the highest-value class: ESM `import` but not
  `require()` or dynamic `import()`; TCP listeners but not Unix sockets; one
  entry point when there are two.
- **Classic defects** where the diff touches them: races, cancellation, and
  stale async results; unvalidated input reaching queries, shell commands, or
  paths; N+1 access and hot-path work; swallowed errors; off-by-one;
  exhaustiveness and type-narrowing gaps.

Blast radius means reading code the diff does not touch:

```bash
rg -n --hidden -g '!.git' '<changed symbol, key, or format>'
```

Each lens returns candidates as: anchor, what is wrong, why it was flagged, and
what it actually read. Do not stop at the first qualifying candidate — a lens
returns everything it found. Pool them all before judging any of them.

Do not build, typecheck, or run the suite in order to *find* candidates. CI does
that, and it is where the reviewer's time disappears. Run something only to
settle a specific candidate in step 4.

## 4. Verify each candidate independently

**The lens that found a candidate never clears it.** Verify each one in a fresh
context — a separate subagent where available — given the candidate, the diff,
and the repository rules, and nothing about who raised it or why they were
confident.

**Score whether the claim is true, not whether it matters.** A real but trivial
defect scores exactly as high as a real and catastrophic one. Step 5 prices
findings, and step 5 only ever sees what this step lets through — so importance
reasoning here deletes severe findings before anything can price them.

Each verifier scores 0–100 against this rubric, used verbatim:

- **0** — Refuted. You read the code and it does not do what the candidate says.
- **25** — Unverifiable from here; the evidence needed was not available.
- **50** — Probably true, but a link in the chain is assumed rather than read.
- **80** — Verified. You read the code and the claim is accurate. For a rule
  violation: the rule says one thing and this code does another.
- **100** — Verified, and the failure path traced end to end or reproduced.

**Drop everything below 80.**

None of the following is a refutation. Each is a real reason a true finding gets
wrongly killed:

- **Other code in the repository already does the same thing.** Precedent is not
  compliance. The rule still says what it says, and this change is still adding
  another violation.
- **The consequence looks small,** or smaller than the rest of the PR. That is
  severity. Score the truth and let step 5 decide it is a P3.
- **The rule could be read more narrowly.** Read it as written. If it genuinely
  does not cover this case, score 0 and name the words you relied on — do not
  narrow a rule to dispose of a candidate.

  The reverse is equally wrong, and is the more common failure: a rule read
  wider than the section it lives under. Open the file and check what the
  heading above the rule is about. A rule under "Infrastructure" saying "encrypt
  at rest everywhere" governs the infrastructure, however absolute the wording;
  applying it to a different layer invents a requirement nobody wrote. When the
  cited rule does not govern the surface under review, score **0** and say which
  section it belongs to.
- **It is hard to trigger.** Reachability belongs to the admission criteria
  below, not to whether the claim is true.

For a repository-rule candidate, open the cited file and check the rule against
the code. A rule paraphrased into something it does not say scores 0. A rule
that says what the candidate claims, against code that does otherwise, is
verified at 80 — whatever you think of the rule.

Confidence is not severity. This gate decides whether a defect is **real**;
step 5 decides what it **costs**. Never let a low score become a low priority,
and never let a severe consequence inflate a score.

A candidate that survives at 80+ becomes an inline comment only when all of
these hold:

1. **Introduced:** the change creates it, worsens it, or newly exposes it. A
   pre-existing defect this change makes reachable *is* introduced — a new
   caller of an unvalidated helper, a removed guard that made a bad branch dead,
   a flag flipped on.
2. **Reachable:** name a supported input, state, call path, or environment that
   triggers it. For code the change adds for others to call — a guard,
   middleware, helper, endpoint, exported type — reachability is its **intended
   use**, not its current call count. "Nothing mounts it yet" is what shipping a
   broken guard looks like on the day it lands; the callers arrive next week and
   the defect is already merged.
3. **Consequential:** name the incorrect user or system outcome. The test is
   whether you can *name* one, not whether it is big. A small named consequence
   is a P3 finding, not a dropped one.
4. **Actionable:** identify the broken boundary and a plausible fix direction.
   And **warranted** — say what makes the behaviour you are asking for required.
   Exactly one of: a stated requirement (a rule that governs *this* surface, a
   spec, an acceptance criterion, an existing contract), or a demonstrated
   failure of code that already exists. Absent both, you are asking for a
   different design, not reporting a defect. "This should be encrypted",
   "this should be validated", "this needs a retry" are preferences until
   something in the repository asks for them or something concretely breaks
   without them.
5. **Anchored:** cite the changed line closest to the defect. When the defect
   lives in an unchanged file, anchor on the changed line that exposed it and
   name the real location in the body. That the bad line sits outside the diff
   tells you where to anchor, never whether to report.

**These criteria are not a second severity filter.** They ask whether there is a
finding at all, not whether it is worth anyone's time — step 5 decides that, and
step 5 only sees what survives here. If you catch yourself dropping a verified
defect because the impact seems minor, the codebase does this elsewhere, or it
is "only" a convention violation, you are pricing it. Confirm it and let step 5
price it at P3 or P4.

Known false positives, worth naming so verifiers kill them fast:

- A pre-existing problem this change leaves untouched — *unless* the change
  makes it reachable, more likely, or worse, which is criterion 1.
- Anything a linter, type checker, compiler, or test run would catch. CI runs.
- Pedantic nitpicks a senior engineer would not raise.
- General code-quality complaints — thin tests, weak docs, vague security
  unease — unless a repository rule requires it.
- Hardening the change never claimed to do. Storing data locally is not a defect
  for want of encryption, and a new endpoint is not defective for want of a rate
  limit, unless this repository asks for it on this surface or you can show what
  breaks without it. Best practice from elsewhere is not this project's
  requirement.
- A rule cited from a section that governs a different layer. Check the heading.
- A rule violation that the code explicitly and deliberately silences.
- Behavior changes that are plainly intentional and central to the PR.

Keep a private ledger through steps 3–5:

```text
anchor | lens | what is wrong | confidence | price-if-true | status
```

`status` is `confirmed`, `dropped (reason)`, or `unproved-severe`. Every
candidate any lens raised gets a row, including the ones you kill. The ledger is
never published; its `unproved-severe` rows all reach step 9.

## 5. Price the survivors

Read [references/severity.md](references/severity.md) before assigning
priorities.

Run the P1 gate first for every survivor. Ask whether the reachable defect can
break a core supported flow, bypass a security or tenant boundary, corrupt or
lose data, repeat an irreversible side effect, prevent deployment or startup, or
make the PR's central guarantee false. If yes, classify it P1 unless the
severity reference clearly places its limited impact in P2.

Do not start at P3 and wait for extraordinary proof to move upward. Do not
downgrade because the fix is small, the faulty line looks harmless, a test
passes, or the review would otherwise contain a P1.

Priority describes impact and exposure. Confidence describes whether the finding
is proved, and step 4 already settled it. Never collapse the two: a defect that
scored 85 and would take the service down is a P1, not a P3 with reservations.

**Only P1 and P2 reach the pull request.** The script drops P3/P4 at post time:
a review padded with deferrable notes buries the finding that matters. P3/P4
survivors stay in the ledger and get one line each in the step 9 report. That
makes the P2/P3 boundary the posting decision, so take it from the severity
reference alone — do not lift a P3 to P2 to make it visible, and do not park a
P2 at P3 to avoid defending it. Pass `--include-low` to `post` only when the
user explicitly asks for the low tiers.

A candidate whose consequence would be P1 or P2 but which could not clear 80
does not vanish. It goes to step 9 as an unproved severe suspicion, with the one
check that would settle it. Silence is not available for that class.

After pricing everything, make a second severity-only pass: compare each finding
with its neighbors and with the archetypes in the reference.

## 6. Attack the silence

Step 4 attacked the findings. This step attacks the conclusion that everything
else is fine, which is the failure a quiet review cannot see.

For each P1 archetype in the severity reference that this change plausibly
touches, name the specific code you read that rules it out. If you cannot name
it, you have not ruled it out; go read it.

A review with no P1 and no P2 is a hypothesis, not a result. Before accepting
one, account to yourself for each of: authorization and tenant scope, data
durability, units and encodings, retry and idempotency, resource bounds,
producer/consumer compatibility, and deploy or migration safety. For each, name
either the code that makes it safe or the reason the change does not touch it.
"I did not think about it" is neither.

Confirm every surviving anchor is part of the PR diff before writing findings.

## 7. Write concise findings

Write `findings.json`:

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

For each inline comment:

- Use an imperative title that names the required correction.
- Keep the body to 2–4 sentences and at most 120 words.
- State the trigger, incorrect outcome, and fix boundary.
- Tie P1/P2 findings to the affected user, data, security boundary, or release.
- Omit greetings, praise, test transcripts, review history, and reasoning logs.
- Keep one root cause per thread.

Include every priced survivor, P3/P4 too: the script posts only P1/P2 and drops
the rest, so a low tier in this file costs nothing on the pull request — an
inflated tier does. Keep P3/P4 bodies to a single sentence; they exist for the
record and for `--include-low`, not for the review.

The script supplies badges and summary formatting. See
[references/codex-format.md](references/codex-format.md) for the exact output.

## 8. Dry-run, then post

Always render and validate first:

```bash
python3 <skill>/scripts/pr_review.py post --workdir <workdir> \
  --findings-file findings.json --suspicions-file suspicions.json --dry-run
```

Write `suspicions.json` from the ledger's `unproved-severe` rows — omit the flag
only when there are none:

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

Sign the review with the model that actually read the diff, so a reader can tell
which one did:

```bash
--signed-by 'rehanhaider/pr-review-skill · <your model>'          # --reviewer local
--signed-by 'rehanhaider/pr-review-skill · cursor-agent claude-opus-4-6'   # --reviewer cursor
```

The `rehanhaider/pr-review-skill` part is load-bearing, not branding:
`ship-issue`'s watcher refuses to call a pull request clean unless the review
body contains that exact string, so a `--signed-by` value that replaces it
instead of extending it leaves an automated loop stuck forever on a PR that is
actually fine. Add the model as a suffix; never substitute it. Omitting
`--signed-by` entirely is safe — the default is the bare signature.

On success `post` prints the review's URL. Hand it back to the caller — for
automation it is the proof that this specific review landed.

## 9. Clean up and report

Run:

```bash
python3 <skill>/scripts/pr_review.py cleanup --workdir <workdir>
```

Then respond with:

1. The verdict, the reviewed SHA, and which reviewer read the diff.
2. Posted findings ordered P1 → P2, or “No findings.” Then any P3/P4
   survivors, one line each, marked as recorded but not posted.
3. **Unproved severe suspicions** — confirmation of what you posted, not the
   delivery mechanism. They go on the pull request via `--suspicions-file`
   (step 8), because an automated loop can only act on what GitHub shows it.
   A suspicion left in chat is a suppressed P1 that nobody will ever read.
4. Coverage: which P1 archetypes you ruled out by reading code, plus any
   material validation limit or unreviewed high-risk area.
5. The GitHub review link. If posting was explicitly suppressed or failed, say
   so instead.

Do not repeat inline-comment bodies or publish the private candidate ledger.

## References

- [Severity decision ladder and archetypes](references/severity.md)
- [Rendered GitHub comment format](references/codex-format.md)
