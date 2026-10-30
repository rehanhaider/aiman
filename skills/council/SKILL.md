---
name: council
description: "Get review or feedback from three delegates on three different models, then fix what they agree on and re-review until all three are satisfied, without letting scope grow. Trigger this if the user says 'council'."
license: MIT
source: adapted from t3dotgg/tstack skills/council at 1085050 (MIT, Copyright (c) 2026 Theo Browne)
---

# Council

Before an audit, address outstanding PR comments, fix known issues, and run the relevant checks. Give the council the updated implementation. Do not hold back known fixes until the reviews return. If the user wants to discard the implementation and explore new ideas, skip fixes to code that is being replaced.

## Members

Bring in three delegates to help with the user's request, usually for review or feedback. If the user's instructions name council members, use those. Otherwise use these three:

| Delegate | Model | Through | Reasoning effort |
| --- | --- | --- | --- |
| Fable | `claude-fable-5-1` | Claude Code | `xhigh` |
| Astra | `gpt-6-astra` | Codex | `xhigh` |
| Opus | `claude-opus-5-5` | Cursor | `xhigh` |

In T3 Code, call `orchestrator_capabilities` to confirm the models, then `delegate_task` to start one delegate per model in parallel. Elsewhere, use the host's subagent tools. If a member is unavailable through its listed provider, report it instead of substituting another model or provider.

## Running a round

Give each delegate the request and the relevant context. For review or feedback, keep their work read-only. Collect their responses and summarize the useful findings, the disagreements, and the recommended next steps.

For a code review, ask each delegate for a score out of 10. Each full review pass is one round. A fresh review after fixes starts a new round, with new delegates. In T3 Code, start each round with new `delegate_task` calls and include the previous findings and your responses to them. Do not send the new round to an old delegate's thread.

If you agree with a recommendation, make the change, then start a fresh round. Continue until all three delegates are satisfied with the outcome.

Do not let repeated reviews cause scope creep. Keep the scope to the original request. Reject a recommendation that adds work the request did not ask for, and say why in the summary.

## Reporting

If the work ends in a pull request, put the results in the PR description. Put this section before the model and harness line at the end:

```markdown
## Council review

Rounds: 2

| Delegate | Round 1 | Round 2 |
| --- | --- | --- |
| Fable | 7/10 | 9/10 |
| Astra | 8/10 | 10/10 |
| Opus | 7/10 | 9/10 |
```

If a delegate gives no score, write `no score`. Do not invent one. If the PR is open, edit its description. Do not post a comment for this. If there is no PR, put the same results in the final reply only.
