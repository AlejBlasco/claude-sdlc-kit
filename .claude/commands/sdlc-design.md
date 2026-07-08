---
description: "SDLC phase 2 — Design. Turns a requirements document (or description) into an implementation guide via the Software Architect agent."
argument-hint: "[requirements-file-path | issue/story URL | free-text requirements]"
---

# sdlc-design

Input received: `$ARGUMENTS`

Delegate this entire task to the **software-architect** subagent using the
Task tool (`subagent_type: "software-architect"`). Do not perform the design
work yourself in this top-level context.

Before delegating:

1. If `.claude/sdlc.config.yaml` exists, note its contents so you can pass
   `documentation` and `paths.design` to the subagent. Otherwise use the
   defaults (`documentation: es`, `paths.design: docs/sdlc/design`).
2. Classify `$ARGUMENTS`:
   - Path to an existing `.md` file (typically produced by `sdlc-analysis`):
     tell the subagent to read it as the requirements source.
   - URL to a tracker item: tell the subagent to fetch it.
   - Free-text requirements: pass verbatim.
3. Remind the subagent to inspect the current repository structure before
   proposing technologies/patterns, so the design fits the existing codebase.

Pass all of this to the subagent in a single, clear task description,
including the reminder that it must never run `git commit` or `git push`.

After the subagent finishes, relay its summary to the user, including the
path of the design document it created and any risks/open decisions it
flagged, and mention `sdlc-development` as the likely next step.
