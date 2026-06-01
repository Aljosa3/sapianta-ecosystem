# DISPATCH_RUNTIME_BOUNDARY_GUARANTEES_V1

## Purpose

Record the boundary guarantees that preserve governance between Worker Assignment and future Worker Invocation.

## Provider Boundary

Providers may never:

- dispatch workers;
- invoke workers;
- approve dispatch;
- select dispatch timing;
- mutate assignment state;
- mutate replay;
- command a worker through dispatch.

Provider output may appear only as upstream proposal or conversational evidence. It is not dispatch authority.

## Worker Boundary

Workers may never:

- self-dispatch;
- self-invoke;
- choose new work;
- expand request scope;
- mutate dispatch artifacts;
- execute from `ASSIGNED` without dispatch evidence;
- execute from `DISPATCHED` without future invocation evidence.

Dispatch makes a worker eligible for future invocation. It does not authorize self-starting execution.

## Human Boundary

Human approval occurs upstream at the proposal approval boundary.

Humans may not directly dispatch a worker outside AiGOL governance and replay-visible dispatch validation.

## AiGOL Governance Boundary

AiGOL is the only actor authorized to validate dispatch.

AiGOL must:

- verify worker assignment lineage;
- verify worker identity;
- verify readiness lineage;
- verify execution request lineage;
- verify capability compatibility;
- verify replay reconstruction;
- verify no cancellation or expiry exists;
- verify no prior dispatch exists;
- emit replay-visible dispatch evidence;
- fail closed when evidence is missing or corrupt.

## Replay Boundary

Replay records dispatch but does not authorize it.

Replay must remain:

- read-only;
- ordered;
- reconstructable;
- hash-bound where artifacts require integrity;
- fail-closed on corrupt or contradictory evidence.

## Fail-Closed Guarantees

Dispatch must fail closed on:

- missing worker assignment;
- corrupt worker assignment;
- invalid assignment status;
- missing worker identity;
- missing readiness evidence;
- missing execution request lineage;
- invalid references;
- duplicate dispatch;
- corrupt replay;
- unsupported capability;
- cancellation before dispatch;
- expiry before dispatch;
- provider-authored dispatch;
- worker-authored dispatch;
- attempted invocation inside dispatch;
- attempted execution inside dispatch;
- attempted completion inside dispatch.

## Constitutional Invariant

The boundary preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Dispatch is an AiGOL governance step. Workers remain non-invoked until a future invocation boundary. Replay records the dispatch decision without creating authority.

## Boundary Classification

The guarantees are sufficient to define dispatch governance. Runtime enforcement remains future work.
