# Execution Request Runtime Model V1

Status: runtime model foundation.

## Artifact

The minimal execution request artifact is:

```text
EXECUTION_REQUEST_ARTIFACT_V1
```

It represents a governed request candidate derived from an approved proposal.

It does not execute work.

It does not dispatch a worker.

It does not grant provider authority.

## Required Fields

```text
execution_request_id
proposal_reference
proposal_hash
approval_reference
approval_hash
requested_by
created_at
request_type
request_payload
status
replay_reference
artifact_hash
```

## Field Semantics

| Field | Meaning |
| --- | --- |
| `execution_request_id` | Deterministic request identity |
| `proposal_reference` | Approved proposal id |
| `proposal_hash` | Hash of the proposal artifact used for derivation |
| `approval_reference` | Approval artifact id |
| `approval_hash` | Hash of approval evidence authorizing derivation |
| `requested_by` | Actor deriving the request; must be `AIGOL` |
| `created_at` | Replay-visible creation timestamp |
| `request_type` | Bounded request class for future worker compatibility |
| `request_payload` | Bounded payload derived from approved proposal scope |
| `status` | Execution request lifecycle status |
| `replay_reference` | Replay event or path reference for reconstruction |
| `artifact_hash` | Deterministic artifact hash |

## Required Boundary Flags

```text
provider_authority = false
provider_invoked = false
worker_dispatched = false
worker_invoked = false
execution_performed = false
approval_created = false
automatic_authorization = false
replay_visible = true
```

## Valid Initial State

The only valid initial state is:

```text
CREATED
```

`READY_FOR_DISPATCH` may only follow a future AiGOL validation transition.

`CANCELLED` may only follow a future AiGOL or human cancellation transition.

## Creation Preconditions

Creation requires:

- valid proposal artifact;
- proposal state `APPROVED`;
- valid approval artifact;
- approval status `APPROVED`;
- proposal reference and hash match approval evidence;
- request payload derived only from approved proposal scope;
- no existing execution request for the same approved proposal unless future duplicate policy permits it;
- AiGOL as creator.

## Invalid Inputs

Creation must fail closed on:

- missing proposal;
- missing approval;
- proposal not `APPROVED`;
- approval not `APPROVED`;
- proposal hash mismatch;
- approval hash mismatch;
- provider-created request;
- worker-created request;
- replay-created request;
- human-direct dispatch request;
- malformed payload;
- unsupported request type;
- duplicate request id;
- corrupt replay evidence.

## Request Payload Rule

`request_payload` must be bounded and derived.

It may contain:

- normalized target;
- approved action class;
- approved parameters;
- explicit constraints;
- source proposal references.

It may not contain:

- unapproved expanded scope;
- provider commands;
- worker commands;
- shell commands unless future governance explicitly certifies that request type;
- credentials;
- hidden network authority;
- automatic approval instructions.

## Reconstruction Model

Replay reconstructs the model from:

```text
EXECUTION_REQUEST_CREATED
EXECUTION_REQUEST_RETURNED
```

Reconstruction validates:

- deterministic ordering;
- wrapper hashes;
- artifact hashes;
- proposal reference;
- approval reference;
- payload hash;
- request status;
- non-execution flags.

Replay reconstruction is read-only.
