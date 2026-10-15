# Agent instructions

## `skills/mizcode-reviewer/` is a copy

`skills/mizcode-reviewer/` is a built copy of the skill in `Mizanic/mizcode-reviewer`. It is here only so `aiman sync` deploys it. Do not edit it in this repo, because the next refresh overwrites it.

To change the skill, change it in `Mizanic/mizcode-reviewer`. After that change merges, refresh the copy by following that repo's `AGENTS.md`.

This copy is temporary. When the mizcode-reviewer plugin ships (Mizanic/mizcode-reviewer#38), delete `skills/mizcode-reviewer/`, remove it from `global.json` and the catalog in `skills/README.md`, run `npm run registry`, and point forge at the plugin's skill.
