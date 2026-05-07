# SAPIANTA Commit Guidelines

These guidelines support deterministic commit preparation. They do not execute git commands and do not automate commits, tags, pushes, milestone generation, runtime mutation, or governance activation.

## Commit Naming Conventions

Use a category prefix followed by a concise deterministic summary:

- `[GOVERNANCE] ...`
- `[RUNTIME] ...`
- `[PRODUCT] ...`
- `[UI] ...`
- `[DEPLOYMENT] ...`
- `[SECURITY] ...`
- `[INFRASTRUCTURE] ...`
- `[RESEARCH] ...`

Example:

`[GOVERNANCE] Add architectural memory foundation`

## Tag Naming Conventions

Use lowercase kebab-case:

- `governance-foundation-v1`
- `runtime-determinism-v2`
- `product-demo-v1`
- `ui-audit-viewer-v1`
- `deployment-fastapi-v1`
- `security-review-v1`

## Milestone Categorization Rules

Store each milestone summary under the most appropriate category:

- Governance decisions, ADR structure, dormant governance lineage: `MILESTONES/governance/`
- Runtime determinism, replay behavior, execution mechanics: `MILESTONES/runtime/`
- Product positioning, AI Decision Validator evolution, enterprise flow: `MILESTONES/product/`
- UI, audit viewer, cinematic landing page, demo interface: `MILESTONES/ui/`
- FastAPI, hosting, release packaging, server/demo deployment: `MILESTONES/deployment/`
- Trust, threat modeling, compliance risk, access controls: `MILESTONES/security/`
- Build systems, environments, repository structure, operational tooling: `MILESTONES/infrastructure/`
- Exploratory research and non-accepted experiments: `MILESTONES/research/`

## Separating Milestone Types

Governance milestones must not include runtime activation, policy engine changes, Decision Spine changes, or enforcement activation unless explicitly approved by a future ADR.

Runtime milestones must be separated from governance milestones when they change execution behavior, replay mechanics, or runtime determinism.

UI milestones must be separated from governance milestones when they change presentation, navigation, visual design, demo flow, or audit viewer experience without changing governance semantics.

Deployment milestones must be separated from UI, runtime, and governance milestones when they change hosting, release, server setup, environment configuration, or operational packaging.

## Avoiding Mixed Commits

Avoid commits that combine unrelated categories. Split changes when they cross architectural boundaries.

Do not mix:

- Governance memory and runtime behavior
- UI design and policy engine logic
- Deployment setup and Decision Spine changes
- Product positioning and enforcement activation
- Experimental ideas and accepted ADR decisions

If a change must cross categories, prepare an explicit summary that lists each affected category, the reason separation is not practical, the affected ADRs, and the milestone category chosen for lineage.

## Deterministic Commit Preparation

Codex may prepare:

- Proposed commit message
- Proposed tag
- Proposed milestone category
- Proposed affected ADRs

Humans must manually review and execute:

- `git commit`
- `git tag`
- `git push`

Automatic git execution is not allowed by this guidance.
