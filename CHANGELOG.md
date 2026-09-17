# Changelog

All notable changes to this kit are documented in this file. Format
loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.6] - 2026-09-17

### Added

- **Fact verification hard rule** (`business-analyst`, `software-architect`):
  both agents must verify any concrete literal they're not 100% certain of
  (model/product IDs, package versions, API endpoints, header names...)
  with WebSearch/WebFetch against an official source before writing it
  down, and never park a publicly verifiable fact as an `Open question`/
  open decision just because they're unsure. Closes a real incident where
  a retired model ID and an invented package version reached the
  development/testing phase undetected — both agents already had
  WebSearch/WebFetch available and simply weren't using them.
- **Naming-collision check** (`software-architect`): mandatory workflow
  step to grep every new project/namespace/type name against the
  framework/BCL's reserved names (e.g. `System.*`, `Application`,
  `Window`, `Console`, `MessageBox` for .NET/WPF) and against the project
  and type names already present in `src/`, before closing the design
  document — moved from being a lucky catch left to the agent's own
  initiative to an explicit required step.
- **Definition of Done, carried per issue** (`business-analyst` →
  `software-architect` → `qa-engineer`): the Business Analyst names, per
  issue, any check that can only be confirmed against a real external
  system no pipeline agent has access to (a real API call, a real
  credential, a live third-party service) as an explicit Definition of
  Done item, separate from the Acceptance Criteria. The Software
  Architect carries it forward into the design doc unchanged. The QA
  Engineer closes it with real evidence — `[x]` only for tests that are
  actually green or a manual step it actually ran itself (build, curl,
  CLI) with the real observed output, `[ ]` **PENDIENTE** with a reason
  for anything that genuinely needs a real external system/credential.
  Closes a gap where an AC like "the API responds 200" stayed as an
  unexecuted note in a doc. (First tried as a generic `definitionOfDone`
  checklist in `sdlc.config.yaml`; replaced with this per-issue,
  doc-carried design after finding an independent, more mature
  implementation of the same idea already in production in a downstream
  repo using this kit — credit due there.)
- **Acceptance Criteria → Test coverage table** (`qa-engineer`): for
  issues with a formal AC list reachable from the input chain, the
  Testing Summary now includes an explicit table mapping each
  GIVEN-WHEN-THEN scenario to the test (or the manual validation) that
  covers it, instead of relying on the Technical Writer noticing gaps as
  a side effect of reading everything downstream.
- **Ambiguity-escalation calibration** (new hard rule 5 on
  `business-analyst` and `software-architect`): resolve
  implementation-level ambiguity with a documented default; escalate as
  an `Open question:`/open decision only genuine product/scope ambiguity
  that changes user-visible behavior or the public surface. Moves this
  rule from the delegating prompt (fragile — depended on the orchestrator
  remembering to ask for it) into the agents themselves.

### Changed

- `README.md` (English and Spanish) — new sections documenting fact
  verification, the naming-collision check, the per-issue Definition of
  Done, Acceptance Criteria → Test traceability, and the
  ambiguity-escalation calibration; version badge bumped `2.5` → `2.6`.

### Verified, no action taken

- Whether custom subagents auto-load the project's `CLAUDE.md` hierarchy,
  to see if delegation prompts in `.claude/commands/*.md` could be
  shortened to "follow CLAUDE.md" instead of repeating rules. Confirmed
  true per Claude Code's own docs (code.claude.com/docs/en/sub-agents:
  every subagent loads the full CLAUDE.md hierarchy the main conversation
  loads, unless its frontmatter sets `omitClaudeMd`, which none of this
  kit's agents do). But none of this kit's delegation prompts actually
  repeat CLAUDE.md content — the one-line reminders they do repeat (e.g.
  "never git commit/push") duplicate each agent's own Hard rule #1, not
  CLAUDE.md, and are cheap enough (one sentence, defense-in-depth against
  a costly mistake) not to be worth trimming.

## [2.5] - 2026-09-01

### Added

- **Frontend/UI quality skills**, extracted from an external freelance
  digital-product-system reference and folded into the existing agents
  (no new pipeline, no new agents — using the kit's own documented
  extension mechanism of adding skill files under
  `.claude/skills/<agent>/`):
  - `software-architect`: `blazor-production-architecture.md` (render
    mode choice, layering, security/performance review).
  - `software-developer`: `premium-design-constitution.md`,
    `style-direction.md`, `design-system-tokens.md`, `motion-design.md`,
    `responsive-engineering.md`, `tailwind-css-conventions.md`,
    `frontend-production-quality.md`, `blazor-ui-system.md`.
  - `qa-engineer`: `accessibility-auditor.md`,
    `frontend-performance-audit.md`, `anti-generic-ai-visual-critique.md`,
    `production-readiness-checklist.md`, `blazor-data-api-review.md`.
  - `technical-writer`: `docs-as-product.md` (structure for
    customer-facing product documentation).
  - `business-analyst`: `commercial-product-definition.md` (audience,
    positioning, pricing hypotheses, licensing for sellable deliverables).

- **"Ad hoc" secondary modes** on the two agents above whose existing
  contract only produced one document shape, so the new skills are
  actually reachable:
  - `business-analyst` — an ad hoc **Commercial Product Definition**
    mode for a sellable/reusable deliverable, alongside the standard
    GIVEN-WHEN-THEN requirements flow.
  - `qa-engineer` — an ad hoc **Product Quality Audits** mode
    (accessibility, performance, visual critique, production readiness,
    Blazor data/API review) alongside the standard unit-test-coverage
    flow used by `sdlc-testing`.

- **External design-taste skills**, sourced from public open-source
  Agent Skills repositories and adapted to drop the framework-specific
  (React/Next.js/GSAP) mechanics that don't apply to this kit's
  .NET/Blazor stack:
  - `software-developer/emil-kowalski-motion-craft.md` — animation
    decision framework, easing/duration rules, component-level motion
    patterns. From Emil Kowalski's `emil-design-eng` skill
    ([github.com/emilkowalski/skills](https://github.com/emilkowalski/skills),
    MIT).
  - `software-developer/design-modes.md` — the Persuade / Operate /
    Read / Experience surface classification. Conceptual extract from
    Paul Bakaus's Impeccable
    ([github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable),
    Apache-2.0).
  - `software-developer/anti-slop-frontend-checklist.md` and
    `software-developer/redesign-protocol.md` — brief-inference
    practice, the AI-tell catalog, and the audit-before-touching
    redesign process. From Taste Skill
    ([github.com/Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill),
    MIT).
  - `qa-engineer/anti-slop-preflight-audit.md` — condensed,
    stack-agnostic pre-flight checklist, also from Taste Skill.

- `CHANGELOG.md` (this file).

### Changed

- `README.md` (English and Spanish) — "Ecosystem skills" table updated
  to list every new skill per agent; version badge bumped `2.4` → `2.5`.

### Deliberately not included

- Notion and mobile-specific content from the freelance reference
  (`06-notion`, `05-mobile`) — this kit has no Notion or mobile
  agent/workflow to attach them to.
- The freelance reference's own orchestration layer (`00-core`,
  `10-workflows`, `11-prompts`) — redundant with this kit's existing
  6-phase `sdlc-*` pipeline.
- Impeccable's full tooling (its `npx` CLI, Node setup scripts, and its
  35 reference playbooks) and Taste Skill's image-generation sub-skills
  (`imagegen-frontend-*`, `brandkit`) — both require external tooling
  (a CLI installer, an image-generation model) this kit doesn't wire up;
  only their portable, text-only guidance was kept.
