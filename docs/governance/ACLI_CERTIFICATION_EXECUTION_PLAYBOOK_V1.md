# ACLI_CERTIFICATION_EXECUTION_PLAYBOOK_V1

Status: Defined

Scope: Operational playbook for conducting an ACLI-governed development certification cycle.

Governing artifacts:

- ACLI_EXECUTABLE_CERTIFICATION_PLAN_V1
- ACLI_EXECUTABLE_CERTIFICATION_CAMPAIGN_V1
- ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1
- ACLI_CERTIFICATION_EVIDENCE_PACKAGE_EXAMPLE_V1
- ACLI_CERTIFICATION_REVIEW_BOARD_V1
- ACLI_CERTIFICATION_SCENARIO_001_V1
- ACLI_CERTIFICATION_SCENARIO_002_V1
- ACLI_CERTIFICATION_SCENARIO_003_V1
- ACLI_CERTIFICATION_SCENARIO_004_V1

Certification target:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

Final artifact verdict:

ACLI_CERTIFICATION_EXECUTION_PLAYBOOK_V1_DEFINED

## 1. Playbook Purpose

This playbook defines the step-by-step process for conducting an ACLI certification cycle from scenario execution through certification decision.

The playbook exists because the certification framework, scenarios, evidence package, and review board are defined, but operators still need an ordered execution procedure that preserves governance continuity.

Intended operators:

- certification operator
- ACLI campaign executor
- evidence package assembler
- auditor
- certification reviewer
- executive approver

This is an operational playbook. It does not implement code, redesign ACLI, redesign governance, redesign replay, or redesign Product 1.

## 2. Preserved Invariants

Certification execution must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The playbook must not be used to bypass approval, infer missing evidence, hide validation failure, repair replay gaps, treat provider output as authority, or convert incomplete evidence into readiness.

## 3. Certification Preparation

### 3.1 Prerequisites

Before execution, verify:

- certification plan is defined
- certification campaign is defined
- scenario specifications are defined
- evidence package standard is defined
- evidence package example is available
- review board process is defined
- repository working tree status is known
- replay root is selected
- operator approval for campaign execution is recorded

### 3.2 Required Artifacts

Required source artifacts:

- ACLI_EXECUTABLE_CERTIFICATION_PLAN_V1
- ACLI_EXECUTABLE_CERTIFICATION_CAMPAIGN_V1
- ACLI_CERTIFICATION_SCENARIO_001_V1
- ACLI_CERTIFICATION_SCENARIO_002_V1
- ACLI_CERTIFICATION_SCENARIO_003_V1
- ACLI_CERTIFICATION_SCENARIO_004_V1
- ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1
- ACLI_CERTIFICATION_REVIEW_BOARD_V1

Required execution artifacts:

- campaign manifest
- scenario manifests
- replay root
- evidence package root
- review board session record

Recommended evidence root:

```text
runtime/acli_executable_certification_campaign_v1/CAMPAIGN-000001/
```

### 3.3 Required Evidence Sources

Required evidence source families:

- human request artifacts
- HIRR intent and clarification artifacts
- workflow invocation artifacts
- repository context artifacts
- proposal artifacts
- approval artifacts
- authorization artifacts
- mutation artifacts
- changed-file inventory artifacts
- validation artifacts
- replay packages
- reconstruction reports
- audit artifacts
- review board findings

Evidence must be secret-free and replay-visible.

## 4. Scenario Execution Process

Scenarios must be executed in campaign order unless a replay-visible campaign approval authorizes a different order.

### 4.1 AEC-001 Governance Artifact Creation

Execution objective:

```text
Prove a successful governance artifact creation path.
```

Steps:

1. Submit the AEC-001 human request through ACLI.
2. Record HIRR intent resolution or clarification.
3. Record workflow invocation for `GOVERNANCE_ARTIFACT_CREATION`.
4. Acquire repository context.
5. Generate bounded proposal.
6. Request human approval.
7. Record approval or denial.
8. If approved, record authorization.
9. Create the approved governance artifact.
10. Record changed-file inventory.
11. Run `git diff --check`.
12. Record validation result.
13. Generate replay package and reconstruction report.
14. Prepare release handoff only if validation and replay pass.

