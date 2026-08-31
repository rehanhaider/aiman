# GitHub review format

`scripts/pr_review.py post` renders `findings.json`. Findings contain review
content; the script owns badges and the top-level summary.

## Top-level review

Keep the initial review body as an index, not a review diary:

```markdown
Reviewed `31ded9d53a` — 3 findings (1 P1, 2 P2).
```

With no findings:

```markdown
Reviewed `31ded9d53a` — no new issues found.
```

Submit this as a GitHub review even though it has no inline comments. A clean
result must be visible on the pull request, not only in chat.

Keep that wording exactly. Automation reads `no new issues found` as the
all-clear signal, and a PR with no review at all also has no findings — the
phrase is what separates "reviewed and clean" from "never reviewed."

Only P1 and P2 findings are posted. `post` drops P3/P4 by default, so a review
whose only survivors were P3/P4 renders this same all-clear sentence — the
signal means nothing merge-relevant, not that the ledger was empty. Pass
`--include-low` to restore the low tiers when the user asks for them.

## Unverified suspicions

A severe candidate that could not be proved is rendered under the summary:

```markdown
Reviewed `31ded9d53a` — no findings, 1 unverified.

Unverified — severe if real, could not be proved:

- `src/auth.ts:42` — A quoted-JSON groups claim parses wrong, locking out every admin. Check: log the raw claim from one deployed request.
```

Supply them with `--suspicions-file`. While any exist the summary does **not**
carry `no new issues found` — an unresolved severe candidate is not an
all-clear, and automation treats that sentence as ready-to-merge.

These belong on the pull request rather than in a chat reply. The loop that
reads this review is a program; anything not posted here is lost.

## Signature

`post` ends the body with a trailer naming who produced the review:

```markdown
Reviewed `31ded9d53a` — no new issues found.

— rehanhaider/pr-review-skill · Claude Opus 5
```

`rehanhaider/pr-review-skill` is the default and is what automation matches on;
keep that part unchanged. Use `--signed-by` to append the model, and
`--signed-by ''` to omit the trailer. It is always the last line, never the
first, so a reader — human or machine — sees the verdict before the
attribution.

The trailer marks the review as machine-produced rather than typed by hand, and
records which model produced it. It does not make the review independent: it is
posted by the same GitHub account that authored the pull request, and nothing
stops a person typing the same line by hand.

The summary must not contain:

- praise or an explanation of correct code
- test commands or pass counts
- “checked and fine” cases
- resolved-thread history
- pre-existing or out-of-scope issues
- the agent's investigation or severity reasoning

With `--include-low`, when the inline cap is exceeded only overflow P3/P4
titles appear beneath the count. P1/P2 findings always remain inline and are
never capped.

## Inline finding

The renderer produces:

```markdown
**<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>  Keep tenant scope on the fallback query**

When the primary lookup misses, this fallback queries by email alone. A user in one tenant can therefore receive another tenant's record when both use the same email. Include `tenantId` in the fallback predicate, matching the primary path.
```

Badge colors:

| Priority | Color |
| --- | --- |
| P1 | orange |
| P2 | yellow |
| P3 | lightgrey (only with `--include-low`) |
| P4 | lightgrey (only with `--include-low`) |

## Writing rule

Use one root cause per thread. In 2–4 sentences:

1. Name the concrete trigger or path.
2. State the incorrect outcome and why it matters.
3. Point to the boundary that must change.

Use an imperative title. Avoid labels such as “Bug”, greetings, sign-offs,
review history, long code tours, and unneeded praise.
