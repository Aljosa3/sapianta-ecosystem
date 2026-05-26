# GOVERNED_IDENTITY_AND_AUTHORITY_MODEL_V1

## Purpose

The Governed Identity and Authority Model v1 defines runtime-governance identity for AiGOL/SAPIANTA.

Runtime-governance identity is not only login identity. A login can identify a user, but runtime governance must determine what that identity may request, route, approve, inspect, retain, export, or block inside governed execution boundaries.

User authority affects runtime eligibility, capability routing, approval requirements, replay visibility, policy scope, retention authority, and audit export authority. These decisions must be explicit, replay-visible, deterministic, and fail closed.

This milestone is documentation and evidence only. It does not implement authentication, authorization enforcement, API endpoints, runtime execution changes, provider activation changes, or capability behavior changes.

## Core Identity Fields

Canonical runtime identity attributes:

- `user_id`: stable runtime-governance user identifier.
- `organization_id`: stable organization boundary for governance scope, replay partitioning, and policy application.
- `domain`: bounded operational domain in which the user may request analysis or capability use.
- `role`: governance role assigned by explicit policy or human authority.
- `trust_level`: deterministic trust classification used by future policy and exposure layers.
- `governance_scope`: explicit scope in which authority may be evaluated.
- `authority_profile_id`: stable reference to the resolved authority profile.

If any required identity attribute cannot be resolved, the runtime authority decision must fail closed.

## Authority Classes

Canonical authority classes:

- `READ_ONLY`
- `CAN_REQUEST_ANALYSIS`
- `CAN_USE_LOW_RISK_CAPABILITY`
- `CAN_APPROVE_LOW_RISK`
- `CAN_APPROVE_HIGH_RISK`
- `CAN_CREATE_POLICY`
- `CAN_REGISTER_PROVIDER`
- `CAN_EXECUTE_MUTATION`
- `CAN_OVERRIDE_EXPOSURE_POLICY`
- `CAN_VIEW_USER_REPLAY`
- `CAN_VIEW_ORGANIZATION_REPLAY`
- `CAN_EXPORT_AUDIT_EVIDENCE`

Authority classes are eligibility descriptors only. They do not execute capabilities, activate providers, grant automatic approval, mutate governance, or bypass replay visibility.

## Runtime Scope Model

Runtime authority must be evaluated across explicit scopes:

- Domain scope: the operational domain in which the identity may act.
- Organization scope: the organization boundary for policy, replay, retention, and audit evidence.
- Sandbox scope: the execution isolation profile available to the identity.
- Filesystem scope: explicit read or mutation boundary, if any future capability permits it.
- Provider scope: providers the identity may request through governed activation.
- External API scope: external systems the identity may request through future governed interfaces.
- Replay scope: replay evidence the identity may inspect, export, redact, or freeze.

Unresolved scope means no authority. Scope must not be inferred from LLM text, provider output, or implicit organization membership.

## Capability Entitlement Model

Identity affects capability access through explicit entitlement evaluation:

- Allowed capabilities: capabilities eligible for execution after policy, sandbox, approval, and replay checks.
- Blocked capabilities: capabilities unavailable to the identity in the current scope.
- Approval-required capabilities: capabilities requiring explicit human approval before execution eligibility.
- Local-only capabilities: capabilities limited to local governed runtime surfaces.
- Cloud-eligible capabilities: capabilities eligible for governed provider or cloud execution surfaces.

Capability entitlement is not capability execution. Entitlement only informs routing and eligibility. Actual capability execution remains subject to sandbox, policy, approval, replay, and runtime boundary checks.

This model explicitly supports future semantic exposure governance by allowing exposure eligibility to depend on identity, authority profile, governance scope, capability class, replay scope, and organization policy.

This model explicitly supports future monetization by allowing product tiers or governed commercial scopes to map to capability entitlements, approval requirements, replay visibility, audit export eligibility, and retention controls without changing execution authority semantics.

## Approval Authority Model

Approval hierarchy:

- Requester: may request governed analysis or capability use within explicit entitlement.
- Reviewer: may inspect request evidence and recommend approval outcomes.
- Approver: may approve bounded actions within the approver's explicit authority class.
- Governance admin: may manage governed policy and authority profile configuration within constitutional boundaries.
- Auditor: may inspect replay-visible evidence without mutation authority.
- Emergency override authority: may override defined exposure or execution policy only when explicitly granted, logged, replay-visible, and bounded by separate governance procedure.

Fail-closed rule:

If authority cannot be resolved, approval is denied.

Approval authority is not automatic approval. A user with approval authority may only approve within explicit scope, risk class, replay evidence, and governance policy.

## Replay Visibility Model

Replay visibility levels:

- `OWN_RUNTIME_ONLY`: may view replay evidence for the user's own governed runtime actions.
- `TEAM_SCOPE`: may view replay evidence within explicit team boundary.
- `ORGANIZATION_SCOPE`: may view organization-level replay evidence within explicit policy.
- `AUDITOR_READ_ONLY`: may view replay evidence for audit without mutation authority.
- `GOVERNANCE_ADMIN`: may view governance replay evidence and administer policy within explicit scope.
- `REDACTED_ONLY`: may view redacted replay evidence only.
- `NO_REPLAY_ACCESS`: may not view runtime replay evidence.

Replay visibility is partitioned by identity, organization, domain, role, authority profile, and policy scope. Replay visibility is not mutation authority.

## Retention Authority

Retention authority must define who can:

- View retention policy.
- Request deletion.
- Approve deletion.
- Export audit evidence.
- Extend retention.
- Freeze replay evidence.

Retention actions must be explicit, replay-visible, and governed. Deletion, extension, export, and freeze authority must fail closed when identity, authority, scope, or policy cannot be resolved.

## Identity Resolution Flow

Canonical runtime flow:

```text
request received
-> identity resolved
-> authority profile resolved
-> governance scope resolved
-> capability entitlement resolved
-> approval authority resolved
-> execution eligibility evaluated
-> replay visibility evaluated
-> fail closed if unresolved
```

No hidden identity inference is allowed. LLM output, provider output, prompt text, or Codex suggestions cannot grant authority.

## Boundary Guarantees

- Identity is not execution.
- Authority is not execution.
- Approval authority is not automatic approval.
- Capability entitlement is not capability execution.
- Replay visibility is not mutation authority.
- LLM cannot grant authority.
- Codex cannot grant authority.
- Human governance remains the final strategic authority.
- Codex execution authority remains bounded, explicit, governed, replay-visible, and non-sovereign.
- Unresolved identity, authority, entitlement, approval, replay scope, or retention authority fails closed.

## Downstream Enablement

This model provides the constitutional authority substrate for:

- `SEMANTIC_EXPOSURE_MODEL_V1`
- `CAPABILITY_GOVERNANCE_MATRIX_V1`
- `LOCAL_NODE_ARCHITECTURE_V1`
- `SOVEREIGN_REPLAY_ARCHITECTURE_V1`

Those milestones must preserve identity partitioning, replay visibility boundaries, authority separation, and fail-closed identity resolution.
