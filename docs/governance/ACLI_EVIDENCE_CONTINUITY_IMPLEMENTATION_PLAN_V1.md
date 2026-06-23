# ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_PLAN_V1

Status: Defined

Scope: Implementation plan for closing ACLI execution-to-evidence continuity gaps.

Input artifacts:

- ACLI_CERTIFICATION_EXECUTION_001_EXECUTED
- ACLI_EXECUTION_GAP_ANALYSIS_V1
- ACLI_EVIDENCE_INSTRUMENTATION_ANALYSIS_V1
- ACLI_EVIDENCE_CONTINUITY_REMEDIATION_PLAN_V1
- ACLI_DEVELOPMENT_REPLAY_RUNTIME_V1
- ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1

Current remediation verdict:

```text
MAJOR_REMEDIATION
```

Implementation verdict:

```text
SUBSTANTIAL_IMPLEMENTATION
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_PLAN_V1_DEFINED
```

## 1. Purpose

This artifact translates the evidence continuity remediation plan into concrete implementation work required to make ACLI executions generate certifiable evidence.

This is an implementation-planning artifact. It does not redesign ACLI, governance, replay, Product 1, certification semantics, or the human authority model.

Implementation work must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Implementation must not infer approval, fabricate replay, weaken fail-closed behavior, bypass review, or claim `ACLI_GOVERNED_DEVELOPMENT_READY`.

## 2. Remediation Summary

Observed continuity gap:

```text
Execution occurred, but mandatory lifecycle evidence did not become persistent, replayable, reviewable certification evidence.
```

Observed AEC-001 result:

```text
governance artifact creation: PASS
git diff --check: PASS
certification evidence completeness: FAIL
```

Missing evidence families:

- HIRR evidence
- workflow invocation evidence
- repository context evidence
- approval evidence
- authorization evidence
- replay evidence
- review-board evidence

Implementation objective:

```text
Create the minimum execution-to-evidence path required for AEC-001 rerun evidence to satisfy ACLI_CERTIFICATION_EXECUTION_001_EVIDENCE_V1.
```

Non-objective:

```text
Do not broaden certification scope beyond AEC-001 until evidence continuity is proven.
```

## 3. HIRR Evidence Work

### 3.1 Work Item HIRR-001: HIRR Evidence Artifact Schema

Priority:

```text
P1
```

Implementation candidate:

Define a persisted HIRR evidence artifact for certification executions.

Required fields:

- execution id
- scenario id
- original human request reference
- resolved intent
- clarification required flag
- clarification artifact references when applicable
- ambiguity status
- fail-closed status
- next workflow input reference
- replay reference

Closure test:

AEC-001 rerun writes a HIRR artifact before workflow invocation.

### 3.2 Work Item HIRR-002: HIRR Capture Hook

Priority:

```text
P1
```

Implementation candidate:

Add an execution hook that captures human request intake and HIRR resolution into the certification evidence root.

Required behavior:

- capture original request or approved request reference
- classify intent as governance artifact creation
- record clarification as not required or record clarification evidence
- fail closed on unresolved ambiguity

Closure test:

Workflow invocation must refuse to proceed when HIRR evidence is missing or unresolved.

## 4. Workflow Invocation Evidence Work

### 4.1 Work Item WF-001: Workflow Invocation Artifact Schema

Priority:

```text
P0
```

Implementation candidate:

Define persisted workflow invocation evidence for certification executions.

Required fields:

- execution id
- scenario id
- HIRR artifact reference
- candidate workflows
- selected workflow
- rejected workflows
- selection rationale
- ambiguity status
- escalation status
- invocation verdict
- replay reference

Closure test:

AEC-001 rerun persists `GOVERNANCE_ARTIFACT_CREATION` selection and rejected candidates before repository mutation.

### 4.2 Work Item WF-002: Deterministic Selection Capture

Priority:

```text
P0
```

Implementation candidate:

