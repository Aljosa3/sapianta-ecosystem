# Execution Request Runtime Boundary Guarantees V1

Status: boundary guarantee foundation.

## Guarantee Summary

Execution Request Runtime is a boundary between approved proposal evidence and future worker execution.

It preserves separation between:

```text
approval
execution request derivation
dispatch
execution
result recording
```

Only derivation is in scope for this foundation.

## Provider Boundary

Providers may contribute upstream proposal evidence only.

Providers may not:

- create execution requests;
- approve execution requests;
- mutate request payloads;
- mark requests ready for dispatch;
- dispatch workers;
- execute work;
- infer missing approval;
- claim governance authority.

Required artifact flags:

```text
provider_authority = false
provider_invoked = false
```

## Worker Boundary

Workers are future downstream actors.

Workers may not:

- create execution requests;
- approve execution requests;
- self-select work;
- self-dispatch;
- infer missing approval;
- expand scope;
- mutate proposal or approval evidence.

Required artifact flags:

```text
worker_dispatched = false
worker_invoked = false
execution_performed = false
```

## Human Boundary

Human approval is upstream evidence.

Human approval does not directly dispatch work.

Human may cancel a request before dispatch if future runtime supports that transition.

Human may not bypass AiGOL request derivation or worker authorization.

## AiGOL Boundary

AiGOL may:

- validate approved proposal lineage;
- derive execution request artifacts;
- validate request payload bounds;
- record replay-visible request events;
- mark future dispatch readiness only after validation.

AiGOL may not execute worker tasks through this foundation.

## Replay Boundary

Replay records and reconstructs.

Replay may not:

- create execution requests;
- mutate request state;
- infer missing approval;
- repair corrupt evidence;
- dispatch workers;
- execute work.

## Governance Boundary

Execution Request Runtime must preserve governance constraints:

- no hidden authority;
- no unapproved scope expansion;
- no provider authority;
- no worker self-authorization;
- no replay mutation;
- no execution without future dispatch and worker runtime certification.

## Fail-Closed Guarantees

The boundary fails closed on:

- missing proposal evidence;
- missing approval evidence;
- non-approved proposal state;
- non-approved approval disposition;
- invalid actor;
- invalid request type;
- malformed payload;
- payload outside approved scope;
- corrupt artifacts;
- corrupt replay;
- duplicate request id;
- duplicate derivation for same approval lineage;
- implied worker dispatch;
- implied execution.

## Constitutional Invariant

The boundary preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Meaning:

- LLM/provider output may only be upstream evidence;
- AiGOL derives and governs the request;
- Worker execution remains future-only;
- Replay records derivation evidence.
