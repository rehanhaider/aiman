# aiman

Central store for my AI tooling: the skill library, the agent instruction files I run
globally, the analysis behind them, and the helper scripts.

This repo is also a **Claude Code plugin marketplace** — every skill is published as a
single-skill plugin, so skills are installed and versioned rather than symlinked by hand.

## Layout

| Path | What lives there |
| --- | --- |
| `skills/` | The skill library — one directory per skill, each with a `SKILL.md`. See [skills/README.md](skills/README.md) for the catalog and conventions. |
| `.claude-plugin/marketplace.json` | The registry: one entry per skill, with its version. Generated from `skills/` by `pnpm sync` — don't hand-edit names, sources, or descriptions. |
| `scripts/` | `skills.ts` (validate + registry), `manage-skills.sh` (Codex/Cursor symlinks), and the usage-check scripts under `claude/` and `codex/`. |
| `snapshots/` | The instruction files as deployed — `snapshots/claude/CLAUDE.md` (`~/.claude/CLAUDE.md`) and `snapshots/codex/AGENTS.md` (`~/.codex/AGENTS.md`). |
| `analysis/` | Working notes the instruction files came out of, e.g. the per-model failure analyses in `analysis/AGENTS/`. |

## Install skills into Claude Code

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

## Install skills into Codex or Cursor

Both read `.agents/skills/` in the project and `~/.agents/skills/` globally, so one symlink
covers everything, with `git pull` as the update path:

```bash
ln -s ~/Projects/aiman/skills ~/.agents/skills          # global
./scripts/manage-skills.sh install hallmark             # or per project
```

Claude Code does not read `.agents/skills`; it uses the marketplace above.

## Working on the library

```bash
pnpm check                      # validate skills, registry, and catalog
pnpm sync                       # refresh the registry after adding or renaming a skill
pnpm release <skill> [patch|minor|major]
```

`pnpm check` runs the library rules (frontmatter, description limit, link and path
resolution), verifies the registry and the README catalog match `skills/`, and then runs
`claude plugin validate --strict`. Run it before committing.

Releasing is just a version bump in the registry: installed copies pick the new version up
on the next marketplace refresh, because Claude Code only ships an update when the `version`
string changes. Skills are versioned individually.

Requires Node >= 22.6 — `scripts/skills.ts` runs directly, no build step and no dependencies.
