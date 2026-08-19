# Q1

can you look through my history with models like fable, opus, and gpt-5.6-sol in claude code and codex on this machine to see what the most common mistakes are? want to make sure we optimise to steer away from those.

I want you to break down the most common failure modes and how often each model hits them

# GPT-5.6-Sol

You could not have prevented every failure through better prompting. Many failures happened after you had already given clear instructions. The main improvement is to turn preferences into persistent rules, explicit stop conditions, and machine-checkable gates.

The highest-value change is this:

> Do not let the agent decide what “done,” “allowed,” or “correct” means during the task. Define those before work starts.

## 1. Use one persistent operating contract

Put this in the global or repository `AGENTS.md`, not in every prompt:

```md
## Operating contract

1. Answer the exact question in the first sentence.
2. When asked what is next, recommend one item. Do not return a menu unless asked.
3. Treat the documented source of truth as authoritative. Separate:
   - documented contract;
   - current implementation;
   - open decision;
   - your proposal.
4. Do not add a dependency, feature flag, service, architecture layer, compatibility
   path, migration, or workflow unless the task requires it.
5. Do not install software, open a PR, push, merge, deploy, delete, reset, or modify
   external state unless the request or named workflow authorizes that exact action.
6. Use the repository commands and skills. Do not replace them with direct package,
   build, Gradle, browser, or GitHub commands without a verified reason.
7. Do not stop at an intermediate state. Continue until the stated terminal condition
   is reached or a real blocker requires a user decision.
8. Before claiming completion, verify the result through the requested interface:
   tests, browser, emulator, screenshot, deployed system, or exact PR head.
9. Preserve unrelated changes. Inspect repository state before editing or cleaning.
10. Every user correction becomes an active constraint for the rest of the task.
    Re-check current work for the same violation immediately.
11. After compaction, model switching, or handoff, reconstruct the active constraints
    and terminal condition before continuing.
12. Ask a question only when the missing answer would materially change scope,
    architecture, cost, security, or external state.
```

## 2. Start important tasks with a task contract

For larger tasks, use this template:

```md
Task:
[Exact objective]

Required outcome:
[Concrete artifact or working behavior]

Source of truth, in order:
1. [Product specification]
2. [Issue or PR]
3. [Repository instructions]
4. [Current implementation]

In scope:
- [...]

Out of scope:
- [...]

Authorized actions:
- [...]

Actions requiring separate approval:
- install dependencies
- add infrastructure or architecture
- deploy or change live state
- open or merge a PR
- delete or rewrite history

Required proof:
- [Tests]
- [Browser/emulator/live verification]
- [Exact PR or commit state]

Terminal condition:
[The condition that means the task is complete]

Do not stop after planning, partial implementation, pushing, or requesting review.
Continue until the terminal condition is reached or report one concrete blocker.
```

This would have prevented many “I thought you meant…” failures.

## 3. Add an action-permission table

Agents often confuse normal autonomy with permission for unrelated changes.

| Action | Default |
|---|---|
| Read files, inspect state, run safe checks | Proceed |
| Implement the requested change | Proceed |
| Fix a defect required for the requested outcome | Proceed and explain |
| Add a dependency or feature flag | Stop for approval |
| Introduce a new architecture or service | Stop for approval |
| Change an unrelated file | Do not proceed |
| Push or open a PR | Only when explicitly requested or required by the named workflow |
| Merge, deploy, delete, reset, or rewrite history | Require exact authorization |
| Use mock data when live validation was requested | Prohibited |
| Replace repository commands with direct commands | Prohibited unless the repository path fails |

This is especially useful for Fable.

## 4. Define workflow terminal states

“Implement this” is often interpreted as “make some changes.” Define the end state.

For implementation:

```md
Done means:
- requested behavior is implemented;
- focused tests pass;
- the live interface is checked when applicable;
- the diff has been reviewed;
- no unrelated changes were introduced;
- the result is committed or published only if requested.
```

For PR shepherding:

```md
Done means:
- the exact current head has passed the required checks;
- a fresh review has completed against that head;
- every actionable thread has a response;
- addressed threads are resolved;
- no newer review or comment is waiting;
- the PR is reported ready to merge.

Do not merge unless I explicitly ask.
```

