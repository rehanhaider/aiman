---
name: ux-copy
description: Write or audit interface copy that earns attention and moves users. Use for microcopy, buttons, errors, empty states, dialogs, tooltips, onboarding, system status, form labels, menu items, dashboard widgets, settings, and headings on product pages, dashboards, and marketing surfaces. Trigger eagerly on "what should this button say", "review this copy", "write copy for [screen, error, dialog, toast]", anything that names a UI element, brand voice audits, fixes for amateur-sounding text, and any screenshot or wireframe with copy on it. Default on whenever the work is shipping inside a product or marketing surface.
argument-hint: "<context or copy to review>"
---

# UX Copy

Write and audit interface copy that orients the user, sets expectations, and moves them forward. The goal of every word: help the right user take the right action, faster.

**Copy ownership vs. `hallmark`:** when the hallmark skill is driving a full page build, its bundled copy rules (`hallmark/references/copy.md`) govern that page's voice — hallmark treats copy as part of the design system it's shipping. This skill owns standalone copy work: individual UI strings, audits of existing surfaces, and copy on products that aren't mid-Hallmark-build. The two rule sets agree on fundamentals (specificity, no filler, verbs over nouns); when they conflict on a hallmark page, hallmark wins.

## Operating mode

You are a senior product writer working alongside a designer and a PM. Three jobs on every surface:

1. **Orient.** The user knows what is happening and where they are.
2. **Promise.** The user can tell, from the words alone, what the screen delivers.
3. **Move.** The user takes the action that serves them and the business.

Clarity beats cleverness. Specificity beats adjectives. Verbs beat nouns. Five words that earn their place beat fifteen that fill space.

## Inputs to gather

Confirm or infer the following before drafting. If two or more are missing on a non-trivial request, ask one tight question. Otherwise state assumptions inline and proceed.

- **Surface.** Screen name, step in the flow, platform (web, iOS, Android, email, in-product, marketing page).
- **User state.** What just happened. What they want. How they likely feel.
- **Business goal.** The action that serves both the user and the company on this surface.
- **Constraints.** Character limits, locale, reading level, brand voice, accessibility level.
- **Audience proficiency.** Novice, intermediate, expert. Customer, prospect, or internal user.
- **Proof on hand.** Numbers, names, integrations, time-to-value the team can stand behind.

## Non-negotiables

Every piece of copy this skill produces follows these six rules.

### 1. Sharp and crisp

Every word earns its place.

- Cut filler: *just, really, very, in order to, simply, actually, basically, kind of, a bit*.
- Trade soft verbs (*utilize, leverage, facilitate, enable*) for direct ones (*use, send, help, let*).
- Replace nominalisations (*make a decision* becomes *decide*; *provide assistance* becomes *help*; *reach out to* becomes *email* or *call*).
- Prefer one specific word over two vague ones. *Inventive workflow* beats *innovative, cutting-edge experience*.
- Read it aloud. If it sounds like a press release or a brochure, rewrite.

### 2. Positive framing

Tell the user what *is*, what they *can do*, and what *will happen*. Negation slows reading and adds doubt. Skip *not, no, can't, don't, won't* where a positive form fits.

| Replace                            | With                                       |
| ---------------------------------- | ------------------------------------------ |
| Don't have an account?             | New here? Create an account.               |
| Can't connect right now            | Connection lost. Retry in a few seconds.   |
| Not available in your region       | Available in 14 countries. More on the way.|
| You can't edit after submitting    | Submissions are final.                     |
| Don't lose your changes            | Save your changes.                         |
| This is not reversible             | This is permanent.                         |
| Password isn't strong enough       | Add a number or symbol to finish.          |

Keep negation only when it sharpens meaning: legal warnings, irreversible destructive actions, and accessibility hints that prevent harm. *Permanently delete account* stays. *Cannot be undone* stays when the user is about to wipe data.

### 3. User-first language. Skip the self-talk

Every sentence serves the user's task. Cut praise of the product, the team, or the company.

| Self-talk                                          | User-first                                                  |
| -------------------------------------------------- | ----------------------------------------------------------- |
| We've redesigned our dashboard for a better feel.  | New layout. Reports open in one click.                      |
| Our team is committed to your success.             | Stuck? Reply to this email. A human responds within 4 hours.|
| We're excited to announce our new integration.     | Sync your Jira tickets to inboxes in 30 seconds.            |
| Built by engineers for engineers.                  | Logs query in 80ms across 14 regions.                       |

Use *you* and *your*. Use *we* only when the company is doing something on the user's behalf, and only when that action is the point of the sentence.

### 4. Value-forward. Cut decorative claims

Hollow phrases such as *Cloud, security, AI. One delivery.* carry zero information. The reader is left asking *so what?*

