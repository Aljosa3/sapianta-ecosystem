# WORKER_INVOCATION_RUNTIME_TRANSITIONS_V1

## Purpose

Define legal and forbidden transitions around the worker invocation governance boundary.

## Legal Transitions

| From | To | Actor | Meaning |
| --- | --- | --- | --- |
| `DISPATCHED` | `INVOKED` | AiGOL | AiGOL delivered bounded invocation parameters to the dispatched worker. |
| `DISPATCHED` | `FAILED_INVOCATION` | AiGOL | Invocation could not be completed and no execution occurred. |
| `DISPATCHED` | `CANCELLED` | Human or AiGOL | Dispatch is stopped before invocation. |
| `DISPATCHED` | `EXPIRED` | AiGOL | Dispatch is no longer eligible for invocation. |

## Positive Invocation Transition

`DISPATCHED -> INVOKED` requires:

- valid dispatch artifact;
- dispatch status `DISPATCHED`;
- dispatch created by AiGOL;
- valid worker assignment reference;
- valid worker identity reference;
- valid readiness reference;
- valid execution request reference;
- capability compatibility preserved;
- bounded invocation parameters;
- invocation parameter hash;
- replay reconstruction succeeds;
- no duplicate invocation;
- no cancellation;
- no expiry;
- no execution;
- no completion;
- no provider authority;
- AiGOL governance validation.

## Failed Invocation

`DISPATCHED -> FAILED_INVOCATION` may be recorded only when:

- dispatch evidence is valid;
- invocation was attempted by AiGOL;
- worker execution did not start;
- no result or completion evidence exists;
- failure reason is replay-visible;
- failure does not mutate the approved request scope.

`FAILED_INVOCATION` is terminal for that invocation attempt unless a future retry foundation explicitly defines a governed retry boundary.

## Forbidden Transitions

The following transitions are invalid:

- `DISPATCHED -> EXECUTING`;
- `DISPATCHED -> COMPLETED`;
- `DISPATCHED -> FAILED`;
- `DISPATCHED -> INVOKED` by Provider;
- `DISPATCHED -> INVOKED` by Worker;
- `DISPATCHED -> INVOKED` by Replay;
- `DISPATCHED -> INVOKED` by Human acting directly outside AiGOL governance;
- `ASSIGNED -> INVOKED`;
- `CANCELLED -> INVOKED`;
- `EXPIRED -> INVOKED`;
- `FAILED_INVOCATION -> INVOKED`;
- `INVOKED -> INVOKED`;
- `INVOKED -> COMPLETED`.

Worker execution must be handled by a future execution runtime. Invocation alone does not prove work started, work completed, or result evidence exists.

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
WORKER_INVOCATION_VALIDATED
WORKER_INVOCATION_RETURNED
```

If replay sees invocation before dispatch, invocation before assignment, duplicate invocation, or invocation after cancellation or expiry, reconstruction must fail closed.

## Human Approval

No new human approval is required for invocation if the proposal was explicitly approved upstream and dispatch matches that approved execution request lineage.

Human authority may cancel before invocation where supported, but human action alone cannot bypass AiGOL invocation validation.

## Transition Classification

The transition model is ready for future invocation runtime implementation and preserves the separation between invocation and execution.
