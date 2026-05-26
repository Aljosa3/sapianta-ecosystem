# CAPABILITY_GOVERNANCE_MATRIX_V1_ADR

## Context

AiGOL/SAPIANTA now has constitutional models for governed identity and semantic exposure. Future local node, sovereign replay, provider federation, and execution policy milestones require a matrix that maps capability classes to identity authority, payload class, exposure level, routing scope, approval requirements, and replay visibility.

Capability access cannot be governed by a single permission bit. Runtime eligibility depends on who is acting, which organization and domain scope applies, what payload class is involved, which exposure level is permitted, where cognition may route, what approval is required, and what replay evidence may be visible or exported.

## Decision

Define `CAPABILITY_GOVERNANCE_MATRIX_V1` as a documentation-only constitutional governance milestone.

The matrix defines:

- canonical capability classes;
- capability eligibility dimensions;
- payload-aware capability restrictions;
- exposure-aware capability restrictions;
- routing scope governance;
- approval-aware capability governance;
- replay-aware capability governance;
- local versus cloud execution governance;
- organization policy overlays;
- fail-closed capability resolution.

This milestone does not implement policy engine logic, routing execution, provider federation, capability enforcement, local runtime execution, API endpoints, replay implementation changes, or runtime execution changes.

## Consequences

Future execution policy engines, provider routing, local node execution, and sovereign replay layers must evaluate capability eligibility before execution eligibility.

Capability eligibility must remain partitioned from execution authority. A capability may be eligible only after identity, authority, governance scope, payload class, exposure level, routing, approval, and replay visibility have been resolved.

Unresolved capability eligibility, routing eligibility, authority, payload class, exposure level, or replay visibility must fail closed.

## Non-Goals

- Implement a policy engine.
- Implement capability execution.
- Implement provider orchestration.
- Implement routing execution.
- Implement provider federation.
- Implement local runtime execution.
- Add API endpoints.
- Modify runtime execution code.
- Modify replay implementation.

## Rejected Alternatives

- Unrestricted capability execution: rejected because capability use must be identity-, payload-, exposure-, approval-, and replay-governed.
- Payload-blind capability routing: rejected because payload classification determines local-only, cloud eligibility, replay, and approval constraints.
- Cloud-first execution by default: rejected because confidential, regulated, and secret payloads require sovereign local governance.
- Replay without capability partitioning: rejected because replay visibility, retention, redaction, and export depend on capability class.
- Frontend-only permissions: rejected because capability governance must operate at runtime and replay boundaries, not only interface access.
- Trust-based implicit capability access: rejected because trust level does not replace authority, payload classification, exposure, or approval resolution.
- Provider execution without routing governance: rejected because semantic routing and provider use must be resolved before provider execution.
- Capability access without authority resolution: rejected because identity and authority are constitutional prerequisites.
