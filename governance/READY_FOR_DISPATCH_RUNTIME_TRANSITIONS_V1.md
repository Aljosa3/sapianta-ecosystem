# READY_FOR_DISPATCH_RUNTIME_TRANSITIONS_V1

## Purpose

Define legal and forbidden transitions around the `READY_FOR_DISPATCH` governance boundary.

## Legal Transitions

| From | To | Actor | Meaning |
| --- | --- | --- | --- |
| `CREATED` | `READY_FOR_DISPATCH` | AiGOL | The execution request passed deterministic readiness validation. |
| `CREATED` | `CANCELLED` | Human or AiGOL | The execution request is stopped before readiness. |
| `CREATED` | `EXPIRED` | AiGOL | The execution request is no longer eligible because its validity window ended. |
| `READY_FOR_DISPATCH` | `CANCELLED` | Human or AiGOL | The execution request is stopped before worker assignment. |

## Positive Readiness Transition

`CREATED -> READY_FOR_DISPATCH` requires:

- valid execution request artifact;
- `CREATED` execution request status;
- valid proposal lineage;
- valid `APPROVED` approval lineage;
- valid replay reconstruction;
- valid request type;
- bounded request payload;
- stable payload hash;
- no cancellation;
- no expiry;
- no previous readiness transition;
- no worker assignment;
- no dispatch;
- no execution;
- AiGOL governance validation.

## Forbidden Transitions

The following transitions are invalid:

- `CREATED -> ASSIGNED`;
- `CREATED -> EXECUTING`;
- `CREATED -> COMPLETED`;
- `CREATED -> FAILED`;
- `CREATED -> READY_FOR_DISPATCH` by Provider;
- `CREATED -> READY_FOR_DISPATCH` by Worker;
- `CREATED -> READY_FOR_DISPATCH` by Replay;
- `CREATED -> READY_FOR_DISPATCH` by Human acting directly outside AiGOL governance;
- `REJECTED Proposal -> READY_FOR_DISPATCH`;
- `EXPIRED Proposal -> READY_FOR_DISPATCH`;
- `CANCELLED -> READY_FOR_DISPATCH`;
- `EXPIRED -> READY_FOR_DISPATCH`;
- `READY_FOR_DISPATCH -> READY_FOR_DISPATCH`;
- `READY_FOR_DISPATCH -> EXECUTING`;
- `READY_FOR_DISPATCH -> COMPLETED`.

Worker assignment must be handled by a future Worker Runtime transition. Readiness alone does not select, invoke, or authorize a worker.

## Replay Ordering

Replay must observe this order for a valid positive path:

```text
PROPOSAL_CREATED
APPROVAL_DECISION(APPROVED)
EXECUTION_REQUEST_CREATED
EXECUTION_REQUEST_RETURNED
READY_FOR_DISPATCH_VALIDATED
READY_FOR_DISPATCH_RETURNED
```

If replay sees readiness before execution request creation, readiness before approval, duplicate readiness, or readiness after cancellation or expiry, reconstruction must fail closed.

## Human Approval

No new human approval is required for readiness if the proposal has already been explicitly approved and the execution request matches that approved lineage.

Human authority may cancel a request before worker assignment, but human action alone cannot bypass AiGOL readiness validation.

## Transition Classification

The transition model is ready for future runtime implementation and preserves the separation between readiness and worker dispatch.
