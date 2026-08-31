# The value test

Most copy fails on one quiet failure: the claim is true, the claim is grammatical, and the claim says nothing. *Cloud, security, AI. One delivery.* checks every box that has a checkbox. The reader still walks away with no information.

This document is the rubric for catching the void. Use it on every claim, every heading, every section, every email subject line.

## The So What ladder

For every claim, ask *so what?* three times. Each rung adds information the reader can act on.

### Example: a feature claim

| Rung           | Claim                                                                     |
| -------------- | ------------------------------------------------------------------------- |
| 0. Category    | Powerful integrations.                                                    |
| 1. Mechanism   | Pulls tickets from Jira, GitHub, and Linear.                              |
| 2. Outcome     | Pulls tickets from Jira, GitHub, and Linear into one queue.               |
| 3. Magnitude   | Pulls tickets from Jira, GitHub, and Linear into one queue, in 30 seconds.|

Rung 0 reads as marketing. Rung 3 reads as a product update worth scrolling for.

### Example: a security claim

| Rung           | Claim                                                                     |
| -------------- | ------------------------------------------------------------------------- |
| 0. Category    | Enterprise-grade security.                                                |
| 1. Mechanism   | SOC 2 Type II audited yearly. Data encrypted in transit and at rest.      |
| 2. Outcome     | Audited yearly, retained for 7 years, every change reversible for 30 days.|
| 3. Magnitude   | Audited yearly. 14 controls, 0 findings in our last audit. Reversible for 30 days.|

A reader at rung 3 can predict what shows up in a buying conversation.

Climbing to rung 3 takes effort and sometimes proof. When proof is missing, settle at rung 2. Skip rung 0 entirely.

## The Capability, Mechanism, Result triplet

Every section of marketing or product page copy benefits from the triplet. Spell each out.

- **Capability:** what the product can do, in a single verb phrase.
- **Mechanism:** how it does it, in plain technical terms.
- **Result:** what the user gets, in a unit the user already cares about.

### Worked example

- **Capability:** Drafts replies to support tickets.
- **Mechanism:** Reads the ticket, the customer history, and the last 30 days of resolved tickets, then writes a draft in the agent's voice.
- **Result:** First-reply time drops from 6 hours to 90 seconds. Agents close 40% more tickets a day.

Pulled together: *Reply to support tickets in 90 seconds, with a draft already written. The draft reads your customer's history and the last 30 days of resolved tickets, then matches your team's voice. Agents close 40% more tickets a day.*

The capability is the heading. The mechanism is the proof. The result is the reason to care.

## The three bars

A claim earns its spot when it clears all three bars.

1. **Factual.** The claim is true today. No future-tense aspiration disguised as present-tense capability. (*We are launching* is honest. *We let you* before the feature ships is not.)
2. **Falsifiable.** A skeptical reader can imagine the test that would prove the claim wrong. *Fast* fails. *Under 200 ms p95* passes.
3. **Felt.** The claim moves the reader, because it sits in a unit they care about. *40% more tickets a day* is felt. *Higher throughput* is not.

When a claim clears only one bar, rewrite. When it clears two, climb one more rung. When it clears all three, ship it.

## Decorative copy. Cut on sight

The patterns below show up everywhere. Each is a tell that the line is decoration, not information.

### 1. The buzzword stack
*Cloud, security, AI. One delivery.*

Each noun is a market category. The stack tells the reader nothing about what the product does, for whom, or with what result. The right move is to name the friction the product removes — usually a coordination cost, an audit risk, or a hand-off failure between teams.

Rewrite: *Cloud, security, and AI engineers ship together. The security review stays in lockstep with the architecture; the AI work never outruns the controls.*

Avoid reaching for monetary language (*one bill, one invoice, one charge, one payment*) in the rewrite. Money belongs on the pricing page. In a hero, it reads as crude and answers no real customer pain — *so what if it's one bill?* If the real benefit of consolidation is fewer vendor hand-offs or no finger-pointing during an audit, name that friction.

#### Decorative buzzwords vs. category markers

Not every buzzword is decoration. A buzzword that names a real, audience-recognised product category — and points at a differentiator your team actually has — does work the plain version cannot.

