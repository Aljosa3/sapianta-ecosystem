# WORKER_INVOCATION_RUNTIME_BOUNDARY_GUARANTEES_V1

## Purpose

Record the boundary guarantees that preserve governance between Dispatch Runtime and future Worker Execution.

## Provider Boundary

Providers may never:

- invoke workers;
- provide invocation authority;
- create invocation parameters as authority;
- mutate dispatch evidence;
- mutate worker identity;
- receive a direct provider-to-worker path;
- expand execution scope.

Provider output may appear only as upstream proposal or conversational evidence. It is not invocation authority.

## Worker Boundary

Workers may never:

- self-invoke;
- choose invocation parameters;
- expand request scope;
- mutate invocation artifacts;
- begin execution without invocation evidence;
- record completion through invocation;
- create result evidence at invocation.

Invocation permits future execution to begin only through a separate execution boundary.

## Human Boundary

Human approval occurs upstream at the proposal approval boundary.

Humans may not directly invoke a worker outside AiGOL governance and replay-visible invocation validation.

## AiGOL Governance Boundary

AiGOL is the only actor authorized to record invocation.

AiGOL must:

- verify dispatch lineage;
- verify worker assignment lineage;
- verify worker identity;
- verify readiness lineage;
- verify execution request lineage;
- verify invocation parameters;
- verify capability compatibility;
- verify replay reconstruction;
- verify no cancellation or expiry exists;
- verify no prior invocation exists;
- emit replay-visible invocation evidence;
- fail closed when evidence is missing or corrupt.

## Replay Boundary

Replay records invocation but does not authorize it.

Replay must remain:

- read-only;
- ordered;
- reconstructable;
- hash-bound where artifacts require integrity;
- fail-closed on corrupt or contradictory evidence.

## Fail-Closed Guarantees

Invocation must fail closed on:

- missing dispatch artifact;
- corrupt dispatch artifact;
- invalid dispatch status;
- missing worker assignment;
- missing worker identity;
- worker identity mismatch;
- missing readiness evidence;
- missing execution request lineage;
- invalid invocation parameters;
- invocation parameter hash mismatch;
- authority-bearing invocation parameters;
- duplicate invocation;
- corrupt replay;
- cancellation before invocation;
- expiry before invocation;
- provider-authored invocation;
- worker-authored invocation;
- attempted execution inside invocation;
- attempted completion inside invocation.

## Constitutional Invariant

The boundary preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Invocation is an AiGOL governance step. Worker execution remains future and separate. Replay records invocation without creating execution or completion authority.

## Boundary Classification

The guarantees are sufficient to define invocation governance. Runtime enforcement remains future work.