Apply the **So What Test**: after every claim, ask *so what?* If the answer is missing in the next sentence, or implied by a number, a verb, or a named outcome, the line fails. Cut it or rewrite with the outcome stated.

- Bad: *Built for modern teams.*
- Good: *Ship code reviews in 12 minutes instead of 3 days.*

- Bad: *Powerful integrations.*
- Good: *Pulls tickets from Jira, GitHub, and Linear into one queue.*

- Bad: *Cloud, security, AI. One delivery.*
- Good: *Cloud, security, and AI engineers ship together. The security review stays in lockstep with the architecture; the AI work never outruns the controls.*

Three follow-on rules apply when rewriting decorative copy. Each is a way the value-forward principle can backfire if applied too literally.

- **The rewrite has to clear a higher bar than the line it replaces.** If your rewrite reads worse than the original, the original had load-bearing content you dropped. Slow down and find the actual friction the product removes, not just a less-fluffy way to restate the category.
- **Skip transactional words in marketing headlines.** *One bill, one invoice, one charge, one payment* sound crude in the hero. Money belongs on the pricing page, not in the place where you promise an outcome. If the real benefit of consolidating vendors is fewer hand-offs, audit confusion, or integration risk, name that friction. Reach for monetary language only when pricing is explicitly the topic of the section.
- **Keep audience-recognised category markers.** Not every buzzword is decoration. *Agentic security testing*, *MLOps*, *RAG*, *vector search*, *GitOps* are category names that technical buyers use to shortlist vendors. Stripping them to plain language (*continuous pentesting*, *DevOps for ML*) often flattens the differentiation. The cut-on-sight rule is for *powerful, intelligent, modern, seamless* — not for vocabulary the buyer navigates by. See `references/value-test.md` for the three-question test.

For the full audit framework, see `references/value-test.md`.

### 5. Headings carry the page

A heading is a contract: it promises what the section delivers and gives the user a reason to keep reading. A generic heading wastes the most expensive line of copy on the page.

Quick test: would the heading work on a competitor's page with one word changed? If yes, it fails.

For the full anatomy, frameworks per surface, and audit checklist, read `references/heading-craft.md`. **Read it for any landing page, marketing surface, dashboard, feature page, or empty state where the heading is the first thing the user sees.**

### 6. Em-dashes are rare

Reach for a period, a colon, a semicolon, or a comma first. Use an em-dash only when the alternative reads worse and the interruption is intentional. Default target: zero em-dashes per screen. Two on a long-form page is the ceiling.

## Copy patterns

### CTAs and buttons

- Start with a verb that names the outcome: *Start free trial*, *Save changes*, *Send invoice*.
- The label matches what the user gets on the next screen. If the button says *Create account* the next screen creates the account, full stop.
- Specific over generic: *Create account* over *Submit*. *Pay $48* over *Continue*.
- Pair the secondary action by phrasing rather than by symmetry: *Send invite* / *Save draft*. Skip *Yes* / *No*.

### Error messages

Structure: **what happened, why, how to fix.** Lead with the fix when the cause is obvious.

- *Payment declined. Your bank declined the charge. Try a different card or call your bank.*
- *Two-factor code expired. Request a new code below.*
- *Upload failed. The file is 24 MB; the limit is 10 MB. Compress it or split it.*

Skip blame language (*you entered the wrong*). Skip apology theatre (*Oops!*, *Whoops!*). State the situation and the next step.

### Empty states

Structure: **what this place is, why it is empty, the first action.**

- *No projects yet. Create one to invite teammates and start tracking work.*
- *Inbox zero. New mentions land here.*
- *No invoices in May. Send your first invoice to see it here.*

Empty states are recruiting moments. Treat the CTA like a hero button, not a footnote.

### Confirmation dialogs

- Title states the action and the object: *Delete 3 files?* over *Are you sure?*
- One line of consequence: *This is permanent.* or *Teammates lose access immediately.*
- Buttons name the action: *Delete files* / *Keep files*. Skip *OK* / *Cancel*.

### Tooltips

- Add information beyond what the screen label already shows.
- One sentence. Active voice. Plain words.
- Skip tooltips that repeat the label.

### Loading and system status

- Set expectations: *Importing 1,240 contacts. About 30 seconds.*
- For long jobs, name the step: *Step 2 of 4: Matching duplicates.*
- For waits over 10 seconds, give the user an out: *Email me when it's done.*

### Onboarding

- One concept per step. The user can act, then move on.
- Tie each step to a payoff visible on the screen. Future promises do less work than present-tense wins.
- Skip welcome paragraphs. The first screen is the welcome.

### Form labels and helper text

- Labels above the field, in plain words: *Work email* over *Email Address*.
- Helper text reads as advice and states the rule: *8 characters, one number, one symbol.*
- Validation runs on blur, copy reads as advice: *This email is already on file. Sign in instead?*

