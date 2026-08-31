# Article Structures by Type

Pick the structure that matches what the user is writing. Each section gives the canonical scaffold, the SEO/GEO/AEO checkpoints baked in, and the "what makes this type work or fail" notes drawn from the methodology.

The default scaffold (long-form deep-dive) lives in `SKILL.md` § Mode 2. The structures below are variations.

---

## 1. Engineering deep-dive

**For:** A technical audience that overlaps with your stack. Goal is to share an insight worth their time.

**Length:** 2,500–4,000 words.

**Structure:**

```
1. Title — states the kernel ("Why caching at the harness beats caching at the model")
2. Hero image — SVG architecture diagram OR isometric tech illustration
3. Lede — 2–3 sentences setting up the problem; the kernel teased but not yet stated
4. Direct-answer paragraph — 40–60 words, kernel stated plainly, [data-speakable]
5. TL;DR — 3–5 bullets for scanners
6. Background — what was the world before this work; ≤1 H2 worth of context
7. The first thing we tried (and why it didn't work) — H2
8. The second thing we tried (and why it was almost-right) — H2
9. The thing that actually worked — H2 with the secret
10. Diagram of the working architecture — SVG inline
11. Numbers — benchmarks, latency tables, error-rate before/after
12. Caveats and limitations — H2
13. What we'd do differently next time — H2
14. FAQ — 3–5 question-phrased H3s
15. Sources — ≥2 authoritative citations
16. Author byline + updated date
```

**SEO/GEO/AEO touchpoints:**
- Title carries the kernel (SEO + GEO).
- Direct-answer paragraph (AEO snippet bait + GEO citation).
- Question H2s for failure sections (AEO).
- Numbers / benchmarks = original data (GEO citation magnet).
- Diagram with text-as-text in SVG (SEO accessible content + GEO entity coverage).

**Common failure modes:**
- Skipping the failures. Kills the credibility and the most-shared moments.
- Jumping to the architecture diagram before establishing why the obvious approach fails. Diagrams without motivation read as PowerPoint.
- Claiming the working solution was foreseen. Don't lie about the iteration. Engineering audiences prefer earned simplicity.

---

## 2. Tutorial / How-to

**For:** Reader wants to accomplish a specific task. They have less context than a deep-dive reader.

**Length:** 800–2,000 words.

**Structure:**

```
1. Title — task-focused ("How to add real-time presence to your Astro site in 30 minutes")
2. Hero image — screenshot of the end state OR a thematic illustration
3. Direct-answer paragraph — 40–60 words: what the tutorial does + prerequisites + outcome
4. Prerequisites — bulleted, with versions ("Node 20+, Astro 6+, ...")
5. Time estimate + cost estimate (HowTo schema fields totalTime + estimatedCost)
6. Steps — H2 per major phase, H3 per sub-step; numbered list inside each H2
7. Code blocks — every snippet runnable as-is; include filenames
8. Diagram of the final architecture — SVG
9. Verification — how the reader knows they did it right (commands to run, output to expect)
10. Common errors and fixes — H2 with H3 per error
11. What's next — links to deeper content
12. FAQ — 3–5 question-phrased H3s
13. Sources — ≥2 authoritative citations (official docs preferred)
```

**SEO/GEO/AEO touchpoints:**
- HowTo schema with `totalTime`, `tool[]`, `supply[]`, `estimatedCost: MonetaryAmount`, `step[]`.
- Each step is a separate `HowToStep` with `name` + `text` + optional `image`.
- Verification + common errors qualify for AEO ("how do I check X works", "why does Y error appear").
- Note: Google removed HowTo rich results from SERP in late 2023, but Bing + AI engines still parse the schema. Ship it.

**Common failure modes:**
- Pasting code without filenames or context. Forces the reader to reverse-engineer where each block goes.
- Skipping the "how do I know it worked" step. Tutorials that don't verify leave the reader uncertain.
- Hard-selling a product mid-tutorial. Push it in the "What's next" section instead.
- Missing cleanup. Anything that costs money or persists (cloud resources, daemons) gets a Cleanup section — and a warning where the default surprises ("`cdk destroy` will NOT delete the bucket; the removal policy is Retain").

**Craft rules for the body** (full detail in `voice-and-style.md`):
- Show the visible workflow (numbered list of the whole path) before the first step of any long tutorial.
- One step, one code block: a sentence of intent before, the expected result or verification after ("You should see...").
- Placeholders like `<bucket-name>` for user-specific values — never plausible fake literals.
- Lettered sub-steps for console/UI walkthroughs ("a) Click **Instances**...").
- For course-style series: link prerequisites to the earlier lessons, carry `series`/order metadata in frontmatter, and end with a link to the next lesson.

