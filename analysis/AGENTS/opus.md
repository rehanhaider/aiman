# Q1
can you look through my history with models like fable, opus, and gpt-5.6-sol in claude code and codex on this machine to see what the most common mistakes are? want to make sure we optimise to steer away from those.

I want you to break down the most common failure modes and how often each model hits them

# Opus

**Biggest lever, costs nothing: abandon the turn after the second failed correction.** Once you correct once, the next turn is a correction 28.2% of the time vs 11.8% otherwise — 2.4×. Every long profanity chain in your history is a spiral you pushed through instead of restarting.

---

## The uncomfortable finding first

**Your prompting was not the cause.** I tested 2,667 prompt→outcome pairs. Base correction rate 14.2%. The best predictor got to 19.8% — and that one ("you gave a negative constraint") is reverse causality: you write "don't X" *because* you're already correcting.

| Prompt shape | correction next |
|---|---|
| bare "ok / go ahead / pls fix" | **10.3%** ← *below* base |
| delegated to subagents | **7.3%** (n=41) |
| long detailed brief (>800 chars) | 17.9% |
| open-ended "what's pending?" | 18.1% |

Writing longer, more careful prompts did not help you. Short ones did slightly better. So the fix is not "prompt better" — it's session hygiene and mechanical guardrails.

---

## Tier 1 — Behavioural (free, highest impact)

1. **Two-strike rule.** Second correction on the same point → `/clear`, restate the goal fresh. Do not keep arguing. (28.2% spiral)
2. **Cap build sessions at ~15 turns.** Correction rate: 9.9% at turns 1–5 → 15.1% at 6–15 → **19.1% at 16–30**. Your median session is only 4–8 turns, so this costs you almost nothing — it's the p90 sessions (33+ turns) doing the damage.
3. **Never let it self-report "done".** Every "did you even test it" correction came after a claimed completion. Ask for the artifact — screenshot, exit code, URL — not the summary.

---

## Tier 2 — Guardrails you don't have yet

You have `includeCoAuthoredBy: false` ✅ and exactly **one** hook (SessionStart). No `permissions.deny` rules at all. That's the gap.

| Guardrail | Kills | Corrections it would have prevented |
|---|---|---|
| `PreToolUse` deny on `npm/pnpm install <pkg>` | silent dep adds | 7 |
| `PreToolUse` deny on `gh pr create` unless asked | unrequested PRs | ~6 |
| `Stop` hook: fail if git tree dirty or TODOs added | stopped-early | 26 |
| `PostToolUse` on `package.json` writes → diff review | wrong-library drift | 27 |

These can't be ignored by the model. Instructions can.

---

## Tier 3 — Two real documentation bugs I found

This is the part that isn't the models' fault:

1. **`emcp-crm/AGENTS.md` says "shadcn-style components on headless Base UI instead."** You corrected "why is there `@base-ui/react` when I specifically told you shadcn" — but the repo's own spec told it to do exactly that. The model followed your docs. **Fix the file, not the prompt.**
2. **"No backward compatibility" is in `naqid/AGENTS.md` only as a fact** — "there are no production users" — never as a directive. You corrected this 10 times. The model read a fact and didn't infer a rule.

**Rewrite pattern:** state facts as prohibitions.
- ❌ "There are no production users."
- ✅ "Never write a migration, compat shim, or `V1`/`V2` branch. There are no users. If you think one is needed, stop and ask."

---

## Instructions that would actually have worked

Your current rules are unenforceable because they aren't checkable. Make them countable:

| Instead of | Write |
|---|---|
| "be concise" | "Max 5 lines before the answer. Detail goes below a `---`." |
| "don't use jargon" | "Never use a proper noun you haven't defined in the same message." |
| "don't do unrequested work" | "List every file you will create or delete, one line each, before touching any." |
| "give me a recommendation" | "If you write 'the tradeoffs are' — stop. Pick one, state it in one line, then justify." |

---

**Next:** pick one — I'll write the `permissions.deny` + `Stop` hook block into `~/.claude/settings.json`, or fix the `emcp-crm/AGENTS.md` shadcn contradiction. The AGENTS.md fix is smaller and removes a bug that is actively misleading every model you run there.

# Q2 (2026-09-24, Opus 5.5)
Can you perform an audit of the various failure modes of my prompts with Fable 5.1 and Opus 5.5? Look through my history with fable 5/5.1, opus 5.5, and gpt-5.6-sol in claude code and codex on this machine to see what the most common mistakes are. Break down the most common failure modes and how often each model hits them.

# Opus 5.5

