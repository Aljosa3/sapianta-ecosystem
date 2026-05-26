# GOVERNED_IDENTITY_AND_AUTHORITY_MODEL_V1_ADR

## Context

AiGOL/SAPIANTA now contains governed runtime dispatch, sandboxing, provider activation, capability routing, policy evaluation, continuity, memory, observability, and human approval checkpoints.

Those layers require a constitutional runtime identity and authority model before introducing Semantic Exposure, Capability Governance Matrix, Local Node Architecture, and Sovereign Replay Architecture.

Frontend login identity is insufficient because runtime governance must evaluate capability eligibility, policy scope, approval authority, replay visibility, retention authority, and audit export boundaries.

## Decision

Define `GOVERNED_IDENTITY_AND_AUTHORITY_MODEL_V1` as a documentation-only constitutional governance milestone.

The model establishes:

- canonical identity fields;
- explicit authority classes;
- runtime scope evaluation;
- capability entitlement semantics;
- human approval authority hierarchy;
- replay visibility partitioning;
- retention authority;
- fail-closed identity resolution;
- boundary guarantees that preserve LLM and Codex non-authority.

This ADR does not activate enforcement, add authentication, create API endpoints, modify runtime execution, or change capability/provider behavior.

## Consequences

Future semantic exposure, capability governance, local node, and sovereign replay milestones must resolve identity and authority before evaluating exposure, capability access, replay access, retention actions, or audit export.

All unresolved identity or authority states must fail closed.

LLM output, provider output, prompt text, and Codex suggestions remain non-authoritative and cannot grant authority.

Human governance remains the final strategic authority, while runtime execution remains bounded by explicit governance artifacts.

## Non-Goals

- Implement login.
- Implement frontend RBAC.
- Add authentication middleware.
- Add API endpoints.
- Modify runtime execution code.
- Change capability execution behavior.
- Activate provider behavior.
- Add enforcement beyond documentation and evidence.
- Introduce automatic approval or self-approval.

## Rejected Alternatives

- Frontend-only RBAC: rejected because runtime governance requires replay-visible authority evaluation beyond interface access.
- Login-only identity: rejected because authentication does not define runtime eligibility, capability entitlement, approval authority, retention authority, or replay visibility.
- LLM-inferred authority: rejected because LLMs are non-authoritative and cannot grant runtime or governance authority.
- Implicit organization trust: rejected because organization membership alone does not define domain, replay, capability, retention, or approval scope.
- Capability access without runtime authority: rejected because capability execution must remain governed by identity, policy, sandbox, approval, replay, and lineage boundaries.
- Replay visibility without partitioning: rejected because replay evidence requires user, team, organization, auditor, and redaction boundaries.
