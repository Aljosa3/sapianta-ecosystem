# AIGOL_OCS_TO_EXECUTION_HANDOFF_CONTRACT_V1

## Status

Governance contract definition and certification milestone.

No execution runtime was implemented. No repair runtime was implemented. No retry behavior was implemented. No new worker was implemented. No CLI behavior was changed.

## Purpose

Define the canonical contract by which OCS cognition output may become a governed execution-intake candidate for later human approval, execution authorization, and worker request creation.

This contract does not execute work. It defines the admissible handoff object between:

```text
OCS cognition output
-> human-reviewed execution intake
-> existing execution authorization chain
-> existing worker request chain
```

## Canonical Artifact

```text
OCS_EXECUTION_HANDOFF_ARTIFACT_V1
```

This artifact is the only canonical OCS-originated object allowed to cross from cognition into execution-intake review.

It is:

- replay-visible;
- hash-bound to OCS cognition evidence;
- non-authoritative;
- human-review-bound;
- execution-readiness-gated;
- worker-selection-constrained.

It is not:

- approval;
- execution authorization;
- worker assignment;
- worker dispatch;
- worker invocation;
- worker execution;
- repair;
- retry;
- autonomous continuation.

## Contract Position

```text
Human Prompt
-> OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1
-> OCS_EXECUTION_HANDOFF_ARTIFACT_V1
-> Human Approval / Rejection / Revision
-> EXECUTION_READY_STATUS_ARTIFACT_V1
-> EXECUTION_AUTHORIZATION_ARTIFACT_V1
-> WORKER_INVOCATION_REQUEST_ARTIFACT_V1
-> WORKER_ASSIGNMENT_ARTIFACT_V1
-> WORKER_DISPATCH_ARTIFACT_V1
-> WORKER_INVOCATION_ARTIFACT_V1
-> WORKER_RESULT_CAPTURE_ARTIFACT_V1
-> WORKER_RESULT_VALIDATION_ARTIFACT_V1
-> POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1
-> GOVERNED_TERMINATION_ARTIFACT_V1
```

`OCS_EXECUTION_HANDOFF_ARTIFACT_V1` is upstream of approval and authorization. It may not replace any existing downstream artifact.

## Required Fields

### Identity

Required fields:

- `artifact_type`
- `artifact_version`
- `handoff_id`
- `chain_id`
- `created_at`
- `handoff_status`
- `handoff_hash`
- `artifact_hash`

Required values:

```text
artifact_type = OCS_EXECUTION_HANDOFF_ARTIFACT_V1
artifact_version = 1
handoff_status = EXECUTION_HANDOFF_CANDIDATE | FAILED_CLOSED
```

### OCS Cognition Lineage

Required fields:

- `ocs_cognition_reference`
- `ocs_cognition_hash`
- `ocs_cognition_replay_reference`
- `human_prompt_hash`
- `human_facing_cognition_hash`
- `findings_hash`
- `assumptions_hash`
- `risks_hash`
- `uncertainties_hash`
- `clarification_questions_hash`
- `recommended_next_milestone_hash`

Requirements:

- OCS lineage must reconstruct from replay.
- Cognition content must be normalized cognition content, not raw provider payload.
- Provider response hashes may be referenced only through the certified OCS cognition artifact lineage.
- Missing or corrupt cognition lineage fails closed.

### Execution Intake

Required fields:

- `execution_intake_id`
- `execution_intent_summary`
- `execution_candidate_scope`
- `requested_outcomes`
- `non_goals`
- `allowed_outputs`
- `forbidden_operations`
- `required_validation`
- `execution_readiness_requirements`
- `human_review_required`

Requirements:

- `human_review_required` must be `true`.
- `allowed_outputs` must be explicit and non-empty.
- `forbidden_operations` must be explicit and non-empty.
- `execution_candidate_scope` must be bounded and reconstructable from normalized OCS cognition.
- Raw provider payloads are not valid execution-intake input.

### Authority Binding

Required fields:

- `provider_authority`
- `ocs_authority`
- `approval_authority`
- `execution_authority`
- `worker_authority`
- `governance_authority`
- `replay_authority`
- `authorization_created`
- `worker_request_created`
- `worker_assigned`
- `worker_dispatched`
- `worker_invoked`
- `execution_started`
- `repair_started`
- `retry_started`

Required values:

```text
provider_authority = false
ocs_authority = false
approval_authority = false
execution_authority = false
worker_authority = false
governance_authority = false
replay_authority = false
authorization_created = false
worker_request_created = false
worker_assigned = false
worker_dispatched = false
worker_invoked = false
execution_started = false
repair_started = false
retry_started = false
```

Authority rule:

`OCS_EXECUTION_HANDOFF_ARTIFACT_V1` carries a candidate into review. It grants no authority to approve, authorize, assign, dispatch, invoke, execute, repair, retry, mutate replay, or mutate governance.

### Approval Binding

Required fields:

- `approval_required`
- `approval_status`
- `approval_reference`
- `approval_hash`
- `approval_scope_requirements`
- `approval_expiry_requirements`
- `approval_revocation_requirements`
- `approval_actor_requirements`

Required initial values:

```text
approval_required = true
approval_status = PENDING_HUMAN_REVIEW
approval_reference = null
approval_hash = null
```

Approval rule:

The handoff artifact is not an approval. A later approval artifact must bind to the handoff by `handoff_id` and `handoff_hash`, preserve the handoff scope, and may not broaden `allowed_outputs`, weaken `forbidden_operations`, or bypass required validation.

