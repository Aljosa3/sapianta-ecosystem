# IMPROVEMENT_REVIEW_MODEL_V1

## Artifact

```text
IMPROVEMENT_REVIEW_ARTIFACT_V1
```

## Required Fields

```text
artifact_type
improvement_review_version
improvement_review_id
canonical_chain_id
improvement_proposal_reference
improvement_proposal_hash
evaluation_reference
evaluation_hash
result_reference
result_hash
review_source
review_method
review_criteria
review_findings
review_status
approval_recommended
approval_reference
implementation_authorized
implementation_reference
reviewed_by
reviewed_at
replay_reference
replay_visible
artifact_hash
```

## Valid Review Status

```text
IMPROVEMENT_REVIEWED
FAILED_CLOSED
```

## Review Sources

Allowed review sources:

```text
AIGOL_DETERMINISTIC_REVIEW
HUMAN_OBSERVATION_RECORDED
WORKER_REPORT_RECORDED
PROVIDER_ASSISTED_NON_AUTHORITATIVE
GOVERNANCE_CONTEXT_REVIEW
COMBINED_EVIDENCE
```

Provider-assisted review may contribute text only. It may not approve, reject, implement, govern, execute, or create the formal review artifact.

## Required False Authority Flags

```text
provider_authority = false
governance_authority = false
worker_authority = false
approval_authority = false
implementation_authority = false
self_improvement_authority = false
proposal_approved = false
proposal_rejected = false
implementation_authorized = false
implementation_applied = false
execution_requested = false
worker_dispatched = false
worker_invoked = false
governance_mutated = false
replay_mutated = false
```

## Creation Preconditions

Improvement review creation requires:

- valid `IMPROVEMENT_PROPOSAL_ARTIFACT_V1`;
- valid proposal artifact hash;
- proposal status of `IMPROVEMENT_PROPOSED`;
- `approval_required = true`;
- `proposal_approved = false`;
- `implementation_authorized = false`;
- valid evaluation reference and hash;
- valid result reference and hash;
- matching canonical chain id;
- deterministic review criteria;
- JSON-serializable review findings;
- replay-visible proposal evidence.

## Review Findings

Review findings may include:

- proposal completeness notes;
- evidence sufficiency notes;
- scope and constraint notes;
- implementation risk notes;
- governance compatibility notes;
- replay continuity notes;
- approval readiness recommendation;
- known gaps or blockers.

Review findings may not include:

- approval transition;
- rejection transition;
- implementation command;
- execution request;
- worker dispatch instruction;
- provider command;
- credential material;
- governance mutation instruction;
- replay repair instruction;
- self-improvement action.

## Approval Recommendation

`approval_recommended` may be:

```text
true
false
```

Recommendation is not approval.

At creation:

```text
approval_reference = null
proposal_approved = false
proposal_rejected = false
approval_authority = false
```

If approval later exists, it must be represented by a separate explicit approval artifact.

## Implementation Fields

At creation:

```text
implementation_authorized = false
implementation_reference = null
implementation_applied = false
```

Review must not authorize or apply implementation.

## Replay Events

Future Improvement Review Runtime should persist:

```text
000_improvement_review_recorded.json
001_improvement_review_returned.json
```

Replay reconstruction should return:

```text
improvement_review_id
canonical_chain_id
improvement_proposal_reference
review_status
approval_recommended
implementation_authorized
reviewed_at
replay_hash
```

## Non-Goals

`IMPROVEMENT_REVIEW_ARTIFACT_V1` does not encode:

- approval decision;
- rejection decision;
- implementation execution;
- result certification;
- reflection state;
- self-improvement state;
- worker dispatch;
- worker invocation;
- governance mutation;
- replay repair.
