# SAPIANTA Ecosystem Topology Specification v1

## Document Role

This document defines the governed ecosystem topology for the SAPIANTA meta-root workspace.

It is documentation-only. It does not implement runtime orchestration, activate governance, change execution behavior, or introduce autonomous behavior.

## Topology Summary

SAPIANTA is a governed AI operating ecosystem composed of:
- meta-root workspace
- governed runtime system
- isolated domain repositories
- isolated factory and sandbox environment
- governance lineage layer

The ecosystem is designed as federated deterministic AI infrastructure. Each repository has bounded authority, explicit mutation limits, and replay-aware lineage expectations.

## Extension Layers

Repository interaction flow and lifecycle semantics are defined in:
- `ARCHITECTURE/REPOSITORY_INTERACTION_FLOW_v1.md`
- `ARCHITECTURE/DOMAIN_LIFECYCLE_MODEL_v1.md`
- `ARCHITECTURE/FACTORY_PROPOSAL_FLOW_v1.md`
- `ARCHITECTURE/RUNTIME_ACCEPTANCE_GATE_v1.md`

These documents extend this topology specification without redefining authority, activation, or runtime semantics.

Governed artifact identity and replay lineage continuity are defined in:
- `ARCHITECTURE/ARTIFACT_IDENTITY_MODEL_v1.md`
- `ARCHITECTURE/REPLAY_LINEAGE_PROPAGATION_v1.md`
- `ARCHITECTURE/PROMOTION_LINEAGE_CONTINUITY_v1.md`
- `ARCHITECTURE/AUDIT_CONTINUITY_MODEL_v1.md`
- `ARCHITECTURE/GOVERNED_ARTIFACT_INHERITANCE_v1.md`

These documents extend lineage semantics without redefining repository topology or activation authority.

## Meta Root Authority

Canonical workspace:
`~/work/sapianta`

Role:
- ecosystem coordination root
- governance lineage root
- topology root
- orchestration root
- architecture memory root
- roadmap and milestone root
- cross-domain memory root

Not responsible for:
- runtime execution
- Decision Spine execution
- policy engine execution
- autonomous activation
- production mutation

The meta root records authority and lineage. It does not execute governed runtime behavior.

## Governed Runtime Authority

Canonical workspace:
`~/work/sapianta/sapianta_system`

Role:
- runtime authority
- deterministic execution authority
- governance enforcement authority when explicitly implemented
- validator runtime authority
- production/demo runtime authority

Forbidden:
- uncontrolled external mutation
- factory authority over runtime
- autonomous governance mutation
- implicit activation from architectural memory
- policy or Decision Spine mutation without explicit human-reviewed lineage

## Domain Repository Model

Canonical examples:
- `~/work/sapianta/sapianta-domain-trading`
- `~/work/sapianta/sapianta-domain-credit`

Role:
- isolated bounded domains
- deterministic contract domains
- replay-safe experimentation domains
- capability-specific logic roots
- activation-gated domain surfaces

Domain repositories are non-authoritative for governance mutation and runtime activation.

Future domain onboarding requires:
- domain boundary documentation
- deterministic contract definition
- replay lineage model
- activation requirements
- human review before runtime consumption

## Factory Model

Canonical workspace:
`~/work/sapianta/sapianta_factory`

Role:
- sandbox-only proposal generation environment
- isolated experimentation layer
- bounded autonomous exploration surface
- proposal generation without authority

Forbidden:
- production mutation
- runtime mutation
- governance mutation
- autonomous activation
- direct promotion into runtime
- direct modification of domain authority

Factory output remains proposal-only until reviewed and promoted through explicit governance-aware workflow.

## Governance Lineage Layer

Canonical memory:
`~/work/sapianta/runtime/governance/master`

Meta-root architecture index:
`~/work/sapianta/ARCHITECTURE`

Role:
- append-only milestone lineage
- ADR lineage
- system state memory
- roadmap memory
- current focus memory
- domain state memory
- governance maturity memory

Governance memory is not runtime execution and has no activation authority.

## Ecosystem Constraints

- Documentation-only
- Deterministic only
- Replay-safe intent
- Explicit repository authority
- Bounded mutation surfaces
- Append-only governance lineage
- No implicit runtime activation
- No autonomous promotion
- No uncontrolled cross-repository mutation
