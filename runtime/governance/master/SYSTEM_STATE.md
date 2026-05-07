# SAPIANTA System State

## Document Role

This is a canonical state document. It records the current authoritative governance memory state only.

Historical milestone summaries, ADRs, and governance lineage files remain append-only lineage documents. They are not collapsed or deleted by this canonical state.

## Current Architecture Status

SAPIANTA has a deterministic governance architectural memory foundation under `runtime/governance/master/`.

This layer records current system state, architectural decisions, governance maturity, architecture boundaries, development focus, and lineage pointers for future Codex, Claude, GPT, and human review sessions.

This layer is documentation-only. It is not runtime governance, not self-modifying cognition, not runtime automation, and not an enforcement surface.

## Meta-Root Memory Clarification

Architectural memory is meta-root memory for the `/sapianta` workspace.

`runtime/governance/master/` is the existing physical location of governance memory, but its current architectural role is orchestration memory, meta-governance memory, cross-domain lineage memory, ADR lineage, roadmap memory, and domain memory.

Runtime is not governance memory. Governance memory is not runtime execution. Domain memory belongs to orchestration lineage and must not be treated as domain activation.

The authoritative meta-root architecture index is tracked in:
- `ARCHITECTURE/WORKSPACE_BOUNDARIES.md`
- `ARCHITECTURE/REPOSITORY_AUTHORITIES.md`
- `ARCHITECTURE/CANONICAL_ROOTS.md`
- `ARCHITECTURE/WORKSPACE_INTEGRITY_LAYER.md`

## Current Governance State

Governance memory is stable, frozen, deterministic, replay-safe, dormant, and observational only.

Frozen means stable for future reference and append-only lineage updates. It does not mean runtime activation.

ACTIVE has no runtime meaning. Any use of the word ACTIVE in this architectural memory indicates current human development focus or documentation status only. It does not activate runtime enforcement, policy execution, approval logic, arbitration, or automated reads.

## Frozen Runtime And Governance Components

- Decision Spine
- Policy engine behavior
- Runtime governance activation
- Enforcement activation
- Approval validation execution
- Governance arbitration
- Any runtime mutation path

These components remain unchanged by governance memory canonicalization.

## Active Focus

Current active development focus is the server/demo branch.

Primary product focus:
- AI Decision Validator productization
- cinematic enterprise demo
- audit viewer polish
- EU AI Act positioning
- explainability UX
- enterprise trust narrative

Governance memory remains frozen while product-facing demo work advances.

Dormant domain state memory now exists for Trading and Explosion under `runtime/governance/master/domains/`.

## Stable Components

- Meta-root architecture index under `ARCHITECTURE/`
- Architectural memory structure under `runtime/governance/master/`
- ADR lineage structure
- Milestone categorization structure
- Deterministic milestone workflow
- Governance maturity map
- Architecture boundaries
- Commit preparation guidance
- Governance sidecar concept
- PatternMemory
- ControlCandidateRegistry
- ShadowValidation
- PromotionLifecycle
- GovernanceReplayVerifier
- Lifecycle legality verification lineage
- Replay verification lineage
- Append-only validation lineage
- Deterministic hashing validation lineage
- Lineage integrity validation lineage

## Experimental Components

- Governance graph visualization
- Governance-native cognition
- AI-generated ADR draft assistance
- Governance replay UI
- Adaptive governance pressure
- Explosion as a possible future acceleration domain

Experimental components are ideas only. They are not accepted architecture unless later promoted through human-reviewed ADRs.

## Important Constraints

- Documentation-only
- Deterministic only
- Append-only philosophy
- No runtime mutation
- No Decision Spine changes
- No policy engine changes
- No enforcement activation
- No runtime integration
- No active reads
- No governance activation
- Dormant governance only
- Observational governance only
- Inspection-first
- Human-governed milestone and commit workflow

## Current Product Positioning

The market-facing product is AI Decision Validator.

The current positioning emphasizes enterprise decision validation, auditability, explainability, governance readiness, EU AI Act alignment, demo clarity, and enterprise trust.

Governance internals remain dormant and observational while productization proceeds.

## Current Branch Separation

Current milestone branch: `feature/governance-evolution-loop`

The server/demo branch is intentionally separated from dormant governance foundation work. This separation allows product-facing demo surfaces to evolve without implying runtime governance activation or modifying core governance decisions.

## Latest Governance Milestone

Latest governance milestone: `GOVERNANCE_MEMORY_FOUNDATION_FINALIZATION_V1`

Milestone file: `runtime/governance/master/MILESTONES/governance/GOVERNANCE_MEMORY_FOUNDATION_FINALIZATION_V1.md`

Milestone tag: `governance-memory-foundation-v1`

## Latest Research Milestone

Latest research milestone: `TRADING_EXPLOSION_DOMAIN_STATE_INVESTIGATION_V1`

Milestone file: `runtime/governance/master/MILESTONES/research/TRADING_EXPLOSION_DOMAIN_STATE_INVESTIGATION_V1.md`

Milestone tag: `domain-state-investigation-v1`

Research lineage status: physically re-applied as documentation-only architectural memory.

Persistence status: confirmed in workspace as documentation-only domain lineage state.

## Current Governance Maturity

Current maturity:
- governance memory: implemented and frozen
- governance foundations: implemented
- governance testing lineage: implemented
- replay verification: implemented
- lifecycle legality: implemented
- architecture boundaries: implemented
- governance maturity map: implemented
- commit preparation guidance: implemented
- runtime governance activation: NOT IMPLEMENTED
- governed enforcement: NOT IMPLEMENTED
- approval execution: NOT IMPLEMENTED
- runtime integration: NOT IMPLEMENTED
- governance arbitration: NOT IMPLEMENTED
- Trading domain: LEVEL 2 dormant validation/simulation domain
- Explosion domain: LEVEL 1 conceptual latent acceleration domain

Governance maturity tracked in:
`runtime/governance/master/GOVERNANCE_MATURITY_MAP.md`

Architecture boundaries tracked in:
`runtime/governance/master/ARCHITECTURE_BOUNDARIES.md`

Domain state reports:
- `runtime/governance/master/domains/trading/SYSTEM_STATE.md`
- `runtime/governance/master/domains/explosion/SYSTEM_STATE.md`

Domain reports are inspection-only and do not activate runtime behavior.

## Standard Milestone Workflow

After every major milestone, the human-governed workflow is:

1. Commit
2. Git tag
3. Milestone summary
4. ADR update if semantic decisions changed
5. `SYSTEM_STATE.md` update
6. `CURRENT_FOCUS.md` update
7. `ROADMAP.md` update
8. `GOVERNANCE_MATURITY_MAP.md` update if maturity status changed

Purpose: create persistent architectural lineage and reduce AI context loss across long-horizon development.

This workflow is human-governed. Do not automate milestone generation logic, ADR generation, git commits, git pushes, tag creation, runtime mutation, or governance activation.
