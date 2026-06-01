# Proposal Approval Runtime V1

Status: first replay-visible Proposal Approval Runtime implementation.

Final classification:

```text
PROPOSAL_APPROVAL_RUNTIME_STATUS = CERTIFIED
```

## Scope

`PROPOSAL_APPROVAL_RUNTIME_V1` implements only human-authorized approval disposition for valid proposal runtime artifacts.

Supported transitions:

```text
CREATED -> APPROVED
CREATED -> REJECTED
CREATED -> EXPIRED
```

It does not implement execution, worker dispatch, provider approval, automatic approval, execution requests, proposal mutation beyond approval disposition evidence, approval UI, or deployment behavior.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/proposal_approval_runtime.py
```

Implemented tests:

```text
tests/test_proposal_approval_runtime_v1.py
```

## Accepted Input

The runtime accepts a valid:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1
```

Required proposal preconditions:

- artifact hash is valid;
- artifact type is valid;
- proposal status is `CREATED`;
- `created_by = AIGOL`;
- replay visibility is present;
- no authority, approval, execution, provider authority, provider invocation, or worker invocation is present.

## Approval Artifact

The runtime emits:

```text
PROPOSAL_APPROVAL_ARTIFACT_V1
```

The approval artifact records:

- `approval_id`
- `proposal_id`
- `proposal_hash`
- `proposal_status_before`
- `human_decision`
- `approval_status`
- `decision_reason`
- `operator_label`
- `created_at`
- `replay_reference`
- non-authority and non-execution flags
- `artifact_hash`

## Replay Events

The runtime records:

```text
PROPOSAL_APPROVED
PROPOSAL_REJECTED
PROPOSAL_APPROVAL_EXPIRED
PROPOSAL_APPROVAL_RETURNED
```

Replay reconstructs:

- approval identity;
- proposal identity;
- proposal hash;
- prior proposal status;
- human decision;
- approval status;
- operator label;
- non-execution boundary evidence;
- artifact hashes.

## Fail-Closed Cases

The runtime fails closed on:

- missing proposal;
- corrupt proposal artifact;
- invalid proposal status;
- non-AiGOL proposal creator;
- invalid human decision;
- missing approval fields;
- duplicate approval replay artifacts;
- corrupt approval artifact;
- corrupt replay wrapper;
- replay ordering corruption;
- approval reference mismatch;
- execution request creation;
- provider approval;
- worker approval;
- automatic approval.

## Boundary Guarantees

The runtime preserves:

```text
authority = false
provider_approval = false
worker_approval = false
automatic_approval = false
execution_requested = false
execution_request_created = false
provider_invoked = false
worker_invoked = false
```

No provider approves.

No worker approves.

No execution request is created.

No worker is dispatched.

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
| LLM proposes | Provider evidence remains non-authoritative |
| AiGOL governs | AiGOL validates proposal and records human disposition |
| Worker executes | Worker execution is absent |
| Replay records | Replay records approval decision and return artifacts |

## Validation

Focused validation:

```text
python -m pytest tests/test_proposal_approval_runtime_v1.py
```

Result:

```text
19 passed
```

## Final Result

AiGOL can record replay-visible proposal approval dispositions from `CREATED` proposal artifacts.

```text
PROPOSAL_APPROVAL_RUNTIME_STATUS = CERTIFIED
```
