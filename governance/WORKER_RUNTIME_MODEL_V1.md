# Worker Runtime Model V1

Status: model foundation.

## Worker Definition

A Worker is a bounded runtime executor with explicit identity, capability binding, assignment evidence, result evidence, and termination evidence.

Workers execute only after AiGOL governance has validated a replay-visible execution request.

## Worker Artifact Set

Minimal future Worker Runtime requires:

```text
WORKER_IDENTITY_ENVELOPE_V1
WORKER_CAPABILITY_BINDING_V1
WORKER_ASSIGNMENT_ARTIFACT_V1
WORKER_RESULT_ARTIFACT_V1
WORKER_TERMINATION_ARTIFACT_V1
```

This foundation defines the artifacts but does not implement them.

## Worker Identity Envelope

Required fields:

```text
worker_id
worker_type
worker_version
declared_capabilities
trust_boundary
created_at
replay_reference
artifact_hash
```

Required flags:

```text
governance_authority = false
approval_authority = false
proposal_authority = false
provider_authority = false
self_authorization = false
replay_mutation_authority = false
```

## Worker Capability Binding

Required fields:

```text
capability_binding_id
worker_id
capability_id
supported_request_types
allowed_effects
forbidden_effects
created_at
replay_reference
artifact_hash
```

`allowed_effects` must be explicit.

Any unstated effect is forbidden.

## Worker Assignment Artifact

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

Valid `assignment_status`:

```text
ASSIGNED
```

## Worker Result Artifact

Required fields:

```text
worker_result_id
worker_assignment_id
worker_id
execution_request_reference
execution_status
result_payload
started_at
completed_at optional
failure_reason optional
replay_reference
artifact_hash
```

Valid `execution_status`:

```text
EXECUTING
COMPLETED
FAILED
```

## Worker Termination Artifact

Required fields:

```text
worker_termination_id
worker_assignment_id
worker_id
termination_status
terminated_at
replay_reference
artifact_hash
```

Termination must be recorded for both success and failure paths.

## Worker States

```text
AVAILABLE
ASSIGNED
EXECUTING
COMPLETED
FAILED
```

## State Meaning

| State | Meaning |
| --- | --- |
| `AVAILABLE` | Worker identity exists and can be considered for future assignment |
| `ASSIGNED` | AiGOL assigned a dispatch-ready execution request |
| `EXECUTING` | Worker has begun bounded work |
| `COMPLETED` | Worker completed bounded work and returned result evidence |
| `FAILED` | Worker failed and returned failure evidence |

## Request Eligibility

The model allows Worker assignment only when:

```text
execution_request.status = READY_FOR_DISPATCH
```

Current Execution Request Runtime only produces:

```text
execution_request.status = CREATED
```

Therefore current execution requests are not worker-eligible.

## Non-Authority Model

Workers never hold:

- proposal authority;
- approval authority;
- governance authority;
- provider authority;
- replay mutation authority;
- self-authorization authority;
- scope expansion authority.

## Reconstruction Model

Replay reconstructs Worker identity and activity from append-only Worker artifacts.

Reconstruction verifies:

- worker id consistency;
- capability binding;
- assignment reference;
- execution request hash;
- result lineage;
- termination lineage;
- artifact hashes;
- replay wrapper hashes.

Replay reconstruction is read-only.
