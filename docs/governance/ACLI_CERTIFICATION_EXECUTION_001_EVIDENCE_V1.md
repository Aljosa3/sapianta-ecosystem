# ACLI_CERTIFICATION_EXECUTION_001_EVIDENCE_V1

Status: Defined

Scope: Evidence recording template for ACLI_CERTIFICATION_EXECUTION_001_V1.

Execution reference:

- ACLI_CERTIFICATION_EXECUTION_001_V1

Scenario reference:

- ACLI_CERTIFICATION_SCENARIO_001_V1

Evidence status:

```text
EVIDENCE_RECORD_TEMPLATE_DEFINED
NO_EXECUTION_CLAIMED
NO_EVIDENCE_CLAIMED
NO_CERTIFICATION_COMPLETED
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

Final artifact verdict:

ACLI_CERTIFICATION_EXECUTION_001_EVIDENCE_V1_DEFINED

## 1. Purpose

This artifact defines the evidence recording structure for the first ACLI certification execution cycle.

It is intended to be populated during actual execution of:

```text
ACLI_CERTIFICATION_EXECUTION_001_V1
```

using:

```text
AEC-001 Governance Artifact Creation
```

This artifact is a template only. It does not claim execution occurred, evidence exists, certification completed, or `ACLI_GOVERNED_DEVELOPMENT_READY`.

## 2. Preserved Invariants

Evidence recording must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Evidence recording must not infer approval, fabricate evidence, bypass replay, hide validation failure, treat provider output as authority, or convert incomplete evidence into readiness.

## 3. Execution Metadata

Required execution identifiers:

```text
execution_id: PENDING_EVIDENCE
execution_artifact: ACLI_CERTIFICATION_EXECUTION_001_V1
scenario_id: AEC-001
scenario_name: Governance Artifact Creation
campaign_id: PENDING_EVIDENCE
evidence_package_id: PENDING_EVIDENCE
operator_reference: PENDING_EVIDENCE
execution_started_at: PENDING_EVIDENCE
execution_completed_at: PENDING_EVIDENCE
execution_status: PENDING_EVIDENCE
replay_root: PENDING_EVIDENCE
evidence_root: runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/
```

Allowed execution status values:

```text
PENDING_EXECUTION
IN_PROGRESS
COMPLETED
FAILED
INCONCLUSIVE
BLOCKED
```

Default template status:

```text
PENDING_EXECUTION
```

## 4. Scenario Metadata

Scenario:

```text
AEC-001 Governance Artifact Creation
```

Expected workflow:

```text
GOVERNANCE_ARTIFACT_CREATION
```

Expected validation:

```text
git diff --check
```

Expected lifecycle:

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

Scenario evidence status:

```text
PENDING_EVIDENCE
```

## 5. Workflow Evidence Section

Required workflow evidence fields:

```text
human_request_artifact: PENDING_EVIDENCE
hirr_intake_artifact: PENDING_EVIDENCE
hirr_intent_resolution_artifact: PENDING_EVIDENCE
hirr_clarification_artifact: PENDING_EVIDENCE_OR_NOT_APPLICABLE
workflow_invocation_inputs_artifact: PENDING_EVIDENCE
workflow_invocation_decision_artifact: PENDING_EVIDENCE
workflow_candidate_selection_artifact: PENDING_EVIDENCE
selected_workflow: PENDING_EVIDENCE
rejected_workflow_candidates: PENDING_EVIDENCE
workflow_selection_rationale: PENDING_EVIDENCE
workflow_invocation_status: PENDING_EVIDENCE
provider_participation: PENDING_EVIDENCE_OR_NOT_APPLICABLE
worker_invoked_before_authorization: PENDING_EVIDENCE_EXPECTED_FALSE
```

Required workflow evidence verdict:

```text
WORKFLOW_EVIDENCE_PENDING
```

Completion condition:

Workflow evidence is complete only when selected workflow, rejected candidates, selection rationale, and replay-visible invocation artifacts are present.

## 6. Approval Evidence Section

Required approval evidence fields:

```text
development_proposal_artifact: PENDING_EVIDENCE
approval_request_artifact: PENDING_EVIDENCE
human_approval_artifact: PENDING_EVIDENCE_OR_DENIAL_ARTIFACT
approval_status: PENDING_EVIDENCE
approved_scope: PENDING_EVIDENCE
approved_target_artifact_path: PENDING_EVIDENCE
approved_validation_plan: PENDING_EVIDENCE
approval_recorded_at: PENDING_EVIDENCE
authorization_artifact: PENDING_EVIDENCE_WHEN_APPROVED
authorization_status: PENDING_EVIDENCE
authorized_scope: PENDING_EVIDENCE
authorization_recorded_at: PENDING_EVIDENCE
approval_precedes_authorization: PENDING_EVIDENCE_EXPECTED_TRUE
authorization_precedes_mutation: PENDING_EVIDENCE_EXPECTED_TRUE
```

Allowed approval status values:

```text
APPROVED
DENIED
MODIFIED_SCOPE
MISSING
STALE
PENDING_EVIDENCE
```

Required approval evidence verdict:

```text
APPROVAL_EVIDENCE_PENDING
```

Completion condition:

Approval evidence is complete only when proposal, approval request, human decision, approved or denied scope, and authorization linkage are replay-visible.

## 7. Validation Evidence Section

Required validation evidence fields:

```text
validation_plan_artifact: PENDING_EVIDENCE
validation_execution_artifact: PENDING_EVIDENCE
validation_result_artifact: PENDING_EVIDENCE
validation_family: documentation-only governance artifact validation
validation_command: git diff --check
validation_started_at: PENDING_EVIDENCE
validation_completed_at: PENDING_EVIDENCE
validation_exit_code: PENDING_EVIDENCE
validation_stdout_reference: PENDING_EVIDENCE_OR_EMPTY
validation_stderr_reference: PENDING_EVIDENCE_OR_EMPTY
validation_result_classification: PENDING_EVIDENCE
validation_failures: PENDING_EVIDENCE_OR_EMPTY
validation_inconclusive_reasons: PENDING_EVIDENCE_OR_EMPTY
release_handoff_eligible: PENDING_EVIDENCE
```

Expected validation command:

```bash
git diff --check
```

Allowed validation result classifications:

```text
PASS
FAIL
INCONCLUSIVE
BLOCKED
PENDING_EVIDENCE
```

Required validation evidence verdict:

```text
VALIDATION_EVIDENCE_PENDING
```

Completion condition:

Validation evidence is complete only when validation plan, command execution, result classification, timestamps or ordering markers, and release handoff eligibility are recorded.

## 8. Replay Evidence Section

Required replay evidence fields:

```text
development_replay_package: PENDING_EVIDENCE
replay_artifact_index: PENDING_EVIDENCE
replay_reconstruction_report: PENDING_EVIDENCE
replay_reconstruction_status: PENDING_EVIDENCE
missing_evidence_report: PENDING_EVIDENCE_OR_EMPTY
secret_free_evidence_assessment: PENDING_EVIDENCE
replay_reconstructs_human_request: PENDING_EVIDENCE
replay_reconstructs_hirr: PENDING_EVIDENCE
replay_reconstructs_workflow_invocation: PENDING_EVIDENCE
replay_reconstructs_repository_context: PENDING_EVIDENCE
replay_reconstructs_proposal: PENDING_EVIDENCE
replay_reconstructs_approval: PENDING_EVIDENCE
replay_reconstructs_authorization: PENDING_EVIDENCE
replay_reconstructs_mutation: PENDING_EVIDENCE
replay_reconstructs_validation: PENDING_EVIDENCE
replay_reconstructs_review: PENDING_EVIDENCE
```

Allowed replay reconstruction status values:

```text
REPLAY_RECONSTRUCTED
REPLAY_PARTIAL
REPLAY_FAILED
REPLAY_INCONCLUSIVE
PENDING_EVIDENCE
```

Required replay evidence verdict:

```text
REPLAY_EVIDENCE_PENDING
```

Completion condition:

Replay evidence is complete only when replay reconstructs the full AEC-001 lifecycle or explicitly records missing evidence and blocks readiness.

## 9. Audit Evidence Section

Required audit evidence fields:

```text
scenario_review_artifact: PENDING_EVIDENCE
evidence_completeness_assessment: PENDING_EVIDENCE
workflow_finding_reference: PENDING_EVIDENCE
approval_finding_reference: PENDING_EVIDENCE
authorization_finding_reference: PENDING_EVIDENCE
mutation_finding_reference: PENDING_EVIDENCE
validation_finding_reference: PENDING_EVIDENCE
replay_finding_reference: PENDING_EVIDENCE
secret_safety_finding_reference: PENDING_EVIDENCE
trust_verification_status: PENDING_EVIDENCE
reviewer_reference: PENDING_EVIDENCE
review_completed_at: PENDING_EVIDENCE
```

Allowed trust verification values:

```text
TRUST_VERIFIED
TRUST_NOT_VERIFIED
TRUST_INCONCLUSIVE
PENDING_EVIDENCE
```

Required audit evidence verdict:

```text
AUDIT_EVIDENCE_PENDING
```

Completion condition:

Audit evidence is complete only when review findings cover workflow, approval, authorization, mutation, validation, replay, and secret-safety evidence.

## 10. Findings Section

Required reviewer finding fields:

```text
finding_id: PENDING_EVIDENCE
scenario_id: AEC-001
criterion: PENDING_EVIDENCE
classification: PENDING_EVIDENCE
evidence_references: PENDING_EVIDENCE
rationale: PENDING_EVIDENCE
blocker_status: PENDING_EVIDENCE
required_remediation: PENDING_EVIDENCE_OR_NOT_APPLICABLE
reviewer_reference: PENDING_EVIDENCE
recorded_at: PENDING_EVIDENCE
```

Allowed finding classifications:

```text
PASS
CONDITIONAL_PASS
FAIL
INCONCLUSIVE
PENDING_EVIDENCE
```

Minimum findings expected:

- workflow finding
- approval finding
- authorization finding
- mutation finding
- validation finding
- replay finding
- secret-safety finding

Findings must not infer missing evidence.

## 11. Certification Recommendation Section

Required recommendation fields:

```text
execution_verdict: PENDING_EVIDENCE
scenario_verdict: PENDING_EVIDENCE
evidence_package_status: PENDING_EVIDENCE
readiness_recommendation: ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
recommendation_rationale: PENDING_EVIDENCE
blocking_findings: PENDING_EVIDENCE_OR_EMPTY
known_limitations: PENDING_EVIDENCE_OR_EMPTY
next_action: PENDING_EVIDENCE
review_board_reference: PENDING_EVIDENCE_OR_NOT_APPLICABLE
executive_approval_reference: PENDING_EVIDENCE_OR_NOT_APPLICABLE
```

Allowed execution verdict values:

```text
ACLI_CERTIFICATION_EXECUTION_001_PASS
ACLI_CERTIFICATION_EXECUTION_001_FAIL
ACLI_CERTIFICATION_EXECUTION_001_INCONCLUSIVE
PENDING_EVIDENCE
```

Important restriction:

```text
This evidence record cannot recommend ACLI_GOVERNED_DEVELOPMENT_READY by itself.
```

## 12. Evidence Completeness Rules

Evidence package status values:

```text
COMPLETE
INCOMPLETE
FAILED
INCONCLUSIVE
PENDING_EVIDENCE
```

Evidence is COMPLETE only when:

- execution metadata is populated
- scenario metadata is populated
- workflow evidence is complete
- approval evidence is complete
- authorization evidence is complete when approval is granted
- mutation evidence is complete when mutation occurs
- validation evidence is complete
- replay evidence is complete
- audit evidence is complete
- findings are recorded
- secret-free evidence assessment passes
- no mandatory evidence field remains `PENDING_EVIDENCE`

Evidence is INCOMPLETE when:

- any required artifact reference is missing
- any mandatory field remains `PENDING_EVIDENCE`
- approval, authorization, validation, replay, or audit evidence is absent
- missing evidence markers are not recorded

Evidence is FAILED when:

- mutation occurs before approval
- authorization occurs before approval
- validation failure is hidden
- replay cannot reconstruct mandatory lifecycle stages
- evidence contains secrets or credential material
- evidence claims readiness from AEC-001 alone

Evidence is INCONCLUSIVE when:

- required tooling, repository context, validation output, replay output, or review output is unavailable or uninterpretable.

## 13. Template Outcome

Template status:

```text
EVIDENCE_RECORD_TEMPLATE_DEFINED
```

Certification status:

```text
NO_EXECUTION_CLAIMED
NO_EVIDENCE_CLAIMED
NO_CERTIFICATION_COMPLETED
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

This artifact defines the canonical evidence record for the first certification cycle. It does not execute the cycle, populate evidence, certify readiness, or authorize release.

Final artifact verdict:

```text
ACLI_CERTIFICATION_EXECUTION_001_EVIDENCE_V1_DEFINED
```
