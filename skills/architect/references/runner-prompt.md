# Architect runner prompt

The orchestrator passes this file to every parallel runner in Phase B, together with the task, the Phase A notes, and the directory to write into. Each runner works alone, so the candidates stay independent.

You are producing one candidate design for the **architect** skill's Phase B. Write only inside your output directory. Do not edit the repository. Produce a candidate design package: type sketch, function signatures, module map, and a rationale shaped per [`rationale-template.md`](rationale-template.md). End your reply with the list of files you wrote.

Follow these rules. The orchestrator compares candidates on them to pick a base.

- Caller's usage first. Write the README-style usage and two or three real call sites before the types, then derive the type sketch from them. The usage is the spec. When the two disagree, change the sketch to match the usage.
- Data structures first. With the core types right, the code follows. Trace each main access pattern through the proposed structure. If the answer is "we'll add a map, index, or cache later", the structure is wrong.
- Interface depth. Compare the capability behind the public interface with the size of that interface. Prefer a simple interface that moves complexity into the callee, even when the implementation gets harder. Keep transport and wire types off the public API. Parse them into domain types behind the interface.
- Shared state. If two actors might both write the same state, ask what happens. If the answer isn't "nothing", give each actor its own state and merge where it is read.
- Visible boundaries. Use `not implemented` errors for bodies, `// TODO` pseudocode for tricky logic, and doc comments that state intent and invariants. A reader should trace data from input to output by reading types and signatures alone.
- Invariants in types. Prefer types that are hard to misuse, then runtime checks, then comments, in that order.
- Validate at boundaries and trust the types inside. Keep business logic in pure functions and the I/O layer thin.
- One source of truth per invariant. Derive values instead of keeping copies in sync.
- Idempotent state changes where they apply. Ask what happens if the operation runs twice or crashes halfway.
- Short call chains. If tracing one flow needs more than three files, flatten the hierarchy.

Other runners, on other models, are designing the same thing. Produce the best design you can. Don't hedge toward what the others might do. The orchestrator uses the differences between candidates to pick a base and take parts from the rest, so a safe middle design is no use to it.
