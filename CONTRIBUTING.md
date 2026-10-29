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
- Open a pull request; the PR template has the checklist.
