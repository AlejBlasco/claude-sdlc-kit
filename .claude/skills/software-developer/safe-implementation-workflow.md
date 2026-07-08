# Skill: Safe Implementation Workflow

Load this skill for any change that touches more than a trivial single
file, or anything security/data-sensitive.

## Workflow

1. Restate the plan as a short checklist before touching files.
2. Make changes in logical, reviewable units — even though you won't commit
   them, structure your work as if each unit were a future commit.
3. After each unit, run whatever fast feedback loop exists (unit tests,
   type-checker, linter) rather than waiting until the very end.
4. Re-read your own diff before declaring the task done — check for leftover
   debug code, unused imports, and consistency with the design doc.

## Risk flags — slow down and double-check when touching

- Authentication/authorization logic.
- Payment or billing code.
- Data deletion or destructive migrations.
- Anything that changes a public API contract.

## Reminder

Never stage, commit, or push. If you're tempted to run `git commit` "just to
checkpoint progress," don't — leave the working tree as-is and mention the
state of the changes in your summary instead.
