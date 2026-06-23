# ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_BACKLOG_V1

Status: Defined

Scope: Executable implementation backlog for ACLI evidence continuity.

Source plan:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_PLAN_V1
```

Backlog status:

```text
IMPLEMENTATION_BACKLOG_READY
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_BACKLOG_V1_DEFINED
```

## 1. Purpose

This artifact converts the ACLI evidence continuity implementation plan into an actionable backlog.

The backlog exists to close the execution-to-evidence continuity gap discovered during:

```text
ACLI_CERTIFICATION_EXECUTION_001_EXECUTED
```

This is not an ACLI redesign, governance redesign, replay redesign, or certification redesign.

Implementation work must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Backlog completion must not automatically claim `ACLI_GOVERNED_DEVELOPMENT_READY`.

## 2. P0 Backlog

P0 items are mandatory before AEC-001 may be rerun for certification evidence.

### P0-001 Workflow Invocation Artifact Schema

Source work item:

```text
WF-001
```

Goal:

Define a persisted workflow invocation artifact for certification executions.

Acceptance criteria:

- artifact records execution id and scenario id
- artifact links to HIRR evidence or explicitly records missing HIRR as fail-closed
- artifact records candidate workflows
- artifact records selected workflow
- artifact records rejected workflows
- artifact records selection rationale
- artifact records ambiguity and escalation status
- artifact records replay reference

Evidence required to close:

- schema or model artifact
- example AEC-001 workflow invocation artifact
- validation showing required fields are present

### P0-002 Deterministic Workflow Selection Capture

Source work item:

```text
WF-002
```

Goal:

Persist deterministic workflow selection results before mutation.

Acceptance criteria:

- no workflow match blocks execution
- multiple workflow matches block execution or require clarification
- selected workflow must be `GOVERNANCE_ARTIFACT_CREATION` for AEC-001
- mutation cannot occur before workflow evidence exists
- missing invocation evidence fails closed

Evidence required to close:

- workflow invocation output for AEC-001
- fail-closed output for missing or ambiguous workflow state
- replay reference linking workflow evidence to execution

### P0-003 Proposal And Approval Evidence Persistence

Source work item:

```text
GOV-001
```

Goal:

Persist proposal, approval request, and human decision evidence before mutation.

Acceptance criteria:

- proposal artifact exists before approval request
- approval request artifact records target path, mutation type, and validation plan
- human approval or denial artifact is persisted
- approved scope is explicit
- denied or modified scope is preserved when applicable
- missing or stale approval blocks mutation

Evidence required to close:

- development proposal artifact
- approval request artifact
- human approval or denial artifact
- approval ordering proof or replay reference

### P0-004 Bounded Authorization Evidence Persistence

Source work item:

```text
GOV-002
```

Goal:

Persist bounded authorization evidence after approval and before mutation.

Acceptance criteria:

- authorization artifact cannot exist without approval reference
- authorization scope cannot exceed approval scope
- authorization records target path and allowed operation
- authorization records mutation boundary
- mutation cannot occur before authorization
- unauthorized mutation fails closed

Evidence required to close:

- bounded authorization artifact
- approval-to-authorization linkage
- authorization-to-mutation linkage
- fail-closed evidence for missing authorization

### P0-005 Certification Evidence Root

Source work item:

```text
RP-001
```

Goal:

Create deterministic certification evidence root for AEC-001 execution artifacts.

Acceptance criteria:

- evidence root exists for execution id and scenario id
- evidence root contains lifecycle directories
- all emitted artifacts are written under or referenced from the evidence root
- root contains manifest or index reference

Required root pattern:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/
```

Evidence required to close:

- evidence root manifest
- directory inventory
- artifact path inventory

### P0-006 Replay Package Generator

Source work item:

```text
RP-002
```

Goal:

Generate replay package, replay index, reconstruction report, missing-evidence report, and secret-free assessment.

Acceptance criteria:

- replay package includes all lifecycle artifact references
- replay artifact index is generated
- replay reconstruction report is generated
- missing evidence is reported explicitly
- secret-free assessment is generated
- replay fails closed when mandatory evidence is absent
- replay does not repair or infer missing evidence

Evidence required to close:

- development replay package
- replay artifact index
- replay reconstruction report
- missing-evidence report
- secret-free evidence assessment
- negative test or fixture showing fail-closed missing evidence handling