For architecture work:

```md
Done means:
- existing decisions are identified first;
- current behavior and desired behavior are separate;
- no proposal is presented as an agreed requirement;
- each proposed change names the problem it solves;
- unresolved decisions are listed explicitly;
- no implementation begins without authorization.
```

## 5. Use a correction register

Add this rule:

```md
When I correct you:

1. Restate the correction in one sentence.
2. Add it to the active constraint list.
3. Check whether the current work violates it elsewhere.
4. Correct every existing occurrence.
5. Do not require me to repeat the correction.
```

Examples of useful active constraints:

```text
- Use Makefile commands, not direct Gradle commands.
- Perform a live test, not a mock test.
- Do not add Claude or AI attribution to commits.
- Do not add feature flags.
- Do not open a PR until explicitly requested.
- Naqid uses rebase merge, never squash merge.
```

## 6. Require evidence before completion claims

For UI work:

```md
Do not call UI work complete from code inspection alone.

Before completion:
1. Open the actual page or app.
2. Check the relevant viewport and theme.
3. Compare it with the named reference.
4. Check spacing, contrast, typography, copy, and interaction states.
5. Capture a screenshot or describe the observed result.
6. Fix visible regressions before reporting completion.
```

For runtime work:

```md
A build or unit test does not prove the live workflow.

Run the requested live path with the requested environment and credentials.
Do not substitute mocks, local-only checks, or a different interface.
```

For reviews:

```md
Do not infer that a PR is clean from silence, old reviews, or zero visible threads.
Check the exact head, current review threads, recent comments, and required checks.
```

## 7. Constrain communication explicitly

For Opus and Sol, add:

```md
Communication rules:

- First sentence: direct answer or recommendation.
- Use plain language.
- Do not restate the question.
- Do not provide more than one recommendation unless alternatives were requested.
- Define necessary technical terms when first used.
- Keep the main answer under 250 words unless detail was requested.
- Put supporting analysis after the answer.
- If the user says the answer is unclear, restart from the concrete scenario.
  Do not paraphrase the same abstraction.
```

For design sessions:

```md
Handle one decision at a time.

For each decision provide:
1. Current agreed state.
2. Exact unresolved question.
3. Your recommendation.
4. Why.
5. What changes if accepted.

Do not introduce a new decision while resolving the current one.
```

## 8. Add model-specific steering

For Fable:

```md
Use strict scope mode.

Do not add dependencies, flags, infrastructure, compatibility behavior, publishing
actions, or alternative test paths. Before UI completion, inspect the live result.
Before any external mutation, confirm that the exact action was authorized.
```

For Opus:

```md
Use completion-owner mode.

Choose the next action when requirements are clear. Do not stop after analysis,
partial implementation, a push, or a review request. Maintain a completion checklist
and continue until its terminal condition is satisfied.
```

For GPT-5.6 Sol:

```md
Use contract-first architecture mode.

Before proposing architecture:
1. Read the authoritative product contract.
2. State the existing agreed model.
3. Identify the exact open decision.
4. Make one recommendation in plain language.
5. Check the recommendation against the product hierarchy and authority boundaries.

Do not invent new product concepts merely to make the architecture symmetrical.
```

## 9. Make important guardrails mechanical

Instructions help, but enforced checks are stronger:

- Protect branches and restrict merge methods.
- Use a repository command for PR readiness.
- Make local signoff attach to the exact commit.
- Add lint checks for forbidden imports, generated files, and dependency boundaries.
- Add production scans for fixtures and mock data.
- Require a changeset when applicable.
- Add scripts that inspect unresolved review threads.
- Put build and emulator commands behind Make targets.
- Require dependency changes to appear as a separate, reviewable commit.
- Use wrappers that refuse destructive Git commands in dirty worktrees.
- Record the reviewed commit SHA and compare it before merging.

The ideal pattern is:

```text
Instruction prevents the first mistake
Checklist catches it during work
Automated gate prevents it from shipping
```

The most important three changes would be:

1. A persistent operating contract.
2. A task-specific terminal condition.
3. Mechanical gates for publishing, merging, dependencies, and live verification.