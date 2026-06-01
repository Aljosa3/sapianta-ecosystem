# READY_FOR_DISPATCH_RUNTIME_BOUNDARY_GUARANTEES_V1

## Purpose

Record the boundary guarantees that preserve governance between Execution Request Runtime and future Worker Runtime.

## Provider Boundary

Providers may never:

- mark an execution request `READY_FOR_DISPATCH`;
- validate readiness;
- assign workers;
- dispatch work;
- mutate execution request state;
- override replay;
- create approval evidence.

Provider output may appear only as historical context upstream of proposal creation. It is not readiness authority.

## Worker Boundary

Workers may never:

- self-assign;
- self-dispatch;
- approve proposals;
- mark readiness;
- mutate execution request artifacts;
- execute a `CREATED`, `CANCELLED`, or `EXPIRED` request;
- execute a request without future dispatch evidence.

Worker Runtime may only consider requests that have already reached `READY_FOR_DISPATCH` through AiGOL governance.

## Human Boundary

Humans may approve or reject proposals at the approval boundary and may request cancellation where supported.

Humans may not directly convert an execution request into worker eligibility without AiGOL validation and replay-visible readiness evidence.

## AiGOL Governance Boundary

AiGOL is the only actor authorized to validate readiness.

AiGOL must:

- verify proposal lineage;
- verify approval lineage;
- verify execution request integrity;
- verify replay reconstruction;
- verify request type eligibility;
- verify payload bounds;
- verify no cancellation or expiry exists;
- emit replay-visible readiness evidence;
- fail closed when evidence is missing or corrupt.

## Replay Boundary

Replay records readiness but does not authorize it.

Replay must remain:

- read-only;
- ordered;
- reconstructable;
- hash-bound where artifacts require integrity;
- fail-closed on corrupt or contradictory evidence.

## Fail-Closed Guarantees

Readiness must fail closed on:

- missing execution request;
- corrupt execution request;
- invalid execution request status;
- missing proposal;
- missing approval;
- non-approved proposal lineage;
- invalid references;
- duplicate readiness;
- corrupt replay;
- request payload mismatch;
- unsupported request type;
- cancellation before readiness;
- expiry before readiness;
- provider-authored readiness;
- worker-authored readiness;
- attempted dispatch inside readiness.

## Constitutional Invariant

The boundary preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Readiness is the AiGOL governance step that prevents a proposal-derived execution request from reaching Worker Runtime until the approved lineage and replay evidence are valid.

## Boundary Classification

The guarantees are sufficient to define readiness governance. Runtime enforcement remains future work.
