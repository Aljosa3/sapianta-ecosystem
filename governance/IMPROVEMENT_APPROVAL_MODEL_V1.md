# IMPROVEMENT_APPROVAL_MODEL_V1

## Artifact

```text
IMPROVEMENT_APPROVAL_ARTIFACT_V1
```

## Required Fields

```text
artifact_type
improvement_approval_version
improvement_approval_id
canonical_chain_id
improvement_review_reference
improvement_review_hash
improvement_proposal_reference
improvement_proposal_hash
evaluation_reference
evaluation_hash
result_reference
result_hash
decision
decision_reason
decision_authority
human_authorization_reference
approval_status
implementation_authorized
implementation_reference
recorded_by
recorded_at
replay_reference
replay_visible
artifact_hash
```

## Valid Decisions

```text
APPROVED
REJECTED
```

## Valid Approval Status

```text
APPROVED
REJECTED
FAILED_CLOSED
```

## Required Authority Fields

```text
decision_authority = HUMAN
recorded_by = AIGOL
provider_authority = false
worker_authority = false
aigol_autonomous_approval = false
implementation_authority = false
self_improvement_authority = false
governance_mutation_authority = false
```

## Creation Preconditions

Improvement approval creation requires:

- valid `IMPROVEMENT_REVIEW_ARTIFACT_V1`;
- valid review artifact hash;
- review status of `IMPROVEMENT_REVIEWED`;
- valid improvement proposal reference and hash;
- valid evaluation reference and hash;
- valid result reference and hash;
- matching canonical chain id;
- explicit human authorization reference;
- decision value of `APPROVED` or `REJECTED`;
- deterministic decision reason;
- replay-visible review evidence.

## Decision Semantics

`APPROVED` means:

- the reviewed improvement proposal may enter a future implementation path;
- implementation remains separate;
- execution request creation is not performed by approval;
- governance artifacts are not mutated by approval.

`REJECTED` means:

- the reviewed improvement proposal may not enter implementation;
- no execution request may be created from that approval;
- proposal, review, evaluation, result, and replay history remain immutable.

## Implementation Fields

At approval artifact creation:

```text
implementation_reference = null
implementation_performed = false
execution_requested = false
worker_dispatched = false
worker_invoked = false
```

For `APPROVED`, `implementation_authorized` may be:

```text
true
```

For `REJECTED`, `implementation_authorized` must be:

```text
false
```

Authorization is not implementation. Future implementation must be recorded by separate governed artifacts.

## Required False Mutation Flags

```text
governance_mutated = false
replay_mutated = false
proposal_mutated = false
review_mutated = false
evaluation_mutated = false
result_mutated = false
execution_history_modified = false
self_modification_performed = false
self_improvement_performed = false
```

## Replay Events

Future Improvement Approval Runtime should persist:

```text
000_improvement_approval_recorded.json
001_improvement_approval_returned.json
```

Replay reconstruction should return:

```text
improvement_approval_id
canonical_chain_id
improvement_review_reference
improvement_proposal_reference
decision
approval_status
implementation_authorized
recorded_at
replay_hash
```

## Non-Goals

`IMPROVEMENT_APPROVAL_ARTIFACT_V1` does not encode:

- implementation execution;
- execution request creation;
- worker dispatch;
- worker invocation;
- result certification;
- reflection state;
- self-improvement state;
- governance mutation;
- replay repair.
