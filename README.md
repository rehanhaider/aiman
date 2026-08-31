# aiman

Central store for my AI tooling: the skill library, the agent instruction files I run
globally, the analysis behind them, and the helper scripts.

Skills install two ways: symlinked into the agent directories with `npm run link-skills`
(simple, always current), or from the **Claude Code plugin marketplace** this repo
publishes, when a project wants a pinned version.

## Layout

| Path | What lives there |
| --- | --- |
| `skills/` | The skill library — one directory per skill, each with a `SKILL.md`. See [skills/README.md](skills/README.md) for the catalog and conventions. |
| `.claude-plugin/marketplace.json` | The registry: one entry per skill, with its version. Generated from `skills/` by `npm run sync` — don't hand-edit names, sources, or descriptions. |
| `scripts/` | `skills.ts` — validate, registry, install — and the usage-check scripts under `claude/` and `codex/`. |
| `snapshots/` | The instruction files as deployed — `snapshots/claude/CLAUDE.md` (`~/.claude/CLAUDE.md`) and `snapshots/codex/AGENTS.md` (`~/.codex/AGENTS.md`). |
| `analysis/` | Working notes the instruction files came out of, e.g. the per-model failure analyses in `analysis/AGENTS/`. |

## Install every skill globally

One command links the library into the directories the agents read — Claude Code's
`~/.claude/skills`, and `~/.agents/skills` for Codex and Cursor:

```bash
npm run link-skills                 # all skills, both directories
npm run link-skills forge hallmark  # just these
npm run unlink-skills forge         # remove
```

They are symlinks into `skills/`, so an edit here is live everywhere on the next
session — no reinstall, no version bump. To link into the current repo's
`.claude/skills` and `.agents/skills` instead of the home directory, run
`npm run link-skills -- --project` — npm needs the `--` before any flag, though
plain skill names pass through without it.

Existing links pointing somewhere else are repointed; a real directory is never
overwritten, it is reported and skipped. `unlink-skills` only removes symlinks that
point into this library.

## Install as a Claude Code plugin instead

Use this when a project should pin a version rather than track the working copy.
Add the marketplace once per machine, then install what you want:

```bash
claude plugin marketplace add rehanhaider/aiman
claude plugin install hallmark@aiman                   # global, all projects
claude plugin install hallmark@aiman --scope project   # this repo only
```

A project-scope install writes `extraKnownMarketplaces` and `enabledPlugins` into that
repo's `.claude/settings.json`, so the repo records which skills it expects. Plugin skills
are namespaced: `hallmark` is invoked as `/hallmark:hallmark`.

Each installed skill costs roughly 30 tokens of always-on context, so installing all
fifteen is cheap; the skill body is only loaded when it fires.

### Turn updates on

Third-party marketplaces ship with auto-update **off**. Enable it once:

`/plugin` → **Marketplaces** → **aiman** → **Enable auto-update**

After that Claude Code refreshes the catalog and updates installed skills in the background
shortly after each session starts, then prompts for `/reload-plugins`. Without it, update on
demand with `claude plugin marketplace update aiman` and `claude plugin update <skill>@aiman`.

Codex and Cursor have no plugin equivalent — `npm run link-skills` is their only path.
Claude Code does not read `.agents/skills`, which is why the linker writes both.

## Working on the library

```bash
npm run check                      # validate skills, registry, and catalog
npm run sync                       # refresh the registry after adding or renaming a skill
npm run release <skill> [patch|minor|major]
npm run link-skills / unlink-skills
```

`npm run check` runs the library rules (frontmatter, description limit, link and path
resolution), verifies the registry and the README catalog match `skills/`, and then runs
`claude plugin validate --strict`. Run it before committing.

Releasing is just a version bump in the registry: installed copies pick the new version up
on the next marketplace refresh, because Claude Code only ships an update when the `version`
string changes. Skills are versioned individually.

Requires Node >= 22.6 — `scripts/skills.ts` runs directly, no build step and no
dependencies. There is nothing to install, so `npm install` is never needed and any
package manager works; the scripts are a convenience over `node scripts/skills.ts <cmd>`.
