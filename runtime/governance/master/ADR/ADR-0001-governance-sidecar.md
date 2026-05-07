# ADR-0001: Governance Sidecar

## STATUS

Accepted as dormant architectural foundation.

## CONTEXT

SAPIANTA needs governance memory and validation concepts that can be inspected without changing runtime behavior. Embedding governance directly into runtime execution would increase activation risk and blur the boundary between architectural lineage and enforcement.

The market-facing product is AI Decision Validator, so governance must support auditability and decision validation positioning without prematurely becoming runtime control logic.

ACTIVE has no runtime meaning.

## DECISION

Represent governance as a sidecar architectural foundation. The sidecar records decisions, constraints, lineage, and validation concepts adjacent to runtime systems, but it does not execute, enforce, mutate, or read actively at runtime.

Governance remains dormant, replay-safe, and observational only.

## CONSEQUENCES

The architecture gains persistent memory and reviewability while preserving runtime safety. Future activation remains possible only through explicit human-reviewed ADRs and implementation milestones.

The sidecar cannot be treated as enforcement until a later accepted ADR changes that status.

## NON-GOALS

- Runtime governance activation
- Policy engine changes
- Decision Spine changes
- Automated enforcement
- Runtime mutation
