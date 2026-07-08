---
description: "SDLC phase 6 — Implementation and Maintenance. Reserved for future use (deployment/release/maintenance), currently a no-op via the DevOps Engineer agent."
argument-hint: "[free-text description] (optional — this phase is not yet implemented)"
---

# sdlc-implementation

Input received: `$ARGUMENTS`

Delegate to the **devops-engineer** subagent using the Task tool
(`subagent_type: "devops-engineer"`). This agent is currently a stub by
design — do not attempt to perform deployment, release, or maintenance
actions yourself in its place.

Pass `$ARGUMENTS` (if any) to the subagent so it can acknowledge what was
asked for in its "not yet implemented" response.

Relay the subagent's response to the user as-is.
