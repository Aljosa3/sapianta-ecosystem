# WORKER_INVOCATION_RUNTIME_MODEL_V1

## Artifact

The minimal invocation artifact is:

`WORKER_INVOCATION_ARTIFACT_V1`

This artifact records that AiGOL has invoked a dispatched worker with bounded invocation parameters.

## Required Fields

```json
{
  "worker_invocation_id": "string",
  "dispatch_reference": "string",
  "dispatch_hash": "string",
  "worker_assignment_reference": "string",
  "worker_assignment_hash": "string",
  "worker_reference": "string",
  "worker_hash": "string",
  "readiness_reference": "string",
  "execution_request_reference": "string",
  "invoked_by": "AiGOL",
  "invoked_at": "RFC3339 timestamp",
  "invocation_status": "INVOKED",
  "request_type": "string",
  "capability_id": "string",
  "invocation_parameters": {},
  "invocation_parameters_hash": "string",
  "validation_results": [],
  "replay_reference": "string",
  "artifact_hash": "string"
}
```

## Field Semantics

`worker_invocation_id` is a deterministic identifier for the invocation event.

`dispatch_reference` and `dispatch_hash` bind invocation to a replay-valid dispatch artifact.

`worker_assignment_reference` and `worker_assignment_hash` bind invocation to the assignment that dispatch authorized.

`worker_reference` and `worker_hash` identify the invoked worker.

`readiness_reference` identifies the readiness decision that made the execution request worker-eligible.

`execution_request_reference` identifies the approved execution request lineage.

`invoked_by` must be `AiGOL`.

`invoked_at` records the invocation timestamp used in replay evidence.

`invocation_status` must be `INVOKED` for positive invocation.

`request_type` and `capability_id` record compatibility with the assigned worker.

`invocation_parameters` contains the bounded parameter envelope delivered to the worker.

`invocation_parameters_hash` binds the invocation to the exact parameter envelope.

`validation_results` records deterministic validation checks and outcomes.

`replay_reference` points to the replay event that records invocation.

`artifact_hash` protects the invocation artifact from silent mutation.

## Invocation Parameter Envelope

The minimal parameter envelope is:

```json
{
  "execution_request_reference": "string",
  "request_type": "string",
  "capability_id": "string",
  "payload_reference": "string",
  "payload_hash": "string",
  "allowed_effects": [],
  "forbidden_effects": []
}
```

Any unstated effect is forbidden.

## Boundary Flags

An invocation artifact must preserve:

```json
{
  "provider_authority": false,
  "worker_self_invoked": false,
  "execution_started": false,
  "execution_performed": false,
  "completion_recorded": false,
  "automatic_authorization": false,
  "scope_expansion": false
}
```

## Valid Invocation States

The invocation boundary recognizes:

- `DISPATCHED`;
- `INVOKED`;
- `FAILED_INVOCATION`;
- `CANCELLED`;
- `EXPIRED`.

The invocation artifact records only successful transition to `INVOKED`. Failed invocation, cancellation, and expiry require separate replay-visible outcomes and must not be represented as successful invocation.

## Invalid Artifacts

AiGOL must reject the artifact if:

- any required field is missing;
- dispatch reference or hash is malformed;
- worker assignment reference or hash is malformed;
- worker identity does not match dispatch evidence;
- readiness reference does not match dispatch lineage;
- invocation parameters are missing;
- invocation parameters hash does not match;
- invocation parameters contain authority-bearing fields;
- `invoked_by` is not AiGOL;
- `invocation_status` is not `INVOKED`;
- any boundary flag grants provider, worker self-invocation, execution, completion, automatic authorization, or scope expansion;
- replay reconstruction fails.

## Model Classification

The model is sufficient for a future invocation runtime implementation, but it is not an execution, completion, result, or termination model.
