# ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_SEQUENCE_V1

Status: Defined

Scope: Deterministic implementation sequence for closing ACLI evidence continuity gaps.

Source backlog:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_BACKLOG_V1
```

Sequence verdict:

```text
IMPLEMENTATION_SEQUENCE_READY
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_SEQUENCE_V1_DEFINED
```

## 1. Purpose

This artifact defines the implementation order for closing ACLI evidence continuity gaps.

It focuses only on sequencing. It does not redesign ACLI, governance, replay, certification, or Product 1.

Implementation sequencing must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

No stage may infer missing upstream evidence or convert incomplete evidence into readiness.

## 2. P0 Implementation Sequence

The P0 implementation sequence is:

```text
S0 Evidence Root
-> S1 HIRR Evidence Persistence
-> S2 Workflow Invocation Persistence
-> S3 Repository Context Persistence
-> S4 Approval Persistence
-> S5 Authorization Persistence
-> S6 Mutation And Validation Persistence
-> S7 Replay Linkage Persistence
-> S8 Completeness And Review Evidence
-> S9 AEC-001 Re-Execution Gate
```

### S0 Evidence Root

Backlog reference:

```text
P0-005 Certification Evidence Root
```

Implementation target:

Create the deterministic evidence root before any lifecycle artifact is emitted.

Expected root:

```text
runtime/acli_executable_certification_campaign_v1/EXEC-001/scenarios/AEC-001/
```

Verification:

- root exists
- lifecycle directories exist
- manifest or index exists
- emitted artifacts can be written under the root

Expected evidence after S0:

- evidence root manifest
- directory inventory
- artifact path policy

### S1 HIRR Evidence Persistence

Backlog references:

```text
P1-001 HIRR Evidence Artifact Schema
P1-002 HIRR Capture Hook
```

Implementation target:

Persist human request intake and resolved intent before workflow invocation.

Verification:

- original request is captured or referenced
- resolved intent is recorded
- ambiguity status is recorded
- unresolved ambiguity fails closed
- HIRR artifact links to the evidence root

Expected evidence after S1:

- HIRR intake artifact
- HIRR intent resolution artifact
- clarification artifact or not-applicable marker
- fail-closed ambiguity evidence when applicable

### S2 Workflow Invocation Persistence

Backlog references:

```text
P0-001 Workflow Invocation Artifact Schema
P0-002 Deterministic Workflow Selection Capture
```

Implementation target:

Persist deterministic workflow selection before repository context acquisition and mutation.

Verification:

- workflow invocation artifact links to HIRR evidence
- selected workflow is recorded
- rejected candidate workflows are recorded
- selection rationale is recorded
- no-match and multi-match cases fail closed
- mutation is blocked until workflow evidence exists

Expected evidence after S2:

- workflow invocation inputs artifact
- workflow invocation decision artifact
- workflow candidate selection artifact
- fail-closed workflow ambiguity artifact when applicable

### S3 Repository Context Persistence

Backlog reference:

```text
P1-003 Repository Context Evidence Persistence
```

Implementation target:

Persist repository context before proposal, approval, authorization, or mutation.

Verification:

- repository root is recorded
- target governance artifact path or family is recorded
- relevant governance references are recorded
- working tree state or summary is recorded
- context freshness marker is recorded
- context links to workflow invocation evidence

Expected evidence after S3:

- repository context artifact
- context freshness artifact
- workflow-to-context linkage

### S4 Approval Persistence

Backlog reference:

```text
P0-003 Proposal And Approval Evidence Persistence
```

Implementation target:

Persist proposal, approval request, and human decision evidence before authorization.

Verification:

- proposal exists before approval request
- approval request records target path, operation type, and validation plan
- human approval or denial is persisted
- approved scope is explicit
- missing, stale, denied, or out-of-scope approval blocks authorization

Expected evidence after S4:

- development proposal artifact
- approval request artifact
- human approval or denial artifact
- approval ordering evidence

### S5 Authorization Persistence

Backlog reference:

```text
P0-004 Bounded Authorization Evidence Persistence
```

Implementation target:

Persist bounded authorization after approval and before mutation.

Verification:

- authorization links to approval
- authorization scope does not exceed approval scope
- authorized path and operation are recorded
- mutation boundary is recorded
- mutation is blocked until authorization exists
- missing authorization fails closed

Expected evidence after S5:

- bounded authorization artifact
- approval-to-authorization linkage
- authorization-to-mutation boundary evidence
- fail-closed missing authorization artifact when applicable

### S6 Mutation And Validation Persistence

Backlog reference:

```text
P1-004 Validation Evidence Binding
```

Implementation target:

Persist mutation and validation evidence after authorization.

Verification:

- mutation record links to authorization
- changed-file inventory is recorded
- validation command is recorded
- `git diff --check` exit code is recorded
- stdout and stderr references are recorded
- validation evidence links to mutation

Expected evidence after S6:

- mutation record artifact
- changed-file inventory artifact
- validation execution artifact
- validation result artifact

### S7 Replay Linkage Persistence

Backlog reference:

```text
P0-006 Replay Package Generator
```

Implementation target:

Generate replay package and reconstruction evidence from persisted lifecycle artifacts.

Verification:

- replay package includes all mandatory lifecycle references
- replay artifact index exists
- reconstruction report exists
- missing-evidence report exists when applicable
- secret-free evidence assessment exists
- replay fails closed when mandatory artifacts are absent

Expected evidence after S7:

- development replay package
- replay artifact index
- replay reconstruction report
- missing-evidence report
- secret-free evidence assessment

### S8 Completeness And Review Evidence

Backlog references:

```text
P1-005 Evidence Completeness Matrix
P1-006 Scenario Review Artifact
P2-001 Review-Board Decision Artifact
```

Implementation target:

Generate reviewable evidence summaries after replay linkage exists.

Verification:

- completeness matrix includes all mandatory evidence families
- missing evidence blocks readiness recommendation
- scenario findings link to source evidence
- review-board decision artifact refuses readiness when package is incomplete

Expected evidence after S8:

- evidence completeness matrix
- scenario review artifact
- finding-to-evidence traceability map
- review-board decision artifact when P2 is complete

### S9 AEC-001 Re-Execution Gate

Implementation target:

Confirm AEC-001 can be rerun with persistent, replay-linked, reviewable evidence.

Verification:

- all S0 through S7 outputs are available
- S8 completeness and review evidence generation is available or ready to run immediately after execution
- missing evidence fails closed
- no readiness claim is made before review

Expected gate result:

```text
AEC_001_RE_EXECUTION_READY
```

## 3. Dependency Validation

Ordering matters because each lifecycle stage depends on prior evidence.

Dependency chain:

| Stage | Depends on | Reason |
| --- | --- | --- |
| Evidence root | none | Later evidence needs stable persistence location |
| HIRR | evidence root | Intent evidence must be persisted before workflow selection |
| Workflow invocation | HIRR | Workflow selection must derive from resolved human intent |
| Repository context | workflow invocation | Context must match the selected workflow and target scope |
| Approval | context and proposal | Human approval must reference what is proposed |
| Authorization | approval | Governance authorization cannot exist without human approval |
| Mutation | authorization | Worker execution must be bounded before mutation |
| Validation | mutation or blocked mutation | Validation must check actual mutation state |
| Replay | lifecycle evidence | Replay reconstructs completed or blocked lifecycle stages |
| Review | replay | Review must evaluate replay-linked evidence, not assumptions |

Dependency validation rule:

```text
If a dependency is missing, the dependent stage must fail closed.
```

## 4. Incremental Verification

Each implementation stage must be verified before the next stage becomes certification-relevant.

Verification sequence:

| Stage | Incremental verification |
| --- | --- |
| S0 | Create root and manifest; verify artifact write path |
| S1 | Generate HIRR artifact; verify unresolved ambiguity blocks workflow |
| S2 | Generate workflow artifact; verify missing or ambiguous workflow fails closed |
| S3 | Generate context artifact; verify target path and freshness are present |
| S4 | Generate approval artifacts; verify denied or missing approval blocks authorization |
| S5 | Generate authorization artifact; verify unauthorized mutation is blocked |
| S6 | Generate mutation and validation artifacts; verify `git diff --check` result is persisted |
| S7 | Generate replay package; verify missing mandatory evidence is reported |
| S8 | Generate completeness and review artifacts; verify incomplete evidence blocks recommendation |
| S9 | Run pre-rerun checklist; verify `AEC_001_RE_EXECUTION_READY` or fail closed |

Minimum validation command for documentation-only implementation changes:

```bash
git diff --check
```

Additional tests may be added when implementation code is touched.

## 5. Re-Execution Gates

### Gate G1: Evidence Root Ready

Required before S1:

- evidence root exists
- manifest exists
- lifecycle directories exist

Gate verdicts:

```text
EVIDENCE_ROOT_READY
EVIDENCE_ROOT_NOT_READY
```

### Gate G2: Pre-Mutation Governance Ready

Required before any repository mutation in AEC-001:

- HIRR evidence exists
- workflow invocation evidence exists
- repository context evidence exists
- approval evidence exists
- authorization evidence exists

Gate verdicts:

```text
PRE_MUTATION_GOVERNANCE_READY
PRE_MUTATION_GOVERNANCE_NOT_READY
```

### Gate G3: Replay Ready

Required before review:

- mutation and validation evidence exist or blocked mutation evidence exists
- replay package generator can reconstruct lifecycle evidence
- missing evidence is recorded explicitly
- secret-free assessment is available

Gate verdicts:

```text
REPLAY_READY
REPLAY_NOT_READY
```

### Gate G4: Re-Execution Ready

Required before rerunning AEC-001:

- S0 through S7 are complete
- S8 can produce review artifacts
- fail-closed missing-evidence behavior has been verified

Gate verdicts:

```text
AEC_001_RE_EXECUTION_READY
AEC_001_RE_EXECUTION_NOT_READY
```

## 6. Rollback Strategy

Rollback means stopping the sequence and preserving evidence of failure. It does not mean erasing evidence.

Rollback requirements:

- preserve all artifacts already emitted
- write or update missing-evidence report
- record failing stage
- record blocker reason
- do not proceed to downstream stages
- do not reuse a contaminated replay root for a clean rerun unless the rerun is explicitly versioned
- do not claim readiness from partial evidence

Rollback outcomes:

```text
IMPLEMENTATION_STAGE_FAILED_CLOSED
EVIDENCE_PRESERVED
DOWNSTREAM_EXECUTION_BLOCKED
```

If an implementation artifact is incorrect, remediation must create a new corrected artifact or versioned rerun evidence. It must not silently rewrite prior replay evidence.

## 7. Evidence Expectations

Expected evidence after each stage:

| Stage | Expected evidence |
| --- | --- |
| S0 | evidence root manifest, directory inventory |
| S1 | HIRR intake, intent resolution, clarification or not-applicable marker |
| S2 | workflow invocation inputs, decision, candidate selection |
| S3 | repository context, freshness marker |
| S4 | proposal, approval request, human approval or denial |
| S5 | bounded authorization, approval-to-authorization link |
| S6 | mutation record, changed-file inventory, validation execution, validation result |
| S7 | replay package, artifact index, reconstruction report, missing-evidence report, secret-free assessment |
| S8 | completeness matrix, scenario review, findings, review-board decision when applicable |
| S9 | re-execution gate verdict |

Evidence quality requirements:

- persisted under or linked from evidence root
- includes execution id and scenario id
- includes replay reference when applicable
- is secret-free
- is reviewable
- fails closed when mandatory inputs are missing

## 8. Success Criteria

Sequence completion succeeds when:

1. S0 through S7 are implemented and verified.
2. S8 review evidence generation is implemented or available immediately after rerun.
3. All re-execution gates pass.
4. Missing evidence fails closed at each dependent stage.
5. AEC-001 can be rerun without relying on chat-only claims.
6. Generated evidence satisfies the structure of `ACLI_CERTIFICATION_EXECUTION_001_EVIDENCE_V1`.
7. No readiness claim is made before replay and review.

Sequence completion does not equal:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

## 9. Final Recommendation

Recommendation:

```text
Implement the sequence S0 through S8, then permit AEC-001 re-execution only after Gate G4 returns AEC_001_RE_EXECUTION_READY.
```

Sequence completion should permit:

```text
AEC-001 re-execution
```

only when evidence persistence, replay linkage, and fail-closed missing-evidence handling have been verified.

## 10. Final Verdict

Final sequence verdict:

```text
IMPLEMENTATION_SEQUENCE_READY
```

Rationale:

The implementation backlog has been converted into a deterministic execution order with stage-level verification, gates, rollback handling, and expected evidence outputs. The sequence leads to AEC-001 re-execution without redesigning ACLI or governance.

Readiness boundary:

```text
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_IMPLEMENTATION_SEQUENCE_V1_DEFINED
```
