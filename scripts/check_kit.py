#!/usr/bin/env python3
"""Consistency checks for the kit's own files.

Run from anywhere:  python scripts/check_kit.py
Exits 1 if any check fails; prints one line per problem.

Level 1 (static) checks:
  1. Frontmatter of every agent and command.
  2. Every `.claude/...` path mentioned in agents, commands and skills exists.
  3. Skill structure: folder matches an agent, `# Skill:` title and a
     "Load this skill" line near the top, and sibling-skill references resolve.
  4. Relative markdown links in every .md file resolve.
  5. Third-party skills (`Source:` header) and THIRD_PARTY_NOTICES.md agree.
  6. The install trees in the README (EN and ES) match the real files.
  7. The README version badge matches the latest CHANGELOG entry.

Standard library only.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AGENT_KEYS = ("name", "description", "model", "color")
COMMAND_KEYS = ("description", "argument-hint")

# Files that live in this repo but are not part of what users copy, so the
# README install tree does not list them.
REPO_ONLY = (
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/pull_request_template.md",
    ".github/workflows/",
)

TREE_ROOTS = ("your-repo/", "tu-repo/")

# Files that skills mention by bare name but that live in the user's own repo,
# not in this one.
USER_REPO_FILES = ("CLAUDE.md", "STYLE.md")


def read(path):
    return Path(path).read_text(encoding="utf-8")


def repo_files():
    """Tracked files plus new, not-ignored ones, so local runs see work in progress."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def frontmatter(text):
    """Return the top-level `key: value` pairs of a leading --- block, or None."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        m = re.match(r"([A-Za-z][\w-]*):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return None  # never closed


def check_frontmatter(errors):
    for folder, keys in ((".claude/agents", AGENT_KEYS), (".claude/commands", COMMAND_KEYS)):
        for path in sorted((ROOT / folder).glob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            fields = frontmatter(read(path))
            if fields is None:
                errors.append(f"{rel}: missing or unclosed frontmatter")
                continue
            for key in keys:
                if not fields.get(key):
                    errors.append(f"{rel}: frontmatter key '{key}' is missing or empty")
            if folder.endswith("agents") and fields.get("name") and fields["name"] != path.stem:
                errors.append(f"{rel}: name '{fields['name']}' does not match the file name")


def check_references(errors):
    pattern = re.compile(r"\.claude/[A-Za-z0-9_./<>*-]*")
    for folder in (".claude/agents", ".claude/commands", ".claude/skills"):
        for path in sorted((ROOT / folder).rglob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            for ref in sorted(set(pattern.findall(read(path)))):
                ref = ref.rstrip(".")
                if any(c in ref for c in "<>*"):
                    continue  # placeholder such as .claude/skills/<agent>/
                if not (ROOT / ref).exists():
                    errors.append(f"{rel}: references '{ref}', which does not exist")


def skill_files():
    """Skill files proper: every .md under .claude/skills except folder READMEs."""
    return sorted(
        p for p in (ROOT / ".claude/skills").rglob("*.md") if p.name != "README.md"
    )


def check_skills(errors):
    skills_dir = ROOT / ".claude/skills"
    for folder in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        if not (ROOT / ".claude/agents" / f"{folder.name}.md").exists():
            errors.append(
                f".claude/skills/{folder.name}/: no agent .claude/agents/{folder.name}.md"
            )
    for path in skill_files():
        rel = path.relative_to(ROOT).as_posix()
        lines = read(path).splitlines()
        title = lines[0] if lines else ""
        if not title.startswith("# Skill:"):
            errors.append(f"{rel}: first line must start with '# Skill:'")
        reserved = "(reserved" in title
        if not reserved and not any("Load this skill" in l for l in lines[:20]):
            errors.append(f"{rel}: no 'Load this skill' line in the first 20 lines")


def check_skill_refs(errors):
    """Backticked `*.md` names in a skill must point to an existing file."""
    pattern = re.compile(r"`([^`\s]+\.md)`")
    for path in skill_files():
        rel = path.relative_to(ROOT).as_posix()
        for ref in sorted(set(pattern.findall(read(path)))):
            if any(c in ref for c in "<>*") or ref.startswith(("http", ".claude/")):
                continue  # placeholders; .claude/ paths are covered by check_references
            if ref in USER_REPO_FILES:
                continue
            bases = (path.parent, ROOT / ".claude/skills", ROOT, ROOT / ".github/ISSUE_TEMPLATE")
            if not any((b / ref).exists() for b in bases):
                errors.append(f"{rel}: references '{ref}', which does not exist")


def check_links(errors):
    link = re.compile(r"\]\(([^)\s]+)\)")
    fence = re.compile(r"```.*?```", re.S)
    for rel in repo_files():
        if not rel.endswith(".md"):
            continue
        base = (ROOT / rel).parent
        for target in sorted(set(link.findall(fence.sub("", read(ROOT / rel))))):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not (base / target.split("#")[0]).exists():
                errors.append(f"{rel}: link to '{target}', which does not exist")


def check_third_party(errors):
    notices = read(ROOT / "THIRD_PARTY_NOTICES.md")
    listed = set(re.findall(r"^\| `(\.claude/skills/[^`]+)`", notices, re.M))
    for rel in sorted(listed):
        if not (ROOT / rel).exists():
            errors.append(f"THIRD_PARTY_NOTICES.md: lists '{rel}', which does not exist")
    for path in skill_files():
        rel = path.relative_to(ROOT).as_posix()
        has_source = any(l.startswith("Source:") for l in read(path).splitlines()[:15])
        if has_source and rel not in listed:
            errors.append(f"{rel}: has a 'Source:' header but is not in THIRD_PARTY_NOTICES.md")
        if rel in listed and not has_source:
            errors.append(f"{rel}: is in THIRD_PARTY_NOTICES.md but has no 'Source:' header")


def parse_tree(block):
    """Parse a `├──`/`└──` tree into (files, wildcard_dirs, dirs) of relative paths."""
    files, wildcards, dirs = set(), set(), set()
    stack = []
    for line in block[1:]:
        m = re.match(r"^([│ ]*)[├└]── (.+?)\s*$", line)
        if not m:
            continue
        depth = len(m.group(1)) // 4
        name = m.group(2)
        stack = stack[:depth]
        if name.endswith("/..."):
            wildcards.add("/".join(stack + [name[:-4]]))
        elif name.endswith("/"):
            dirs.add("/".join(stack + [name[:-1]]))
            stack.append(name[:-1])
        else:
            files.add("/".join(stack + [name]))
    return files, wildcards, dirs


def tree_blocks(readme):
    """Yield the lines of each fenced block that opens with an install-tree root."""
    for m in re.finditer(r"```[^\n]*\n(.*?)```", readme, re.S):
        lines = m.group(1).splitlines()
        if lines and lines[0].strip() in TREE_ROOTS:
            yield lines


def check_readme_tree(errors):
    actual = {
        f
        for f in repo_files()
        if f.startswith((".claude/", ".github/")) and not f.startswith(REPO_ONLY)
    }
    blocks = list(tree_blocks(read(ROOT / "README.md")))
    if len(blocks) != 2:
        errors.append(f"README.md: expected 2 install trees (EN and ES), found {len(blocks)}")
    for n, block in enumerate(blocks, 1):
        files, wildcards, _ = parse_tree(block)
        label = f"README.md install tree #{n} ({block[0].strip()})"
        for f in sorted(files):
            if f not in actual:
                errors.append(f"{label}: lists '{f}', which does not exist")
        for w in sorted(wildcards):
            if not any(a.startswith(w + "/") for a in actual):
                errors.append(f"{label}: lists '{w}/...', which has no files")
        for a in sorted(actual):
            covered = a in files or any(a.startswith(w + "/") for w in wildcards)
            if not covered:
                errors.append(f"{label}: does not list '{a}'")


def check_version(errors):
    badge = re.search(r"badge/version-([0-9][0-9.]*)-", read(ROOT / "README.md"))
    entry = re.search(r"^## \[([0-9][0-9.]*)\]", read(ROOT / "CHANGELOG.md"), re.M)
    if not badge:
        errors.append("README.md: version badge not found")
    if not entry:
        errors.append("CHANGELOG.md: no '## [x.y]' entry found")
    if badge and entry and badge.group(1) != entry.group(1):
        errors.append(
            f"README badge says {badge.group(1)} but latest CHANGELOG entry is {entry.group(1)}"
        )


def main():
    errors = []
    for check in (
        check_frontmatter,
        check_references,
        check_skills,
        check_skill_refs,
        check_links,
        check_third_party,
        check_readme_tree,
        check_version,
    ):
        check(errors)
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        print(f"\n{len(errors)} problem(s) found.")
        return 1
    print("All kit checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
