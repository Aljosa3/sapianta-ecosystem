# IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_MODEL_V1

## Bridge Artifact

This foundation does not create a new runtime artifact.

It defines the derivation model for a future:

```text
EXECUTION_REQUEST_ARTIFACT_V1
```

when the source is:

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
```

## Required Source Artifact

The source artifact must be:

```text
artifact_type = IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
plan_status = IMPLEMENTATION_PLAN_CREATED
implementation_authorized = true
execution_request_created = false
execution_request_reference = null
implementation_performed = false
replay_visible = true
```

The source artifact must have a valid artifact hash and replay reference.

## Required Authorization

Future request derivation requires human authorization evidence.

Required fields for a future implementation-plan-derived execution request:

```text
execution_request_id
execution_request_source_type
implementation_plan_reference
implementation_plan_hash
improvement_approval_reference
improvement_approval_hash
human_authorization_reference
canonical_chain_id
requested_by
created_at
request_type
request_payload
status
replay_reference
artifact_hash
```

Required values:

```text
execution_request_source_type = IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
requested_by = AIGOL
status = CREATED
provider_authority = false
worker_authority = false
replay_authority = false
automatic_authorization = false
implementation_performed = false
worker_dispatched = false
worker_invoked = false
execution_performed = false
replay_visible = true
```

## Request Payload Rule

The future `request_payload` must be bounded to the implementation plan.

It may include:

- implementation plan target references;
- approved action class;
- bounded parameters;
- plan constraints;
- validation expectations;
- explicit non-goals;
- source chain references.

It may not include:

- unapproved scope expansion;
- hidden shell execution authority;
- provider commands;
- worker self-selection authority;
- credentials;
- replay repair instructions;
- governance mutation instructions;
- self-application instructions.

## Valid Derivation State

The only valid initial future execution request state is:

```text
CREATED
```

`CREATED` does not mean ready for dispatch, dispatch, invocation, execution, completion, or result capture.

## Invalid Source States

Execution request derivation must fail closed if the implementation plan has:

```text
plan_status != IMPLEMENTATION_PLAN_CREATED
implementation_authorized != true
execution_request_created != false
execution_request_reference != null
implementation_performed != false
```

Derivation must also fail closed on:

- rejected improvement approval;
- missing human authorization evidence;
- missing replay evidence;
- canonical chain mismatch;
- corrupt hashes;
- duplicate request id;
- duplicate derivation for the same implementation plan unless certified later;
- provider, worker, or replay creator authority.

## Reconstruction Model

Replay reconstruction must prove:

```text
RESULT_CREATED
RESULT_EVALUATION_CREATED
IMPROVEMENT_PROPOSAL_CREATED
IMPROVEMENT_REVIEW_CREATED
IMPROVEMENT_APPROVAL_RECORDED
IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED
FUTURE_EXECUTION_REQUEST_CREATED
```

Reconstruction must validate:

- event ordering;
- replay wrapper hashes;
- artifact hashes;
- implementation plan reference;
- approval reference;
- authorization reference;
- canonical chain id;
- request payload bounds;
- non-dispatch and non-execution flags.

Replay reconstruction is read-only.
