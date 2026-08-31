# Severity decision ladder

Assign priority from the demonstrated consequence and its exposure. Do not use
priority as a substitute for confidence: prove an uncertain claim or omit it.

Only P1 and P2 are posted to the pull request; P3 and P4 are recorded in the
final report but never posted by default. The tier you assign is therefore
also the posting decision. That raises the stakes of the P2/P3 line without
changing where it sits: classify from consequence and exposure alone, neither
lifting a P3 to make it visible nor parking a P2 to keep the review quiet.

## Decision order

Evaluate every finding from the top down:

1. **P1:** Must the author block merge because a supported path can cause
   severe user, security, data, availability, or release harm?
2. **P2:** Is there meaningful incorrect behavior or a contract break with
   limited reach, recoverable impact, or an uncommon trigger?
3. **P3:** Is the defect real but low impact, narrow, and safe to defer?
4. **P4:** Is it only a small readability or style improvement? Usually omit it.

When two labels seem plausible, write the trigger and consequence in plain
language. Classify from those facts, not from how large the diff or fix is.

## P1 — must fix before merge

Use P1 for a reachable merge blocker, including:

- Authentication or authorization bypass, cross-tenant access, injection,
  credential disclosure, or a material privacy leak.
- Data loss, corruption, silent mis-association, duplicate irreversible work,
  or an invalid migration on supported data.
- A core user action crashes, fails, hangs, or returns materially wrong results
  for normal supported use.
- The service cannot start, deploy, upgrade, or pass a required release gate in
  a supported environment.
- The PR's central safety or correctness guarantee is bypassed on a supported
  entry point, making the feature ineffective.
- A common failure or retry path leaves durable state inconsistent.
- A destructive or irreversible operation runs with the wrong scope: a delete,
  truncate, overwrite, or bulk update whose predicate is missing or widened.
- Resource exhaustion under normal supported load — unbounded memory or result
  sets, a non-terminating loop, a deadlock, a lock held across I/O, or pool and
  handle exhaustion that takes the service down.
- A producer and its consumer now disagree about a shape, unit, encoding,
  timezone, or key, so data is silently written or read wrongly — including
  during a rolling deploy, where old and new code run at once.
- A breaking change to a contract external clients depend on — public API,
  webhook payload, CLI flag, exported type, on-disk or wire format — with no
  compatible path.
- The change removes, weakens, or bypasses an existing check, guard, limit, or
  test, so a property that was enforced is now unenforced.
- The change makes an existing dormant defect reachable for the first time.

Examples:

- A fallback query omits `tenantId`, exposing records across organizations.
- A payment retry uses a new idempotency key and can charge twice.
- A seconds/milliseconds mismatch expires every active session immediately.
- A required database migration adds a non-null column without a compatible
  backfill, so deployment fails on existing rows.
- A boundary rule blocks static imports but a supported runtime entry point
  uses an unchecked loader and bypasses the rule entirely.
- A cleanup job's `DELETE` loses its tenant predicate and empties the table.
- An endpoint loads every row to count them and exhausts memory at production
  data size.
- The writer emits a new enum value the untouched reader rejects, so every
  event fails for the duration of the rolling deploy.
- A rate limiter moves to an in-process counter, so the limit is now
  per-replica and effectively absent.
- The PR adds the first caller of an existing helper that never validated its
  path argument, making directory traversal reachable for the first time.

Do not downgrade these because the triggering code is short, the fix is easy,
or only one test is missing.

## P2 — meaningful but limited

Use P2 when behavior is wrong and worth fixing before normal merge, but the
impact or exposure is constrained:

- A secondary flow or uncommon supported input fails with a recoverable result.
- A compatibility break affects one supported client, platform, or deployment
  mode rather than the main path.
- A validation or boundary gap has limited access or low-value impact without a
  practical security escape.
- Realistic load causes a significant but non-catastrophic performance
  regression.
- Error handling masks a failure but does not corrupt durable state.
- A test claims a guarantee while exercising a weaker path, and the unproved
  implementation has a concrete regression route.
