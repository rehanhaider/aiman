# Article-level SEO / GEO / AEO Checklist

Calibrated for a single technical article — what to check on the page itself. For full-site infrastructure (sitemaps, llms.txt, OG card pipelines, schema helpers), defer to the sibling `seo-expert` skill in this repo.

The dimensions:

- **SEO** — Search Engine Optimization (Google, Bing). Indexing and ranking signals.
- **GEO** — Generative Engine Optimization (Perplexity, ChatGPT Search, Google AI Overviews, Claude, Gemini). Whether AI search engines cite your article.
- **AEO** — Answer Engine Optimization (featured snippets, voice search, "People also ask"). Whether algorithms can extract a clean answer from your page.

These overlap heavily. A question-phrased H2 with a 50-word direct answer is good SEO, good GEO, and good AEO simultaneously. Optimize once; benefit thrice.

---

## SEO — on-page signals

### Title tag

- 50–60 characters (longer truncates in SERP).
- Primary keyword in the first 30 characters when natural.
- Specific, not clickbait. "Why X breaks at scale" beats "We learned something amazing about X".
- Don't repeat the brand in every title — let the platform append it (most do).

### Meta description

- 150–160 characters.
- One sentence summarizing the kernel + a soft CTA ("Read the postmortem" / "See the benchmarks").
- Should make sense out of context — assume readers see only this in a search result.

### URL slug

- Hyphen-separated, lowercase, descriptive.
- Stable — never rename a slug after publish without a 301.
- 3–6 words. Match the kernel, not just the title.

### H1

- Exactly one per page.
- Often (but not always) identical to title — diverge when the title is search-optimized but the H1 is editorial.
- Contains the primary keyword.

### Heading hierarchy

- H1 → H2 → H3, no skips. (`<h2>` followed by `<h4>` is broken.)
- H2s carry the main beats. 4–8 H2s is typical for a deep-dive; more starts to feel like a list of bullet points.
- Sub-points under an H2 use H3s.

### Image alt text

- Every image, including SVG (`<title>` element) and inline screenshots.
- Describe what the image *shows*, not what it's *for*.
- For diagrams: describe the components and their relationships ("Three-box pipeline: ingest → enrich → publish, with a feedback loop from publish back to enrich").
- For decorative images: empty alt (`alt=""`) so screen readers skip them.

### Internal links

- Link to ≥3 related articles on your site if you have them.
- Link from passing mentions, not "click here".
- Use descriptive anchor text matching the linked page's primary keyword.

### Outbound authoritative citations

- ≥2 per long-form post, in a `## Sources` or `## References` section.
- Authoritative sources: Wikipedia, IETF RFCs, ISO standards, NIST publications, peer-reviewed papers, official documentation, primary-source government data.
- Avoid: SEO blogs, content farms, marketing pages, paywalled academic gates.

### Word count

- Reference / explainer pieces: 800–1500 words.
- Deep-dives / postmortems: 1500–4000 words.
- Pillar content: 2500+ words, with internal links from short-form pieces.
- Don't pad. Long-form ≠ verbose. The kernel determines length, not vice versa.

### Hero image + responsive variants

- Per-post hero image (not a generic site fallback) — required for Article schema rich-result eligibility.
- Provide width and height (the Image schema property requires both).
- WebP / AVIF for modern browsers, JPEG/PNG fallback.
- `loading="eager"` + `fetchpriority="high"` for above-fold heroes (lazy-loading kills LCP).

### Updated date

- Show `Updated: <date>` in the published byline if the post has been revised post-publish.
- Reflect the same value in the Article schema's `dateModified`.

---

## GEO — signals for AI-powered search

### Direct factual claims at the top

- Open with a sentence that states the kernel as a plain factual claim, with no hedging.
- "We reduced latency by 40% by caching at the harness layer" — citable.
- "We made some performance improvements to our system" — useless to an AI engine.

### Entity clarity

- Name products, libraries, people, places consistently across the article.
- Use the canonical form (e.g., "PostgreSQL" not "Postgres" in the entity-establishing sentence; can use "Postgres" later).
- If the article is about your own product, link to your homepage on first mention.

### Speakable markup

- Mark the H1 + the direct-answer paragraph as `data-speakable="true"`.
- Schema layer should emit a `SpeakableSpecification` with `cssSelector: ["[data-speakable]"]`.
- Don't over-mark. Two elements is typically the right number.

### Originality

- Include at least one piece of original information: a benchmark you ran, a chart of your own data, a quote from your own user research, a code snippet from your own production.
- AI engines weight unique data heavily — reposted facts get no citation lift.

### Author E-E-A-T

- Visible byline with author name (not "Admin" or "The team").
- Author page at `/author/<slug>` with bio, jobTitle, and `sameAs[]` links to GitHub / LinkedIn / personal site.
- Author byline links to the author page.
- Article schema's `author` is a `Person` with `@id` matching the author page URL + `#person`.

### Outbound citations to canonical sources

- See SEO section. Same rule, different reason.
- AI engines use this as an alignment signal — when they parse your page and see you cite the same Wikipedia / RFC / official-docs page they'd cite, your article gets co-cited.

### Comprehensive entity coverage

