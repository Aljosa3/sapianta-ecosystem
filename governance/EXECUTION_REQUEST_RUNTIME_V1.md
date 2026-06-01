# Execution Request Runtime V1

Status: first replay-visible Execution Request Runtime implementation.

Final classification:

```text
EXECUTION_REQUEST_RUNTIME_STATUS = CERTIFIED
```

## Scope

`EXECUTION_REQUEST_RUNTIME_V1` implements only deterministic execution request creation.

It creates:

```text
EXECUTION_REQUEST_ARTIFACT_V1
```

with:

```text
status = CREATED
requested_by = AIGOL
```

It does not implement dispatch, worker runtime, execution, completion, provider authority, approval changes, or proposal mutation.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/execution_request_runtime.py
```

Implemented tests:

```text
tests/test_execution_request_runtime_v1.py
```

## Approved Proposal Representation

The current runtime represents an approved proposal as:

```text
valid PROPOSAL_RUNTIME_ARTIFACT_V1
matching PROPOSAL_APPROVAL_ARTIFACT_V1 with approval_status = APPROVED
```

The proposal artifact itself remains immutable and records `status = CREATED`.

The approval artifact is the replay-visible evidence that the proposal may be used for execution request derivation.

## Execution Request Artifact

The runtime emits `EXECUTION_REQUEST_ARTIFACT_V1` with mandatory fields:

- `execution_request_id`
- `proposal_reference`
- `requested_by`
- `created_at`
- `request_type`
- `request_payload`
- `status`
- `replay_reference`

The runtime also records:

- `proposal_hash`
- `approval_reference`
- `approval_hash`
- `request_payload_hash`
- `artifact_type`
- `execution_request_runtime_version`
- `replay_visible`
- `provider_authority`
- `provider_invoked`
- `worker_dispatched`
- `worker_invoked`
- `execution_performed`
- `approval_created`
- `automatic_authorization`
- `artifact_hash`

## Supported Values

Supported request type:

```text
CAPABILITY_EXECUTION_REQUEST
```

Supported status:

```text
CREATED
```

Supported creator:

```text
AIGOL
```

## Replay Events

The runtime records:

```text
EXECUTION_REQUEST_CREATED
EXECUTION_REQUEST_RETURNED
```

Replay reconstructs:

- execution request identity;
- proposal reference;
- approval reference;
- request type;
- request payload;
- status;
- replay reference;
- non-dispatch and non-execution flags;
- artifact hashes.

## Fail-Closed Cases

The runtime fails closed on:

- missing proposal;
- missing approval;
- invalid proposal artifact;
- corrupt proposal artifact;
- corrupt approval artifact;
- approval status `REJECTED`;
- approval status `EXPIRED`;
- proposal reference mismatch;
- proposal hash mismatch;
- missing execution request fields;
- invalid request type;
- invalid status;
- authority-bearing payload;
- duplicate append-only replay artifacts;
- corrupt execution request artifact;
- corrupt replay wrapper;
- replay ordering corruption;
- execution request reference mismatch.

## Boundary Guarantees

The runtime preserves:

```text
provider_authority = false
provider_invoked = false
worker_dispatched = false
worker_invoked = false
execution_performed = false
approval_created = false
automatic_authorization = false
```

No provider is invoked.

No worker is dispatched.

No worker is invoked.

No execution is performed.

No completion state is recorded.

## Constitutional Invariant

The runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Runtime mapping:

| Role | Runtime meaning |
| --- | --- |
| LLM proposes | Provider evidence remains upstream proposal evidence only |
| AiGOL governs | AiGOL derives a bounded request from approved proposal evidence |
| Worker executes | Worker execution is absent |
| Replay records | Replay records request creation and return artifacts |

## Validation

Focused validation:

```text
python -m pytest tests/test_proposal_runtime_v1.py tests/test_proposal_approval_runtime_v1.py tests/test_execution_request_runtime_v1.py
```

Result:

```text
56 passed
```

## Final Result

AiGOL can create replay-visible execution request artifacts in `CREATED` state from approved proposal evidence.

```text
EXECUTION_REQUEST_RUNTIME_STATUS = CERTIFIED
```