### 2a. Snippet (micro-tutorial)

**For:** One focused problem or small tool setup — "make X work in WSL2", "run Jupyter from the terminal".

**Length:** 300–800 words. As short as accuracy allows.

**Structure:**

```
1. Title — the exact task ("Fix Git authentication prompts in WSL2")
2. One or two short paragraphs naming the scenario or problem — no hero required
3. Optional prerequisites (only if non-obvious)
4. Action headings ("Install X", "Configure Y", "Run Z")
5. Commands with a short explanation before and after each
6. Verification step
```

**What makes it work:** speed to the fix. No TL;DR, no FAQ, no background section — the direct-answer paragraph and the first command are nearly adjacent. Snippets earn disproportionate search traffic because they match a query exactly; don't inflate them into full tutorials.

---

## 3. Postmortem / Failure case study

**For:** Reader who's run into a similar failure or wants to learn from yours. Highest-trust article type when done well.

**Length:** 1,500–3,000 words.

**Structure:**

```
1. Title — names the failure plainly ("Why our deploy hung for 3 hours" / "How we lost 6h of writes to a config typo")
2. Hero image — timeline graphic OR an architecture diagram with the failure point highlighted
3. Direct-answer paragraph — 40–60 words: what failed, what was the impact, what was the root cause
4. Timeline — H2 with timestamps (UTC), each entry one or two sentences
5. What we thought was happening — H2; the wrong hypothesis
6. What was actually happening — H2; the root cause, with a diagram
7. The fix — H2; what we changed; why it works
8. What we changed about our process — H2; the prevention layer
9. What we got wrong about our response — H2; honesty section
10. Followups still open — H2; what's still TODO
11. Acknowledgments — by name; pages link to author profiles
12. Sources — runbooks, docs, related incidents
```

**SEO/GEO/AEO touchpoints:**
- Direct-answer paragraph is high-citation density (specific numbers, named systems).
- Timeline with timestamps = highly extractable structured data for AI engines.
- Architecture diagram = SVG with text-as-text for indexing.
- Linking to your runbooks / docs strengthens internal-link graph.

**Common failure modes:**
- Sanitizing too much. The post becomes a marketing piece about how reliable your team is. Reader can't extract lessons.
- No timeline or vague timestamps. Reduces extractability and credibility.
- Blame language. Postmortems are about systems, not people. Use "the on-call engineer" not names.
- No "what we got wrong about our response" section. Even good responses have lessons.

---

## 4. "Day in the life" / Workflow piece

**For:** Reader curious about how someone uses a tool / works in a role. Strong sales-enablement content.

**Length:** 1,200–2,500 words.

**Structure:**

```
1. Title — names the role + the workflow ("A day building agents at Anthropic" / "How I ship features as a solo founder")
2. Hero image — illustrative (your desk, your screen, an isometric scene)
3. Lede — 1 paragraph framing
4. Direct-answer paragraph — 40–60 words: what's distinctive about this workflow
5. Setup — H2; what's on your machine, in 60 seconds
6. The morning — H2; first task, with screenshots or short video clips
7. The hard problem — H2; the part of the day that's actual work
8. Tools at work — H2; what you reach for when, and why (don't read like an ad)
9. The end-of-day reflection — H2; what worked, what didn't
10. The 3-hour video pattern (if applicable) — sidebar; how the article was made
11. FAQ — common questions about this workflow
12. Sources / Further reading
```

**SEO/GEO/AEO touchpoints:**
- Authentic voice is the primary signal — readers come for the human, not the optimization.
- Each tool mention links to docs / homepage.
- Screenshots have descriptive alt text.
- The workflow itself is the original-data signal that GEO engines value.

**Common failure modes:**
- Sounds like a sponsored post. The methodology's authenticity check is non-negotiable here.
- Generic ("I use my IDE, then I run my tests"). Be specific. Names of files. Names of slack channels. Names of the hard problem.
- Skipping the hard problem. The most-shared sections are usually the parts where things didn't go smoothly.

---

## 5. Comparison post (X vs Y)

**For:** Reader at the bottom of the funnel choosing between two products / approaches. High commercial intent.

**Length:** 1,500–3,000 words.

**Structure:**

```
1. Title — names both options ("Postgres vs SQLite for embedded apps")
2. Hero image — a 2-column comparison illustration
3. Direct-answer paragraph — 40–60 words: when to pick X, when to pick Y, the dividing line
4. Quick-reference comparison table — side-by-side, dimensional
5. When X is the right choice — H2 with concrete scenarios
6. When Y is the right choice — H2 with concrete scenarios
7. The dimensions that matter — H2 per dimension (latency, cost, ergonomics, etc.)
8. The dimensions that don't matter as much as people think — H2; counter-conventional wisdom section
9. Edge cases and pitfalls — H2
10. FAQ — including "what if I need both"
11. Sources — official docs for both, benchmark sources
```

