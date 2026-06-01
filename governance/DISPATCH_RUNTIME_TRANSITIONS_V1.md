# DISPATCH_RUNTIME_TRANSITIONS_V1

## Purpose

Define legal and forbidden transitions around the dispatch governance boundary.

## Legal Transitions

| From | To | Actor | Meaning |
| --- | --- | --- | --- |
| `ASSIGNED` | `DISPATCHED` | AiGOL | Assigned worker passed deterministic dispatch validation. |
| `ASSIGNED` | `CANCELLED` | Human or AiGOL | Assignment is stopped before dispatch. |
| `ASSIGNED` | `EXPIRED` | AiGOL | Assignment is no longer eligible for dispatch. |
| `DISPATCHED` | `CANCELLED` | Human or AiGOL | Dispatch is stopped before invocation, where supported by future runtime. |

## Positive Dispatch Transition

`ASSIGNED -> DISPATCHED` requires:

- valid worker assignment artifact;
- assignment status `ASSIGNED`;
- worker state after assignment `ASSIGNED`;
- assignment created by AiGOL;
- valid worker reference;
- valid readiness reference;
- valid execution request reference;
- capability compatibility preserved;
- replay reconstruction succeeds;
- no duplicate dispatch;
- no cancellation;
- no expiry;
- no worker invocation;
- no execution;
- no completion;
- no provider authority;
- AiGOL governance validation.

## Forbidden Transitions

The following transitions are invalid:

- `ASSIGNED -> INVOKED`;
- `ASSIGNED -> EXECUTING`;
- `ASSIGNED -> COMPLETED`;
- `ASSIGNED -> FAILED`;
- `ASSIGNED -> DISPATCHED` by Provider;
- `ASSIGNED -> DISPATCHED` by Worker;
- `ASSIGNED -> DISPATCHED` by Replay;
- `ASSIGNED -> DISPATCHED` by Human acting directly outside AiGOL governance;
- `AVAILABLE -> DISPATCHED`;
- `UNAVAILABLE -> DISPATCHED`;
- `CANCELLED -> DISPATCHED`;
- `EXPIRED -> DISPATCHED`;
- `DISPATCHED -> DISPATCHED`;
- `DISPATCHED -> EXECUTING`;
- `DISPATCHED -> COMPLETED`.

Worker invocation must be handled by a future invocation runtime. Dispatch alone does not call, run, execute, complete, or persist worker results.

## Replay Ordering

Replay must observe this order for a valid positive path:

```text
PROPOSAL_CREATED
APPROVAL_DECISION(APPROVED)
EXECUTION_REQUEST_CREATED
READY_FOR_DISPATCH_VALIDATED
WORKER_REGISTERED
WORKER_ASSIGNED
DISPATCH_VALIDATED
DISPATCH_RETURNED
```

If replay sees dispatch before assignment, dispatch before readiness, duplicate dispatch, or dispatch after cancellation or expiry, reconstruction must fail closed.

## Human Approval

No new human approval is required for dispatch if the proposal was explicitly approved upstream and the assignment matches the approved execution request lineage.

Human authority may cancel before invocation where supported, but human action alone cannot bypass AiGOL dispatch validation.

## Transition Classification

The transition model is ready for future dispatch runtime implementation and preserves the separation between dispatch and worker invocation.
