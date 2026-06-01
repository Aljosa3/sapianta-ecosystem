# DISPATCH_RUNTIME_ADR_V1

## Status

Accepted as foundation review.

## Context

AiGOL has:

- Proposal Runtime;
- Proposal Approval Runtime;
- Execution Request Runtime;
- Ready For Dispatch Runtime;
- Worker Runtime.

Workers can be registered and assigned to readiness-valid execution requests. The remaining boundary before a worker can be invoked is dispatch.

## Decision

AiGOL will treat dispatch as an explicit governance boundary between Worker Assignment and future Worker Invocation.

Only AiGOL governance may dispatch.

Dispatch requires replay-valid evidence that:

- a worker assignment exists;
- the assignment status is `ASSIGNED`;
- the worker identity is valid;
- readiness evidence exists;
- execution request lineage exists;
- assignment and readiness references match;
- no cancellation, expiry, invocation, execution, or completion has occurred;
- dispatch validation is recorded in replay.

## Non-Goals

This ADR does not implement:

- dispatch runtime code;
- worker invocation;
- worker execution;
- execution completion;
- worker result persistence;
- provider authority;
- automatic dispatch;
- worker self-dispatch.

## Consequences

Worker assignments remain non-invoked until a future dispatch runtime records replay-valid `DISPATCH_ARTIFACT_V1` evidence.

Future invocation runtime must reject any worker assignment that lacks replay-valid dispatch evidence.

Provider and worker authority remain isolated from dispatch validation.

Replay reconstructs dispatch history, but replay does not authorize dispatch.

## Known Gaps

- No dispatch runtime implementation exists in this foundation.
- No dispatch runtime tests exist in this foundation.
- No worker invocation runtime exists.
- No worker execution runtime exists.
- No completion or result persistence runtime exists.
- Current Worker Runtime remains assignment-only.

## Constitutional Alignment

The decision preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

AiGOL governs dispatch. Future workers execute only after a separate invocation and execution boundary. Replay records the dispatch decision.