**Fable 5.1 is the model you correct most often: 13.7 real mistakes per 100 of your messages. Most of them are about how it explains things, not what it builds.** Opus 5.5 is the lowest at 5.2 per 100, but that comes from only three days of use (134 messages), so it is an early reading.

## Method

- **Sources:** 5,035 Claude Code transcripts (25 Aug – 24 Sep; older transcripts are no longer on disk) and 1,061 Codex rollouts (Apr – Sep, including archived ones).
- **What counts as your message:** only messages you typed. Excluded: sub-agent threads, the Codex `guardian` auto-reviewer, `codex exec` runs launched by forge, task notifications and command output. Codex resumes, which rewrite the same session twice, are deduplicated by text and timestamp.
- **How mistakes were found:** a keyword filter flagged 839 of your messages as possible pushback. Seven classifier agents read each flagged message next to the model's previous reply and kept only the ones where you corrected something the model did. That left 480 (57%). Each one got one primary category from a fixed list of 13, plus a severity score: 1 = irritation, 2 = rework, 3 = damage or a profane escalation.
- **Not comparable:** interrupt rate. Claude sessions run through T3 Code do not record Esc interrupts.
- **Working data:** `/tmp/model-audit/` (`genuine.json` has file, timestamp and a note for every mistake).

## Headline

| Model | Your messages | Sessions | Real mistakes | Per 100 messages | Severity 3 | Signature |
|---|---|---|---|---|---|---|
| Fable 5.1 | 1,472 | 70 | 202 | **13.7** | 44% | explains in jargon and walls of text; repeats corrected mistakes |
| Fable 5 | 125 | 19 | 16 | 12.8 | 38% | over-complicated designs |
| GPT-5.6-Sol | 2,310 | 158 | 231 | 10.0 | 37% | communication + wrong design approach, then misstates docs |
| Opus 5 (reference) | 294 | 48 | 24 | 8.2 | 50% | wrong approach, "done" without proof |
| Opus 5.5 | 134 | 13 | 7 | **5.2** | 0% | says UI is "verified" when it does not match the mockup |

Same project, same period (navinier, since 2 Sep): Fable 5.1 **16.1** per 100 (1,153 messages), Sol 12.1 (248), Opus 5 4.5 (44), Opus 5.5 2.7 (73). On other projects Fable 5.1 drops to 5.0. So it struggles most in navinier's long spec and design sessions. 166 of its 202 mistakes are in navinier, and one session alone has 42.

## Failure modes by model (share of that model's mistakes, primary category)

| Failure mode | Fable 5.1 (202) | Fable 5 (16) | Sol (231) | Opus 5.5 (7) |
|---|---|---|---|---|
| Communication: jargon, undefined terms, walls of text, menus | **38%** | 6% | **24%** | 1 |
| Wrong approach: over-engineered or wrong design | 17% | **44%** | 20% | 0 |
| Ignored an earlier instruction | 11% (22% incl. secondary) | 12% | 13% | 1 |
| Misread the ask | 9% | 25% | 12% | 1 |
| Process: skimmed specs, didn't check state, wrong tool | 7% | 0 | 6% | 1 |
| Early stop / needless question / deferral | 5% | 6% | 5% | 0 |
| Scope creep | 4% | 0 | 3% | 0 |
| False "done" / "verified" | 3% | 0 | 5% | **2** |
| Fabrication: misstated docs or code | 1% | 6% | 6% | 0 |
| Unauthorized external action | 2.5% (all severity 3) | 0 | 1% | 0 |
| Broke something / workaround | 1% | 0 | 4% | 1 |

### Fable 5.1
1. **Communication (76).** You asked for plain explanations. It answered with jargon ("calibration registry", "handoff schema", V1–V6 labels) and "ten pages of prose" where you wanted a worked scenario, a diagram or an HTML walkthrough. After being told, it kept doing it. Most cases are 2–5 Sep in navinier design sessions.
2. **Over-complicated structure (34).** It turned three simple calculators into a module tree, ran regex over free-form LLM text, and re-proposed gating it had already been told was hacky.
3. **Repeat violations (45 with secondary).** Worktrees after "use the checked-out branch" (4×). `Refs` instead of `Closes` (3×). Unspecced features after "no spec, no build". Calling the engine directly after "everything goes through the orchestrator".
4. **Skimming specs (15 process + 3 fabrication).** "Skimmed with grep", "hadn't read the full spec", guessed behaviour instead of reading it.
5. **Destructive actions (5, all severity 3).** It deleted remote branches when you asked for local cleanup, then called it harmless. It resolved review threads without asking, and opened a pull request editing AGENTS.md that nobody asked for. Contract rule 5 already forbade all three.

