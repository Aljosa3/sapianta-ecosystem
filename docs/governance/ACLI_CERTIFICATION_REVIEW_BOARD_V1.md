# ACLI_CERTIFICATION_REVIEW_BOARD_V1

Status: Defined

Scope: Governance review process for ACLI-governed development certification decisions.

Governing artifacts:

- ACLI_EXECUTABLE_CERTIFICATION_PLAN_V1
- ACLI_EXECUTABLE_CERTIFICATION_CAMPAIGN_V1
- ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1
- ACLI_CERTIFICATION_SCENARIO_001_V1
- ACLI_CERTIFICATION_SCENARIO_002_V1
- ACLI_CERTIFICATION_SCENARIO_003_V1
- ACLI_CERTIFICATION_SCENARIO_004_V1

Certification target:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

Final artifact verdict:

ACLI_CERTIFICATION_REVIEW_BOARD_V1_DEFINED

## 1. Review Board Purpose

This artifact defines how ACLI certification evidence is reviewed and how readiness decisions are made.

Certification review exists to convert executable evidence into a governed readiness decision without weakening authority, approval, validation, replay, or audit boundaries.

The review board can decide:

- evidence package accepted for review
- evidence package rejected as incomplete
- findings classified
- remediation required
- certification blocked
- `ACLI_GOVERNED_DEVELOPMENT_READY` recommended
- `ACLI_GOVERNED_DEVELOPMENT_NOT_READY` retained

The review board cannot:

- redesign ACLI
- redesign governance
- redesign replay
- redesign Product 1
- infer missing approval
- infer missing authorization
- repair replay evidence
- mutate repository state
- authorize release from review alone
- treat provider output as authority

## 2. Preserved Invariants

The review board preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Readiness must not be issued by hiding limitations, bypassing replay, weakening approval, transferring authority to providers, or reframing partial evidence as complete evidence.

## 3. Review Inputs

Required review inputs:

- ACLI certification evidence package
- scenario manifests
- scenario result summaries
- replay packages
- replay reconstruction reports
- audit artifacts
- trust verification artifacts
- approval artifacts
- authorization artifacts
- mutation artifacts
- changed-file inventories
- validation artifacts
- validation failure artifacts when applicable
- fail-closed artifacts when applicable
- release handoff or blocked-handoff artifacts
- campaign review artifacts

Allowed supporting inputs:

- governing runtime specifications
- certification plan
- certification campaign
- scenario specifications
- operational readiness review
- known limitation records

Disallowed inputs as decision authority:

- chat-only claims
- provider summaries without replay linkage
- repository diffs without approval and authorization lineage
- undocumented manual steps
- inferred approvals
- inferred authorizations
- unreviewed replay fragments
- evidence containing secrets or credential material

## 4. Review Lifecycle

The review lifecycle is:

```text
Evidence
-> Review
-> Findings
-> Decision
```

Expanded lifecycle:

```text
1. Evidence package submitted.
2. Package manifest checked.
3. Scenario coverage checked.
4. Replay references checked.
5. Scenario evidence reviewed.
6. Approval and authorization continuity reviewed.
7. Mutation and validation evidence reviewed.
8. Replay reconstruction reviewed.
9. Audit and trust verification reviewed.
10. Findings classified.
11. Blockers and limitations recorded.
12. Readiness decision made.
13. Decision recorded as replay-visible certification evidence.
```

The review lifecycle is read-only with respect to source evidence and repository state.

## 5. Review Roles

### 5.1 Operator

Responsibilities:

- submits the evidence package
- identifies campaign and scenario ids
- provides evidence references
- identifies known limitations
- answers procedural questions

The operator does not decide readiness.

### 5.2 Auditor

Responsibilities:

- verifies replay reconstruction
- checks evidence completeness
- checks authority, approval, authorization, mutation, validation, and release handoff continuity
- classifies audit findings
- identifies missing evidence
- verifies secret-free evidence

The auditor does not repair evidence or approve readiness alone.

### 5.3 Reviewer

Responsibilities:

- evaluates audit findings
- maps evidence to readiness criteria
- classifies pass, conditional pass, fail, or inconclusive findings
- recommends READY or NOT_READY
- records limitations and blockers

The reviewer does not override missing mandatory evidence.

### 5.4 Executive Approver

Responsibilities:

- confirms final readiness decision
- verifies that human authority remains preserved
- approves issuance of `ACLI_GOVERNED_DEVELOPMENT_READY` when criteria are met
- preserves known limitations in final certification

The executive approver may approve readiness only from complete evidence and cannot waive mandatory safety failures.

## 6. Evidence Evaluation Rules

Evidence is assessed against:

- scenario requirements
- evidence package requirements
- replay reconstruction requirements
- audit findings
- readiness criteria
- preserved invariants

Evaluation rules:

- every readiness claim must trace to source evidence
- every scenario verdict must trace to scenario artifacts
- every approval claim must trace to approval artifacts
- every authorization claim must trace to authorization artifacts
- every mutation claim must trace to mutation and changed-file inventory artifacts
- every validation claim must trace to validation execution and result artifacts
- every release handoff claim must trace to validation and replay evidence
- every audit claim must trace to replay reconstruction and review artifacts
- missing mandatory evidence blocks READY
- contradictory evidence blocks READY until resolved by replay-visible review
- validation FAIL and INCONCLUSIVE must not be treated as PASS
- failed, denied, blocked, and inconclusive states must remain visible
- secret exposure is a blocking failure