Instrument the workflow invocation path to record deterministic selection results and fail-closed outcomes.

Required behavior:

- no workflow match blocks execution
- multiple workflow matches block execution or require clarification
- selected workflow must link to HIRR evidence
- mutation must not occur before invocation evidence exists

Closure test:

Removing workflow invocation evidence causes AEC-001 certification to fail closed.

## 5. Approval And Authorization Evidence Work

### 5.1 Work Item GOV-001: Proposal And Approval Evidence

Priority:

```text
P0
```

Implementation candidate:

Add formal proposal and approval evidence emission before repository mutation.

Required artifacts:

- development proposal artifact
- approval request artifact
- human approval or denial artifact

Required fields:

- proposed target path
- proposed mutation type
- validation plan
- approval status
- approved scope
- denied or modified scope when applicable
- timestamp or ordering marker
- replay reference

Closure test:

AEC-001 mutation is blocked when approval evidence is absent, denied, stale, or out of scope.

### 5.2 Work Item GOV-002: Bounded Authorization Evidence

Priority:

```text
P0
```

Implementation candidate:

Add an authorization step that translates approved scope into a bounded authorization artifact before mutation.

Required fields:

- authorization id
- approval artifact reference
- approved artifact path
- authorized operation
- authorized scope
- mutation boundary
- authorization status
- authorization timestamp or ordering marker
- replay reference

Required behavior:

- authorization cannot exist without approval
- authorization cannot broaden approval
- mutation cannot occur before authorization
- unauthorized mutation fails closed

Closure test:

AEC-001 rerun proves approval precedes authorization and authorization precedes mutation.

## 6. Replay Evidence Work

### 6.1 Work Item RP-001: Certification Replay Root

Priority:

```text
P0
```

Implementation candidate:

Create a deterministic evidence root for each certification execution.