### GPT-5.6-Sol
Communication and wrong approach lead again (44%). Misreading the ask is 12%. Sol misstates docs more than any other model here (fabrication, 14). Rate before and after the 19 Aug contract: **9.2 → 11.0 per 100**. The mix shifted: wrong approach fell 30 → 16, while ignored instructions rose 12 → 17 and fabrication rose to 8. The contract changed which mistakes you see, not how many.

### Fable 5 (16, 25–30 Aug)
Its design proposals kept getting rejected: model-config tables, tier fields, agent factories. It also misread which document governed, treating v0.6 markdown as the spec over the HTML you meant.

### Opus 5.5 (7, 22–24 Sep)
No severity-3 mistakes. Two are "done and verified" UI that did not match the approved mockup (wrong logo, pink page, wrong icons). One used static screenshots as evidence for an interaction change. One raised Gradle memory to get a build passing after you had set it deliberately. Its gap is treating "I looked at it" as verification instead of "it matches the reference". It has too few messages yet to trust the rate.

## Failure modes in the prompts and instructions themselves

1. **A rule points at a skill that does not exist.** Rule 1 of the deployed `~/.claude/CLAUDE.md` says "Always use the /my-voice skill". `~/.claude/skills/` has forge, grill-me, pr-review, svg-animations, synced and unslop. There is no my-voice there, and none in this repo. Every session starts with an instruction it cannot follow. (Separately, `snapshots/claude/CLAUDE.md` has an uncommitted edit that drops rule 1 entirely. The snapshot and the deployed file disagree.)
2. **A skill and a repo contradict each other, and the skill wins.** navinier `AGENTS.md:60` requires `closes #<n>`. `skills/forge/SKILL.md:173` says "Use `Closes #<n>` only when the merge should close a GitHub issue". navinier tracks work in Linear, so the model wrote `Refs`, and you corrected it three times. Worktrees were the same story: `AGENTS.md:20` forbids them, forge used them, and you corrected it four times until `678b9e1` on 16 Sep.
3. **Style rules in prose don't hold for Fable.** "Use plain language", "define terms" and "never use an undefined proper noun" have been in CLAUDE.md since 1 Sep. Fable 5.1 still produced 76 communication failures under them. The rules are in the right place. Fable 5.1 does not follow them in long design threads.
4. **Project rules that live only in chat.** "No spec, no build", "orchestrator invariant", "no regex on LLM output", "no backcompat on the provider switch": each was said in chat, then broken in a later session. None of them is in navinier's `AGENTS.md` as a directive.
5. **Marathon sessions.** Fable 5.1's correction rate is 10% of messages for turns 1–15 and 16–17% after turn 15. Sol's goes from 6% in turns 1–5 to 10–13% later.
6. **Pushing through a spiral.** Right after a real correction, your next message is another correction 33% of the time with Fable 5.1 (11% otherwise) and 28% with Sol (9% otherwise). Repeating the correction rarely fixes it on the next turn.

## What to change, ranked by mistakes it would have prevented

1. **Send navinier explanation and design conversations to Opus 5.5 and keep Fable 5.1 for bounded implementation.** This targets the 76 communication and 34 approach failures, more than half of Fable 5.1's total. The evidence is 16.1 vs 2.7 per 100 on the same project. The Opus 5.5 sample is small, so re-check after about 500 messages.
2. **Fix the forge `Closes` line.** It should say: "Use `Closes <issue-id>` for the tracker in use (GitHub `#n` or Linear `NAV-n`), unless the issue must stay open." Also align navinier `AGENTS.md:60` with it.
3. **Fix or remove rule 1 in `~/.claude/CLAUDE.md`.** Either create the my-voice skill or point the rule at `unslop`, then commit the snapshot so it matches the deployed file.
4. **Promote the four chat-only navinier rules into navinier `AGENTS.md` as prohibitions.** For example: "Never add a module or feature that has no spec section. Stop and ask."
5. **Block the destructive git actions mechanically.** Add a `PreToolUse` deny for `git push --delete`, `git push origin :*` and `gh pr create` unless the prompt asked for them. Rule 5 already says this in prose, and Fable 5.1 broke it anyway.
6. **Two strikes, then start over.** After the second correction on the same point, start a fresh session with the constraint in the first message. Keep build sessions to about 15 turns.
7. **For Opus 5.5:** change contract rule 7's "verify" to "compare against the named reference (mockup, spec section) and state each difference". For interaction changes, the evidence is a recording, not a screenshot.
