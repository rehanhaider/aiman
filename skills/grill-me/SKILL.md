---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

# Grill Me

The user has a plan or design and wants it stress-tested through relentless questioning until you both reach shared understanding.

## How to run the interview

1. **Read the plan first**, and explore the codebase for anything the code can answer — never ask the user something you can look up yourself.
2. **Map the decision tree.** Identify the plan's open branches: architecture, data model, failure modes, migration path, testing, rollout, edge cases, and anything the plan hand-waves.
3. **Ask one question at a time.** For every question, state your recommended answer and why — the user should react to a position, not face a blank quiz.
4. **Resolve dependencies in order.** Settle upstream decisions before asking questions that depend on them.
5. **Push back.** When an answer conflicts with an earlier answer, the code, or a constraint, surface the contradiction immediately instead of moving on.

## Stopping condition

Stop when every branch is resolved or explicitly deferred — not when the questions run out of steam. Deferred items are recorded as open questions, not silently dropped. Close with: "No unresolved branches left — want the decision log written into the plan?"

## Artifact

When the interview ends, append a `## Decisions` section to the plan document (or produce one in chat if the plan has no file): one line per resolved decision — the question, the choice, the reason — plus an `Open questions` list of what was consciously deferred. The interview's value only survives if it lands in the doc.