Recommended root pattern:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/
```

Required directories:

- intent
- workflow
- context
- approval
- authorization
- mutation
- validation
- replay
- review

Closure test:

AEC-001 rerun writes all required evidence families under one execution root.

### 6.2 Work Item RP-002: Replay Package Generator

Priority:

```text
P0
```

Implementation candidate:

Generate replay package, artifact index, reconstruction report, missing-evidence report, and secret-free assessment from persisted lifecycle artifacts.

Required outputs:

- development replay package
- replay artifact index
- replay reconstruction report
- missing-evidence report
- secret-free evidence assessment

Required behavior:

- replay must fail closed when mandatory artifacts are missing
- replay must not repair missing evidence
- replay must link validation output
- replay must expose approval and authorization continuity

Closure test:

Deleting any mandatory artifact causes replay reconstruction to report failure or incompleteness.

### 6.3 Work Item RP-003: Validation Evidence Binding

Priority:

```text
P1
```

Implementation candidate:

Persist validation command, exit code, stdout/stderr references, and timestamp or ordering markers as replay-linked validation evidence.

Required command for AEC-001:

```bash
git diff --check
```

Closure test:

AEC-001 evidence package includes validation execution evidence and replay references.

## 7. Review Evidence Work

### 7.1 Work Item RV-001: Evidence Completeness Matrix

Priority:

```text
P1
```

Implementation candidate:

Generate an evidence completeness matrix from the evidence package template.

Required statuses:

```text
COMPLETE
INCOMPLETE
FAILED
INCONCLUSIVE
PENDING_EVIDENCE
```

Closure test:

AEC-001 rerun produces a completeness matrix that identifies each mandatory evidence family.

### 7.2 Work Item RV-002: Scenario Review Artifact

Priority:

```text
P1
```

Implementation candidate:

Generate a scenario review artifact that records findings for workflow, approval, authorization, mutation, validation, replay, and secret safety.

Required finding classes:

```text
PASS
CONDITIONAL_PASS
FAIL
```

Closure test:

AEC-001 rerun produces review findings that are traceable to replay evidence.

### 7.3 Work Item RV-003: Review-Board Decision Artifact

Priority:

```text
P2
```

Implementation candidate:

Persist a review-board decision artifact after evidence package and scenario review are complete.

Required fields:

- evidence package reference
- replay reconstruction reference
- reviewer role references
- findings
- blockers
- recommendation
- readiness boundary

Closure test:

Review decision cannot recommend readiness when evidence package is incomplete.

## 8. Dependency Analysis

Implementation dependency order:

```text
1. Certification execution root
2. HIRR evidence capture
3. Workflow invocation evidence capture
4. Repository context evidence capture
5. Proposal and approval evidence capture
6. Bounded authorization evidence capture
7. Mutation and validation evidence capture
8. Replay package generation
9. Evidence completeness matrix
10. Scenario review artifact
11. Review-board decision artifact
12. AEC-001 rerun
```

Dependency constraints:

- workflow evidence depends on HIRR evidence
- approval evidence depends on proposal and repository context evidence
- authorization evidence depends on approval evidence
- mutation evidence depends on authorization evidence
- replay evidence depends on lifecycle evidence and validation evidence
- review evidence depends on replay reconstruction
- readiness recommendation depends on review evidence

Fail-closed dependency rule:

```text
No downstream stage may infer or recreate missing upstream evidence.
```

## 9. Prioritization

### 9.1 P0 Work

P0 implementation work:

- WF-001 Workflow Invocation Artifact Schema
- WF-002 Deterministic Selection Capture
- GOV-001 Proposal And Approval Evidence
- GOV-002 Bounded Authorization Evidence
- RP-001 Certification Replay Root
- RP-002 Replay Package Generator

Reason:

These items close the mandatory continuity chain for workflow selection, human authority, bounded mutation, and replay source of truth.

### 9.2 P1 Work

P1 implementation work:

- HIRR-001 HIRR Evidence Artifact Schema
- HIRR-002 HIRR Capture Hook
- RP-003 Validation Evidence Binding
- RV-001 Evidence Completeness Matrix
- RV-002 Scenario Review Artifact

Reason:

These items make the execution reviewable and ensure that validation and findings are tied to the same replay-visible lifecycle.

### 9.3 P2 Work

P2 implementation work:

- RV-003 Review-Board Decision Artifact

Reason:

The review-board decision artifact is necessary for certification completion but depends on the upstream evidence package and scenario review being produced first.

## 10. Success Criteria

Implementation is complete when AEC-001 rerun produces:

1. A stable execution evidence root.
2. HIRR evidence artifact.
3. Workflow invocation decision artifact.
4. Workflow candidate selection artifact.
5. Repository context artifact.
6. Development proposal artifact.
7. Approval request artifact.
8. Human approval or denial artifact.
9. Bounded authorization artifact.
10. Mutation record and changed-file inventory.
11. Validation evidence including `git diff --check`, exit code, output references, and timestamp or ordering marker.
12. Replay package.
13. Replay artifact index.
14. Replay reconstruction report.
15. Missing-evidence report when applicable.
16. Secret-free evidence assessment.
17. Evidence completeness matrix.
18. Scenario review artifact.
19. Review-board decision artifact.

Implementation closure requires:

```text
Evidence generated = true
Evidence persisted = true
Evidence replay-linked = true
Evidence reviewable = true
Missing evidence fail-closed = true
```

Readiness remains separate:

```text
Implementation complete does not automatically certify ACLI_GOVERNED_DEVELOPMENT_READY.
```

## 11. Final Verdict

Final implementation verdict:

```text
SUBSTANTIAL_IMPLEMENTATION
```

Rationale:

The architecture and specifications are already defined, but closing the observed certification blocker requires an integrated execution-to-evidence implementation path across workflow invocation, approval, authorization, replay, and review. This is more than a small instrumentation patch, but it remains bounded to evidence continuity and does not require governance redesign.

Readiness boundary:

```text
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_PLAN_V1_DEFINED
```