- *Cloud, security, AI* is decorative. Each word is a market label, generic enough to apply to a thousand vendors.
- *Agentic security testing* is a category marker. To a CTO who reads vendor pages weekly, it signals "AI-agent techniques applied to penetration testing" — meaningfully different from *continuous pentesting*, which is a commodity many vendors offer.
- *Custom AI products* and *Production AI agents* point at different offerings, not the same thing dressed up two ways. The first signals tailored, high-touch work; the second signals ready-to-ship engineering. Specificity is not a tie-breaker when the words carry brand positioning.

Before stripping a buzzword to plain language, ask three questions.

1. Is the buzzword a recognised name for a real category in this audience's vocabulary? *MLOps, GitOps, agentic, RAG, vector search, observability, FinOps* often qualify. *Powerful, intelligent, modern, seamless* never do.
2. Does the audience use this term to shortlist vendors or navigate the market? Technical buyers often do; consumers usually do not.
3. Is the differentiator real? A buzzword that names a capability your product actually has earns its spot. A buzzword that inflates a commodity capability does not.

When all three answers are yes, keep the buzzword. When any is no, deflate.

### 2. The capability adjective
*Powerful. Robust. Scalable. Seamless. Intelligent.*

These words feel like value and carry none. *Powerful* describes nothing the user can picture. Replace with a number or a verb.

- *Powerful search* becomes *Search across 1.2 billion records in under 300 ms*.
- *Scalable architecture* becomes *Handles 50,000 concurrent users on a single tenant*.

### 3. The category claim disguised as a benefit
*The modern way to manage projects.*

The reader still does not know what the product does or how it changes their day. The category is restated. Rewrite around a single change: *Cut project meetings by 6 hours a week. One status doc, auto-updated.*

### 4. The internal milestone
*We've redesigned our editor. We are excited to announce our new dashboard.*

The company is celebrating. The user came for a problem. Reframe to the user's outcome: *Edit on touch devices without the lag. Reports open in one click.*

### 5. The hedged superlative
*One of the most trusted platforms in the industry.*

The qualifier (*one of*) admits the claim has no anchor. If the proof exists, name it (*Trusted by 14 of the Fortune 100*). If it does not, cut the claim.

### 6. The empty trinity
*Faster, smarter, simpler. Built for the way you work.*

Three adjectives in a row are a red flag. Pick the one the user cares about most and prove it with a number, a name, or a comparison.

## The audit ritual

When you receive a page of copy to review, run it through this ritual before suggesting edits.

1. **Mark every claim.** A claim is any sentence that promises something to the reader. Underline them.
2. **Run the So What Test.** For each claim, ask *so what?* once. If the answer is missing within one sentence, the claim has failed the test.
3. **Identify the rung.** Tag each failed claim with the rung it currently sits at (0, 1, 2, or 3) and the rung it should reach.
4. **Find the proof.** For every claim you want to push to rung 2 or 3, search the source material for a number, a name, a customer story, or a metric. If none exists, ask the team for it before rewriting.
5. **Rewrite or cut.** Claims that cannot be elevated and are not loadbearing get cut. The page reads better with five sharp claims than fifteen vague ones.

## A side-by-side gallery

Each pair below is built from a real marketing page in the wild.

### Hero

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| The future of customer support.         | Reply to support tickets in 90 seconds. The draft reads your customer's history first. |
| Powerful insights for modern teams.     | See which campaign drove every dollar, by day, region, and SKU.  |

### Security block

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Built with security at the core.        | SOC 2 Type II, audited yearly. Data encrypted in transit and at rest. Reversible for 30 days. |
| We take privacy seriously.              | We hold customer data for 90 days, then purge it. You can export or delete at any time. |

### Integrations block

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Connects with the tools you love.       | Two-way sync with Jira, GitHub, Linear, Slack, and Notion. Setup in 30 seconds. |
| Powerful API.                           | REST and GraphQL APIs, 10,000 requests per minute, 99.95% uptime over the last 12 months. |

### Pricing

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Plans that scale with your business.    | Pay per active reviewer. Start at $0 for 3 seats. Scale to 50,000 with one toggle. |
| Simple, transparent pricing.            | Every plan includes SSO, audit logs, and 24x7 support. No upsell tiers. |

## Final pass

When the copy reads like it could appear in any of your competitor's funding announcements, it has failed the value test. The fix is rarely longer copy. The fix is more specific copy. Strip an adjective, add a number, name the user, and re-read. The page should sound like someone who has used the product for a month explaining it to a colleague over coffee.
