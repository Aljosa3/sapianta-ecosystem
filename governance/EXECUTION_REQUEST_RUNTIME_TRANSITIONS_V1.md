# Execution Request Runtime Transitions V1

Status: transition foundation.

## Principle

Execution Request transitions are governed derivation states.

They are not worker execution states.

They are not dispatch states unless a future dispatch runtime is certified.

## State Set

```text
CREATED
READY_FOR_DISPATCH
CANCELLED
```

## Transition Table

| From | To | Actor | Human approval required | Rule |
| --- | --- | --- | --- | --- |
| `APPROVED` proposal | `CREATED` execution request | AiGOL | Already present in approval evidence | AiGOL derives bounded request from approved proposal |
| `CREATED` | `READY_FOR_DISPATCH` | AiGOL | No new approval in V1 foundation | AiGOL validates request type, payload bounds, lineage, and worker compatibility |
| `CREATED` | `CANCELLED` | AiGOL or Human | No | Request is invalid, stale, manually cancelled, or boundary-violating |
| `READY_FOR_DISPATCH` | `CANCELLED` | AiGOL or Human | No | Request is cancelled before worker dispatch |
| Any recorded state | replay reconstruction | Replay | No | Replay reconstructs read-only request history |

## Allowed Creation Source

Only:

```text
Proposal.status = APPROVED
Approval.status = APPROVED
```

may create:

```text
ExecutionRequest.status = CREATED
```

## Forbidden Creation Sources

Execution Request creation is forbidden from:

```text
Proposal.status = CREATED
Proposal.status = INSPECTED
Proposal.status = REJECTED
Proposal.status = EXPIRED
Proposal.status = EXECUTED
Proposal.status = REPLAY_RECONSTRUCTED
```

## Actor Rules

AiGOL may:

- derive a request from approved proposal evidence;
- validate request lineage;
- validate request payload bounds;
- mark a request ready for future dispatch;
- cancel a request.

Human may:

- approve proposal upstream;
- cancel an execution request before dispatch.

Human may not:

- directly dispatch a worker through this foundation;
- bypass AiGOL validation;
- create execution evidence manually.

Provider may not:

- create request state;
- approve request state;
- expand payload;
- dispatch a worker;
- execute work.

Worker may not:

- create request state;
- approve request state;
- infer missing approval;
- expand payload;
- self-dispatch.

Replay may:

- reconstruct request history.

Replay may not:

- mutate request state;
- infer missing approval;
- dispatch execution.

## READY_FOR_DISPATCH Meaning

`READY_FOR_DISPATCH` means:

```text
The request passed AiGOL validation and may be considered by a future dispatch runtime.
```

It does not mean:

- worker has been selected;
- worker has been invoked;
- execution has begun;
- result exists;
- proposal has been executed.

## Fail-Closed Rules

Transitions must fail closed if:

- source proposal is missing;
- approval evidence is missing;
- approval is not `APPROVED`;
- proposal reference mismatch exists;
- proposal hash mismatch exists;
- approval hash mismatch exists;
- request payload exceeds approved scope;
- actor authority is invalid;
- replay lineage is missing;
- duplicate request exists;
- state order is invalid;
- worker dispatch is implied by transition alone.
