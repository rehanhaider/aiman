---
name: architect
description: "Sketch types, signatures, and module structure before code, compare at least two independent candidate designs, then implement against the chosen sketch and scrap it if implementation keeps fighting it. Use for /architect, 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape."
disable-model-invocation: true
license: MIT
source: adapted from cursor/plugins pstack/skills/architect at 00b14f1 (MIT, Copyright (c) 2026 Lauren Tan)
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Get at least two independent candidate designs, synthesize one, then fill in code against it.

## Start

Open a todo list with one entry per phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Naming a file isn't grounding. For each subsystem, read the code and write down:

- its entry points and who calls them;
- the types that cross its boundaries;
- which module owns each piece of state;
- the invariants its callers rely on.

If the design changes ownership or layering, also find out why the current shape exists. Read `git log` and `git blame` on the files that carry the design, plus any linked issue or design doc. Record the reason as a constraint, so the new design keeps it or drops it on purpose.

Skip Phase A only when the work is greenfield with no surrounding system to integrate.

## Phase B: Sketch

Design it twice. Get at least two structurally distinct candidates before synthesis, even when the first looks sufficient. They must be different whole shapes, not point fixes inside one shape.

### Run the candidates

1. Make a sketch directory outside the repo with `mktemp -d`. Each runner gets its own subdirectory and writes only there. Runners must not edit the repo.
2. Start two or more runners in parallel with the host's subagent tool. In Claude Code, send all `Agent` calls in one message. In Codex, use `spawn_agent` and wait for every runner.
3. Give each runner a different model when the host offers a choice. Different models produce more different designs.
4. Give each runner the same brief: the task, the Phase A notes, its output subdirectory, and the full text of [`references/runner-prompt.md`](references/runner-prompt.md).
5. If the host has no subagent tool, write the candidates yourself, one after the other. Write the second without reusing the first one's core types.

### Screen and compare

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md). Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare the candidates that pass on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public interface. A rich interface can keep call chains short by putting capability in one place instead of spreading it across layers.

### Synthesize

Pick one candidate as the base. Take specific parts from the others where they are better, and only where they fit the base's core types. Do not average the candidates into a middle shape. Record the result in the rationale's "Synthesis decision" section: the base and why, what you took from each other candidate, and what you rejected and why.

## Phase C: Agree

Default: stop after synthesis. Show the usage sketch, the type sketch, and the rationale, then wait for sign-off before Phase D.

Skip the stop only when the invoker says to go straight through, for example "/architect, no checkpoint" or "design it and build it".

The sketch can ship as its own commit before the implementation, when the invoker wants commits. Planned breakage while the bodies are filled in is fine if the sketch said where it happens. For adversarial pressure on the design before implementing, run the **grill-me** skill on the synthesized sketch.

If the human pushes back on the shape, at the checkpoint or later, treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code, and pseudocode with logic. The synthesized sketch is the contract. Report each deviation from it instead of absorbing it silently. If a function needs a parameter the sketch didn't expect, decide which is true: the sketch was wrong, a requirement was missed, or the implementation is doing too much.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design. Fix the cause, which is the shape.

The signal is a repeated pattern, not a single instance. Tells:

- The same kind of workaround appears in unrelated code.
- Several unrelated edge cases each need a special-case branch.
- Types need escape hatches to compile: `any`, casts, or optional fields that are always set in practice.
- The code needs a lock where the sketch said the state wasn't shared.
- Callers must know the abstraction's internal rules to use it.
- Phase D produced two or more independent deviations of the same kind.

Use judgment. A few edge cases don't condemn an architecture. Some problems are complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Re-run Phase A over what has been built.
2. Redesign as if the new constraints had been known on day one.
3. Remove before you add. The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and run the candidates again.

## Outputs

Write the caller's usage first and derive the type sketch from it. For a small change, put the new types and signatures in one file. For larger work, give a module map plus the type definitions. The sketch goes into the repo as code with `not implemented` bodies.

The rationale ships with the sketch, shaped per [`references/rationale-template.md`](references/rationale-template.md), including the usage sketch and the synthesis decision. Put it where the repo keeps design docs. If the repo has no such place, put it in the PR description, or in chat when there is no PR.
