# SAPIANTA Canonical Roots

## Document Role

This document defines canonical root locations for AI tooling, human review, and deterministic workspace navigation.

It is documentation-only. It does not move files, rewrite repositories, activate governance, or introduce automation.

## Canonical Meta Root

Root:
`/sapianta`

Current local workspace:
`/home/pisarna/work/sapianta`

Role:
- orchestration root
- architectural memory root
- cross-domain lineage root
- governance memory root
- roadmap and milestone root
- workspace authority root

## Canonical Governance Memory Root

Authoritative index:
`/sapianta/ARCHITECTURE/`

Existing physical memory location:
`/sapianta/runtime/governance/master/`

Role:
- AI-readable architectural memory
- governance memory
- system state memory
- current focus memory
- roadmap memory
- ADR lineage
- milestone lineage
- domain state memory

Clarification:
The existing `runtime/governance/master/` path is a physical location for meta-root memory. It is not runtime execution and must not be interpreted as governance activation.

## Canonical Runtime Root

Root:
`/sapianta/sapianta_system`

Role:
- deterministic runtime kernel
- replay-safe execution
- Decision Spine
- policy engine
- validators
- governance runtime substrate

## Canonical Factory Root

Root:
`/sapianta/sapianta_factory`

Role:
- sandboxed AI generation
- isolated mutation proposals
- bounded experimentation
- proposal generation without authority

## Canonical Domain Roots

Pattern:
`/sapianta/sapianta-domain-*`

Examples:
- `/sapianta/sapianta-domain-trading`
- `/sapianta/sapianta-domain-credit`

Role:
- capability domains
- replay-safe domain modules
- activation-gated domain logic

## AI Tooling Requirements

Before applying changes, AI tooling must verify:
- current workspace root
- intended canonical root
- repository authority for the target files
- whether the change is documentation-only or runtime-affecting
- whether milestone or ADR lineage must remain append-only
- whether filesystem writes actually persisted

AI tooling must not infer authority from:
- an open IDE tab
- a conversational summary
- a path name alone
- generated but unpersisted patch text
- stale prior-session memory