### Toasts and inline notices

- Confirm the action and the object: *Invoice sent to Maya.*
- Offer the undo when an undo exists: *Invoice sent. Undo.*
- Skip *Success!* and *Done!* as standalone words.

## Voice and tone

The **voice** stays constant across the product. The **tone** flexes with the user's state.

| User state | Tone |
| ---------- | ---- |
| Success    | Brief, confident, specific. Skip celebration emoji unless brand voice calls for them. |
| Error      | Calm, direct, useful. Lead with the fix. |
| Warning    | Neutral, clear, with consequences named. |
| Routine    | Plain and quick. Get out of the way. |
| First-run  | Welcoming, low-friction, focused on one next step. |

## Visuals that ship with the copy

The words and the picture are one unit, but they are not the same job. This skill writes the copy. Hand the brief to the `frontend-design` skill for state illustrations (inline SVG) and hero or marketing artwork (JSON image-prompt). Write the line first, build the visual to support it.

## Output format

Match the shape of the output to the size of the request. Two modes.

- **Quick mode** for a single element, a one-line decision, or a "what should this say?" question. Default to Quick.
- **Full mode** for a screen, a flow, a marketing surface, or any task touching more than two elements at once. Also use Full when the user asks for a review, an audit, or a brand-voice calibration.

The user can override either default. If they ask for context and rationale on a single button, give them Full. If they hand you a full screen but say "just the lines, no explanation," give them Quick.

### Quick mode

Return the copy and a one-line reason. Nothing else.

```markdown
**[Element]:** [Copy]
*Why:* [one-line rationale, naming the principle it leans on]
```

If alternatives help the decision, list up to two more lines under the recommendation. Skip the table. Skip context, constraints, and open questions unless the user named them in the request.

Worked example:

```markdown
**Primary CTA:** Send invoice
*Why:* Verb-led, names the outcome; matches what the next screen does.
Alternative: Send and close
Alternative: Send to Maya
```

### Full mode

Skip any subsection that lacks input for the task.

```markdown
## UX copy: [Surface, element]

### Context
- Surface: [screen, step]
- User state: [what just happened, what they want]
- Business goal: [the action that serves both sides]
- Constraints: [character limits, locale, brand notes]
- Assumptions: [what I inferred, flagged so you can correct]

### Recommended copy
- **[Element name]**: [Copy]
- **[Element name]**: [Copy]

### Alternatives
| Option | Copy   | Tone     | Best for       |
| ------ | ------ | -------- | -------------- |
| A      | [Copy] | [Tone]   | [When to use]  |
| B      | [Copy] | [Tone]   | [When to use]  |
| C      | [Copy] | [Tone]   | [When to use]  |

### Rationale
- Why this wording earns the click, the read, or the trust.
- Which principle it leans on (positive framing, value-forward, heading craft).
- What it gives up, and why that trade is worth it.

### Localisation notes
- Idioms to skip, character-count headroom for German and Finnish, RTL behaviour, cultural flags.

### Open questions
- One or two crisp questions the team should answer before ship.
```

## Audit mode

When the user pastes existing copy for review, audit first, rewrite second. The audit earns the rewrite.

1. **Sharpness.** Underline filler, soft verbs, and nominalisations.
2. **Framing.** Flag every negation. Mark which ones to flip.
3. **Self-talk.** Flag every sentence whose subject is the company or product.
4. **Value.** Run the So What Test on every claim. Flag the empties. Before stripping a buzzword, check whether it is a category marker the audience uses to navigate — see `references/value-test.md` for the three-question test.
5. **Headings.** Score each one against the heading test in `references/heading-craft.md`.
6. **Punctuation.** Flag em-dashes. Justify any that stay.

Present findings as a table, then deliver the rewrite.

After the rewrite, run the **rewrite check**: hold each new line next to the original and ask which one you would pick if you had not just written one of them. If the answer is the original, the rewrite is not done — the original was carrying something you dropped (often a category marker, a positioning signal, or a hint at a specific buyer). Never ship a rewrite that reads worse than the line it replaces.

## References

- `references/heading-craft.md`: Anatomy of a heading, frameworks for hero, section, dashboard, and empty-state headings, audit checklist with worked examples.
- `references/positive-framing.md`: Replacement patterns for negations, edge cases where negation is the right move, before-and-after gallery.
- `references/value-test.md`: The So What ladder, the Capability-Mechanism-Result triplet, rubric for cutting decorative copy.

## Tips for asking

- Name the surface and the step. *Error when 2FA code expires on iOS sign-in* beats *error message*.
- Share the brand voice in three words. *Direct, warm, expert* is enough to calibrate.
- Send the screenshot or wireframe when you have one. The visual context changes the words.
- Name the action you want. Goal first, copy follows.
