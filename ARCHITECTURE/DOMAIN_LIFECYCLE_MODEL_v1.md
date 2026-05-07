# SAPIANTA Domain Lifecycle Model v1

## Document Role

This document defines lifecycle states for SAPIANTA domain repositories.

It is documentation-only. It does not activate domains, implement lifecycle enforcement, or modify runtime semantics.

## Lifecycle States

### CONCEPT

A domain capability exists as an idea or architectural need.

Authority:
No execution authority.

### DRAFT

Initial contracts, notes, schemas, tests, or artifacts exist.

Authority:
Documentation and proposal authority only.

### VALIDATION

The domain has deterministic validation artifacts or tests.

Authority:
Validation-only. No runtime activation.

### SIMULATION

The domain can produce replay-safe or deterministic simulation evidence.

Authority:
Simulation-only. No production execution.

### REVIEW

The domain is under governance-aware review for possible promotion.

Authority:
Review-only. No activation.

### APPROVED

The domain artifact or contract has explicit governance approval for a bounded purpose.

Authority:
Approved for the specified scope only.

### INTEGRATED

The domain artifact has been integrated through an approved deterministic interface.

Authority:
Integration authority is bounded by the approved contract.

### ACTIVE

The domain is approved for a defined active role.

Important:
ACTIVE does not automatically imply runtime execution. ACTIVE requires explicit governance approval, runtime boundary validation, and activation lineage for any execution behavior.

### DEPRECATED

The domain or artifact remains in lineage but is no longer preferred for new work.

Authority:
Historical and compatibility authority only.

### REVOKED

The domain or artifact has been explicitly withdrawn from approved use.

Authority:
No new use. Historical lineage remains append-only.

## Allowed Transitions

- CONCEPT to DRAFT
- DRAFT to VALIDATION
- VALIDATION to SIMULATION
- VALIDATION to REVIEW
- SIMULATION to REVIEW
- REVIEW to APPROVED
- APPROVED to INTEGRATED
- INTEGRATED to ACTIVE
- APPROVED to DEPRECATED
- INTEGRATED to DEPRECATED
- ACTIVE to DEPRECATED
- APPROVED to REVOKED
- INTEGRATED to REVOKED
- ACTIVE to REVOKED

## Governance-Gated Transitions

These transitions require explicit governance review:
- REVIEW to APPROVED
- APPROVED to INTEGRATED
- INTEGRATED to ACTIVE
- any state to REVOKED

These transitions require runtime boundary review if they affect execution:
- APPROVED to INTEGRATED
- INTEGRATED to ACTIVE

## Forbidden Transitions

- CONCEPT directly to ACTIVE
- DRAFT directly to ACTIVE
- VALIDATION directly to ACTIVE
- SIMULATION directly to ACTIVE
- factory proposal directly to ACTIVE
- domain artifact directly to runtime without approval
- any dormant domain to runtime execution without activation lineage

## Dormant Domain Rule

Dormant domains remain dormant until explicitly promoted through governance-gated lifecycle transitions.

Trading and Credit domain repositories must not be treated as runtime-active solely because they exist in the workspace.
