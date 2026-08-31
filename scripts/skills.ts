#!/usr/bin/env node
// Skill library tooling: validate the library, and keep the plugin registry
// (.claude-plugin/marketplace.json) in step with skills/.
//
//   node scripts/skills.ts check              validate library + registry
//   node scripts/skills.ts sync               rewrite the registry from skills/
//   node scripts/skills.ts release <s> <lvl>  bump a skill's version
//
// Stdlib only. Node >= 22.6 runs this file directly (native type stripping).

import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const LIB = join(REPO, "skills");
const REGISTRY = join(REPO, ".claude-plugin", "marketplace.json");
const DESC_LIMIT = 1024;

// Seeds the category of a skill the first time it enters the registry. After
// that the registry is authoritative, so hand-edits survive a sync.
const DEFAULT_CATEGORY: Record<string, string> = {
  "browser-extension-builder": "frontend",
  forge: "productivity",
  "frontend-design": "frontend",
  "grill-me": "productivity",
  hallmark: "frontend",
  "pr-review": "productivity",
  "react-expert": "frontend",
  "react-native": "frontend",
  "seo-expert": "writing",
  "svg-animations": "frontend",
  "technical-writer": "writing",
  "terraform-expert": "infrastructure",
  unslop: "writing",
  "ux-copy": "writing",
  webapp: "frontend",
};

type Frontmatter = Record<string, string>;

type Entry = {
  name: string;
  source: string;
  description: string;
  version: string;
  category: string;
};

type Marketplace = {
  $schema?: string;
  name: string;
  description: string;
  owner: { name: string; url?: string };
  plugins: Entry[];
};

// `fm` is the top-level frontmatter. `meta` also carries keys nested under a
// block such as `metadata:` (top level wins), because several skills declare
// related-skills there.
type Skill = { name: string; dir: string; fm: Frontmatter | null; meta: Frontmatter };

