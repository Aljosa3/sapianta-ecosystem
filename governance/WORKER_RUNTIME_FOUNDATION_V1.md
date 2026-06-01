# Worker Runtime Foundation V1

Status: foundation review.

Final classification:

```text
WORKER_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Scope

This artifact defines Worker Runtime boundaries for future execution.

It does not implement worker execution, dispatch, provider authority, worker adapters, worker selection, execution completion, result persistence, deployment behavior, or governance mutation.

## Context

AiGOL now has:

- Proposal Runtime;
- Proposal Approval Runtime;
- Execution Request Runtime.

Execution Requests exist in:

```text
CREATED
```

The next missing layer is Worker Runtime, which must remain downstream of governed execution request validation and dispatch readiness.

## 1. What Is A Worker?

A Worker is a bounded execution component that may perform a specific approved capability only after AiGOL supplies a replay-valid execution request through a future dispatch boundary.

A Worker is:

- execution-only;
- capability-bound;
- identity-bound;
- request-scoped;
- replay-visible;
- non-authoritative;
- governed by AiGOL before invocation.

## 2. What Is Not A Worker?

The following are not Workers:

- provider;
- LLM;
- human operator;
- replay system;
- proposal artifact;
- approval artifact;
- execution request artifact;
- governance artifact;
- shell access without worker identity;
- network access without worker identity;
- automatic retry loop;
- hidden background process.

## 3. Execution Requests That May Reach A Worker

Only execution requests that satisfy all conditions may reach a Worker:

- artifact type `EXECUTION_REQUEST_ARTIFACT_V1`;
- replay reconstruction succeeds;
- status is future-certified `READY_FOR_DISPATCH`;
- proposal lineage is present;
- approval lineage is present;
- request payload hash is valid;
- request type is supported by the assigned worker capability;
- dispatch authorization exists;
- worker identity envelope is recorded;
- no provider authority is present;
- no prior terminal worker result exists for the same dispatch lineage.

Current V1 execution requests are only `CREATED`, so they may not yet reach a Worker.

## 4. Execution Requests That May Never Reach A Worker

The following execution requests may never reach a Worker:

```text
status = CREATED
status = CANCELLED
status = COMPLETED
status = FAILED
```

Requests also may never reach a Worker if:

- replay reconstruction fails;
- approval lineage is missing;
- proposal lineage is missing;
- request payload exceeds approved scope;
- request type is unsupported;
- provider authority is implied;
- worker identity is missing;
- dispatch authorization is missing;
- replay is corrupt;
- duplicate dispatch ambiguity exists.

## 5. Replay Evidence Required Before Dispatch

Before dispatch, replay must contain:

- proposal runtime artifact;
- proposal approval artifact with `approval_status = APPROVED`;
- execution request artifact;
- execution request replay reconstruction evidence;
- execution request status `READY_FOR_DISPATCH`;
- AiGOL dispatch validation evidence;
- worker identity envelope;
- worker capability binding;
- payload hash;
- dispatch id;
- no provider authority flags;
- no previous terminal worker result for the same dispatch lineage.

## 6. Worker Assignment Recording

Worker assignment must be recorded as:

```text
WORKER_ASSIGNMENT_ARTIFACT_V1
```

Required fields:

```text
worker_assignment_id
worker_id
worker_type
capability_id
execution_request_reference
execution_request_hash
assigned_by
assigned_at
assignment_status
replay_reference
artifact_hash
```

Required flags:

```text
assigned_by = AIGOL
provider_authority = false
worker_self_assigned = false
execution_completed = false
replay_visible = true
```

## 7. Worker Identity Reconstruction

Replay reconstructs Worker identity from:

```text
WORKER_IDENTITY_ENVELOPE
WORKER_CAPABILITY_BINDING
WORKER_ASSIGNMENT_ARTIFACT_V1
WORKER_RESULT_ARTIFACT_V1
WORKER_TERMINATION_ARTIFACT_V1
```

Reconstruction must verify:

- worker id;
- worker type;
- capability binding;
- assigned execution request reference;
- execution request hash;
- dispatch id;
- result lineage;
- termination state;
- replay wrapper hashes;
- artifact hashes.

Replay reconstruction may prove Worker identity and activity.

Replay reconstruction may not create worker authority, repair missing identity, or infer missing dispatch.

## 8. Constitutional Preservation

Worker Runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Worker Runtime meaning |
| --- | --- |
| LLM proposes | Provider evidence remains upstream proposal evidence only |
| AiGOL governs | AiGOL validates, authorizes, and assigns bounded worker work |
| Worker executes | Worker performs only assigned bounded work |
| Replay records | Replay records assignment, execution, result, and termination evidence |

## 9. Worker States

Worker state vocabulary:

```text
AVAILABLE
ASSIGNED
EXECUTING
COMPLETED
FAILED
```

These states describe Worker activity. They do not replace execution request status.

## 10. Execution Request Integration

Worker Runtime integrates with Execution Request Runtime as:

```text
EXECUTION_REQUEST.CREATED
-> future AiGOL validation
-> EXECUTION_REQUEST.READY_FOR_DISPATCH
-> WORKER.ASSIGNED
-> WORKER.EXECUTING
-> WORKER.COMPLETED or WORKER.FAILED
```

Current Execution Request Runtime implements only `CREATED`.

Therefore Worker Runtime Foundation is ready with gaps until a future dispatch-readiness transition is implemented and certified.

## Gaps

The foundation is ready with gaps because:

- Worker Runtime is not implemented;
- dispatch is not implemented;
- execution is not implemented;
- execution request readiness is not implemented;
- worker identity envelope is not implemented;
- capability binding runtime is not implemented;
- worker result replay is not implemented;
- worker termination replay is not implemented.

```text
WORKER_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```
