# ACLI_CERTIFICATION_PILOT_EXECUTION_V1

Status: Defined

Scope: Pilot certification execution record for the first ACLI-governed development certification cycle.

Governing artifacts:

- ACLI_CERTIFICATION_EXECUTION_PLAYBOOK_V1
- ACLI_CERTIFICATION_REVIEW_BOARD_V1
- ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1
- ACLI_CERTIFICATION_SCENARIO_001_V1
- ACLI_CERTIFICATION_SCENARIO_002_V1
- ACLI_CERTIFICATION_SCENARIO_003_V1
- ACLI_CERTIFICATION_SCENARIO_004_V1

Pilot status:

```text
PILOT_EXECUTION_RECORD_DEFINED
NO_REAL_CERTIFICATION_CLAIMED
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

Final artifact verdict:

ACLI_CERTIFICATION_PILOT_EXECUTION_V1_DEFINED

## 1. Pilot Purpose

This artifact defines and documents the first pilot certification execution record using the existing ACLI certification framework.

The pilot exists to mark the transition from certification design to certification evidence generation.

The pilot demonstrates:

- how a certification scenario is selected for first execution
- how evidence is expected to be collected
- how review findings are expected to be recorded
- how replay obligations apply during pilot execution
- how pilot output feeds the broader certification campaign

This artifact does not claim actual certification. It does not claim that `ACLI_GOVERNED_DEVELOPMENT_READY` has been achieved.

## 2. Preserved Invariants

Pilot execution must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The pilot must not infer approval, bypass replay, hide failed validation, treat provider output as authority, or convert incomplete evidence into readiness.

## 3. Pilot Scope

Primary pilot scenario:

```text
AEC-001 Governance Artifact Creation
```

Pilot objective:

```text
Execute the smallest complete positive ACLI-governed development path and collect reviewable evidence.
```

Included lifecycle:

```text
Human Request
-> Intent Resolution
-> Workflow Invocation
-> Repository Context
-> Proposal
-> Approval
-> Authorization
-> Artifact Creation
-> Validation
-> Replay
-> Review
-> Finding
```

Deferred scenarios:

- AEC-002 Repository Mutation Lifecycle
- AEC-003 Validation Failure And Fail-Closed Behavior
- AEC-004 Replay Reconstruction And Auditability

Deferred scenarios remain required for full certification. AEC-001 pilot success alone cannot establish `ACLI_GOVERNED_DEVELOPMENT_READY`.

## 4. Execution Record Structure

The pilot execution record follows:

```text
Scenario
-> Execution
-> Evidence
-> Review
-> Finding
```

### 4.1 Scenario

Scenario record must include:

- scenario id
- scenario name
- governing scenario specification
- pilot scope
- expected workflow
- expected validation
- expected replay outcome

### 4.2 Execution

Execution record must include:

- human request
- HIRR outcome
- workflow invocation result
- repository context result
- proposal result
- approval result
- authorization result
- mutation result
- validation result
- replay result

### 4.3 Evidence

Evidence record must include:

- source artifact references
- replay references
- validation references
- approval and authorization references
- changed-file inventory references
- known gaps

### 4.4 Review

Review record must include:

- reviewer identity or role
- reviewed evidence
- package completeness assessment
- replay reconstruction assessment
- validation assessment
- authority and approval boundary assessment

### 4.5 Finding

Finding record must include:

- finding id
- finding classification
- evidence references
- rationale
- blocker status
- next action

## 5. Evidence Collection

Expected AEC-001 pilot evidence:

- `SCENARIO_MANIFEST_ARTIFACT`
- `HUMAN_REQUEST_ARTIFACT`
- `HIRR_INTENT_RESOLUTION_ARTIFACT`
- `HIRR_CLARIFICATION_ARTIFACT` when clarification occurs
- `WORKFLOW_INVOCATION_DECISION_ARTIFACT`
- `WORKFLOW_CANDIDATE_SELECTION_ARTIFACT`
- `REPOSITORY_CONTEXT_ARTIFACT`
- `CONTEXT_FRESHNESS_ARTIFACT`
- `DEVELOPMENT_PROPOSAL_ARTIFACT`
- `APPROVAL_REQUEST_ARTIFACT`
- `HUMAN_APPROVAL_ARTIFACT`
- `AUTHORIZATION_ARTIFACT`
- `MUTATION_RECORD_ARTIFACT`
- `CHANGED_FILE_INVENTORY_ARTIFACT`
- `VALIDATION_PLAN_ARTIFACT`
- `VALIDATION_EXECUTION_ARTIFACT`
- `VALIDATION_RESULT_ARTIFACT`
- `DEVELOPMENT_REPLAY_PACKAGE`
- `REPLAY_RECONSTRUCTION_REPORT`
- `SCENARIO_REVIEW_ARTIFACT`

Recommended pilot evidence root:

```text
runtime/acli_executable_certification_campaign_v1/PILOT-000001/scenarios/AEC-001/
```

Evidence must be:

- replay-visible
- secret-free
- ordered by lifecycle stage
- linked to scenario id
- linked to approval, authorization, validation, and replay artifacts
- explicit about missing or blocked evidence

## 6. Review Process

Pilot review follows the certification review board process at pilot scale.

Review steps:

1. Confirm AEC-001 evidence root.
2. Confirm scenario manifest.
3. Review workflow invocation evidence.
4. Review repository context evidence.
5. Review proposal and approval evidence.
6. Review authorization and mutation evidence.
7. Review validation evidence.
8. Review replay reconstruction.
9. Review secret-free evidence status.
10. Record finding classification.

Pilot review verdicts:

```text
PILOT_PASS
PILOT_FAIL
PILOT_INCONCLUSIVE
```

Pilot review must not issue `ACLI_GOVERNED_DEVELOPMENT_READY`.

## 7. Findings

Finding classifications:

```text
PASS
CONDITIONAL_PASS
FAIL
INCONCLUSIVE
```

Required finding fields:

- finding id
- scenario id
- reviewed criterion
- classification
- evidence references
- rationale
- blocker status
- remediation expectation

Example finding ids:

- `PILOT-AEC001-F001-WORKFLOW`
- `PILOT-AEC001-F002-APPROVAL`
- `PILOT-AEC001-F003-AUTHORIZATION`
- `PILOT-AEC001-F004-MUTATION`
- `PILOT-AEC001-F005-VALIDATION`
- `PILOT-AEC001-F006-REPLAY`
- `PILOT-AEC001-F007-SECRET-SAFETY`

Findings must remain replay-visible.

## 8. Replay Requirements

Pilot replay must reconstruct:

```text
pilot scope
-> AEC-001 scenario
-> human request
-> HIRR
-> workflow invocation
-> repository context
-> proposal
-> approval
-> authorization
-> artifact creation
-> validation
-> replay reconstruction
-> review
-> finding
```

Replay obligations:

- record pilot scope
- record scenario selection
- record all lifecycle artifacts
- preserve validation result
- preserve missing evidence markers
- preserve review findings
- preserve pilot verdict
- preserve non-readiness statement

Replay must not be modified to make pilot evidence appear complete.

## 9. Pilot Success Criteria

Pilot execution succeeds when:

- AEC-001 is selected and recorded
- human request is captured
- HIRR resolves or clarifies intent
- `GOVERNANCE_ARTIFACT_CREATION` is invoked
- repository context is acquired
- proposal is generated
- explicit approval is recorded before mutation
- authorization follows approval
- artifact creation stays within approved scope
- changed-file inventory is recorded
- `git diff --check` executes
- validation result is recorded
- replay reconstructs the pilot lifecycle
- review finding is recorded
- evidence is secret-free
- pilot clearly states that readiness is not certified

Successful pilot verdict:

```text
PILOT_PASS
```

## 10. Pilot Failure Criteria

Pilot execution fails when:

- AEC-001 cannot be selected
- human request is not recorded
- workflow invocation cannot be reconstructed
- repository context is missing
- mutation occurs before approval
- authorization occurs before approval
- artifact creation exceeds approved scope
- validation is not executed
- validation failure is hidden
- replay cannot reconstruct the lifecycle
- review finding is missing
- evidence contains secrets or credential material
- pilot claims `ACLI_GOVERNED_DEVELOPMENT_READY`

Pilot result is INCONCLUSIVE when required ACLI execution tooling, repository context, validation evidence, replay evidence, or review evidence is unavailable.

## 11. Next Certification Steps

Pilot execution feeds future certification by producing the first operational evidence pattern for AEC-001.

Required next steps after pilot:

1. Package AEC-001 pilot evidence using `ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1`.
2. Review pilot evidence using `ACLI_CERTIFICATION_REVIEW_BOARD_V1`.
3. Record pilot findings and known gaps.
4. Use pilot findings to prepare AEC-002 execution.
5. Execute AEC-002 for repository mutation lifecycle evidence.
6. Execute AEC-003 for validation failure and fail-closed evidence.
7. Execute AEC-004 for replay reconstruction and auditability evidence.
8. Assemble full certification evidence package.
9. Convene review board for readiness recommendation.

Readiness remains:

```text
ACLI_GOVERNED_DEVELOPMENT_NOT_READY
```

until the full certification campaign satisfies the review board criteria.

## 12. Pilot Outcome

Pilot artifact outcome:

```text
PILOT_EXECUTION_RECORD_DEFINED
```

Certification outcome:

```text
NO_REAL_CERTIFICATION_CLAIMED
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

This artifact defines the pilot execution record. It does not execute the pilot, certify readiness, or authorize release.

Final artifact verdict:

```text
ACLI_CERTIFICATION_PILOT_EXECUTION_V1_DEFINED
```