Fail-closed approval conditions:

- approval missing;
- approval hash mismatch;
- approval scope broader than handoff scope;
- approval actor invalid;
- approval expired;
- approval revoked;
- approval attempts to authorize execution directly from OCS cognition without the handoff artifact.

### Worker Selection Binding

Required fields:

- `worker_selection_required`
- `worker_role_requirements`
- `target_worker_family`
- `candidate_worker_constraints`
- `worker_capability_requirements`
- `worker_exclusion_rules`
- `worker_registry_requirements`
- `worker_selection_status`
- `worker_reference`
- `worker_hash`

Required initial values:

```text
worker_selection_required = true
worker_selection_status = NOT_SELECTED
worker_reference = null
worker_hash = null
```

Worker rule:

The handoff artifact may constrain worker eligibility but may not select, assign, dispatch, or invoke a worker. Worker selection must occur later through the existing worker assignment boundary and registered worker evidence.

Fail-closed worker binding conditions:

- missing worker role requirements;
- ambiguous target worker family;
- worker constraints conflict with forbidden operations;
- worker target not reconstructable from handoff scope;
- worker reference present before assignment;
- worker hash present before assignment.

### Replay Lineage Requirements

Required fields:

- `replay_root_reference`
- `ocs_stage_replay_references`
- `handoff_replay_reference`
- `lineage_refs`
- `upstream_artifact_refs`
- `downstream_expected_artifact_refs`
- `hash_bindings`
- `replay_integrity_requirements`

Requirements:

- Replay must reconstruct OCS cognition before reconstructing the handoff.
- Handoff replay must be append-only.
- Handoff replay must preserve hashes for OCS cognition, human-facing cognition, execution intake, authority flags, approval requirements, worker constraints, and artifact hash.
- Downstream authorization and worker request artifacts must reference the handoff lineage once a runtime exists.

Required downstream expected artifacts:

- `EXECUTION_READY_STATUS_ARTIFACT_V1`
- `EXECUTION_AUTHORIZATION_ARTIFACT_V1`
- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`
- `WORKER_ASSIGNMENT_ARTIFACT_V1`
- `WORKER_DISPATCH_ARTIFACT_V1`
- `WORKER_INVOCATION_ARTIFACT_V1`
- `WORKER_RESULT_CAPTURE_ARTIFACT_V1`
- `WORKER_RESULT_VALIDATION_ARTIFACT_V1`
- `POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1`
- `GOVERNED_TERMINATION_ARTIFACT_V1`

### Execution-Readiness Requirements

Required fields:

- `execution_readiness_status`
- `readiness_preconditions`
- `readiness_validation_requirements`
- `readiness_failure_conditions`
- `execution_packet_requirements`
- `authorization_compatibility_requirements`

Required initial value:

```text
execution_readiness_status = NOT_EXECUTION_READY
```

Readiness rule:

The handoff artifact is not execution-ready. It defines the requirements that a later execution-ready packet must satisfy before `EXECUTION_AUTHORIZATION_ARTIFACT_V1` can be created.

Minimum readiness preconditions:

- valid OCS cognition lineage;
- normalized human-facing cognition available;
- bounded execution intent;
- explicit allowed outputs;
- explicit forbidden operations;
- explicit required validation;
- human approval binding;
- worker role constraints;
- replay lineage continuity;
- no authority escalation flags.

## Failure Conditions

The contract fails closed when any of the following are true:

- OCS cognition artifact missing;
- OCS cognition replay missing or corrupt;
- normalized cognition missing;
- raw provider payload used as execution intake;
- execution scope ambiguous;
- allowed outputs missing;
- forbidden operations missing;
- validation requirements missing;
- human review not required;
- approval reference present in the initial handoff artifact;
- approval hash present in the initial handoff artifact;
- worker selected before worker assignment;
- worker dispatched or invoked before authorization;
- any authority flag is true;
- execution started;
- repair started;
- retry started;
- replay lineage cannot be reconstructed;
- handoff hash mismatch;
- downstream artifact attempts to broaden handoff scope.

Failure output status:

```text
handoff_status = FAILED_CLOSED
```

## Governance Boundaries

`OCS_EXECUTION_HANDOFF_ARTIFACT_V1` preserves the invariant:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The artifact may contain normalized cognition-derived intent and constraints. It may not contain raw provider payloads as operative execution instructions.

Provider output remains non-authoritative. OCS cognition remains advisory. Human approval and execution authorization remain separate downstream boundaries.

## Certification Scope

This milestone certifies:

- the canonical artifact name;
- required fields;
- authority binding;
- approval binding;
- worker selection binding;
- replay lineage requirements;
- execution-readiness requirements;
- fail-closed conditions;
- non-goals.

This milestone does not certify:

- a handoff runtime;
- execution authorization from OCS;
- worker request creation from OCS;
- worker assignment;
- worker dispatch;
- worker invocation;
- repair;
- retry;
- new worker behavior.

## Final Outputs

```text
HANDOFF_CONTRACT_DEFINED = TRUE
AUTHORITY_BINDING_DEFINED = TRUE
APPROVAL_BINDING_DEFINED = TRUE
WORKER_SELECTION_BINDING_DEFINED = TRUE
REPLAY_BINDING_DEFINED = TRUE
EXECUTION_READINESS_DEFINED = TRUE
READY_FOR_HANDOFF_RUNTIME = TRUE_WITH_CONTRACT_ONLY_RUNTIME_NOT_IMPLEMENTED
```
