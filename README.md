# aiman

Central store for my AI tooling: the skill library, the agent instruction files I run
globally, the analysis behind them, and the helper scripts.

## Layout

| Path | What lives there |
| --- | --- |
| `skills/` | The skill library — one directory per skill, each with a `SKILL.md`. See [skills/README.md](skills/README.md) for the catalog and conventions. |
| `scripts/` | Tooling: `manage-skills.sh` (list/install/uninstall/doctor), `skills-doctor.py` (library validator), plus the usage-check scripts under `claude/` and `codex/`. |
| `snapshots/` | The instruction files as deployed — `snapshots/claude/CLAUDE.md` (`~/.claude/CLAUDE.md`) and `snapshots/codex/AGENTS.md` (`~/.codex/AGENTS.md`). |
| `analysis/` | Working notes the instruction files came out of, e.g. the per-model failure analyses in `analysis/AGENTS/`. |

## Installing skills into a project

```bash
cd /path/to/project
/path/to/aiman/scripts/manage-skills.sh install hallmark   # symlinks into ./.agents/skills
```

`SKILLS_SOURCE_DIR` and `SKILLS_TARGET_DIR` override the source library and the install target.

## Before committing a skill change

```bash
scripts/manage-skills.sh doctor
```

Zero errors required; warnings are advisory.
