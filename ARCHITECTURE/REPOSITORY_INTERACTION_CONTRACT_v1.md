# SAPIANTA Repository Interaction Contract v1

## Document Role

This document defines how SAPIANTA ecosystem repositories may communicate.

It is documentation-only. It does not implement imports, runtime integration, automation, or promotion logic.

## Repository Classes

Meta root:
`~/work/sapianta`

Governed runtime:
`~/work/sapianta/sapianta_system`

Domain repositories:
- `~/work/sapianta/sapianta-domain-trading`
- `~/work/sapianta/sapianta-domain-credit`
- future `~/work/sapianta/sapianta-domain-*`

Factory:
`~/work/sapianta/sapianta_factory`

Governance memory:
`~/work/sapianta/runtime/governance/master`

## Allowed Interaction Patterns

Runtime may consume:
- approved domain contracts
- approved domain schemas
- approved deterministic validators
- approved replay artifacts

Domains may expose:
- deterministic APIs
- contracts
- schemas
- replay-safe simulations
- validation artifacts

Factory may emit:
- proposals
- candidate artifacts
- experiment summaries
- non-authoritative patches

Governance memory may record:
- ADR lineage
- milestone lineage
- approval decisions
- promotion rationale
- domain state
- replay lineage pointers

Meta root may coordinate:
- topology documentation
- roadmap memory
- repository authority metadata
- cross-domain lineage references

## Forbidden Interaction Patterns

Factory must not mutate runtime directly.

Domains must not mutate governance memory, Decision Spine behavior, or policy engine behavior.

Meta-root memory must not execute runtime behavior.

Governance memory must not activate runtime governance.

Runtime must not consume domain artifacts unless their contracts and lineage are approved.

No repository may silently import mutable authority from another repository.

## Import Authority Rules

Allowed import direction must be explicit and bounded:
- runtime may import approved domain contracts
- runtime may import approved runtime-owned validators
- domains may import shared contracts only when explicitly allowed
- factory may read public contracts for proposal generation
- governance memory may reference artifacts as lineage, not executable imports

Forbidden import direction:
- domains importing runtime internals for mutation
- factory importing runtime internals for mutation
- factory importing governance memory as an execution authority
- governance memory importing runtime modules for active execution
- runtime importing unapproved factory proposals

## Promotion Boundaries

Promotion from factory or domain work into runtime requires:
- human review
- deterministic artifact identity
- contract validation
- replay-safety review
- milestone update
- ADR update if semantic architecture changes
- explicit approval before runtime consumption

## Approval Semantics

Approval is a governance memory event unless and until future runtime-safe approval execution is implemented.

Approval records do not automatically activate runtime behavior.