## 3. P1 Backlog

P1 items are required for review-quality evidence and should be completed before final certification review, but they may be implemented after the P0 lifecycle spine is working.

### P1-001 HIRR Evidence Artifact Schema

Source work item:

```text
HIRR-001
```

Goal:

Define persisted HIRR evidence for certification executions.

Acceptance criteria:

- artifact records original request reference
- artifact records resolved intent
- artifact records clarification status
- artifact records ambiguity status
- artifact links to workflow invocation input
- artifact links to replay

Evidence required to close:

- HIRR evidence schema or model
- example AEC-001 HIRR artifact
- field completeness validation

### P1-002 HIRR Capture Hook

Source work item:

```text
HIRR-002
```

Goal:

Capture human request intake and resolved intent into the certification evidence root.

Acceptance criteria:

- original request is captured or referenced
- AEC-001 intent is classified
- clarification is recorded as required or not required
- unresolved ambiguity blocks workflow invocation
- HIRR artifact is written before workflow invocation

Evidence required to close:

- HIRR capture output
- ordering reference showing HIRR before workflow invocation
- fail-closed output for unresolved ambiguity

### P1-003 Repository Context Evidence Persistence

Source work item:

```text
CONTEXT-001
```

Goal:

Persist repository context evidence before proposal and mutation.

Acceptance criteria:

- artifact records repository root
- artifact records target artifact path
- artifact records relevant governance references
- artifact records working tree state or summary
- artifact records context freshness marker
- artifact links to workflow invocation evidence

Evidence required to close:

- repository context artifact
- context freshness artifact
- workflow-to-context linkage

### P1-004 Validation Evidence Binding

Source work item:

```text
RP-003
```

Goal:

Persist validation evidence and bind it into replay.

Acceptance criteria:

- validation command is recorded
- `git diff --check` exit code is recorded
- stdout and stderr references are recorded
- timestamp or ordering marker is recorded
- validation evidence links to mutation and replay

Evidence required to close:

- validation execution artifact
- validation result artifact
- replay reference linking validation result

### P1-005 Evidence Completeness Matrix

Source work item:

```text
RV-001
```

Goal:

Generate a matrix showing completeness of mandatory evidence families.

Acceptance criteria:

- matrix includes HIRR, workflow, context, approval, authorization, mutation, validation, replay, and review evidence
- matrix uses allowed statuses
- missing evidence is explicit
- incomplete evidence blocks readiness recommendation

Evidence required to close:

- evidence completeness matrix
- blocked recommendation output when evidence is incomplete

### P1-006 Scenario Review Artifact

Source work item:

```text
RV-002
```

Goal:

Generate scenario findings from replay-linked evidence.

Acceptance criteria:

- findings use `PASS`, `CONDITIONAL_PASS`, or `FAIL`
- findings link to source evidence
- blockers are listed
- review outcome is recorded
- readiness boundary is preserved

Evidence required to close:

- scenario review artifact
- finding-to-evidence traceability map

## 4. P2 Backlog

P2 items support certification polish and future expansion after AEC-001 evidence continuity is proven.

### P2-001 Review-Board Decision Artifact

Source work item:

```text
RV-003
```

Goal:

Persist review-board decision evidence after evidence package and scenario review are complete.

Acceptance criteria:

- artifact references evidence package
- artifact references replay reconstruction
- artifact records reviewer role references
- artifact records blockers and recommendation
- artifact refuses readiness recommendation when evidence is incomplete

Evidence required to close:

- review-board decision artifact
- readiness recommendation boundary evidence

### P2-002 Multi-Scenario Backlog Expansion

Source work item:

```text
FUTURE-001
```

Goal:

Prepare backlog extension for AEC-002 through AEC-004 after AEC-001 evidence continuity is demonstrated.

Acceptance criteria:

- no AEC-002 through AEC-004 work begins before AEC-001 rerun evidence is reviewable
- extension preserves the same evidence families
- extension does not weaken fail-closed behavior

Evidence required to close:

- future backlog addendum
- AEC-001 reviewable evidence package reference

## 5. Dependencies

Implementation order:

