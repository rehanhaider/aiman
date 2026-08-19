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