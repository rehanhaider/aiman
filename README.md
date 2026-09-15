# aiman

Central store for my AI tooling: the skill library, the agent instruction files I run
globally, the analysis behind them, and the helper scripts.

Skills install two ways: copied into a project's agent directories with the `aiman` CLI,
or from the **Claude Code plugin marketplace** this repo publishes, when a project
wants a pinned version.

## Layout

| Path | What lives there |
| --- | --- |
| `skills/` | The skill library — one directory per skill, each with a `SKILL.md`. See [skills/README.md](skills/README.md) for the catalog and conventions. |
| `.claude-plugin/marketplace.json` | The registry: one entry per skill, with its version. Generated from `skills/` by `aiman sync` — don't hand-edit names, sources, or descriptions. |
| `scripts/` | `skills.ts` — the `aiman` CLI — and the usage-check scripts under `claude/` and `codex/`. |
| `snapshots/` | The instruction files as deployed — `snapshots/claude/CLAUDE.md` (`~/.claude/CLAUDE.md`) and `snapshots/codex/AGENTS.md` (`~/.codex/AGENTS.md`). |
| `analysis/` | Working notes the instruction files came out of, e.g. the per-model failure analyses in `analysis/AGENTS/`. |

## Install the CLI once

From this repo:

```bash
npm link
```

That puts `aiman` on your PATH. The library always lives here; `check` / `sync` /
`release` operate on this repo. `link` / `unlink` always target the directory you
are standing in.

## Install skills into a project

`cd` into any project, then:

```bash
aiman link                 # all skills → .claude/skills and .agents/skills
aiman link forge hallmark  # just these
aiman unlink forge         # remove
```

Claude Code reads `.claude/skills`; Codex and Cursor read `.agents/skills`. Both
get a real copy (not a symlink). Re-run `aiman link` after editing a skill here
so project copies refresh.

A leftover symlink is replaced with a copy. A directory this command previously
installed is refreshed. Any other real directory is never overwritten; it is
reported and skipped. `aiman unlink` only removes copies (or leftover symlinks)
this library installed.

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

Codex and Cursor have no plugin equivalent — `aiman link` is their only path.
Claude Code does not read `.agents/skills`, which is why the installer writes both.

## Working on the library

```bash
aiman check                      # validate skills, registry, and catalog
aiman sync                       # refresh the registry after adding or renaming a skill
aiman release <skill> [patch|minor|major]
aiman link / unlink              # from any project directory
```

`aiman check` runs the library rules (frontmatter, description limit, link and path
resolution), verifies the registry and the README catalog match `skills/`, and then runs
`claude plugin validate --strict`. Run it before committing.

Releasing is just a version bump in the registry: installed copies pick the new version up
on the next marketplace refresh, because Claude Code only ships an update when the `version`
string changes. Skills are versioned individually.

Requires Node >= 22.6 — `scripts/skills.ts` runs directly, no build step and no
dependencies. `npm link` is the only install step.
