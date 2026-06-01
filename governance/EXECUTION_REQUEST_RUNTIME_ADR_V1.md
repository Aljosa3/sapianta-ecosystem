# Execution Request Runtime ADR V1

Status: accepted foundation decision.

## Decision

AiGOL will define Execution Request Runtime as a replay-visible derivation boundary between approved proposals and future worker execution.

The minimal artifact is:

```text
EXECUTION_REQUEST_ARTIFACT_V1
```

The artifact may be created only by AiGOL from replay-valid approved proposal evidence.

## Context

AiGOL has certified runtime support for:

- proposal creation;
- proposal approval disposition;
- resolution strategy selection;
- replay reconstruction.

Approved proposals now exist, but no explicit execution request boundary exists.

Without this boundary, future worker execution would risk conflating:

- proposal approval;
- execution request derivation;
- dispatch;
- execution.

## Rationale

Execution Request Runtime must be explicit because approval is not execution.

The request artifact creates a narrow checkpoint where AiGOL can validate:

- approved proposal lineage;
- approval evidence;
- request payload bounds;
- future worker compatibility;
- replay reconstruction requirements;
- no provider or worker authority.

## Decision Rules

1. Execution Request creation requires an approved proposal.
2. Execution Request creation requires replay-visible approval evidence.
3. Execution Request creation is performed only by AiGOL.
4. Providers cannot create, approve, dispatch, or execute requests.
5. Workers cannot create, approve, or self-dispatch requests.
6. Replay records and reconstructs only.
7. `CREATED` is the only initial execution request state.
8. `READY_FOR_DISPATCH` is a validation state, not execution.
9. `CANCELLED` terminates request eligibility before dispatch.

## Consequences

AiGOL gains a clean future bridge:

```text
APPROVED Proposal
-> EXECUTION_REQUEST.CREATED
-> READY_FOR_DISPATCH
-> Future Worker Runtime
```

This preserves separation between approval and execution.

## Non-Goals

This ADR does not implement:

- execution request runtime code;
- worker runtime;
- dispatch;
- execution;
- provider authority;
- automatic approval;
- approval changes;
- proposal mutation.

## Known Gaps

- Runtime implementation is absent.
- Tests are absent.
- Worker authorization integration is absent.
- Dispatch semantics are absent.
- Duplicate request derivation policy is not implemented.
- Current Proposal Approval Runtime supports `CREATED -> APPROVED`, while earlier foundation documents prefer inspection before approval.

## Final Decision

The execution request boundary is accepted as a foundation design and should be implemented separately before any worker dispatch runtime depends on approved proposals.

```text
EXECUTION_REQUEST_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```
