# Pre-Publish Checklist

Run this before hitting publish on any technical article. Each item is a yes/no, not a guess.

## Methodology gates (the non-negotiables)

- [ ] **Authenticity check.** Do you actually use the setup, tool, or workflow you're describing?
- [ ] **Kernel stated, not teased.** Can a reader who scans the title + first paragraph state the article's thesis in one sentence?
- [ ] **At least one section on what didn't work.** Real prose, not a bullet list at the end. The methodology fails without this.
- [ ] **Load-bearing words preserved.** Every technical term that carries precise meaning is the user's term, not an AI synonym.
- [ ] **No hard-sell language.** Re-read the piece looking for "revolutionary," "game-changing," "the only," "absolute best." Either remove or back with evidence.
- [ ] **Voice is the writer's, not the assistant's.** Read aloud — does it sound like you? If not, rewrite the suspect paragraphs.

## Voice gates (AI-tell sweep — see `references/voice-and-style.md`)

- [ ] **Zero vocabulary tells.** Grep the draft for: delve, dive into, leverage, utilize, seamless, robust, comprehensive, crucial, landscape, journey, "it's important to note", "in conclusion", "in today's". Every hit gets rewritten.
- [ ] **Opening starts at the problem.** First two sentences name the reader's situation or the thing being built — no landscape survey, no restating the title, no section preview.
- [ ] **No mirrored outro.** The piece ends at verification, next steps, or the last insight — not a summary of what was just read.
- [ ] **Rhythm varies.** Not every paragraph is 3–4 sentences; not every list has three bolded bullets; em-dashes aren't carrying every sentence.
- [ ] **The only-the-author test.** At least one real number, real error message, or real surprise that couldn't appear in anyone else's post. All `[VERIFY: ...]` placeholders filled with real values.
- [ ] **Nothing invented.** Every command output, benchmark, version, and price in the piece was actually observed or verified against primary docs.
- [ ] **Tutorial cadence intact** (how-tos): intent before each code block, verification after, placeholders for user-specific values, cleanup section present.

## SEO

- [ ] Title 50–60 characters
- [ ] Primary keyword in the first 30 characters when natural
- [ ] Meta description 150–160 characters
- [ ] URL slug stable, descriptive, hyphenated, lowercase
- [ ] Exactly one H1
- [ ] H2/H3 hierarchy clean (no skipped levels)
- [ ] Every image has descriptive alt text
- [ ] ≥3 internal links to related content on your site
- [ ] ≥2 outbound authoritative citations in `## Sources`
- [ ] Per-post hero image with width and height set
- [ ] Updated date set if revised
- [ ] Word count appropriate for type (≥1,500 for deep-dive)
- [ ] Canonical URL set in frontmatter
- [ ] No accidental `noindex` or `disallow` for this URL

## GEO (AI search engines)

- [ ] Direct factual claim in opening paragraph (not hedged)
- [ ] Named author + author page exists at `/author/<slug>`
- [ ] Author profile has `sameAs[]` links to GitHub / LinkedIn / personal site
- [ ] Article schema's `author` is a typed `Person` with `@id`
- [ ] At least one piece of original data (benchmark, chart, quote, snippet from your own work)
- [ ] Speakable markup on H1 + direct-answer paragraph (`data-speakable="true"`)
- [ ] Entity names consistent across the article
- [ ] Article appears in `/llms.txt` or `/llms-full.txt` after deploy
- [ ] If the article references niche terms, they link to glossary or canonical sources

## AEO (featured snippets / voice)

- [ ] Direct-answer paragraph 40–60 words near top
- [ ] "X is..." definition sentence within the first 200 words
- [ ] ≥2–3 question-phrased H2s where natural
- [ ] Numbered steps for any procedural section
- [ ] FAQ section with 3–5 question-phrased H3s, each with a 1–2 sentence answer
- [ ] Comparison tables where applicable (X vs Y articles)
- [ ] Schema layer emits `Article` + `BreadcrumbList` + `FAQPage` + `SpeakableSpecification`

## Visuals

- [ ] At least one inline diagram for any deep-dive (SVG preferred)
- [ ] All SVGs have `<title>` and `<desc>` elements
- [ ] All SVG text is text (not paths) — searchable, accessible, copyable
- [ ] Hero image generated from a JSON spec (not a stock library / generic site fallback)
- [ ] Hero image alt text written before publishing (not "TODO")
- [ ] Light-mode + dark-mode legibility tested if site supports both

## Code (if applicable)

- [ ] Every code block has a language hint for syntax highlighting
- [ ] Every code block has a filename comment (`// path/to/file.ts`) when context isn't obvious
- [ ] Code is runnable as-is, not pseudo-code-disguised-as-real
- [ ] No hard-coded secrets / personal data / internal URLs
- [ ] Tested on a clean machine if it's a tutorial

## Pricing / positioning

- [ ] No "free forever" / "always free" / "we'll never charge" claims if a paid tier might exist
- [ ] No promises that would be hard to walk back if business changes
- [ ] If freemium, the constraints of the free tier are stated honestly
- [ ] Any "X is private" claims are architectural (e.g., "runs in your browser") not pricing-tier-bound

## Final pass

- [ ] Read the entire article aloud, all the way through, in one sitting
- [ ] Zero typos in the title, H1, direct-answer paragraph, and FAQ
- [ ] Open in mobile preview — does the structure still scan?
- [ ] Click every internal and external link — none broken
- [ ] Verify image URLs resolve in production preview, not just dev
- [ ] Confirm Article schema validates at [validator.schema.org](https://validator.schema.org)
- [ ] If sharing on social, the OG card renders correctly in [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/), [Twitter Card Validator](https://cards-dev.twitter.com/validator), and a Slack unfurl preview

## Post-publish

- [ ] Sitemap updated (auto via build pipeline)
- [ ] Article URL submitted to Google Search Console (request indexing)
- [ ] Article URL submitted to Bing Webmaster Tools
- [ ] Internal links updated on related pages
- [ ] Tag archives auto-update if the platform supports it
- [ ] First reader you trust pings you with feedback inside 48 hours
- [ ] Set a calendar reminder to revisit + update the post in 6 months
