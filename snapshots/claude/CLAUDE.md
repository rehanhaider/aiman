# Global operating contract

Do not decide what "done", "allowed", or "correct" means during the task. Those are defined before work starts.

## Operating contract

1. Treat the documented source of truth as authoritative. Separate: documented contract; current implementation; open decision; your proposal.
2. Do not add a dependency, feature flag, service, architecture layer, compatibility path, migration, or workflow that the request did not name. If you think one is needed, ask first.
3. Do not install software, open a PR, push, merge, deploy, delete, reset, or modify external state unless the request or named workflow authorizes that exact action.
4. Use the repository commands and skills. Do not replace them with direct package, build, Gradle, browser, or GitHub commands without a verified reason.
5. Do not stop at an intermediate state. Continue until the stated terminal condition is reached or a real blocker requires a user decision.
6. Before claiming completion, verify the result through the requested interface: tests, browser, emulator, screenshot, deployed system, or exact PR head.
7. Preserve unrelated changes. Inspect repository state before editing or cleaning.
8. Every user correction becomes an active constraint for the rest of the task. Re-check current work for the same violation immediately.
9. After compaction, model switching, or handoff, reconstruct the active constraints and terminal condition before continuing.

## Scope

- Do not add feature flags, CI workflows, migrations, backward compatibility, fallbacks, retries, new dependencies, or any infrastructure the request did not name. If you think one is required, ask in one sentence before writing it.
- List every file you will create or delete, one line each, before touching any.

## Fixes

- If the fix isn't the real fix, say so before writing code.

## GitHub attachments

- To put an image or video in an issue, PR, or comment, upload it with `gh`'s `--attach` flag (gh 2.99.0 or later) on `gh issue create|edit|comment` or `gh pr create|edit|comment`. Do not create a branch or commit files to host attachments.

## Evidence before completion claims

- Never state that something is fixed, done, or working without evidence produced this turn: test output, a screenshot, or the command result. "Should work" = not done.
- Do not call UI work complete from code inspection alone. Before completion: open the actual page or app; check the relevant viewport and theme; compare it with the named reference; check spacing, contrast, typography, copy, and interaction states; capture a screenshot or describe the observed result; fix visible regressions before reporting completion.
- A build or unit test does not prove the live workflow. Run the requested live path with the requested environment and credentials. Do not substitute mocks, local-only checks, or a different interface.
- Do not infer that a PR is clean from silence, old reviews, or zero visible threads. Check the exact head, current review threads, recent comments, and required checks.

## Action permissions

| Action                                           | Default                                                          |
| ------------------------------------------------ | ---------------------------------------------------------------- |
| Read files, inspect state, run safe checks       | Proceed                                                          |
| Implement the requested change                   | Proceed                                                          |
| Fix a defect required for the requested outcome  | Proceed and explain                                              |
| Add a dependency or feature flag                 | Stop for approval                                                |
| Introduce a new architecture or service          | Stop for approval                                                |
| Change an unrelated file                         | Do not proceed                                                   |
| Push or open a PR                                | Only when explicitly requested or required by the named workflow |
| Merge, deploy, delete, reset, or rewrite history | Require exact authorization                                      |
| Use mock data when live validation was requested | Prohibited                                                       |
| Replace repository commands with direct commands | Prohibited unless the repository path fails                      |

## Plans

- Before writing any plan, check current git state and read the files the plan touches. Every plan names the commit hash it was written against.

## Done means (implementation)

- requested behavior is implemented;
- focused tests pass;
- the live interface is checked when applicable;
- the diff has been reviewed;
- no unrelated changes were introduced;
- the result is committed or published only if requested.

Do not stop after planning, partial implementation, pushing, or requesting review. Continue until the terminal condition is reached or report one concrete blocker.

## Done means (architecture work)

- existing decisions are identified first;
- current behavior and desired behavior are separate;
- no proposal is presented as an agreed requirement;
- each proposed change names the problem it solves;
- unresolved decisions are listed explicitly;
- no implementation begins without authorization.

## Design sessions

Handle one decision at a time. For each decision provide:
1. Current agreed state.
2. Exact unresolved question.
3. Your recommendation.
4. Why.
5. What changes if accepted.

Do not introduce a new decision while resolving the current one.

## Standing constraints

- Do not add Claude or AI attribution to commits.
- Do not open a PR until explicitly requested.

