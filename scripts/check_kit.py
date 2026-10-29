#!/usr/bin/env python3
"""Consistency checks for the kit's own files.

Run from anywhere:  python scripts/check_kit.py
Exits 1 if any check fails; prints one line per problem.

Checks:
  1. Frontmatter of every agent and command.
  2. Every `.claude/...` path mentioned in agents/commands exists.
  3. The install trees in the README (EN and ES) match the real files.
  4. The README version badge matches the latest CHANGELOG entry.

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


def read(path):
    return Path(path).read_text(encoding="utf-8")


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
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
    for folder in (".claude/agents", ".claude/commands"):
        for path in sorted((ROOT / folder).glob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            for ref in sorted(set(pattern.findall(read(path)))):
                ref = ref.rstrip(".")
                if any(c in ref for c in "<>*"):
                    continue  # placeholder such as .claude/skills/<agent>/
                if not (ROOT / ref).exists():
                    errors.append(f"{rel}: references '{ref}', which does not exist")


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
        for f in tracked_files()
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
    for check in (check_frontmatter, check_references, check_readme_tree, check_version):
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
