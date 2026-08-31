# Skills Library

Agent skills for Claude Code / Cursor / Codex-style assistants. Each skill is a directory with a
`SKILL.md` (frontmatter `name` + `description` drive triggering) and optional `references/`,
`assets/`, and `scripts/`.

## Usage

**Claude Code** installs these from the plugin marketplace this repo publishes:

```bash
claude plugin marketplace add rehanhaider/aiman
claude plugin install hallmark@aiman [--scope project]
```

**Codex and Cursor** read `.agents/skills/`, so symlink them instead:

```bash
scripts/manage-skills.sh list                  # list all skills
scripts/manage-skills.sh install hallmark      # symlink into ./.agents/skills
scripts/manage-skills.sh install-all
scripts/manage-skills.sh uninstall hallmark
```

`SKILLS_SOURCE_DIR` / `SKILLS_TARGET_DIR` override either side. See the
[repo README](../README.md) for updates, versioning, and the global `~/.agents/skills` setup.

## Catalog

### Design & frontend

| Skill | What it does |
| --- | --- |
| `hallmark` | Anti-AI-slop design system for greenfield pages: 22 themes, 69-gate slop test, audit/redesign/study verbs |
| `frontend-design` | Production UI inside an Astro 6 + React islands + Tailwind v4 + DaisyUI v5 stack, token-pure theming |
| `webapp` | Full web apps in the emcp/navinier house style: TanStack Start + Query + Zustand, Base UI primitives, Tailwind v4 tokens, dark-first, bundled starter kit |
| `svg-animations` | Handcrafted SVG graphics and animation (SMIL, CSS, path drawing, morphing) |
| `ux-copy` | Write and audit interface microcopy — buttons, errors, empty states, onboarding |
| `react-expert` | React 18/19, Server Components, React Compiler, state management, testing |
| `react-native` | React Native + Expo (SDK 54-era calibrated defaults, verify-first) |
| `browser-extension-builder` | Manifest V3 extensions: service-worker lifecycle, content scripts, store review |

### Backend & infrastructure

| Skill | What it does |
| --- | --- |
| `terraform-expert` | HashiCorp-aligned Terraform: modules, tests, imports, state discipline |

### Writing & content

| Skill | What it does |
| --- | --- |
| `technical-writer` | Technical articles via Sewing & Reaping: kernel discovery, outlines, SEO/GEO/AEO, visuals |
| `seo-expert` | SEO improve/recover/audit for existing sites + 30-entry implementation playbook |

### Delivery & review

| Skill | What it does |
| --- | --- |
| `pr-review` | Review a PR/branch for real defects, prioritize by impact, post the outcome to GitHub |
| `forge` | Drive one issue (Linear, GitHub, or in-repo docs) to a PR and loop review→rectify until clean; stops before merge. `--tranches` splits the work into an approved plan and waits for feedback after each tranche |

### Meta & utilities

| Skill | What it does |
| --- | --- |
| `grill-me` | Relentless plan-stress-testing interview with a decision log artifact |
| `unslop` | Strip AI tells out of any writing before it ships |

## Library conventions

- Frontmatter `name` must match the directory name; `description` stays under 1024 characters
  and says *when to use* the skill, not just what it is.
- Deep material goes in `references/` (loaded on demand), not in `SKILL.md`.
- Every relative link and `references/...` path must resolve — `pnpm check` enforces this,
  along with the registry and this catalog; run it before committing.
- Evals live in the skill's own `evals/` directory; retired guides live in `.archive/`.
- A new skill needs a `pnpm sync` to enter the registry; it starts at version `0.1.0`.