**SEO/GEO/AEO touchpoints:**
- Comparison table is gold for AEO (extractable, formatted for snippets).
- Specific scenarios in each "when" section qualify for long-tail "is X better than Y for use case Z" queries.
- Be honest about your bias if you have one — note the affiliations / experience that color the comparison.

**Common failure modes:**
- Hatchet job. "X is awful, Y is amazing" reads as marketing. Honest comparisons are more linkable.
- Comparing on the wrong dimensions. Make sure the dimensions match what readers actually care about, not what's easy to benchmark.
- Pre-launch self-comparison. Don't write "your product vs competitor" before your product is in market — you'll over-promise and under-deliver.

---

## 6. Launch / Announcement

**For:** Reader hears about a new feature/product for the first time. Lowest-trust article type — readers expect marketing.

**Length:** 800–2,000 words.

**Structure:**

```
1. Title — names the thing + the headline benefit ("X now supports Y, here's how")
2. Hero image — product screenshot OR an isometric illustration of the feature in use
3. Direct-answer paragraph — 40–60 words: what's new, who it's for, how to get it
4. The problem this solves — H2; user-grounded, not feature-grounded
5. How it works — H2; with a diagram
6. Examples — H2 with sub-sections for 2–3 use cases
7. What didn't work / what we considered and rejected — H2 (this section is what makes the launch credible)
8. Limitations — H2; honest list
9. Roadmap — H2; what's coming next
10. How to start using it — H2; concrete steps
11. FAQ
12. Sources / further reading
```

**SEO/GEO/AEO touchpoints:**
- Title should not lead with brand name (deprioritized in GEO).
- Examples should each link to a more detailed tutorial (internal-link graph).
- Limitations section is the AEO-friendly part — readers ask "is X able to do Y" and limitations sections answer those.

**Common failure modes:**
- Pure feature list. No user grounding. Reader bounces.
- No "what didn't work" section. Reads as glossy marketing; AI engines deprioritize.
- Promises ("free forever", "always"). Boxes you in if pricing changes — see `seo-expert` § Pricing pitfalls.

---

## 7. Glossary / Concept explainer

**For:** Reader looking up what a specific term means. High navigational intent, low time-on-page expectation.

**Length:** 400–1,200 words.

**Structure:**

```
1. Title — "What is X?" or "X (concept), explained"
2. Hero image — illustration or simple SVG diagram
3. Direct-answer paragraph — 40–60 words; the entity-defining sentence + canonical context
4. "X is..." definition sentence — single sentence, plain English
5. Why X exists — H2; the problem it solves (lead with this, not history)
6. How X is used in practice — H2 with concrete examples
7. X vs the familiar alternatives — H2; compare against what the reader already knows
8. When to use X (and when not to) — H2; practical selection guidance with opinions
9. Common misconceptions — H2
10. What to try next — closing pointer (a command, a tutorial link), not a summary
11. Sources — Wikipedia, papers, official references
```

**SEO/GEO/AEO touchpoints:**
- `DefinedTerm` schema — turns the page into a citable entity for AI engines.
- Direct-answer paragraph is the entire post's value for many readers; make it bulletproof.
- "X vs related terms" section captures disambiguation queries.
- Anchor IDs on each term let other articles deep-link to specific definitions.

**Common failure modes:**
- Padding. Glossary entries should be as short as accuracy allows.
- Circular definitions ("X is the process of doing X-ing"). Define using terms simpler than the term itself.
- No disambiguation. Many technical terms have homonyms across fields — clarify which one you mean.

---

## Choosing the type

| User says...                                    | Type                  |
| ----------------------------------------------- | --------------------- |
| "I want to write about how we built X"          | Engineering deep-dive |
| "I want to teach someone to do X"               | Tutorial              |
| "Quick how-to for one specific problem"         | Snippet               |
| "We had an outage / failure"                    | Postmortem            |
| "What's it like to work as a Y"                 | Day in the life       |
| "X vs Y, which should I use"                    | Comparison            |
| "We just shipped X"                             | Launch                |
| "What is X" / "explain X"                       | Glossary              |
| "I want to share what I learned"                | Engineering deep-dive |
| "How I use X every day"                         | Day in the life       |

When the user's intent doesn't fit cleanly, ask. Hybrid types exist (a launch with a deep-dive embedded; a postmortem that's also a tutorial); pick the dominant frame and lean into it.
