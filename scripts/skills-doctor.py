#!/usr/bin/env python3
"""skills-doctor — validate every skill in this library.

Usage: skills-doctor.py [LIBRARY_DIR]      (defaults to <repo>/skills)

Checks per skill:
  E1  SKILL.md exists (and the directory isn't empty)
  E2  frontmatter present with `name:` and `description:`
  E3  frontmatter name matches the directory name
  E4  description is <= 1024 characters
  E5  every relative markdown-link target in every .md file exists
  E6  every backticked `references/|assets/|scripts/|docs/` path in SKILL.md exists
  W1  related-skills entries that don't exist in this library (warning)

Exit 0 when no errors (warnings allowed), 1 otherwise. Stdlib only.
"""

import re
import sys
from pathlib import Path

DESC_LIMIT = 1024
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")
BACKTICK_PATH = re.compile(r"`((?:references|assets|scripts|docs)/[^`\s]+)`")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fm: dict[str, str] = {}
    lines = text[4:end].splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value in (">", ">-", "|", "|-"):
                block: list[str] = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
                    block.append(lines[i].strip())
                    i += 1
                fm[key] = " ".join(filter(None, block))
                continue
            fm[key] = value.strip("\"'")
        elif re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", lines[i]):
            m2 = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
            fm.setdefault(m2.group(1), m2.group(2).strip())
        i += 1
    return fm


def check_skill(skill_dir: Path, all_names: set[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_dir / "SKILL.md"

    if not any(skill_dir.iterdir()):
        return ["empty directory (delete it or add a SKILL.md)"], []
    if not skill_md.exists():
        return ["missing SKILL.md"], []

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append("SKILL.md has no YAML frontmatter")
    else:
        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not name:
            errors.append("frontmatter missing `name`")
        elif name != skill_dir.name:
            errors.append(f"frontmatter name `{name}` != directory name `{skill_dir.name}`")
        if not desc:
            errors.append("frontmatter missing `description`")
        elif len(desc) > DESC_LIMIT:
            errors.append(f"description is {len(desc)} chars (limit {DESC_LIMIT})")

        related = fm.get("related-skills", "")
        for ref in filter(None, (r.strip() for r in related.split(","))):
            if ref not in all_names:
                warnings.append(f"related-skills references `{ref}` which is not in this library")

    # E5: relative markdown links in every .md file must resolve
    for md_file in sorted(skill_dir.rglob("*.md")):
        body = md_file.read_text(encoding="utf-8")
        # ignore link targets inside fenced code blocks and inline code spans
        body_no_code = re.sub(r"```.*?```", "", body, flags=re.S)
        body_no_code = re.sub(r"`[^`\n]*`", "", body_no_code)
        for target in MD_LINK.findall(body_no_code):
            if re.match(r"^(https?:|mailto:|#|/)", target) or "<" in target:
                continue
            path = target.split("#", 1)[0]
            if not path:
                continue
            if not (md_file.parent / path).exists():
                rel = md_file.relative_to(skill_dir)
                errors.append(f"{rel}: broken link -> {target}")

    # E6: backticked internal paths in SKILL.md must exist
    text_no_code = re.sub(r"```.*?```", "", text, flags=re.S)
    for path in set(BACKTICK_PATH.findall(text_no_code)):
        if "<" in path:  # placeholder patterns like references/components/<code>-<slug>.md
            continue
        if not (skill_dir / path).exists():
            errors.append(f"SKILL.md: referenced path `{path}` does not exist")

    return errors, warnings


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "skills"
    skill_dirs = sorted(
        d for d in root.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "node_modules"
    )
    all_names = {d.name for d in skill_dirs}

    total_errors = 0
    total_warnings = 0
    for d in skill_dirs:
        errors, warnings = check_skill(d, all_names)
        total_errors += len(errors)
        total_warnings += len(warnings)
        if errors or warnings:
            print(f"{d.name}:")
            for e in errors:
                print(f"  ERROR   {e}")
            for w in warnings:
                print(f"  warning {w}")
        else:
            print(f"{d.name}: ok")

    print(f"\n{len(skill_dirs)} skills — {total_errors} error(s), {total_warnings} warning(s)")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
