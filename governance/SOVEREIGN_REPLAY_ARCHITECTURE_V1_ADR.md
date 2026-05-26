# SOVEREIGN_REPLAY_ARCHITECTURE_V1_ADR

## Context

Replay is the operational memory of AiGOL/SAPIANTA. It preserves governance evidence, lineage continuity, approval decisions, routing decisions, capability outcomes, policy decisions, and audit context.

The governed identity, semantic exposure, capability governance, and local node architecture milestones establish the authority, payload, capability, and sovereignty boundaries required before replay can be governed across local, organization, auditor, and global scopes.

Replay must be partitioned, authority-scoped, payload-governed, capability-aware, cryptographically verifiable, and fail-closed. It must not become unrestricted logging, unrestricted payload persistence, unrestricted export, or unrestricted observability.

## Decision

Define `SOVEREIGN_REPLAY_ARCHITECTURE_V1` as a documentation-only constitutional governance milestone.

The architecture defines:

- replay domain model;
- replay partitioning;
- replay visibility governance;
- replay payload governance;
- replay export governance;
- replay retention governance;
- replay synchronization governance;
- replay lineage integrity;
- local versus global replay sovereignty;
- organization replay overlays;
- fail-closed replay governance.

This milestone does not implement replay synchronization, replay persistence, databases, cryptographic storage, replay APIs, runtime execution changes, replay implementation changes, or architecture refactors.

## Consequences

Future provider federation, execution policy, confidential execution, and replay trust verification milestones must preserve replay sovereignty and partition replay visibility, synchronization, export, retention, and lineage integrity by identity, authority, organization, payload class, exposure level, capability class, routing scope, and approval scope.

Replay can synchronize metadata, hashes, lineage, classifications, routing decisions, and approval evidence without synchronizing raw payload.

Unresolved replay scope, authority scope, organization scope, payload classification, or replay eligibility must fail closed.

## Non-Goals

- Implement replay synchronization.
- Implement replay persistence.
- Implement databases.
- Implement cryptographic storage.
- Implement replay APIs.
- Modify runtime execution.
- Modify replay implementation.
- Refactor architecture.

## Rejected Alternatives

- Unrestricted replay logging: rejected because replay is governed operational memory, not unrestricted observability.
- Unrestricted replay export: rejected because export requires explicit authority, partitioning, and approval.
- Replay synchronization with unrestricted payload: rejected because synchronization is not raw payload synchronization.
- Replay without partitioning: rejected because local, organization, auditor, governance, redacted, and non-exportable boundaries are required.
- Replay visibility without authority resolution: rejected because replay access must fail closed without identity and authority scope.
- Cloud-centralized replay ownership: rejected because replay sovereignty must support local and organization payload sovereignty.
- Replay without lineage integrity: rejected because replay must preserve auditability and tamper-evident continuity.
- Unrestricted auditor replay visibility: rejected because auditor access remains scoped, read-only, partitioned, and often redacted.
