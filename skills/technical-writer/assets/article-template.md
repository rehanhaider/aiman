---
# Frontmatter — adapt to your platform's schema (Astro / Next / Hugo / Gatsby).
title: "<<< title — 50–60 chars, primary keyword in first 30, kernel stated >>>"
description: "<<< meta description — 150–160 chars, single sentence + soft CTA >>>"
slug: "<<< url-slug-hyphenated-lowercase >>>"
publishDate: 2026-01-01
updatedDate: 2026-01-01
author: "<<< author slug — must match an entry in /content/authors/ >>>"
tags:
  - "<<< primary tag >>>"
  - "<<< secondary tag >>>"
  - "<<< tertiary tag >>>"
heroImage: "../../assets/blog/<<< slug >>>/hero.png"  # generated from JSON image spec
heroImageAlt: "<<< 1–2 sentence alt text describing what the hero image shows >>>"
ogType: article
articleSection: "<<< section name — engineering / postmortem / launch / etc. >>>"
canonical: "https://example.com/blog/<<< slug >>>"
draft: true
---

<!--
  KERNEL: <<< one-sentence claim this article exists to make >>>
  AUDIENCE: <<< peer engineers / new users / sales-enabled customers / mixed >>>
  ARTICLE TYPE: <<< deep-dive / tutorial / postmortem / day-in-the-life / comparison / launch / glossary >>>
  STATUS: <<< draft / in-review / published >>>

  CHECKLIST PRE-PUBLISH:
  - [ ] Authenticity check passed (you actually use this setup)
  - [ ] Direct-answer paragraph 40–60 words
  - [ ] At least one section on what didn't work
  - [ ] ≥2 outbound authoritative citations in Sources
  - [ ] Per-post hero image generated from spec, alt text written
  - [ ] At least one inline diagram (SVG preferred)
  - [ ] FAQ section with 3–5 question-phrased H3s
  - [ ] Question-phrased H2s where natural (≥2)
  - [ ] [data-speakable] on H1 + direct-answer paragraph
  - [ ] Author byline links to /author/<slug>
  - [ ] Updated date set if revised
  - [ ] Schema layer emits Article + BreadcrumbList + FAQPage + Speakable
  - [ ] Article entry added to /llms.txt or /llms-full.txt
-->

# <<< H1 — usually identical to title; can diverge for editorial flavor >>>

<!-- HERO IMAGE: rendered automatically from frontmatter heroImage above -->

<p data-speakable="true">
  <<< Direct-answer paragraph — 40–60 words. Plain English. States the kernel as a stand-alone
  claim. Could be lifted by Google's snippet box or ChatGPT and still make sense. Wraps the
  whole article's value in one paragraph. >>>
</p>

> **<<< Concept >>> is** <<< single-sentence definition — entity-anchor for AI search engines >>>.

## TL;DR

- <<< first key takeaway >>>
- <<< second key takeaway >>>
- <<< third key takeaway >>>
- <<< fourth (optional) >>>
- <<< fifth (optional) >>>

---

## Background

<<< 1–3 paragraphs. What the world looked like before this work. Don't over-explain — assume
the reader has the context implied by the title. >>>

---

## <<< First H2 — question-phrased where natural >>>

<<< Open with a 1–2 sentence answer to the H2 question. Then expand. >>>

<!-- INLINE DIAGRAM placeholder — SVG inline OR image-spec.json reference -->

```language
// Code block with filename hint
// path/to/file.ts
```

---

## <<< Second H2 — what didn't work >>>

<<< Non-negotiable section for deep-dives and postmortems. Describe the variation(s) you
tried that failed. Be specific about why. The methodology: more information in what didn't
work than what did. >>>

---

## <<< Third H2 — the working approach >>>

<<< The kernel's payoff section. Describe the working solution. Diagram it. Show the
numbers (latency before/after, error rate, throughput, whatever). >>>

---

## <<< Fourth H2 — caveats and limitations >>>

<<< Honest list of what this approach doesn't solve, what edge cases break it, what the
trade-offs are. >>>

---

## What we'd do differently

<<< Optional. If you'd take a different approach starting fresh, say so. >>>

---

## FAQ

### <<< Question 1, phrased as a real user would ask it >>>

<<< 1–2 sentence answer. >>>

### <<< Question 2 >>>

<<< Answer. >>>

### <<< Question 3 >>>

<<< Answer. >>>

---

## Sources

- [<<< Source 1 — Wikipedia / RFC / official docs >>>](https://...)
- [<<< Source 2 — peer-reviewed paper / standards body >>>](https://...)
- [<<< Optional source 3 >>>](https://...)

---

<!-- AUTHOR BYLINE — handled by platform layout, but ensure /content/authors/<slug>.md exists with sameAs[] -->
<!-- UPDATED DATE — handled by frontmatter updatedDate -->