- A written repository rule is violated in a way that leaves the thing the rule
  protects unprotected — clients unable to branch on an error, an input reaching
  a sink unvalidated, a documented contract silently changed.
- A defect in code this change adds for others to call, where the intended
  callers are already specified. Price it by what happens when they arrive, not
  by today's call count.

Examples:

- Password reset fails only for accounts imported from a legacy provider.
- A path filter skips one supported package, leaving its checks unenforced.
- Pagination repeats the final page for exact multiples of the page size.
- A query becomes N+1 on a screen that commonly loads hundreds of records.
- A new authorization guard reads an unvalidated path parameter straight into a
  database key; nothing mounts it yet, but four queued issues will.
- Denials ship with no machine-readable code, so every client must match English
  prose to tell "not an admin" from "not a member of this tenant".

## P3 — real, narrow, and deferrable

Use P3 for demonstrated issues with low impact and limited blast radius:

- A rare edge case produces minor, recoverable inconvenience.
- A test is flaky or can pass for the wrong reason, without evidence of a
  current product defect.
- Cleanup or listener behavior leaks a small resource only in a short-lived or
  uncommon path.
- An internal maintainability defect has a concrete near-term cost but does not
  change user-visible behavior.

Examples:

- A test shares module state and becomes order-dependent.
- An optional diagnostic reports stale information after a narrow sequence.
- An internal helper accepts an impossible state and produces a misleading log.

P3 is not a safe default. If the consequence is security exposure, corrupt
data, a broken core flow, or failed deployment, reconsider P1 even when the
trigger is an edge case.

Three phrases that mean you are landing on P3 for the wrong reason. Each is a
statement about *when* the cost arrives, not about how small it is:

- **"Nothing calls it yet."** New shared code is priced by its specified
  callers. See P2.
- **"It is only a convention."** A rule exists to protect something. Price what
  goes unprotected, not the tidiness of the rule.
- **"The codebase already does this elsewhere."** Precedent is not a defence,
  and it was already ruled out as a refutation at the verification step.

If removing the word "only" from your reasoning would change the tier, it was
not a P3.

## P4 — nit

Use P4 only when the user asked for nits or the improvement is unusually useful:

- Naming, formatting, or comment wording.
- A small readability refactor with no behavioral effect.
- A stylistic preference not required by repository rules.

Do not post ordinary P4 comments by default.

## Non-findings

Omit:

- Missing tests without a concrete defect or credible regression path.
- Pre-existing problems the PR does not worsen.
- Hypothetical unsupported inputs or environments.
- Alternative designs that do not correct wrong behavior.
- General advice with no exact trigger and consequence.

## This ladder is stricter than other reviewers' — do not read across

Codex and several other automated reviewers post P1–P4 badges that look
identical to these and mean something different. Their published rubric:

| Theirs | Their definition | Nearest here |
| --- | --- | --- |
| P0 | "Drop everything to fix. Blocking release, operations, or major usage." | **P1** |
| P1 | "Urgent. Should be addressed in the next cycle" | **P2** |
| P2 | "Normal. To be fixed eventually" | **P3** |
| P3 | "Low. Nice to have." | **P4** |

Their GitHub integration posts only their top two tiers, so a pull request
reviewed by both will show their P1 next to this skill's P2 for the same defect.
That is the scales differing, not a disagreement about the code.

Two consequences:

- **Do not inflate to match.** Their P1 means "urgent", not "blocking". Calling
  an urgent defect P1 here would claim it must block the merge, which is a
  different and stronger claim.
- **Do not take the offset as licence to sit at P3.** The offset is one tier.
  Where an external reviewer says P1 and this skill says P3, one tier is the
  scale and the other is a real downgrade — find it.

## Final calibration checks

Before publishing, ask:

- Did I audit P1 failure modes, or only easy test and style issues?
- Am I lowering severity because proof is weak? If so, investigate or omit.
- Would merging expose users, data, security, availability, or deployment?
- Is the affected path core or secondary, common or narrow, recoverable or
  irreversible?
- Would I block merge on the demonstrated consequence?