/** Minimal YAML frontmatter reader: plain, quoted, and folded/literal blocks. */
function parseFrontmatter(text: string): { fm: Frontmatter; meta: Frontmatter } | null {
  if (!text.startsWith("---\n")) return null;
  const end = text.indexOf("\n---", 4);
  if (end === -1) return null;

  const fm: Frontmatter = {};
  const nested: Frontmatter = {};
  const lines = text.slice(4, end).split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const m = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (!m) {
      const child = /^\s+([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
      if (child && !(child[1] in nested)) nested[child[1]] = child[2].trim().replace(/^["'](.*)["']$/s, "$1");
      continue;
    }
    const [, key, rawValue] = m;
    const value = rawValue.trim();

    if ([">", ">-", ">+", "|", "|-", "|+"].includes(value)) {
      const block: string[] = [];
      while (i + 1 < lines.length && (lines[i + 1].startsWith("  ") || lines[i + 1] === "")) {
        block.push(lines[++i].trim());
      }
      fm[key] = block.filter(Boolean).join(value.startsWith("|") ? "\n" : " ");
      continue;
    }
    fm[key] = value.replace(/^["'](.*)["']$/s, "$1");
  }
  return { fm, meta: { ...nested, ...fm } };
}

function readSkills(): Skill[] {
  return readdirSync(LIB, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith("."))
    .map((d) => {
      const dir = join(LIB, d.name);
      const skillMd = join(dir, "SKILL.md");
      const parsed = existsSync(skillMd) ? parseFrontmatter(readFileSync(skillMd, "utf8")) : null;
      return { name: d.name, dir, fm: parsed?.fm ?? null, meta: parsed?.meta ?? {} };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

function walk(dir: string, suffix: string, found: string[] = []): string[] {
  for (const item of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, item.name);
    if (item.isDirectory()) walk(path, suffix, found);
    else if (item.name.endsWith(suffix)) found.push(path);
  }
  return found;
}

const stripCode = (s: string) => s.replace(/```[\s\S]*?```/g, "").replace(/`[^`\n]*`/g, "");

/** Library checks, ported from the retired skills-doctor.py. */
function checkSkill(skill: Skill, allNames: Set<string>) {
  const errors: string[] = [];
  const warnings: string[] = [];
  const skillMd = join(skill.dir, "SKILL.md");

  if (readdirSync(skill.dir).length === 0) return { errors: ["empty directory"], warnings };
  if (!existsSync(skillMd)) return { errors: ["missing SKILL.md"], warnings };

  const text = readFileSync(skillMd, "utf8");
  if (!skill.fm) {
    errors.push("SKILL.md has no YAML frontmatter");
  } else {
    const { name = "", description = "" } = skill.fm;
    const related = skill.meta["related-skills"] ?? "";
    if (!name) errors.push("frontmatter missing `name`");
    else if (name !== skill.name) errors.push(`frontmatter name \`${name}\` != directory \`${skill.name}\``);
    if (!description) errors.push("frontmatter missing `description`");
    else if (description.length > DESC_LIMIT)
      errors.push(`description is ${description.length} chars (limit ${DESC_LIMIT})`);

    for (const ref of related.split(",").map((r) => r.trim()).filter(Boolean)) {
      if (!allNames.has(ref)) warnings.push(`related-skills references \`${ref}\`, not in this library`);
    }
  }

  // Relative markdown links in every .md file must resolve.
  for (const mdFile of walk(skill.dir, ".md").sort()) {
    const body = stripCode(readFileSync(mdFile, "utf8"));
    for (const [, target] of body.matchAll(/\]\(([^)\s]+)\)/g)) {
      if (/^(https?:|mailto:|#|\/)/.test(target) || target.includes("<")) continue;
      const path = target.split("#")[0];
      if (path && !existsSync(join(dirname(mdFile), path))) {
        errors.push(`${relative(skill.dir, mdFile)}: broken link -> ${target}`);
      }
    }
  }

  // Backticked internal paths named in SKILL.md must exist.
  const paths = new Set(
    [...text.replace(/```[\s\S]*?```/g, "").matchAll(/`((?:references|assets|scripts|docs)\/[^`\s]+)`/g)].map(
      (m) => m[1],
    ),
  );
  for (const path of paths) {
    if (!path.includes("<") && !existsSync(join(skill.dir, path))) {
      errors.push(`SKILL.md: referenced path \`${path}\` does not exist`);
    }
  }

  return { errors, warnings };
}

function readRegistry(): Marketplace {
  if (!existsSync(REGISTRY)) {
    return {
      $schema: "https://www.schemastore.org/claude-code-marketplace.json",
      name: "aiman",
      description: "Rehan Haider's skill library for Claude Code, Codex, and Cursor.",
      owner: { name: "Rehan Haider", url: "https://github.com/rehanhaider" },
      plugins: [],
    };
  }
  return JSON.parse(readFileSync(REGISTRY, "utf8")) as Marketplace;
}

function writeRegistry(market: Marketplace) {
  writeFileSync(REGISTRY, `${JSON.stringify(market, null, 2)}\n`);
}

/** Registry entries derived from the library; versions and categories are preserved. */
function buildEntries(skills: Skill[], existing: Entry[]): Entry[] {
  const byName = new Map(existing.map((e) => [e.name, e]));
  return skills.map((skill) => {
    const prior = byName.get(skill.name);
    return {
      name: skill.name,
      source: `./skills/${skill.name}`,
      description: skill.fm?.description ?? "",
      // A new skill seeds its version from SKILL.md if it declares one, else 0.1.0.
      // From then on the registry owns it — bump with `release`.
      version: prior?.version ?? skill.fm?.version ?? "0.1.0",
      category: prior?.category ?? DEFAULT_CATEGORY[skill.name] ?? "productivity",
    };
  });
}

function sync() {
  const market = readRegistry();
  const before = JSON.stringify(market.plugins);
  const skills = readSkills();
  market.plugins = buildEntries(skills, market.plugins);
  writeRegistry(market);

  const added = market.plugins.filter((e) => !before.includes(`"${e.name}"`)).map((e) => e.name);
  console.log(`registry: ${market.plugins.length} skills${added.length ? ` (added ${added.join(", ")})` : ""}`);
  if (before !== JSON.stringify(market.plugins)) console.log("registry updated — commit .claude-plugin/marketplace.json");
}

function check(): number {
  const skills = readSkills();
  const allNames = new Set(skills.map((s) => s.name));
  let errors = 0;
  let warnings = 0;

  for (const skill of skills) {
    const result = checkSkill(skill, allNames);
    errors += result.errors.length;
    warnings += result.warnings.length;
    if (result.errors.length || result.warnings.length) {
      console.log(`${skill.name}:`);
      for (const e of result.errors) console.log(`  ERROR   ${e}`);
      for (const w of result.warnings) console.log(`  warning ${w}`);
    } else {
      console.log(`${skill.name}: ok`);
    }
  }

  // The registry must describe exactly the skills on disk, at the current text.
  const market = readRegistry();
  const expected = buildEntries(skills, market.plugins);
  if (JSON.stringify(expected) !== JSON.stringify(market.plugins)) {
    console.log("registry:\n  ERROR   .claude-plugin/marketplace.json is stale — run `pnpm sync`");
    errors++;
  }

  // The README catalog must list exactly the skills on disk.
  const readme = readFileSync(join(LIB, "README.md"), "utf8");
  const listed = new Set([...readme.matchAll(/^\|\s*`([a-z0-9-]+)`\s*\|/gm)].map((m) => m[1]));
  for (const name of allNames) if (!listed.has(name)) { console.log(`README:\n  ERROR   \`${name}\` is missing from the catalog`); errors++; }
  for (const name of listed) if (!allNames.has(name)) { console.log(`README:\n  ERROR   catalog lists \`${name}\`, which does not exist`); errors++; }

  // Claude Code's own manifest validation, when the CLI is available.
  const claude = spawnSync("claude", ["plugin", "validate", "--strict", REPO], { encoding: "utf8" });
  if (claude.error) {
    console.log("\nclaude CLI not found — skipped manifest validation");
  } else {
    process.stdout.write(claude.stdout ?? "");
    if (claude.status !== 0) errors++;
  }

  console.log(`\n${skills.length} skills — ${errors} error(s), ${warnings} warning(s)`);
  return errors ? 1 : 0;
}

function release(name: string, level = "patch"): number {
  const market = readRegistry();
  const entry = market.plugins.find((e) => e.name === name);
  if (!entry) {
    console.error(`No skill named '${name}' in the registry. Run \`pnpm sync\` if it is new.`);
    return 1;
  }
  const [major, minor, patch] = entry.version.split(".").map(Number);
  const bumped =
    level === "major" ? [major + 1, 0, 0] : level === "minor" ? [major, minor + 1, 0] : [major, minor, patch + 1];

  const from = entry.version;
  entry.version = bumped.join(".");
  writeRegistry(market);
  console.log(`${name}: ${from} -> ${entry.version}`);
  console.log("Commit and push — installed copies update on the next marketplace refresh.");
  return 0;
}

const [command = "check", ...rest] = process.argv.slice(2);
switch (command) {
  case "check":
    process.exit(check());
  case "sync":
    sync();
    break;
  case "release":
    if (!rest[0]) {
      console.error("Usage: release <skill> [major|minor|patch]");
      process.exit(1);
    }
    process.exit(release(rest[0], rest[1]));
  default:
    console.error(`Unknown command '${command}'. Use: check | sync | release <skill> [level]`);
    process.exit(1);
}
