# Methodology — Sewing, Reaping, and the Load-Bearing Words Problem

This file expands on the `Sewing and Reaping` framework introduced in the SKILL.md, the rules around AI prose, and the practical sub-techniques: finding the narrative kernel, sharing secrets, including failures, and protecting voice. The framework is distilled from a practitioner talk on developer-content strategy; "the practitioner" below refers to that source.

---

## Sewing and Reaping in detail

### Phase I — Sewing (the engineering)

**Goal:** Produce work worth writing about. Without this, the rest is shovelware.

What sewing actually looks like in practice:

- Following curiosity into niches that don't yet have an audience.
- Trying multiple approaches to the same problem (the practitioner's example: three different "ask user" tool implementations before one worked).
- Documenting failures as they happen — failed branches, abandoned PRs, comment threads where you reasoned wrong about a design.
- Iterating until the solution is *simple*. Simplicity is rarely the first answer; it's the destination.
- Continuing to sew even after gaining an audience. The trap most writers fall into is letting "reaping" eat all the time.

**The two-jobs reality.** High-quality technical content is essentially having two roles. The engineering work isn't a free byproduct; it's a parallel commitment. Don't promise content velocity that requires shortchanging the sewing.

**Authenticity test.** A blunt rule: if you wouldn't reach for this setup tomorrow morning unprompted, don't write about it. The practitioner's first post underperformed because it described a setup they didn't actually use. Readers can tell, even when they can't articulate why.

### Phase II — Reaping (the writing)

**Goal:** Turn the work into a story readers want to read AND that an AI engine wants to cite.

The phases are unequal in time. A post that took two days to write was usually backed by months of sewing. Don't compress the wrong half.

The reaping phase has three main sub-tasks:

1. **Find the narrative kernel** (most of the difficulty)
2. **Choose a structure** (relatively easy if the kernel is right)
3. **Write the prose** (mechanical once kernel + structure are clear)

Most writers who struggle are stuck on (1) but think they're stuck on (3).

---

## Finding the narrative kernel

A "kernel" is the one-sentence claim the article exists to make. Strong kernels have shape:

- **"X looks like A, but it's actually B."** (Reframing — usually the strongest pattern.)
  - Example: "Compaction looks like a memory-management problem, but the fix is actually a session-management problem."
- **"The obvious way to do X fails because Y; the working way is Z."** (Lessons-learned shape.)
  - Example: "The obvious way to build an 'ask user' tool — emit a structured JSON request — fails because the model never sees the schema. The working way is a system reminder injected between turns."
- **"We tried 1, 2, 3; only 3 worked, and here's why."** (Variation-grid shape.)
- **"The non-obvious thing about X is Y."** (Secret-sharing shape — see below.)

Weak kernels:
- "We built X." (Description, not insight.)
- "X is great." (Marketing, not knowledge.)
- "Here's how to use X." (Documentation, not story — write docs instead.)

### Talk to users

Identifying the kernel is iterative. The methodology's strongest practice: show drafts (or just kernel sentences) to 2–3 real users *before* writing. The example: a piece that started as "compact" got rewritten as "session management" because users repeatedly described their actual confusion in those words.

If the user has access to their audience — Slack, Discord, customer calls, support tickets, GitHub issues — encourage one round of "does this kernel land?" before they invest in drafting.

### The "secret"

The most-shared technical posts contain at least one secret — a non-obvious technical insight that other practitioners haven't yet realized is a problem worth solving. Examples:
- System reminders injected between tool calls in agent harnesses.
- Caching at the agent harness layer beating caching at the model layer.
- Why the obvious memoization story for React doesn't apply to compiler-managed components.

A secret has two qualities:
1. **Non-obvious** — readers in the same field haven't independently arrived at it.
2. **Transferable** — a reader can apply the insight to their own work, not just admire it.

If the kernel doesn't contain a secret, ask: *what did I learn the hard way that someone else hasn't yet?*

---

## Why we don't do AI prose

This is the rule that most distinguishes the methodology.

### Load-bearing words

Some words in technical writing carry precise meaning that can't be substituted without losing accuracy. Examples:

| Load-bearing word    | "Smoothing" replacement      | Loss                                                       |
| -------------------- | ---------------------------- | ---------------------------------------------------------- |
| compaction           | summarization, pruning       | Compaction is a specific algorithmic operation             |
| harness              | wrapper, framework           | Harness implies orchestration, not just abstraction        |
| idempotent           | repeatable, safe-to-retry    | Idempotent is a formal property; replacements are vibes     |
| backpressure         | slowdown, throttling         | Backpressure is bidirectional flow control                 |
| eventual consistency | eventually correct           | Specific guarantee in distributed systems                  |
| memoization          | caching                      | Memoization is function-result-based; caching is broader   |
| cardinality          | size, count                  | Cardinality is a specific mathematical concept             |
| Pareto frontier      | trade-off curve              | Frontier is the boundary of optimal trade-offs, not any curve |

When AI rewrites prose, it tends to substitute these. The rewrite reads smoother but is *technically wrong*. Engineering audiences notice; AI search engines that match exact technical terms also notice — and stop citing the article.

### What AI is allowed to do

| Task                    | AI         | Human        |
| ----------------------- | ---------- | ------------ |
| Engineering archaeology | ✅ AI does  | Human reads  |
| Outlining               | ✅ AI does  | Human edits  |
| Generating SVG diagrams | ✅ AI does  | Human reviews |
| JSON image specs        | ✅ AI does  | Human iterates |
| SEO/GEO/AEO checking    | ✅ AI does  | Human applies |
| First-pass scaffold of a structure | ⚠️ AI may | Human always rewrites |
| Final prose             | ❌ AI does not | Human writes |
| Voice                   | ❌ AI does not | Human owns |

The "throw-away draft" pattern: it's OK to ask AI for a first draft, but treat it as scaffolding. Rewrite it sentence by sentence. If you copy-paste, the post will read like AI wrote it — because it did — and your audience will react accordingly.

### Voice

A reader's trust in a technical writer comes from voice — the sense that a specific human, with specific experiences, is on the other side. AI prose is voice-flat by default. Recovering voice from an AI draft takes nearly as long as writing from scratch, but it's harder because you're working against the AI's flattening.

Practical rule: if the user's voice is already established (they have a blog, podcast, talks), skim a piece of theirs *before* drafting and explicitly mirror their cadence, sentence length, and idioms. If they don't have a voice yet, ask them to write the first 200 words themselves and use *that* as the voice anchor for the rest.

---

## The "simple isn't easy" principle

Simplicity is the destination of long iteration, not a starting state. The post that *describes* the simple final state without showing the iteration leaves the reader thinking the idea is obvious — and unmemorable.

Posts that win are usually shaped: "Here's the simple thing we ended up with. It looks obvious. It took us four months to get there. Here's why each of the not-simple intermediate states was actually worse."

That last part is what makes the simple final state feel earned.

---

## Including downsides and failures

Two reasons to do this, beyond credibility:

1. **More information.** What didn't work tells the reader what *not* to try in their own context. Often this is more valuable than what did work, because the failure modes are universal but the working approach may be specific to your environment.
2. **Trust calibration.** A piece that says "this approach has these limitations" is read as more credible than a piece that doesn't. Engineering audiences interpret missing limitations as either naïveté or marketing.

Concrete: in any deep-dive, make sure at least one H2 is explicitly about something that didn't work, has a hard limitation, or comes with a caveat. Not "Limitations" as a bullet list at the end — actual prose, with an example.

---

## Long-form vs short-form

The methodology has a strong preference for long-form articles over short-form social posts. The argument:

- **Twitter/X threads** force you to throw out the parts of the story that need development. The 280-char unit doesn't fit nuance.
- **LinkedIn posts** work for an enterprise audience but don't carry technical depth.
- **Long-form articles** let you develop the kernel, show the failures, include diagrams, cite sources, and produce something AI engines can ingest as a coherent argument.

This skill is calibrated for long-form. For short-form, use the long-form post as the source-of-truth and the short-form as a teaser linking to it.

---

## Multimedia: the 3-hour video pattern

The methodology also covers video, which the practitioner produces in ~3 hours end-to-end:

1. AI scans Slack and GitHub history to reconstruct activities.
2. AI generates a slide deck and rough script.
3. The author records a take.
4. The author edits *by script* (text-based editing tool like Descript or similar) — not by traditional timeline.

This skill is text-focused, but if the user wants to produce a companion video, point them at this pattern. The same engineering archaeology technique that produces the article research notes also produces the video script.

---

## Strategic context

Some practical observations from the methodology that are worth remembering:

- **Reach roughly tracks revenue.** For products with a community / developer audience, the reach of long-form technical content correlates with growth. Treat publishing as load-bearing infrastructure, not a hobby.
- **Sales enablement.** Enterprise-targeted content is read by sales teams and used in customer calls. Articles that help customers "reimagine their workflows" are higher-leverage than feature announcements.
- **The audience trap.** Once you have an audience, the temptation is to optimize for the audience instead of the work. This is why content from successful writers tends to decline over time — they stop sewing. Counter this by scheduling sewing time the way you'd schedule reaping time.
- **Niche is power.** Being weirdly specific about a narrow domain often makes you *the best in the world* at that thing. Don't generalize prematurely. The kernel "we tuned this one Postgres parameter and it changed our latency curve" beats the kernel "we improved our database performance".
