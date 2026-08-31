# Heading craft

A heading is the most expensive line of copy on the page. It buys the next read. It promises what the section delivers. It tells the user, in a glance, whether this place is for them.

Most headings fail because they describe what the section *is* instead of what the user *gets*. Generic headings (*Features*, *Why us*, *Get started*) are placeholders that shipped. This document is the working playbook for replacing them.

## The three jobs of a heading

A useful heading does three jobs at once. Score every heading on all three before shipping.

1. **Orient.** The user knows what kind of section this is and where it sits in the page.
2. **Promise.** The user can predict, from the heading alone, the payoff of reading the section.
3. **Differentiate.** The heading would feel wrong on a competitor's page. It belongs to this product, this audience, this moment.

A heading that does only the first job is a label. A heading that does the first two is a sub-heading. Only a heading that does all three earns the spot.

## Anti-patterns. Cut on sight

These appear in the wild, in production, every day. Each example below is a real pattern, not a strawman.

### 1. The label
*Features. Pricing. About. Why us.* These are file-folder tabs, not headings. They orient and stop there. Use them only in navigation, never as section headings on the page itself.

### 2. The hollow superlative
*The smartest way to manage your team. Powerful, beautiful, simple.* Adjectives without a noun the user can picture. The reader skims past. Replace the adjective with a verb and a number.

### 3. The internal milestone
*Introducing our new dashboard. We've redesigned the editor.* The company is celebrating itself. The user came to solve a problem. Reframe to the user's outcome: *Reports open in one click. Edit on touch devices without the lag.*

### 4. The category restatement
*Project management, reinvented.* This tells the reader they are on a project-management website, which they already know. State the specific change that matters.

### 5. The buzzword stack
*Cloud, security, AI. One delivery.* Each noun is a market category, not a benefit. The reader is asked to do the work. Spell out what the stack delivers, and to whom, and how fast.

### 6. The riddle
*Where work works.* Wordplay that needs a second read to decode. Save wordplay for sub-headings or campaign lines, never for the heading that gates the section.

### 7. The first-year-grad heading
*Unlock the power of data with our innovative platform.* Every word is generic. Every word could be cut. Rewrite from the user's problem: *See which campaign drove every dollar of revenue, by day, by region, by SKU.*

## The Specificity Ladder

When a heading feels thin, climb the ladder. Each rung adds one concrete element.

| Rung | Element added            | Example                                                        |
| ---- | ------------------------ | -------------------------------------------------------------- |
| 0    | Category claim           | A better way to manage projects.                               |
| 1    | A verb the user does     | Plan projects without the meeting tax.                         |
| 2    | The user named           | Plan projects without the meeting tax, for product teams.      |
| 3    | A number or unit         | Cut project meetings by 6 hours a week, for product teams.     |
| 4    | A named friction removed | Cut project meetings by 6 hours a week. One status doc, auto-updated.|

Most shipped headings sit at rung 0 or 1. Rungs 3 and 4 are where the page starts to earn its scroll.

Climbing too high makes the heading dense and hard to read. The right rung depends on the surface. Hero headings live at rungs 2 to 3. Section headings sit at rungs 1 to 3. Empty-state and dialog headings stay at rung 1 to 2.

## Frameworks by surface

Pick the framework that matches the surface. Use it as a starting frame, then tighten with the Specificity Ladder.

### Hero heading (landing page, top of fold)

The hero heading answers: *whose life changes, and how?*

Frame: **[Specific outcome] for [specific user], without [common friction].**

- *Close books in 3 days instead of 30, for finance teams that wear ten hats.*
- *Ship code reviews in 12 minutes. For staff engineers, without the back-and-forth.*

If the audience is unambiguous from context (the marketing campaign already targets them), drop the *for [user]* clause.

### Section heading (mid-page on marketing pages)

The section heading answers: *what is the one thing this block proves?*

Frame: **[Capability stated as user action] [number, unit, or named outcome].**

- *Sync invoices to QuickBooks in 30 seconds.*
- *Audit-log every change, retained for 7 years.*

Skip the verb-less section heading (*Integrations*, *Security*) on marketing pages. Use the navigable label form only in product UI.