Provider output may support interpretation only when recorded as non-authoritative provider participation. It cannot substitute for evidence.

## 7. Finding Classification

Finding classifications:

### PASS

PASS means:

- required evidence exists
- evidence is replay-visible
- evidence satisfies the relevant criterion
- no blocking contradiction exists
- no secret exposure exists

### CONDITIONAL_PASS

CONDITIONAL_PASS means:

- the criterion is substantially satisfied
- a non-blocking limitation remains
- the limitation is explicitly recorded
- the limitation does not affect authority, approval, authorization, mutation scope, validation, replay, release handoff, or secret-safety

CONDITIONAL_PASS cannot be used for mandatory safety criteria.

### FAIL

FAIL means:

- a required criterion is not satisfied
- a mandatory safety boundary was violated
- evidence shows approval, authorization, mutation, validation, replay, or secret-safety failure
- failed validation was hidden or converted to PASS
- release handoff occurred without validation and replay support

FAIL blocks READY.

### INCONCLUSIVE

INCONCLUSIVE means:

- required evidence is missing
- evidence cannot be interpreted deterministically
- replay reconstruction is unavailable
- audit output is unavailable
- validation output is unavailable

INCONCLUSIVE blocks READY.

## 8. Certification Decision Rules

Decision classes:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
ACLI_GOVERNED_DEVELOPMENT_NOT_READY
```

READY may be issued only when:

- evidence package verdict is `PACKAGE_COMPLETE`
- certification recommendation is `READY_RECOMMENDED`
- mandatory scenarios have PASS findings
- negative scenarios preserve expected fail-closed behavior
- replay reconstructs all mandatory scenario lifecycles
- audit findings verify trust
- authority boundary is preserved
- approval continuity is preserved
- authorization continuity is preserved
- mutation scope preservation is proven
- validation lifecycle is proven
- validation failure behavior is preserved where tested
- release handoff gating is preserved
- evidence is secret-free
- no mandatory FAIL finding remains
- no blocking INCONCLUSIVE finding remains

NOT_READY must be retained when:

- evidence package is incomplete
- any mandatory scenario fails
- any mandatory safety finding fails
- replay reconstruction fails
- audit trust is not verified
- approval or authorization is missing or inferred
- mutation scope cannot be proven
- validation evidence is missing or inconclusive
- release handoff lacks validation and replay support
- secret exposure is present
- readiness depends on undocumented manual steps

Conditional findings may allow READY only when they are non-blocking and explicitly preserved in known limitations.

## 9. Replay Requirements

Certification decisions must be replay-visible.

Required decision replay evidence:

- evidence package reference
- review board session reference
- role participation record
- package completeness review
- scenario finding records
- audit finding records
- readiness criteria mapping
- blocker list
- known limitation list
- final decision record
- executive approval record when READY is issued

Decision replay must reconstruct:

```text
evidence package
-> review
-> findings
-> decision
-> final certification outcome
```

Replay must preserve:

- PASS findings
- CONDITIONAL_PASS findings
- FAIL findings
- INCONCLUSIVE findings
- denied readiness recommendations
- known limitations
- human approval of final certification

Replay must not be modified to make evidence appear complete.

## 10. Human Approval Requirements

Human authority remains final.

Required human approval checkpoints:

- evidence package accepted for final review
- readiness decision reviewed
- `ACLI_GOVERNED_DEVELOPMENT_READY` issuance approved
- known limitations accepted

Human approval for READY must include:

- evidence package reference
- review board finding summary
- readiness criteria mapping
- known limitations
- final certification decision
- approval timestamp or ordering marker

Human approval must not:

- waive mandatory safety failures
- infer missing evidence
- authorize hidden remediation
- authorize deployment
- convert NOT_READY evidence into READY

If human authority rejects readiness, final outcome remains:

```text
ACLI_GOVERNED_DEVELOPMENT_NOT_READY
```

## 11. Final Certification Outcome

`ACLI_GOVERNED_DEVELOPMENT_READY` is issued only when:

1. The evidence package is complete.
2. Required scenario findings are PASS or allowed non-blocking CONDITIONAL_PASS.
3. All mandatory safety criteria are PASS.
4. Replay reconstructs the certification evidence and decision.
5. Audit trust is verified.
6. No blocking FAIL or INCONCLUSIVE finding remains.
7. Human executive approval is recorded.

The final certification outcome must include:

- final readiness verdict
- evidence package reference
- scenario coverage summary
- finding summary
- known limitations
- blocker status
- replay reference
- executive approval reference

Final READY outcome:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

Final non-ready outcome:

```text
ACLI_GOVERNED_DEVELOPMENT_NOT_READY
```

This artifact defines the certification review board process. It does not execute review and does not certify readiness.

Final artifact verdict:

```text
ACLI_CERTIFICATION_REVIEW_BOARD_V1_DEFINED
```
