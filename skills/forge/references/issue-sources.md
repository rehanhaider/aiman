# Issue sources

An issue lives in exactly one of three places, and which one is a property of
the repository, not of the issue. Detect the source before reading anything.

## Detection

Run these checks in order and stop at the first match. State the detected
source in the run's opening summary so a wrong guess is visible immediately.

| Signal | Source |
| --- | --- |
| The user names a source, a URL, or a full key (`NAV-123`, `#42`, a file path) | Use it verbatim |
| A `docs/issues/` tree, `issues.md`, or a plan document holds the tracked work | In-repo docs |
| A Linear plugin or MCP server is configured for the repository | Linear |
| The GitHub repository has open issues | GitHub Issues |

Known mappings, correct as of 2026-07-25 — verify rather than assume, since a
repository can migrate:

| Repository | Source |
| --- | --- |
| `rehanhaider/naqid` | In-repo docs, `docs/issues/<area>/<KEY>-NNN-slug.md` |
| `Mizanic/Qaleening` | GitHub Issues |
| `Magnolia-Impact/navinier-app` | Linear |

If two sources both look plausible, ask which one is authoritative. Do not
implement against a stale mirror.

## Linear

Read the issue through the Linear plugin or MCP tools. Fetch the description,
acceptance criteria, linked documents, parent or sub-issues, and current state.
Keys look like `NAV-123`.

- If the tools are unavailable, stop and say so. Do not reconstruct the issue
  from the branch name or the user's one-line summary.
- Reference the key in the branch name, commit trailer, and PR body so Linear
  links the PR automatically.
- Move the issue to the in-review state once the PR is open, if the workspace
  uses one. Do not move it to done — this skill never merges.

## GitHub Issues

```bash
gh issue view <number> --repo <owner/name> --json number,title,body,labels,state,url,comments
```

Read the comment thread too; the acceptance criteria are often refined there
rather than in the body.

- Link the issue from the PR body with `Closes #<number>` when merging should
  close it, or `Refs #<number>` when it should not.
- Do not close the issue directly. The merge closes it, and merging is the
  user's step.

## In-repo docs

Tracked work lives as Markdown under version control. Two shapes appear:

**One file per issue** — `docs/issues/<area>/<KEY>-NNN-slug.md`, with YAML
frontmatter carrying `title`, `labels`, `severity`, and `status`. The body holds
the problem statement, the fix, and checkboxes that act as acceptance criteria.
An index `README.md` sits alongside and records authority order and completion
gates.

**One file with many rows** — a table or checklist such as `issues.md`, where
each row is a finding with a severity and an action column.

For either shape:

1. Read the index or table first. It states which documents outrank the issue
   when they conflict, and honouring that order is part of the contract.
2. Follow every authority link the index names before writing code.
3. Treat unchecked checkboxes and the `Action?` column as the scope boundary.
   Rows marked as deferred or not-actionable are out of scope.
4. Update the issue document in the same PR: tick completed checkboxes and move
   `status` forward. Leave it short of closed — closure follows the merge.

## What to extract, whatever the source

Before implementing, write down:

- The acceptance criteria, verbatim where they exist.
- The scope boundary: what this issue explicitly does not cover.
- Every authority document the issue defers to, plus repository `AGENTS.md` and
  `CLAUDE.md`.
- The verification the issue demands — specific tests, gates, or manual checks.

If the acceptance criteria cannot be stated concretely, the issue is not ready.
Ask rather than guessing at the intent.