### Dashboard or product page heading

The page heading answers: *what is this view of the data?*

Frame: **[Object] [scope] [time window].**

- *Invoices, all teams, last 30 days.*
- *Active incidents, US-East, this hour.*

Skip humour. Skip metaphor. The user is in a task, not a reading mood.

### Empty-state heading

The empty-state heading answers: *what will live here, and is that good or bad?*

Frame: **[State as outcome the user wants].**

- *Inbox zero.* (Good.)
- *No projects yet.* (Neutral, paired with a CTA.)
- *Nothing to review today.* (Reassuring.)

Avoid the apologetic empty state (*Sorry, nothing here.*). Avoid the cartoonish empty state (*Looks like a ghost town in here!*) unless the brand voice supports it.

### Dialog or modal heading

The dialog heading answers: *what am I about to do?*

Frame: **[Verb] [object with number or specifier]?**

- *Delete 3 files?*
- *Remove Maya from the workspace?*
- *Publish the November invoice?*

Skip *Confirm*, *Warning*, *Notice*. The verb plus object is the title.

### Feature page heading (product surface, not marketing)

The feature page heading answers: *what does this feature do for me, in product terms?*

Frame: **[Feature name] [verb] [object].**

- *Approvals route invoices to the right reviewer.*
- *Workflows trigger when a deal closes.*

This is a documentation heading. Plain, factual, predictable. The reader wants the answer, not the seduction.

## The audit checklist

Run every heading through these six checks. A heading passes when all six come back clean.

1. **The substitution test.** Could the heading sit on a direct competitor's page with one word changed? If yes, rewrite. The heading is too generic.
2. **The mirror test.** Does the heading describe what the section *delivers* or what the section *is*? Sections that label themselves (*Features*, *Benefits*, *Why us*) fail the mirror test.
3. **The so-what test.** Read the heading. Ask *so what?* If the answer requires the reader to scroll to find out, the heading is doing only half its job.
4. **The numbers test.** Can you add a number, a unit, a name, or a time window without making the heading dishonest? If yes, you probably should.
5. **The verb test.** Does the heading contain a verb the user performs or benefits from? Headings with no verb often read as taxonomies, not promises.
6. **The aloud test.** Read the heading aloud. Does it sound like a person speaking, or like a press release? Press-release prose loses readers.

## Worked examples

Each pairing below is from a real pattern. The "before" line is shippable in the sense that nobody on the team will block it. The "after" line earns the read.

### SaaS hero

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| The modern way to run customer support. | Reply to support tickets in 90 seconds, with a draft already written. |
| Powerful project management, simplified.| Cut project meetings by 6 hours a week. One status doc, auto-updated. |
| AI-powered insights for your business.  | See which campaign drove every dollar, by day, region, and SKU. |

### Security page

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Enterprise-grade security.              | SOC 2 Type II, audited yearly. Data encrypted in transit and at rest. |
| Built with security in mind.            | Every request logged. Every change reversible for 30 days.       |

### Pricing page

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Simple pricing for teams of every size. | Pay per active reviewer. No seat counts, no annual lock-in.      |
| Plans for everyone.                     | Start at $0 for 3 seats. Scale to 50,000 with one toggle.        |

### Dashboard widget

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Recent activity.                        | 14 events in the last hour.                                      |
| Performance.                            | API latency, p95, last 24 hours.                                 |

### Empty state

| Before                                  | After                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Nothing here yet.                       | No invoices in May. Send your first one to see it here.          |
| You don't have any projects.            | Create your first project. Teammates land here when you invite them. |

## Length notes

A hero heading is usually 6 to 14 words. Aim for one sentence, one comma at most, no semicolons. Two short sentences read faster than one long one with two clauses joined by *and*. If the heading runs past 16 words, split it: lead with the outcome, drop the rest into the sub-heading.

Dashboard headings, dialog titles, and empty-state titles stay under 8 words.

## The final pass

When a heading passes the six tests, run one more pass aloud. If the line still reads like advertising, strip one adjective and try again. The best product headings sound like what a clear-headed user would say to a colleague after using the product for a month. That voice is the target.
