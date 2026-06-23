# ACLI_EVIDENCE_CONTINUITY_REMEDIATION_PLAN_V1

Status: Defined

Scope: Execution-to-evidence remediation plan for ACLI certification continuity.

Input analyses:

- ACLI_CERTIFICATION_EXECUTION_001_EXECUTED
- ACLI_EXECUTION_GAP_ANALYSIS_V1
- ACLI_EVIDENCE_INSTRUMENTATION_ANALYSIS_V1

Observed verdict:

```text
MIXED_GAPS
```

Remediation verdict:

```text
MAJOR_REMEDIATION
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_REMEDIATION_PLAN_V1_DEFINED
```

## 1. Purpose

This artifact defines the minimum remediation needed to convert ACLI execution into persistent, replayable, reviewable certification evidence.

This is not an architecture redesign. It does not redefine ACLI, governance, replay, Product 1, or certification semantics.

This plan preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The plan does not fabricate evidence, infer approval, repair missing replay by assertion, or claim `ACLI_GOVERNED_DEVELOPMENT_READY`.

## 2. Observed Problem

`ACLI_CERTIFICATION_EXECUTION_001_EXECUTED` showed that ACLI-governed development preparation was sufficient to create a governance artifact and run basic validation:

```text
governance artifact creation: succeeded
git diff --check: passed
```

However, the execution did not produce reviewable certification evidence for mandatory lifecycle stages:

- HIRR intent resolution
- workflow invocation
- repository context
- approval
- authorization
- replay
- review board

Observed continuity failure:

```text
Execution occurred, but execution evidence did not become persistent certification evidence.
```

Certification consequence:

```text
ACLI_GOVERNED_DEVELOPMENT_READY remains blocked.
```

## 3. Evidence Continuity Model

The remediation target is the following continuity chain:

```text
Execution
-> Evidence Capture
-> Evidence Persistence
-> Replay Linkage
-> Review Artifact
-> Certification Review
```

### 3.1 Execution

Execution is the actual governed activity being certified.

For AEC-001, execution is:

```text
Governance Artifact Creation
```

Execution alone is not certification evidence unless each governed lifecycle transition emits durable evidence.

### 3.2 Evidence Capture

Evidence capture records each lifecycle transition at the time it occurs.

Required captured events:

- human request received
- HIRR intent resolved or clarification requested
- workflow invoked
- repository context acquired
- proposal generated
- approval requested
- human decision recorded
- authorization issued or denied
- mutation performed or blocked
- validation executed
- replay package generated
- review artifact produced

### 3.3 Evidence Persistence

Captured evidence must be written to stable artifact paths with scenario, execution, timestamp or ordering marker, and hash or reference fields.

Evidence must not remain only in conversation, terminal output, transient memory, or unstated operator knowledge.

### 3.4 Replay Linkage

Persisted evidence must be linked into a replay package that reconstructs:

```text
Intent
-> Workflow
-> Repository Context
-> Approval
-> Authorization
-> Mutation
-> Validation
-> Review
```

Replay linkage must expose missing evidence rather than silently repairing it.

### 3.5 Review Artifact

The review artifact converts replay-linked evidence into findings.

Required finding classes:

```text
PASS
CONDITIONAL_PASS
FAIL
```

The review artifact must identify blockers, limitations, and whether certification recommendation is allowed.

### 3.6 Certification Review

Certification review may occur only after the evidence package is complete enough for review-board evaluation.

Certification review must not claim readiness from incomplete evidence.

## 4. HIRR Evidence Remediation

Observed gap:

```text
HIRR intent resolution evidence was missing.
```

Remediation candidates:

1. Emit a HIRR intake artifact when a human request enters AEC-001 execution.
2. Persist the original human request text or approved request reference.
3. Record resolved intent classification.
4. Record whether clarification was required.
5. Record clarification artifacts when applicable.
6. Record fail-closed ambiguity status when intent cannot be resolved.
7. Link HIRR artifact to workflow invocation input.

Minimum closure artifact:

```text
HIRR_INTENT_RESOLUTION_ARTIFACT
```

Minimum closure fields:

- execution id
- scenario id
- original human request reference
- resolved intent
- clarification status
- ambiguity status
- next workflow input reference
- replay reference

## 5. Workflow Evidence Remediation

Observed gap:

```text
Workflow invocation and candidate-selection evidence were missing.
```

Remediation candidates:

1. Emit workflow invocation inputs.
2. Persist selected workflow.
3. Persist rejected workflow candidates.
4. Record workflow selection rationale.
5. Record ambiguity and escalation outcome.
6. Record fail-closed state when no workflow or multiple workflows match.
7. Link workflow invocation to repository context acquisition.

Minimum closure artifacts:

```text
WORKFLOW_INVOCATION_DECISION_ARTIFACT
WORKFLOW_CANDIDATE_SELECTION_ARTIFACT
```

Minimum closure fields:

- execution id
- scenario id
- HIRR artifact reference
- selected workflow
- rejected candidates
- selection rationale
- ambiguity status
- invocation verdict
- replay reference

## 6. Approval And Authorization Remediation

Observed gaps:

```text
Approval request evidence was missing.
Human approval artifact was missing as formal ACLI evidence.
Bounded authorization artifact was missing.
```

Remediation candidates:

1. Emit a proposal artifact before mutation.
2. Emit an approval request artifact with explicit scope.
3. Record the human decision as a formal approval or denial artifact.
4. Preserve approved scope, denied scope, and modified scope when applicable.
5. Emit bounded authorization only after approval.
6. Record authorization-to-mutation linkage.
7. Fail closed when approval is missing, stale, ambiguous, or out of scope.

Minimum closure artifacts:

```text
DEVELOPMENT_PROPOSAL_ARTIFACT
APPROVAL_REQUEST_ARTIFACT
HUMAN_APPROVAL_ARTIFACT
AUTHORIZATION_ARTIFACT
```

Minimum closure fields:

- proposal id
- approval request id
- human decision
- approved artifact path
- approved operation type
- authorization id
- authorized scope
- authorization timestamp or ordering marker
- mutation boundary
- replay reference

## 7. Replay Evidence Remediation

Observed gaps:

```text
Replay package, replay index, replay reconstruction report, and secret-free replay assessment were missing.
```

Remediation candidates:

1. Create a replay root for each certification execution.
2. Persist lifecycle artifacts in replay-linked order.
3. Generate replay artifact index.
4. Generate replay reconstruction report.
5. Generate missing-evidence report when any required evidence is absent.
6. Generate secret-free evidence assessment.
7. Link validation result into replay.
8. Fail closed when replay is missing, partial, non-reconstructable, or manually repaired.

Minimum closure artifacts:

```text
DEVELOPMENT_REPLAY_PACKAGE
REPLAY_ARTIFACT_INDEX
REPLAY_RECONSTRUCTION_REPORT
SECRET_FREE_EVIDENCE_ASSESSMENT
```

Minimum closure fields:

- replay root
- ordered artifact references
- lifecycle reconstruction status
- missing evidence list
- secret-free assessment
- validation reference
- approval and authorization references
- reconstruction verdict

## 8. Review Evidence Remediation

Observed gaps:

```text
Audit review artifact, reviewer assignment evidence, and review-board decision artifact were missing.
```

Remediation candidates:

1. Assign operator, auditor, reviewer, and executive approver roles for the execution.
2. Emit evidence completeness matrix.
3. Emit audit review artifact.
4. Classify findings as `PASS`, `CONDITIONAL_PASS`, or `FAIL`.
5. Record blockers and limitations.
6. Emit review-board decision artifact.
7. Preserve `ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED` unless all mandatory evidence is complete and review approves readiness.

Minimum closure artifacts:

```text
AUDIT_REVIEW_ARTIFACT
EVIDENCE_COMPLETENESS_MATRIX
SCENARIO_REVIEW_ARTIFACT
REVIEW_BOARD_DECISION_ARTIFACT
```

Minimum closure fields:

- reviewer identities or role references
- evidence package reference
- replay reconstruction reference
- findings
- blocker list
- recommendation
- final review outcome

## 9. Prioritization

Remediation priority:

| Priority | Action | Readiness impact |
| --- | --- | --- |
| P0 | Bind replay package generation to AEC-001 execution | Required because replay is the source of truth |
| P0 | Bind approval and authorization artifact creation before mutation | Required because Human = Authority and mutation must be bounded |
| P0 | Emit workflow invocation evidence before repository mutation | Required to prove deterministic governed workflow selection |
| P1 | Emit HIRR evidence before workflow invocation | Required to prove resolved intent |
| P1 | Emit repository context evidence before proposal | Required to prove scoped repository awareness |
| P1 | Emit review-board evidence after replay package generation | Required to convert evidence into certification findings |
| P2 | Add secret-free evidence assessment to every replay package | Required before evidence is accepted for review |

Recommended remediation sequence:

```text
HIRR capture
-> workflow invocation capture
-> repository context capture
-> proposal and approval capture
-> authorization capture
-> mutation and validation capture
-> replay package generation
-> audit review generation
-> rerun AEC-001
```

## 10. Success Criteria

Remediation is complete when an AEC-001 rerun produces all of the following measurable evidence:

1. HIRR artifact exists and links original request to resolved intent.
2. Workflow invocation artifact exists and records selected and rejected workflows.
3. Repository context artifact exists and identifies target governance path.
4. Approval request artifact exists before mutation.
5. Human approval or denial artifact exists before authorization.
6. Authorization artifact exists before mutation and bounds the mutation scope.
7. Mutation record exists and links to authorization.
8. Validation evidence exists and includes `git diff --check` result, exit code, and timestamp or ordering marker.
9. Replay package exists and indexes all mandatory lifecycle artifacts.
10. Replay reconstruction report exists and reconstructs the lifecycle.
11. Secret-free evidence assessment exists.
12. Audit review artifact exists.
13. Review-board decision artifact exists.
14. Evidence package is classified as `COMPLETE` or explicitly fails closed with complete missing-evidence disclosure.

Certification success remains separate:

```text
Evidence continuity remediation complete does not automatically equal ACLI_GOVERNED_DEVELOPMENT_READY.
```

## 11. Failure Criteria

Remediation remains incomplete if any of the following occur:

- execution evidence remains only in conversation
- workflow selection is inferred but not recorded
- approval is inferred from a request but not formalized
- authorization is missing or occurs after mutation
- replay package is absent
- replay reconstruction is absent or partial
- validation is claimed without command evidence
- review-board finding is absent
- missing evidence is hidden, ignored, or converted into readiness

Any failure must be recorded as fail-closed evidence.

## 12. Final Verdict

Final remediation verdict:

```text
MAJOR_REMEDIATION
```

Rationale:

The underlying capabilities appear partially present in the repository, but AEC-001 execution did not convert lifecycle activity into persistent, replayable, reviewable certification evidence. Closing this gap requires an execution-to-evidence continuity path across HIRR, workflow invocation, approval, authorization, replay, and review.

Readiness boundary:

```text
ACLI_GOVERNED_DEVELOPMENT_READY_NOT_CLAIMED
```

Final artifact verdict:

```text
ACLI_EVIDENCE_CONTINUITY_REMEDIATION_PLAN_V1_DEFINED
```