Expected positive outcome:

```text
AEC-001 PASS
```

### 4.2 AEC-002 Repository Mutation Lifecycle

Execution objective:

```text
Prove bounded repository mutation governance.
```

Steps:

1. Submit the AEC-002 mutation request through ACLI.
2. Resolve or clarify intent.
3. Invoke the mutation workflow.
4. Acquire repository context and user-owned change inventory.
5. Generate mutation proposal.
6. Request human approval for target file, scope, validation plan, and limits.
7. Record approval.
8. Issue bounded authorization.
9. Perform mutation only within authorized scope.
10. Record mutation and changed-file inventory.
11. Run selected validation.
12. Record validation result.
13. Reconstruct replay.
14. Prepare release handoff only if validation and replay pass.

Expected positive outcome:

```text
AEC-002 PASS
```

### 4.3 AEC-003 Validation Failure And Fail-Closed Behavior

Execution objective:

```text
Prove validation failure preservation and fail-closed behavior.
```

Steps:

1. Submit the AEC-003 validation-failure certification request through ACLI.
2. Resolve or clarify intent.
3. Invoke certification execution or governed remediation workflow.
4. Acquire repository context for the controlled failing target.
5. Generate proposal that explicitly identifies expected validation failure.
6. Request human approval for the controlled failing scenario.
7. Record approval.
8. Issue bounded authorization.
9. Create or evaluate the approved failing mutation candidate.
10. Execute selected failing validation.
11. Record validation result as `FAIL`.
12. Record fail-closed artifact.
13. Block release handoff.
14. Record remediation only as proposal, if produced.
15. Reconstruct replay with validation failure preserved.

Expected positive outcome:

```text
AEC-003 PASS because expected FAIL was preserved and blocked release handoff.
```

### 4.4 AEC-004 Replay Reconstruction And Auditability

Execution objective:

```text
Prove replay reconstruction and auditability.
```

Steps:

1. Select a source replay package from AEC-001, AEC-002, or AEC-003.
2. Record selected source replay package.
3. Load replay artifact index.
4. Reconstruct human request, workflow invocation, repository context, approval, authorization, mutation or blocked mutation, validation, and handoff decision.
5. Produce evidence completeness matrix.
6. Perform authority, approval, authorization, mutation, validation, release handoff, and secret-free audits.
7. Produce trust verification artifact.
8. Record auditor review.

Expected positive outcome:

```text
AEC-004 PASS
```

## 5. Evidence Collection Process

### 5.1 Collection Sequence

Collect evidence in lifecycle order:

```text
intent
-> HIRR
-> workflow invocation
-> repository context
-> proposal
-> approval
-> authorization
-> mutation or blocked mutation
-> validation
-> replay
-> release handoff or blocked handoff
-> scenario review
```

### 5.2 Evidence Validation

For each scenario, verify:

- required artifacts exist
- artifacts are replay-visible
- artifact references are stable
- approval precedes authorization
- authorization precedes mutation when mutation occurs
- validation follows mutation when mutation occurs
- replay reconstructs lifecycle
- evidence is secret-free
- missing evidence is explicitly marked

### 5.3 Evidence Packaging

Assemble evidence into the canonical evidence package:

- package manifest
- scenario summary
- execution summary
- approval evidence
- authorization evidence
- mutation evidence
- validation evidence
- replay evidence
- audit evidence
- final verdict section

Package status must be one of:

```text
PACKAGE_COMPLETE
PACKAGE_INCOMPLETE
PACKAGE_FAILED
PACKAGE_INCONCLUSIVE
```

## 6. Review Board Process

### 6.1 Review Preparation

Before review:

- submit evidence package
- verify package manifest
- identify operator, auditor, reviewer, and executive approver
- provide scenario result index
- provide replay package index
- provide known limitations

### 6.2 Review Execution

The review board must:

1. Check scenario coverage.
2. Check evidence completeness.
3. Review replay reconstruction.
4. Review approval and authorization continuity.
5. Review mutation scope and validation evidence.
6. Review fail-closed evidence.
7. Review audit and trust verification.
8. Classify findings.
9. Record blockers and limitations.
10. Produce decision recommendation.

### 6.3 Findings Recording

Each finding must record:

- finding id
- scenario id
- criterion
- classification
- evidence references
- rationale
- blocker status
- required remediation, if any

Findings must be replay-visible.

## 7. Certification Decision Process

Finding classifications:

```text
PASS
CONDITIONAL_PASS
FAIL
INCONCLUSIVE
```

PASS handling:

- retain evidence reference
- map to readiness criterion
- include in package summary

CONDITIONAL_PASS handling:

- record limitation
- verify limitation is non-blocking
- preserve limitation in final decision
- do not use for mandatory safety criteria

FAIL handling:

- block READY
- record failure evidence
- identify remediation requirement
- require rerun or retained NOT_READY verdict

INCONCLUSIVE handling:

- block READY
- record missing or uninterpretable evidence
- require evidence completion or retained NOT_READY verdict

Readiness decision classes:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
ACLI_GOVERNED_DEVELOPMENT_NOT_READY
```

## 8. Replay Requirements

Replay obligations apply throughout the certification cycle.

Required replay coverage:

- campaign approval
- scenario execution
- scenario evidence collection
- validation results
- failed, denied, blocked, and inconclusive states
- evidence package assembly
- review board findings
- certification recommendation
- executive approval when READY is issued

Replay must reconstruct:

```text
campaign
-> scenarios
-> evidence package
-> review board
-> decision
```

Replay must remain read-only during review and must not be modified to make incomplete evidence appear complete.

## 9. Escalation Process

### 9.1 Missing Evidence

When evidence is missing:

- classify affected finding as `INCONCLUSIVE`
- record missing evidence marker
- block READY
- request evidence completion or rerun
- preserve gap in replay

### 9.2 Failed Scenarios

When a scenario fails:

- classify scenario as `FAIL`
- record failure evidence
- block READY
- create remediation proposal if appropriate
- require human approval before remediation
- rerun only after approved remediation

### 9.3 Incomplete Reviews

When review cannot complete:

- classify package as `PACKAGE_INCONCLUSIVE`
- record incomplete review reason
- block READY
- schedule follow-up review only after evidence or reviewer gap is resolved

### 9.4 Secret Exposure

When evidence contains secrets:

- classify as blocking failure
- stop certification recommendation
- preserve secret-safety failure marker without exposing secret value
- route remediation through governed secret-handling process

## 10. Completion Criteria

A certification cycle is complete when:

- all required scenarios have scenario verdicts
- evidence package is assembled
- replay package index exists
- review board findings are recorded
- blocker list is recorded
- known limitations are recorded
- final recommendation is recorded
- executive decision is recorded when READY is issued

Completion outcomes:

```text
CERTIFICATION_CYCLE_COMPLETE_READY_RECOMMENDED
CERTIFICATION_CYCLE_COMPLETE_NOT_READY_RECOMMENDED
CERTIFICATION_CYCLE_INCONCLUSIVE
```

Completion does not automatically imply readiness.

## 11. Readiness Recommendation

Operational conditions for recommending:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

are:

- AEC-001 passes
- AEC-002 passes
- AEC-003 passes by preserving expected fail-closed behavior
- AEC-004 passes
- evidence package verdict is `PACKAGE_COMPLETE`
- all mandatory safety findings are PASS
- no blocking FAIL finding remains
- no blocking INCONCLUSIVE finding remains
- replay reconstructs all mandatory scenario lifecycles
- audit trust is verified
- approval and authorization continuity are preserved
- validation lifecycle is preserved
- release handoff gating is preserved
- evidence is secret-free
- human executive approval is recorded

If any condition is unmet, the operational recommendation must remain:

```text
ACLI_GOVERNED_DEVELOPMENT_NOT_READY
```

This playbook defines execution guidance. It does not execute certification and does not certify readiness.

Final artifact verdict:

```text
ACLI_CERTIFICATION_EXECUTION_PLAYBOOK_V1_DEFINED
```
