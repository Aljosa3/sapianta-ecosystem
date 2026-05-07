# SAPIANTA Workspace Boundaries

## Document Role

This document defines the canonical workspace boundary model for the SAPIANTA meta root.

It is documentation-only. It does not move runtime files, activate governance, change execution behavior, grant autonomous authority, or introduce automation.

## META ROOT

Canonical root:
`/sapianta`

Purpose:
- workspace orchestration
- architectural memory
- cross-domain lineage
- governance memory
- roadmap and milestone memory
- AI-readable system memory
- domain memory
- ADR lineage
- repository authority indexing

Authoritative meta-root documentation:
- `ARCHITECTURE/`
- `runtime/governance/master/`

Important clarification:
`runtime/governance/master/` is physically located under `runtime/`, but its current architectural role is meta-root memory. It is not the governed runtime kernel and must not be treated as runtime execution.

Repository interaction flow references:
- `ARCHITECTURE/REPOSITORY_INTERACTION_FLOW_v1.md`
- `ARCHITECTURE/DOMAIN_LIFECYCLE_MODEL_v1.md`
- `ARCHITECTURE/FACTORY_PROPOSAL_FLOW_v1.md`
- `ARCHITECTURE/RUNTIME_ACCEPTANCE_GATE_v1.md`

## GOVERNED RUNTIME ROOT

Canonical root:
`/sapianta/sapianta_system`

Purpose:
- deterministic runtime kernel
- replay-safe execution
- Decision Spine
- policy engine
- validators
- governance runtime substrate
- active execution substrate

Boundary:
Runtime execution authority belongs to the governed runtime root only. Meta-root memory cannot activate, mutate, or implicitly govern runtime execution.

## FACTORY ROOT

Canonical root:
`/sapianta/sapianta_factory`

Purpose:
- sandboxed AI generation
- isolated mutation proposals
- bounded autonomous experimentation
- proposal generation without authority

Boundary:
The factory can propose changes, but it has no authority to activate runtime behavior, mutate governed runtime semantics, modify Decision Spine behavior, or promote generated artifacts without human review.

## DOMAIN ROOTS

Canonical pattern:
`/sapianta/sapianta-domain-*`

Examples:
- `/sapianta/sapianta-domain-trading`
- `/sapianta/sapianta-domain-credit`

Purpose:
- capability domains
- replay-safe domain modules
- activation-gated domain logic
- domain-specific validation surfaces

Boundary:
Domain roots are capability containers. They are not production authority by default, not autonomous execution systems, and not governance activation surfaces.

## Current Boundary Rules

- Architectural memory is meta-root memory.
- Runtime is not governance memory.
- Governance memory is not runtime execution.
- Domain memory belongs to orchestration lineage.
- Factory output is proposal-only.
- No workspace may silently assume authority over another workspace.
- Any cross-root integration requires explicit human review, ADR updates when semantic decisions change, and milestone lineage.
