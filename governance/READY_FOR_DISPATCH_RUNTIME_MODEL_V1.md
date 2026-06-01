# READY_FOR_DISPATCH_RUNTIME_MODEL_V1

## Artifact

The minimal readiness artifact is:

`READY_FOR_DISPATCH_ARTIFACT_V1`

This artifact records that AiGOL governance has validated an execution request for future worker assignment consideration.

## Required Fields

```json
{
  "readiness_id": "string",
  "execution_request_reference": "string",
  "execution_request_hash": "string",
  "proposal_reference": "string",
  "approval_reference": "string",
  "validated_by": "AiGOL",
  "validated_at": "RFC3339 timestamp",
  "readiness_status": "READY_FOR_DISPATCH",
  "request_type": "string",
  "payload_hash": "string",
  "capability_compatibility_reference": "string",
  "validation_results": [],
  "replay_reference": "string",
  "artifact_hash": "string"
}
```

## Field Semantics

`readiness_id` is a deterministic identifier for the readiness decision.

`execution_request_reference` points to the execution request being validated.

`execution_request_hash` binds readiness to the exact execution request artifact observed by AiGOL.

`proposal_reference` points to the proposal that caused the execution request.

`approval_reference` points to the human approval decision that authorized the execution request lineage.

`validated_by` must be `AiGOL`.

`validated_at` records the deterministic readiness timestamp used in replay evidence.

`readiness_status` must be `READY_FOR_DISPATCH` for a positive readiness artifact.

`request_type` records the request class being prepared for future worker assignment.

`payload_hash` binds readiness to the validated request payload without granting mutation authority.

`capability_compatibility_reference` records the governance evidence used to determine that a future worker capability class may accept the request.

`validation_results` records deterministic validation checks and outcomes.

`replay_reference` points to the replay event that records readiness.

`artifact_hash` protects the readiness artifact from silent mutation.

## Boundary Flags

A readiness artifact must preserve these flags:

```json
{
  "provider_authority": false,
  "worker_assigned": false,
  "worker_dispatched": false,
  "worker_invoked": false,
  "execution_performed": false,
  "approval_created": false,
  "automatic_authorization": false
}
```

## Valid Readiness States

For the readiness boundary, execution requests may be observed in these states:

- `CREATED`;
- `READY_FOR_DISPATCH`;
- `CANCELLED`;
- `EXPIRED`.

The readiness artifact itself records only successful validation into `READY_FOR_DISPATCH`. Cancellation and expiry are separate governance outcomes and must not be represented as successful readiness.

## Invalid Artifacts

AiGOL must reject the artifact if:

- any required field is missing;
- a reference is malformed;
- the execution request hash does not match;
- the payload hash does not match;
- the approval reference is not `APPROVED`;
- the validated actor is not AiGOL;
- the readiness status is not `READY_FOR_DISPATCH`;
- any boundary flag grants provider, worker, or automatic authority;
- replay reconstruction fails.

## Model Classification

The model is sufficient for a future runtime implementation of readiness validation, but it is not itself a dispatch or execution model.
