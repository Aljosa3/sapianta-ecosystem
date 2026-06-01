# DISPATCH_RUNTIME_MODEL_V1

## Artifact

The minimal dispatch artifact is:

`DISPATCH_ARTIFACT_V1`

This artifact records that AiGOL has validated an assigned worker for future invocation.

## Required Fields

```json
{
  "dispatch_id": "string",
  "worker_assignment_reference": "string",
  "worker_assignment_hash": "string",
  "worker_reference": "string",
  "worker_hash": "string",
  "readiness_reference": "string",
  "readiness_hash": "string",
  "execution_request_reference": "string",
  "execution_request_hash": "string",
  "dispatched_by": "AiGOL",
  "dispatched_at": "RFC3339 timestamp",
  "dispatch_status": "DISPATCHED",
  "request_type": "string",
  "capability_id": "string",
  "validation_results": [],
  "replay_reference": "string",
  "artifact_hash": "string"
}
```

## Field Semantics

`dispatch_id` is a deterministic identifier for the dispatch decision.

`worker_assignment_reference` points to the assignment being dispatched.

`worker_assignment_hash` binds dispatch to the exact assignment artifact observed by AiGOL.

`worker_reference` and `worker_hash` identify the assigned worker.

`readiness_reference` and `readiness_hash` identify the readiness decision that made the execution request worker-eligible.

`execution_request_reference` and `execution_request_hash` identify the execution request lineage.

`dispatched_by` must be `AiGOL`.

`dispatched_at` records the dispatch timestamp used in replay evidence.

`dispatch_status` must be `DISPATCHED`.

`request_type` and `capability_id` record the compatibility claim validated by AiGOL.

`validation_results` records deterministic validation checks and outcomes.

`replay_reference` points to the replay event that records dispatch.

`artifact_hash` protects the dispatch artifact from silent mutation.

## Boundary Flags

A dispatch artifact must preserve:

```json
{
  "provider_authority": false,
  "worker_self_dispatched": false,
  "worker_invoked": false,
  "execution_performed": false,
  "completion_recorded": false,
  "automatic_authorization": false
}
```

## Valid Dispatch States

The dispatch boundary recognizes:

- `ASSIGNED`;
- `DISPATCHED`;
- `CANCELLED`;
- `EXPIRED`.

The dispatch artifact itself records only successful validation into `DISPATCHED`. Cancellation and expiry are separate governance outcomes and must not be represented as successful dispatch.

## Invalid Artifacts

AiGOL must reject the artifact if:

- any required field is missing;
- a reference is malformed;
- the worker assignment hash does not match;
- the worker reference does not match assignment evidence;
- the readiness reference does not match assignment evidence;
- the execution request reference does not match assignment evidence;
- `dispatched_by` is not AiGOL;
- `dispatch_status` is not `DISPATCHED`;
- any boundary flag grants provider, worker, invocation, execution, completion, or automatic authority;
- replay reconstruction fails.

## Model Classification

The model is sufficient for future runtime implementation of dispatch validation, but it is not an invocation or execution model.
