# Contributing

Thanks for helping improve the kit. Usage is covered in the [README](README.md); this page only lists the rules for changing it.

## Adding or changing a skill

- A skill is a plain markdown file under `.claude/skills/<agent>/`, e.g. `.claude/skills/software-developer/my-skill.md`.
- No registration is needed: each agent's startup steps tell it to load the relevant files from its own folder, choosing by the skill's opening "Load this skill when…" line. Write that line so it says clearly when the skill applies.
- If the skill is derived from third-party material, credit it in the file header and add it to [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) with its license.

## Every change

- Add an entry to [CHANGELOG.md](CHANGELOG.md) and keep the README version badge in sync with it.
- Make README changes in **both English and Spanish**.
- **Hard invariant:** no agent, command or skill may run `git commit` or `git push`, or anything equivalent. Never add instructions that do.
- Run `python scripts/check_kit.py` before opening the PR (needs only Python 3 and git). The same script runs in CI; it checks agent/command frontmatter, `.claude/` references, skill structure (`# Skill:` title, a "Load this skill" line, sibling-skill references), relative markdown links, `Source:` headers against [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), the README install trees and the version badge against the CHANGELOG. If you add or remove a file under `.claude/` or `.github/`, update both README trees.
- Open a pull request; the PR template has the checklist.

## Releasing

Releases are cut by the maintainer; agents never tag or push. Tags start at `v2.8` and are not backfilled: earlier versions live only in the [CHANGELOG](CHANGELOG.md).

1. Finish the `## [x.y]` entry in `CHANGELOG.md` and set the README version badge to the same `x.y` (CI fails if they differ).
2. Merge that change to `master` through a pull request with `validate` passing.
3. On an up-to-date `master`, create an annotated tag on the merge commit and push it: `git tag -a vX.Y -m "vX.Y"` then `git push origin vX.Y`.
4. Publish the release from that tag, e.g. `gh release create vX.Y --title "vX.Y" --notes-file <file>`. The notes are the `## [x.y]` section of the CHANGELOG preceded by a short highlights paragraph for someone seeing the project for the first time.

A published tag is awkward to change, so confirm the CHANGELOG entry is final before step 3.
