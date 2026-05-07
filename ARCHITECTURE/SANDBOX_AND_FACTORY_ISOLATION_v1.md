# SAPIANTA Sandbox and Factory Isolation v1

## Document Role

This document defines isolation semantics for the SAPIANTA factory and sandbox environment.

It is documentation-only. It does not activate the factory, add automation, or implement mutation workflows.

## Factory Role

Canonical workspace:
`~/work/sapianta/sapianta_factory`

The factory is a sandbox-only proposal generation environment.

It may be used for:
- isolated experimentation
- candidate artifact generation
- bounded autonomous exploration
- mutation proposal drafting
- non-authoritative validation experiments

## Factory Non-Authority

The factory has no authority over:
- runtime execution
- governance memory
- Decision Spine behavior
- policy engine behavior
- domain activation
- production deployment
- commit or tag execution

Factory output is not accepted architecture until reviewed and promoted through explicit governance-aware lineage.

## Sandbox Isolation Semantics

Factory work must remain isolated from:
- production runtime state
- governed runtime internals
- governance memory mutation
- domain production authority
- launcher activation authority

Sandbox outputs must be treated as proposals, not executable decisions.

## Forbidden Factory Behavior

The factory must not:
- mutate runtime directly
- mutate governance memory directly
- activate domains
- activate governance
- promote its own output
- execute production workflows
- create background loops with authority
- bypass repository interaction contracts

## Proposal Promotion

Factory proposal promotion requires:
- human review
- deterministic artifact identity
- repository authority check
- validation evidence
- replay-safety review
- milestone lineage
- ADR update if semantic architecture changes

Promotion remains future workflow design. This document does not implement it.
