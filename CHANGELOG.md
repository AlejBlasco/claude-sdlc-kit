# Changelog

All notable changes to this kit are documented in this file. Format
loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
