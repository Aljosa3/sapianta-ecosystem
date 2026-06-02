# IMPROVEMENT_PROPOSAL_MODEL_V1

## Artifact

```text
IMPROVEMENT_PROPOSAL_ARTIFACT_V1
```

## Required Fields

```text
artifact_type
improvement_proposal_version
improvement_proposal_id
canonical_chain_id
evaluation_reference
evaluation_hash
result_reference
result_hash
execution_reference
completion_reference
worker_reference
proposal_source
proposal_text
proposal_reason
proposal_scope
proposal_constraints
proposal_status
approval_required
approval_reference
implementation_authorized
implementation_reference
created_by
created_at
replay_reference
replay_visible
artifact_hash
```

## Valid Proposal Status

```text
IMPROVEMENT_PROPOSED
FAILED_CLOSED
```

## Proposal Sources

Allowed proposal sources:

```text
RESULT_EVALUATION
AIGOL_DETERMINISTIC_REVIEW
HUMAN_OBSERVATION_RECORDED
WORKER_REPORT_RECORDED
PROVIDER_ASSISTED_NON_AUTHORITATIVE
COMBINED_EVIDENCE
```

Provider-assisted sources may contribute proposal language only. They may not approve, implement, execute, or create the formal artifact.

## Required False Authority Flags

```text
provider_authority = false
governance_authority = false
worker_authority = false
approval_authority = false
implementation_authority = false
self_improvement_authority = false
proposal_approved = false
implementation_authorized = false
implementation_applied = false
worker_dispatched = false
worker_invoked = false
execution_requested = false
governance_mutated = false
replay_mutated = false
```

## Creation Preconditions

Improvement proposal creation requires:

- valid `RESULT_EVALUATION_ARTIFACT_V1`;
- `improvement_recommended = true`;
- valid evaluation artifact hash;
- valid result reference;
- valid result hash;
- matching canonical chain id;
- matching execution reference;
- matching completion reference;
- matching worker reference;
- deterministic proposal text;
- explicit proposal scope;
- explicit proposal constraints;
- replay-visible evaluation evidence.

## Proposal Text Requirements

Proposal text must be:

- deterministic;
- bounded;
- human-readable;
- JSON-serializable;
- hash-bound;
- chain-bound;
- explicit about scope and non-implementation status.

Proposal text may not include:

- automatic approval;
- execution command;
- worker dispatch instruction;
- provider command;
- credential material;
- governance mutation instruction;
- replay repair instruction;
- self-improvement action.

## Approval Fields

At creation:

```text
approval_required = true
approval_reference = null
proposal_approved = false
```

If approval later exists, it must be represented by a separate governed approval artifact. `IMPROVEMENT_PROPOSAL_ARTIFACT_V1` must not approve itself.

## Implementation Fields

At creation:

```text
implementation_authorized = false
implementation_reference = null
implementation_applied = false
```

If implementation later exists, it must be represented by separate governed lifecycle artifacts. `IMPROVEMENT_PROPOSAL_ARTIFACT_V1` must not implement itself.

## Replay Events

Future Improvement Proposal Runtime should persist:

```text
000_improvement_proposal_created.json
001_improvement_proposal_returned.json
```

Replay reconstruction should return:

```text
improvement_proposal_id
canonical_chain_id
evaluation_reference
result_reference
proposal_status
approval_required
implementation_authorized
created_at
replay_hash
```

## Non-Goals

`IMPROVEMENT_PROPOSAL_ARTIFACT_V1` does not encode:

- approval decision;
- implementation execution;
- result certification;
- reflection state;
- self-improvement state;
- worker dispatch;
- worker invocation;
- governance mutation;
- replay repair.
