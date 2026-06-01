# READY_FOR_DISPATCH_RUNTIME_ADR_V1

## Status

Accepted as foundation review.

## Context

AiGOL has:

- Source Of Truth Router Runtime;
- Proposal Runtime;
- Proposal Approval Runtime;
- Execution Request Runtime;
- Worker Runtime Foundation.

Execution requests can now be created from approved proposals in `CREATED` state. Worker Runtime Foundation defines that workers may only receive requests that are `READY_FOR_DISPATCH`, but the readiness boundary itself had not been formalized.

## Decision

AiGOL will treat `READY_FOR_DISPATCH` as an explicit governance readiness boundary between Execution Request Runtime and future Worker Runtime.

Only AiGOL governance may mark an execution request `READY_FOR_DISPATCH`.

Readiness requires replay-valid evidence that:

- a proposal exists;
- the proposal was approved;
- an execution request was created from that approved proposal;
- the execution request is still `CREATED`;
- the request payload and type are valid;
- no cancellation, expiry, worker assignment, dispatch, or execution has occurred;
- readiness validation is recorded in replay.

## Non-Goals

This ADR does not implement:

- readiness runtime code;
- worker assignment;
- dispatch;
- worker execution;
- execution completion;
- provider authority;
- automatic approval;
- proposal mutation.

## Consequences

Execution requests in `CREATED` state remain non-dispatchable.

Future Worker Runtime must reject any execution request that lacks a replay-valid `READY_FOR_DISPATCH` artifact.

Provider and worker authority remain isolated from readiness validation.

Replay becomes the source of reconstruction for readiness history, but not the source of readiness authority.

## Known Gaps

- No readiness runtime implementation exists in this foundation.
- No readiness runtime tests exist in this foundation.
- No worker capability registry is implemented.
- No worker assignment or dispatch runtime exists.
- No expiration runtime is implemented.
- Current execution request runtime remains creation-only.

## Constitutional Alignment

The decision preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

The provider may contribute upstream text or classification, AiGOL governs readiness, future workers execute only after a separate dispatch boundary, and replay records the readiness decision.
