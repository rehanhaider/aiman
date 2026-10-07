#!/usr/bin/env node
// aiman — skill library CLI. Install once with `npm link` from this repo, then
// run `aiman` from any project to copy skills into that project's agent dirs.
//
//   aiman check              validate library + registry (this repo)
//   aiman registry           rewrite the registry from skills/
//   aiman release <s> <lvl>  bump a skill's version
//   aiman link [names...]    copy skills into .claude/skills and .agents/skills
//   aiman unlink [names...]  remove those copies
//   aiman deploy             copy snapshots/ to the live instruction files
//   aiman apply              make this device match global.json, then deploy
//   aiman sync               push this repo, then apply on every device in global.json
//
// Stdlib only. Node >= 22.6 runs this file directly (native type stripping).

import { spawnSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  readlinkSync,
  realpathSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { homedir, hostname } from "node:os";
import { dirname, join, relative, resolve, sep } from "node:path";
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

function registry() {
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
    console.log("registry:\n  ERROR   .claude-plugin/marketplace.json is stale — run `aiman registry`");
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
    console.error(`No skill named '${name}' in the registry. Run \`aiman registry\` if it is new.`);
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

// Always the project you are standing in. Claude Code reads .claude/skills;
// Codex and Cursor read .agents/skills.
function targets(): { label: string; dir: string }[] {
  const root = process.cwd();
  return [
    { label: "claude", dir: join(root, ".claude", "skills") },
    { label: "codex/cursor", dir: join(root, ".agents", "skills") },
  ];
}

// Marks a copied skill so unlink/refresh only touch installs this library owns.
const MARKER = ".aiman-source";

function writeMarker(target: string, skillDir: string) {
  writeFileSync(join(target, MARKER), `${skillDir}\n`);
}

function ownedInstall(target: string, skillDir: string): boolean {
  const marker = join(target, MARKER);
  return existsSync(marker) && readFileSync(marker, "utf8").trim() === skillDir;
}

function installCopy(skillDir: string, target: string) {
  cpSync(skillDir, target, { recursive: true });
  writeMarker(target, skillDir);
}

function selectSkills(names: string[]): Skill[] | null {
  const skills = readSkills();
  if (names.length === 0) return skills;
  const chosen: Skill[] = [];
  for (const name of names) {
    const skill = skills.find((s) => s.name === name);
    if (!skill) {
      console.error(`No skill named '${name}'.`);
      return null;
    }
    chosen.push(skill);
  }
  return chosen;
}

function link(names: string[]): number {
  const skills = selectSkills(names);
  if (!skills) return 1;
  let failed = 0;

  for (const { label, dir } of targets()) {
    mkdirSync(dir, { recursive: true });
    console.log(`${label}: ${dir}`);
    for (const skill of skills) {
      const target = join(dir, skill.name);
      const stat = lstatSync(target, { throwIfNoEntry: false });

      if (!stat) {
        installCopy(skill.dir, target);
        console.log(`  copy     ${skill.name}`);
        continue;
      }

      // Leftover symlink from the old installer: replace with a real copy.
      if (stat.isSymbolicLink()) {
        const current = readlinkSync(target);
        rmSync(target);
        installCopy(skill.dir, target);
        console.log(`  replace  ${skill.name} (was symlink ${current})`);
        continue;
      }

      if (stat.isDirectory() && ownedInstall(target, skill.dir)) {
        rmSync(target, { recursive: true });
        installCopy(skill.dir, target);
        console.log(`  refresh  ${skill.name}`);
        continue;
      }

      console.log(`  SKIP     ${skill.name} — a real directory is already there`);
      failed++;
    }
  }
  if (failed) console.log(`\n${failed} skipped — move or delete the real directory, then re-run.`);
  return failed ? 1 : 0;
}

function unlink(names: string[]): number {
  const skills = selectSkills(names);
  if (!skills) return 1;

  for (const { label, dir } of targets()) {
    if (!existsSync(dir)) continue;
    console.log(`${label}: ${dir}`);
    for (const skill of skills) {
      const target = join(dir, skill.name);
      const stat = lstatSync(target, { throwIfNoEntry: false });
      if (!stat) continue;

      const ours =
        (stat.isSymbolicLink() && realpathSync(target) === skill.dir) ||
        (stat.isDirectory() && ownedInstall(target, skill.dir));
      if (!ours) {
        console.log(`  SKIP     ${skill.name} — not an install from this library`);
        continue;
      }
      rmSync(target, { recursive: true });
      console.log(`  removed  ${skill.name}`);
    }
  }
  return 0;
}

// Each snapshot and the live file it is deployed to.
const SNAPSHOTS = [
  { source: join(REPO, "snapshots", "claude", "CLAUDE.md"), target: join(homedir(), ".claude", "CLAUDE.md") },
  { source: join(REPO, "snapshots", "codex", "AGENTS.md"), target: join(homedir(), ".codex", "AGENTS.md") },
];

function deploy(): number {
  for (const { source, target } of SNAPSHOTS) {
    const next = readFileSync(source, "utf8");
    const current = existsSync(target) ? readFileSync(target, "utf8") : null;
    if (current === next) {
      console.log(`unchanged  ${target}`);
      continue;
    }
    if (current !== null) spawnSync("diff", ["-u", target, source], { stdio: "inherit" });
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, next);
    console.log(`${current === null ? "created" : "updated"}    ${target}`);
  }
  return 0;
}

// The global set: skills symlinked into the user-level agent dirs on every
// device, and the devices `sync` reaches over SSH.
const GLOBAL = join(REPO, "global.json");
const GLOBAL_DIRS = [join(homedir(), ".claude", "skills"), join(homedir(), ".agents", "skills")];

type Global = { skills: string[]; devices: string[] };

const isThisDevice = (device: string) => device.toLowerCase() === hostname().toLowerCase();

/** Make this device's global skill dirs match global.json, then deploy the instruction files. */
function apply(): number {
  const global = JSON.parse(readFileSync(GLOBAL, "utf8")) as Global;
  // selectSkills([]) means "all", but an empty global set means none.
  const skills = global.skills.length ? selectSkills(global.skills) : [];
  if (!skills) return 1;
  const wanted = new Set(global.skills);
  let failed = 0;

  for (const dir of GLOBAL_DIRS) {
    mkdirSync(dir, { recursive: true });
    console.log(dir);
    for (const skill of skills) {
      const target = join(dir, skill.name);
      const stat = lstatSync(target, { throwIfNoEntry: false });
      if (stat?.isSymbolicLink() && resolve(dir, readlinkSync(target)) === skill.dir) continue;
      if (stat && !stat.isSymbolicLink()) {
        console.log(`  SKIP     ${skill.name} — a real directory is already there`);
        failed++;
        continue;
      }
      if (stat) rmSync(target);
      symlinkSync(skill.dir, target);
      console.log(`  link     ${skill.name}`);
    }

    // Only symlinks into this library are ours to remove; anything else stays.
    for (const name of readdirSync(dir)) {
      const target = join(dir, name);
      if (wanted.has(name) || !lstatSync(target).isSymbolicLink()) continue;
      if (!resolve(dir, readlinkSync(target)).startsWith(LIB + sep)) continue;
      rmSync(target);
      console.log(`  unlink   ${name}`);
    }
  }

  deploy();
  return failed ? 1 : 0;
}

const git = (...args: string[]) => spawnSync("git", ["-C", REPO, ...args], { encoding: "utf8" });

/** Publish this repo, then run `apply` here and on every other device in global.json. */
function syncDevices(): number {
  if (git("status", "--porcelain").stdout.trim()) {
    console.error("aiman has uncommitted changes — commit them, then re-run `aiman sync`.");
    return 1;
  }
  git("fetch", "--quiet");
  const [behind, ahead] = git("rev-list", "--left-right", "--count", "@{u}...HEAD").stdout.trim().split(/\s+/).map(Number);
  if (behind && ahead) {
    console.error("aiman has diverged from its upstream — rebase or merge, then re-run `aiman sync`.");
    return 1;
  }
  if (behind && git("pull", "--quiet", "--ff-only").status !== 0) return 1;
  if (ahead && spawnSync("git", ["-C", REPO, "push", "--quiet"], { stdio: "inherit" }).status !== 0) return 1;

  const global = JSON.parse(readFileSync(GLOBAL, "utf8")) as Global;
  const remoteRepo = relative(homedir(), REPO);
  const results: [string, boolean][] = [];

  for (const device of global.devices) {
    console.log(`\n== ${device}`);
    if (isThisDevice(device)) {
      results.push([device, apply() === 0]);
      continue;
    }
    // A login shell, so version managers such as mise put node on PATH.
    const remote = `bash -lc 'cd ~/${remoteRepo} && git pull --quiet --ff-only && node scripts/skills.ts apply'`;
    const ssh = spawnSync("ssh", ["-o", "BatchMode=yes", "-o", "ConnectTimeout=8", device, remote], { stdio: "inherit" });
    results.push([device, ssh.status === 0]);
  }

  console.log("");
  for (const [device, ok] of results) console.log(`${ok ? "ok      " : "FAILED  "}${device}`);
  return results.every(([, ok]) => ok) ? 0 : 1;
}

const [command = "check", ...rest] = process.argv.slice(2);
switch (command) {
  case "check":
    process.exit(check());
  case "registry":
    registry();
    break;
  case "release":
    if (!rest[0]) {
      console.error("Usage: aiman release <skill> [major|minor|patch]");
      process.exit(1);
    }
    process.exit(release(rest[0], rest[1]));
  case "link":
  case "unlink":
    process.exit(command === "link" ? link(rest) : unlink(rest));
  case "deploy":
    process.exit(deploy());
  case "apply":
    process.exit(apply());
  case "sync":
    process.exit(syncDevices());
  default:
    console.error(
      `Unknown command '${command}'. Use: aiman check | registry | release <skill> [level] | link [names...] | unlink [names...] | deploy | apply | sync`,
    );
    process.exit(1);
}