```text
P0-005 Certification Evidence Root
-> P1-001 HIRR Evidence Artifact Schema
-> P1-002 HIRR Capture Hook
-> P0-001 Workflow Invocation Artifact Schema
-> P0-002 Deterministic Workflow Selection Capture
-> P1-003 Repository Context Evidence Persistence
-> P0-003 Proposal And Approval Evidence Persistence
-> P0-004 Bounded Authorization Evidence Persistence
-> P1-004 Validation Evidence Binding
-> P0-006 Replay Package Generator
-> P1-005 Evidence Completeness Matrix
-> P1-006 Scenario Review Artifact
-> P2-001 Review-Board Decision Artifact
-> AEC-001 Re-Execution
```

Dependency rules:

- workflow capture depends on HIRR capture
- approval depends on proposal and repository context
- authorization depends on approval
- mutation depends on authorization
- validation depends on mutation or blocked mutation state
- replay depends on lifecycle evidence
- review depends on replay reconstruction
- review-board decision depends on scenario review

Fail-closed rule:

```text
Missing upstream evidence blocks downstream certification evidence.
```

## 6. Acceptance Criteria

Backlog item acceptance requires:

- implementation artifact or code path exists
- emitted evidence artifact exists
- artifact is persisted under the evidence root or linked from it
- artifact includes execution id and scenario id
- artifact has replay linkage
- missing mandatory input fails closed
- at least one positive AEC-001 fixture or run output exists where applicable
- at least one negative missing-evidence check exists where applicable

Backlog acceptance does not require:

- final certification readiness
- AEC-002 through AEC-004 execution
- release automation
- deployment automation

## 7. Evidence Requirements

Required evidence to close the backlog:

| Evidence family | Required closure evidence |
| --- | --- |
| HIRR | HIRR artifact, ambiguity handling, workflow input reference |
| Workflow | invocation artifact, candidate selection artifact, selected/rejected workflow record |
| Context | repository context artifact, freshness marker, target path |
| Approval | proposal, approval request, human decision, approved scope |
| Authorization | bounded authorization, approval linkage, mutation boundary |
| Mutation | mutation record, changed-file inventory, authorization linkage |
| Validation | `git diff --check` command evidence, exit code, output refs, ordering marker |
| Replay | replay package, artifact index, reconstruction report, missing-evidence report |
| Review | completeness matrix, scenario review, findings |
| Decision | review-board decision artifact when P2 is complete |

Evidence must remain secret-free, replay-visible, and reviewable.

## 8. Re-Execution Readiness

AEC-001 may be rerun when all P0 items are complete and the following P1 items are complete:

- P1-001 HIRR Evidence Artifact Schema
- P1-002 HIRR Capture Hook
- P1-003 Repository Context Evidence Persistence
- P1-004 Validation Evidence Binding

Recommended pre-rerun gate:

```text
AEC_001_RE_EXECUTION_READY
```

Required pre-rerun checks:

- evidence root can be created
- HIRR evidence can be persisted
- workflow invocation evidence can be persisted
- repository context evidence can be persisted
- approval evidence can be persisted
- authorization evidence can be persisted
- validation evidence can be persisted
- replay package can be generated
- missing evidence fails closed

P1 review artifacts should be generated during or immediately after the rerun.

P2 review-board decision artifact may follow after the evidence package is reviewable.

## 9. Success Criteria

Backlog closure succeeds when:

1. All P0 items are complete.
2. Required P1 pre-rerun items are complete.
3. AEC-001 rerun produces persisted evidence for HIRR, workflow, context, approval, authorization, mutation, validation, replay, and review.
4. Replay reconstruction succeeds or fails closed with explicit missing evidence.
5. Evidence completeness matrix is generated.
6. Scenario review artifact is generated.
7. Missing evidence cannot be converted into readiness.
8. Evidence package can be submitted to review-board process.

Backlog closure does not equal:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

## 10. Final Recommendation

Recommendation:

```text
Complete backlog P0 and required P1 items, then rerun AEC-001.
```

Backlog completion should enable:

```text
AEC-001 re-execution
```

provided the pre-rerun gate confirms evidence persistence, replay linkage, and fail-closed missing-evidence behavior.

## 11. Final Verdict

Final backlog verdict:

```text
IMPLEMENTATION_BACKLOG_READY
```

Rationale:

The implementation plan has been converted into ordered, scoped, acceptance-tested backlog items. The backlog is sufficient to drive implementation work needed to close the execution-to-evidence continuity gap for AEC-001 without redesigning ACLI or governance.

Readiness boundary:

```text
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_BACKLOG_V1_DEFINED
```
