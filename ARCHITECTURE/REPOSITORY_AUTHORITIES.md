# SAPIANTA Repository Authorities

## Document Role

This document records which workspace root has authority over each architectural responsibility.

It is documentation-only and does not introduce runtime integration, enforcement, automation, or autonomous authority.

## Authority Map

### Runtime Execution

Authority:
`/sapianta/sapianta_system`

Owns:
- deterministic runtime execution
- replay-safe execution substrate
- Decision Spine behavior
- policy engine behavior
- runtime validators
- governed runtime integration points

Forbidden:
- runtime execution must not be activated from architectural memory
- Decision Spine behavior must not be changed by meta-root documentation
- policy engine behavior must not be changed by meta-root documentation
- runtime integration must not be inferred from milestone or ADR presence

### Governance Memory

Authority:
`/sapianta`

Canonical documentation surfaces:
- `/sapianta/ARCHITECTURE/`
- `/sapianta/runtime/governance/master/`

Owns:
- architectural memory
- governance memory
- ADR lineage
- milestone lineage
- roadmap memory
- current focus memory
- domain state memory
- repository authority memory

Forbidden:
- governance memory must not execute
- governance memory must not enforce
- governance memory must not activate runtime governance
- governance memory must not create uncontrolled mutation paths
- governance memory must not imply autonomous approval execution

### Sandbox Mutation Proposals

Authority:
`/sapianta/sapianta_factory`

Owns:
- sandboxed AI generation
- isolated proposal creation
- bounded experimentation
- candidate artifact generation

Forbidden:
- factory output has no runtime authority
- factory output has no governance authority
- factory output must not directly mutate governed runtime behavior
- factory output must not promote itself
- factory output must not bypass human review

### Domain Capability Logic

Authority pattern:
`/sapianta/sapianta-domain-*`

Owns:
- domain-specific contracts
- domain-specific validators
- domain-specific simulations
- domain-specific replay-safe modules
- activation-gated capability logic

Forbidden:
- domain roots must not modify Decision Spine behavior
- domain roots must not modify policy engine behavior
- domain roots must not activate themselves
- domain roots must not claim production authority without explicit activation lineage
- domain roots must not bypass governed runtime boundaries

## Cross-Root Mutation Rules

- Verify the active workspace root before writing.
- Verify the target file belongs to the intended authority root.
- Preserve documentation-only constraints when editing meta-root memory.
- Preserve append-only lineage for milestones and ADRs.
- Do not collapse historical lineage into canonical state documents.
- Do not execute git commits, tags, pushes, or activation commands automatically.
- Do not treat conversational plans as persisted filesystem changes.
