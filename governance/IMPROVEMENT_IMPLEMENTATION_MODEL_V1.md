# IMPROVEMENT_IMPLEMENTATION_MODEL_V1

## Artifact

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
```

## Required Fields

```text
artifact_type
improvement_implementation_plan_version
implementation_plan_id
canonical_chain_id
improvement_approval_reference
improvement_approval_hash
improvement_review_reference
improvement_review_hash
improvement_proposal_reference
improvement_proposal_hash
evaluation_reference
evaluation_hash
result_reference
result_hash
plan_source
plan_text
plan_scope
plan_constraints
planned_artifact_targets
planned_validation
plan_status
execution_request_created
execution_request_reference
implementation_authorized
implementation_performed
created_by
created_at
replay_reference
replay_visible
artifact_hash
```

## Valid Plan Status

```text
IMPLEMENTATION_PLAN_CREATED
FAILED_CLOSED
```

## Plan Sources

Allowed plan sources:

```text
AIGOL_DETERMINISTIC_PLANNING
HUMAN_APPROVED_IMPROVEMENT
PROVIDER_ASSISTED_NON_AUTHORITATIVE
WORKER_REPORT_RECORDED
COMBINED_EVIDENCE
```

Provider-assisted planning may contribute plan language only. It may not create plans directly, create execution requests, dispatch workers, invoke workers, mutate code, or mutate governance.

## Required Authority Fields

```text
created_by = AIGOL
implementation_authorized = true
execution_request_created = false
execution_request_reference = null
implementation_performed = false
provider_authority = false
worker_authority = false
aigol_autonomous_implementation = false
self_improvement_authority = false
governance_mutation_authority = false
```

`implementation_authorized = true` reflects the upstream approved decision. It is not implementation.

## Creation Preconditions

Implementation plan creation requires:

- valid `IMPROVEMENT_APPROVAL_ARTIFACT_V1`;
- approval decision of `APPROVED`;
- approval status of `APPROVED`;
- valid approval artifact hash;
- valid human authorization reference;
- valid improvement review reference and hash;
- valid improvement proposal reference and hash;
- valid evaluation reference and hash;
- valid result reference and hash;
- matching canonical chain id;
- deterministic plan text;
- explicit plan scope;
- explicit plan constraints;
- replay-visible approval evidence.

## Plan Content Requirements

Plan content must be:

- deterministic;
- bounded;
- human-readable;
- JSON-serializable;
- hash-bound;
- chain-bound;
- explicit about scope and non-implementation status.

Plan content may include:

- intended files or artifact classes;
- proposed implementation steps;
- required validation commands;
- expected replay evidence;
- rollback or non-goal notes.

Plan content may not include:

- direct code mutation;
- shell command execution;
- execution request creation;
- worker dispatch instruction;
- provider command;
- credential material;
- governance mutation instruction;
- replay repair instruction;
- self-improvement action.

## Execution Request Fields

At plan creation:

```text
execution_request_created = false
execution_request_reference = null
```

If an execution request later exists, it must be represented by a separate governed execution request artifact. `IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` must not create the request itself.

## Implementation Fields

At plan creation:

```text
implementation_performed = false
code_mutated = false
configuration_mutated = false
governance_mutated = false
replay_mutated = false
self_modification_performed = false
self_improvement_performed = false
```

Planning must not perform implementation.

## Replay Events

Future Improvement Implementation Planning Runtime should persist:

```text
000_improvement_implementation_plan_created.json
001_improvement_implementation_plan_returned.json
```

Replay reconstruction should return:

```text
implementation_plan_id
canonical_chain_id
improvement_approval_reference
improvement_proposal_reference
plan_status
execution_request_created
implementation_performed
created_at
replay_hash
```

## Non-Goals

`IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` does not encode:

- execution request creation;
- code mutation;
- configuration mutation;
- implementation execution;
- worker dispatch;
- worker invocation;
- result certification;
- reflection state;
- self-improvement state;
- governance mutation;
- replay repair.