- If your article references niche terms (algorithms, libraries, formats, protocols), link them — either to your own glossary if you have one, or to Wikipedia / official docs.
- For domain-heavy articles, consider a "Terms used in this article" mini-glossary at the bottom.

### llms.txt entry

- If the host site has an `/llms.txt`, ensure the article appears in it (or in `/llms-full.txt`) after publishing.
- Mention the article's existence in the `Key Facts` section if it documents a product feature.

---

## AEO — signals for featured snippets and voice

### Question-phrased H2s where natural

- "Why does compaction fail at scale?" beats "Compaction failure modes".
- Don't force every H2 into question form — some sections are explanations, not Q&As.
- Aim for at least 2–3 question-phrased H2s in any long-form piece.

### Direct-answer paragraph

- 40–60 words, near the top of the article (right after the lede image).
- Plain English, no jargon-without-introduction.
- Wraps the kernel in a single self-contained paragraph.
- Wrapped in `<p data-speakable="true">` for speakable markup.

### "X is..." definition sentence

- Single sentence that defines the primary topic.
- Useful for entity disambiguation in AI engines.
- Can be embedded in the direct-answer paragraph or stand alone.

### Numbered steps and bullets

- For tutorial / how-to content, use ordered lists with explicit step numbers.
- Keeps each step short (1–2 sentences each).
- Step lists qualify for list-style snippets in Google SERPs and structured AI extraction.

### Comparison tables

- For "X vs Y" content, a markdown table compares dimensions row by row.
- AI engines extract tables cleanly; readers scan them.
- Headers should be specific ("Latency p95" not "Speed").

### FAQ section

- 3–5 question-phrased H3s near the end.
- Each answer is 1–2 sentences.
- Schema layer should emit a `FAQPage` with `mainEntity[]` of `Question` + `acceptedAnswer`.
- Choose questions readers actually ask — if you have search-console data or support tickets, mine them.

### Voice search

- Conversational language in the direct-answer paragraph.
- Long-tail who/what/when/where/why/how question coverage in H2s/H3s.
- For local-relevance content, NAP (name/address/phone) data + local schema.

### Schema markup (handled by the platform)

The article-level schemas to ensure are emitted:

- `Article` (or `BlogPosting`/`NewsArticle`) with full publisher + author + image + datePublished + dateModified
- `BreadcrumbList`
- `FAQPage` (if there's a FAQ section)
- `HowTo` (if step-by-step instructions; note Google removed HowTo rich results from SERP rendering in late 2023, but Bing + AI engines still parse it)
- `SpeakableSpecification` (linked from Article)

Most static-site platforms generate these from frontmatter + helper functions — you write content + frontmatter, the build emits JSON-LD. Don't paste raw JSON-LD into the markdown body.

---

## Pre-publish checklist (article-level)

```
SEO
[ ] Title 50–60 chars, primary keyword in first 30
[ ] Meta description 150–160 chars
[ ] URL slug stable, descriptive, hyphenated, lowercase
[ ] One H1, matching or close to title
[ ] H2/H3 hierarchy clean (no skips)
[ ] Every image has descriptive alt text
[ ] ≥3 internal links to related content
[ ] ≥2 outbound authoritative citations in Sources section
[ ] Per-post hero image with width/height set
[ ] Updated date visible if revised
[ ] Word count appropriate for type (≥1500 for deep-dive)

GEO
[ ] Direct factual claim in opening paragraph
[ ] Named author + author page + sameAs[] links
[ ] At least one piece of original data (benchmark / chart / quote / snippet)
[ ] Speakable markup on H1 + direct-answer paragraph
[ ] Consistent entity naming
[ ] Article exists in /llms.txt or /llms-full.txt

AEO
[ ] Direct-answer paragraph 40–60 words near top
[ ] "X is..." definition sentence
[ ] ≥2–3 question-phrased H2s
[ ] Numbered steps for any procedural section
[ ] FAQ section with 3–5 Qs
[ ] Comparison tables where applicable
[ ] Schema layer emits Article + BreadcrumbList + FAQPage + Speakable
```

---

## Common pitfalls

- **Generic OG image.** Every post sharing the same "company logo on gradient" OG card kills CTR on social and breaks Article schema rich-result eligibility. Generate per-post OG cards (see `seo-expert` skill § 1).
- **Title rewritten for keywords, kernel buried.** A keyword-stuffed title that doesn't state the kernel pulls clicks but loses readers in the first paragraph. Bounce rate kills ranking faster than it helps.
- **No failed-approaches section.** Common in launch announcements and case studies. Without it, reads like marketing — and ranks like marketing.
- **AI-rewritten prose.** Every replacement of a load-bearing word degrades both reader trust and AI search citability. See `methodology.md` § Load-bearing words.
- **Paragraphs over 100 words.** Engineers scan; long paragraphs lose them. Break aggressively.
- **No citations.** Even great original work benefits from grounding in canonical references. Two outbound citations is a floor, not a ceiling.
- **Question H2s without short answers.** A question H2 followed by 800 words of prose doesn't qualify for snippets. The first paragraph after a question H2 should answer the question concisely; deeper detail follows.
- **HowTo schema without enrichment.** A bare HowTo with just `steps` and no `totalTime`, `tool`, `supply`, or `estimatedCost` looks half-done to validators. Either fully enrich or skip it.
