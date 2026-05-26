# LOCAL_NODE_ARCHITECTURE_V1_ADR

## Context

AiGOL/SAPIANTA needs a constitutional local node architecture before sovereign replay, provider federation, execution policy, or confidential execution governance can be safely specified.

The identity, semantic exposure, and capability governance milestones establish who may act, what payload exposure is allowed, and which capabilities are eligible. The Local Node Architecture defines where sensitive execution, semantic processing, replay, memory, and governance metadata may reside without centralized payload ownership.

## Decision

Define `LOCAL_NODE_ARCHITECTURE_V1` as a documentation-only constitutional governance milestone.

The architecture defines:

- local node boundaries;
- local execution domains;
- local versus cloud execution separation;
- local semantic processing;
- local memory governance;
- local replay governance;
- local capability execution governance;
- governance metadata export;
- organization sovereignty;
- fail-closed local governance.

This milestone does not implement local runtime execution, local model execution, provider federation, encrypted storage, confidential computing, replay persistence changes, API endpoints, or execution engine changes.

## Consequences

Future sovereign replay, provider federation, execution policy, and confidential execution milestones must preserve local payload sovereignty, local replay partitioning, local/cloud separation, organization overlays, and fail-closed local governance.

Governance metadata may be exportable when authorized, but raw payload, local memory, secret replay artifacts, and local-only semantic outputs remain governed by local node policy.

The local node remains governed and cannot bypass approvals, capability scope, identity authority, replay constraints, or organization policy.

## Non-Goals

- Implement a local runtime.
- Implement local LLM execution.
- Implement provider federation.
- Implement encrypted storage.
- Implement confidential computing.
- Modify runtime execution code.
- Modify replay persistence.
- Add API endpoints.
- Change provider execution behavior.

## Rejected Alternatives

- Cloud-only execution: rejected because regulated and confidential domains require sovereign local processing.
- Unrestricted payload export: rejected because governance must function without centralized sensitive payload ownership.
- Replay synchronization with raw payload: rejected because replay synchronization is not raw payload synchronization.
- Local execution without governance: rejected because local execution is not a trusted bypass.
- Trust-based local execution: rejected because local trust does not replace identity, authority, capability, approval, or replay checks.
- Unrestricted provider execution: rejected because provider execution must remain governed and scoped.
- Local execution bypassing approvals: rejected because approval hierarchy remains authoritative.
- Local replay without partitioning: rejected because replay visibility and export authority must remain scoped.
