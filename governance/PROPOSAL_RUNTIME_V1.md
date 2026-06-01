# Proposal Runtime V1

Status: first minimal replay-visible Proposal Runtime implementation.

Final classification:

```text
PROPOSAL_RUNTIME_STATUS = CERTIFIED
```

## Scope

`PROPOSAL_RUNTIME_V1` implements only proposal creation.

It creates:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1
```

with:

```text
status = CREATED
created_by = AIGOL
```

It does not implement approval, execution, worker dispatch, provider authority, proposal mutation, routing, or lifecycle transition mutation.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/proposal_runtime.py
```

Implemented tests:

```text
tests/test_proposal_runtime_v1.py
```

## Proposal Artifact

The runtime emits `PROPOSAL_RUNTIME_ARTIFACT_V1` with mandatory fields:

- `proposal_id`
- `proposal_type`
- `proposal_source`
- `proposal_text`
- `created_at`
- `created_by`
- `status`
- `replay_reference`

The runtime also records:

- `artifact_type`
- `proposal_runtime_version`
- `replay_visible`
- `authority`
- `approval_created`
- `execution_requested`
- `provider_authority`
- `provider_invoked`
- `worker_invoked`
- `artifact_hash`

## Supported Values

Supported proposal type:

```text
CAPABILITY_PROPOSAL
```

Supported proposal sources:

```text
CONVERSATION
RESOLUTION_STRATEGY
PROVIDER_EVIDENCE
REPLAY_EVIDENCE
GOVERNANCE_EVIDENCE
HUMAN_PROMPT
COMBINED
```

Supported status:

```text
CREATED
```

## Replay Events

The runtime records:

```text
PROPOSAL_RUNTIME_CREATED
PROPOSAL_RUNTIME_RETURNED
```

Replay reconstructs:

- proposal identity;
- proposal type;
- proposal source;
- proposal text;
- creation timestamp;
- creator;
- status;
- replay reference;
- non-authority flags;
- artifact hashes.

## Fail-Closed Cases

The runtime fails closed on:

- missing mandatory fields;
- invalid proposal type;
- invalid proposal source;
- non-AiGOL creator;
- invalid status;
- duplicate append-only replay artifact;
- corrupt artifact hash;
- corrupt replay hash;
- replay ordering corruption;
- proposal reference mismatch.

## Boundary Guarantees

The runtime preserves:

```text
authority = false
approval_created = false
execution_requested = false
provider_authority = false
provider_invoked = false
worker_invoked = false
```

No provider is invoked.

No worker is invoked.

No execution request is created.

No approval is created.

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
| LLM proposes | Provider evidence can be named as source only; provider has no authority |
| AiGOL governs | AiGOL alone creates proposal artifacts |
| Worker executes | Worker execution is absent |
| Replay records | Replay records proposal creation and return artifacts |

## Validation

Focused validation:

```text
python -m pytest tests/test_proposal_runtime_v1.py
```

Result:

```text
17 passed
```

## Final Result

AiGOL can create replay-visible proposals in `CREATED` state.

```text
PROPOSAL_RUNTIME_STATUS = CERTIFIED
```
