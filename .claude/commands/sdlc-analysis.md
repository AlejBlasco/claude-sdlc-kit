---
description: "SDLC phase 1 — Requirements Analysis. Turns a description or a tracker link into a GIVEN-WHEN-THEN requirements document via the Business Analyst agent."
argument-hint: "[file-path | issue/story URL | free-text description]"
---

# sdlc-analysis

Input received: `$ARGUMENTS`

Delegate this entire task to the **business-analyst** subagent using the Task
tool (`subagent_type: "business-analyst"`). Do not perform the requirements
analysis yourself in this top-level context — the subagent owns this phase.

Before delegating:

1. If `.claude/sdlc.config.yaml` exists, note its contents so you can pass the
   relevant settings (`documentation` language, `paths.requirements`) to the
   subagent as part of its task context. If it doesn't exist, tell the
   subagent to use the documented defaults (`documentation: es`,
   `paths.requirements: docs/sdlc/requirements`).
2. Classify `$ARGUMENTS`:
   - If it looks like a path to an existing `.md` file, tell the subagent to
     read that file as its primary input.
   - If it looks like a URL (Azure DevOps, GitHub, GitLab, Jira, etc.), tell
     the subagent to fetch it as its primary input.
   - Otherwise, treat it as a free-text description and pass it verbatim.

Pass all of this to the subagent in a single, clear task description,
including the reminder that it must never run `git commit` or `git push`.

After the subagent finishes, relay its summary to the user, including the
path of the requirements document it created and any open questions it
flagged.
