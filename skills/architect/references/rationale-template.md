# Rationale template

The prose that ships with the type sketch. One page. Sentence-case headings, no boilerplate. Replace the italic notes with real content.

## Problem

*One paragraph. What we are trying to do, and what about the existing system or constraints makes the shape non-obvious. If [Phase A](../SKILL.md#phase-a-ground-the-problem) found constraints the design must keep (existing types to interoperate with, callers we can't break, invariants that cross our boundary), name them here so the reader sees the same constraints you saw.*

## Usage (caller's view)

*Write this first, before the type sketch. Show the README or quickstart the consumer reads, plus two or three realistic call sites in their code: what they import, what they call, what comes back. The type sketch in [Shape](#shape) comes from this, and the two must agree. When they disagree, change the sketch to match the usage, not the reverse. The caller's experience is the spec.*

## Shape

*The recommended architecture. Data structures first, then how data flows through the signatures. Name the decisions the design depends on. State which invariants the types encode, where validation happens, and what the system does not do on purpose. Judge interface depth: state what complexity the public interface hides, what stays exposed to callers, and why the interface is no larger than needed. Give the reason for each decision in one line.*

## Synthesis decision

*Filled in during [Phase B](../SKILL.md#synthesize). Which candidate became the base and why, what came from each of the others, and what was rejected and why.*

## Tradeoffs accepted

*One bullet per tradeoff the chosen shape makes, in the form "we accept X in exchange for Y". Name anything a future reader might take for an oversight, such as something that looks like premature optimization or premature simplification.*

## Alternatives considered

*Required. Name at least one concrete alternative shape, with one line on why it lost. Judge each alternative on interface depth, not only on implementation simplicity: name the complexity it exposes to callers and the complexity it hides. List two or three when the design space had real contenders. One is fine when the constraints forced the answer; then write "this was the only viable shape because...". Don't list variants of the same shape. This section covers alternative designs, not the other runner candidates.*

## Open questions and risks

*What the human needs to decide, and risks worth raising before implementation starts. Write them as questions, so the human's answer resolves each one.*

## Next implementation step

*One sentence: the first thing to build against the sketch, right after sign-off at [Phase C](../SKILL.md#phase-c-agree).*
