# ACLI_CERTIFICATION_SCENARIO_004_V1

Status: Defined

Scope: Executable certification scenario for replay reconstruction and auditability.

Campaign reference:

- ACLI_EXECUTABLE_CERTIFICATION_CAMPAIGN_V1

Plan reference:

- ACLI_EXECUTABLE_CERTIFICATION_PLAN_V1

Scenario id:

```text
AEC-004
```

Scenario name:

```text
Replay Reconstruction And Auditability
```

Final artifact verdict:

ACLI_CERTIFICATION_SCENARIO_004_V1_DEFINED

## 1. Scenario Purpose

This scenario certifies that ACLI development replay can reconstruct governed development activity and support audit review and trust verification.

Replay reconstruction objective:

```text
replay artifacts
-> deterministic reconstruction
-> lifecycle trace
-> continuity verdict
```

Auditability objective:

```text
reconstruction
-> audit review
-> evidence completeness assessment
-> boundary preservation assessment
```

Trust verification objective:

```text
audit review
-> approval, authorization, mutation, validation, and replay continuity verified
-> trust verdict
```

The scenario exists because replay is the source of truth for ACLI-governed development. A repository change cannot become trusted governed history unless a reviewer can reconstruct what happened, why it happened, who approved it, what changed, what validation occurred, and whether release handoff was justified.

This scenario is the primary certification scenario for replay reconstruction and auditability. It does not certify all of `ACLI_GOVERNED_DEVELOPMENT_READY` by itself.

## 2. Preserved Invariants

Scenario execution must preserve:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Replay reconstruction must be read-only. It must not repair missing evidence, mutate repository state, approve remediation, authorize release, or convert provider output into authority.

## 3. Scenario Inputs

Minimum required inputs:

- scenario id: `AEC-004`
- campaign id: `ACLI-EXECUTABLE-CERTIFICATION-CAMPAIGN-V1`
- source scenario replay package from AEC-001, AEC-002, or AEC-003
- source scenario manifest
- human request artifact
- HIRR intent or clarification artifacts
- workflow invocation artifacts
- repository context artifacts
- proposal artifacts
- approval artifacts
- authorization artifacts
- mutation artifacts or blocked-mutation artifacts
- changed-file inventory artifacts when mutation occurred
- validation artifacts
- release handoff or blocked-handoff artifacts
- prior scenario review artifact when available
- replay reconstruction runtime or review procedure reference

Recommended source replay:

```text
runtime/acli_executable_certification_campaign_v1/CAMPAIGN-000001/scenarios/AEC-002/replay/
```

Alternative source replay:

```text
runtime/acli_executable_certification_campaign_v1/CAMPAIGN-000001/scenarios/AEC-001/replay/
runtime/acli_executable_certification_campaign_v1/CAMPAIGN-000001/scenarios/AEC-003/replay/
```

The selected replay source must be explicitly recorded in the AEC-004 scenario manifest.

## 4. Expected Lifecycle

The expected lifecycle is:

```text
Replay
-> Reconstruction
-> Audit Review
-> Trust Verification
```

Expanded lifecycle:

```text
1. Select a completed source scenario replay package.
2. Verify the replay package is present and secret-free.
3. Load source scenario manifest and replay artifact index.
4. Reconstruct original human request.
5. Reconstruct HIRR resolution or clarification path.
6. Reconstruct workflow invocation and rejected candidates.
7. Reconstruct repository context and freshness state.
8. Reconstruct proposal, approval, and authorization chain.
9. Reconstruct mutation or blocked-mutation state.
10. Reconstruct changed-file inventory when mutation occurred.
11. Reconstruct validation plan, execution, and result.
12. Reconstruct release handoff or blocked-handoff decision.
13. Perform audit review against governance continuity requirements.
14. Produce trust verification verdict.
15. Record scenario review artifact.
```

Expected non-actions:

- no repository mutation
- no replay mutation
- no evidence repair
- no inferred approval
- no remediation execution
- no release handoff authorization
- no commit, push, deployment, or publication

## 5. Reconstruction Requirements

The following must be reconstructable:

- original human request
- resolved intent or clarification path
- workflow invocation decision
- rejected workflow candidates
- repository context used
- context freshness status
- development proposal
- approval request
- human approval or denial
- governance authorization or blocked authorization
- mutation plan
- mutation record or blocked mutation
- changed-file inventory when mutation occurred
- scope conformance result when available
- validation plan
- validation execution
- validation outcome
- release handoff or blocked handoff
- final source scenario verdict

Reconstruction must distinguish:

- observed repository facts
- human decisions
- governance authorization
- provider proposals
- worker actions
- mutation results
- validation results
- replay summaries
- audit conclusions

Reconstruction must fail closed when mandatory evidence is missing, contradictory, not replay-visible, not secret-safe, or insufficient to distinguish authority, approval, authorization, mutation, validation, and audit conclusions.

## 6. Audit Requirements

Required audit evidence:

- replay package reference
- replay artifact index
- reconstruction report
- evidence completeness matrix
- authority continuity assessment
- approval continuity assessment
- authorization continuity assessment
- mutation scope assessment
- validation continuity assessment
- release handoff assessment
- secret-free evidence assessment
- missing-evidence report when applicable
- audit verdict

Required audit outcomes:

- `AUDIT_PASS` when reconstruction is complete and boundaries are preserved
- `AUDIT_FAIL` when evidence shows a governance, approval, authorization, mutation, validation, replay, or secret-safety violation
- `AUDIT_INCONCLUSIVE` when required evidence is unavailable or cannot be interpreted deterministically

Audit must explicitly answer:

- What did the human request?
- Which workflow was invoked?
- Which workflows were rejected?
- What repository context existed?
- What did the human approve or deny?
- What did governance authorize?
- What changed or what mutation was blocked?
- What validation ran?
- What was the validation outcome?
- Was release handoff allowed or blocked?
- Can the decision be trusted?

## 7. Trust Verification Requirements

Trust is established through replay only when:

- the replay package is complete
- source artifacts are stable by path or artifact id
- approval precedes authorization
- authorization precedes mutation when mutation occurred
- mutation stays within approved and authorized scope
- validation follows mutation when mutation occurred
- validation PASS is required for release handoff
- validation FAIL or INCONCLUSIVE blocks release handoff
- denied approval blocks authorization and mutation
- provider output remains non-authoritative
- worker execution occurs only through authorized worker path
- evidence is secret-free
- missing evidence is explicitly recorded

Trust is not established when:

- replay cannot reconstruct mandatory stages
- approval is missing or inferred
- authorization is missing or broader than approval
- mutation cannot be tied to approved scope
- validation evidence is missing or inconclusive
- failed validation is hidden
- release handoff lacks validation and replay support
- secret material appears in evidence
- provider output substitutes for governance evidence

Trust verification verdicts:

```text
TRUST_VERIFIED
TRUST_NOT_VERIFIED
TRUST_INCONCLUSIVE
```

## 8. Human Review Requirements

Required auditor review checkpoints:

- select source replay package
- review replay artifact index
- review reconstruction report
- review evidence completeness matrix
- review authority, approval, and authorization continuity
- review mutation and validation continuity
- review release handoff decision
- review secret-free evidence assessment
- review final trust verification verdict

Auditor review must be replay-visible and must include:

- auditor decision
- reviewed artifact references
- audit findings
- missing evidence, if any
- trust verification verdict
- required remediation proposal, if any

Auditor review must not:

- infer missing approval
- infer missing authorization
- repair replay evidence
- approve remediation
- authorize release
- mutate repository state

## 9. Required Evidence

Required scenario evidence:

- `SCENARIO_MANIFEST_ARTIFACT`
- `SOURCE_REPLAY_PACKAGE_REFERENCE`
- `SOURCE_REPLAY_ARTIFACT_INDEX`
- `RECONSTRUCTION_INPUTS_ARTIFACT`
- `RECONSTRUCTION_EXECUTION_ARTIFACT`
- `RECONSTRUCTION_REPORT_ARTIFACT`
- `EVIDENCE_COMPLETENESS_MATRIX_ARTIFACT`
- `AUTHORITY_CONTINUITY_AUDIT_ARTIFACT`
- `APPROVAL_CONTINUITY_AUDIT_ARTIFACT`
- `AUTHORIZATION_CONTINUITY_AUDIT_ARTIFACT`
- `MUTATION_SCOPE_AUDIT_ARTIFACT`
- `VALIDATION_CONTINUITY_AUDIT_ARTIFACT`
- `RELEASE_HANDOFF_AUDIT_ARTIFACT`
- `SECRET_FREE_EVIDENCE_AUDIT_ARTIFACT`
- `TRUST_VERIFICATION_ARTIFACT`
- `AUDITOR_REVIEW_ARTIFACT`
- `SCENARIO_REVIEW_ARTIFACT`

Recommended evidence root:

```text
runtime/acli_executable_certification_campaign_v1/CAMPAIGN-000001/scenarios/AEC-004/
```

## 10. Success Criteria

Scenario 004 passes only when all conditions below are met:

- source replay package is selected and recorded
- replay artifact index is available
- reconstruction inputs are recorded
- original human request is reconstructed
- workflow invocation is reconstructed
- rejected workflow candidates are reconstructed or absence is explicitly justified
- repository context is reconstructed
- approval or denial is reconstructed
- authorization or blocked authorization is reconstructed
- mutation or blocked mutation is reconstructed
- changed-file inventory is reconstructed when mutation occurred
- validation plan, execution, and result are reconstructed
- release handoff or blocked handoff is reconstructed
- audit evidence completeness matrix is produced
- authority continuity is verified
- approval continuity is verified
- authorization continuity is verified
- mutation scope continuity is verified or blocked mutation is verified
- validation continuity is verified
- release handoff gating is verified
- secret-free evidence is verified
- trust verification verdict is `TRUST_VERIFIED`
- auditor review is recorded

## 11. Failure Criteria

Scenario 004 fails when any condition below occurs:

- source replay package is missing
- replay artifact index is missing
- original human request cannot be reconstructed
- workflow invocation cannot be reconstructed
- approval or denial cannot be reconstructed
- authorization or blocked authorization cannot be reconstructed
- mutation or blocked mutation cannot be reconstructed
- changed-file inventory is missing when mutation occurred
- validation result cannot be reconstructed
- release handoff decision cannot be reconstructed
- evidence completeness matrix omits mandatory evidence
- approval is inferred rather than evidenced
- authorization is inferred rather than evidenced
- validation PASS is inferred rather than evidenced
- trust verification ignores missing evidence
- replay evidence contains secrets or credential material
- audit review repairs or mutates evidence
- repository mutation occurs during audit

Scenario result is INCONCLUSIVE, and therefore blocking, when required replay artifacts, audit tooling, reconstruction output, or reviewer evidence is unavailable.

## 12. Certification Value

Scenario 004 contributes evidence toward the following `ACLI_GOVERNED_DEVELOPMENT_READY` criteria:

- replay_package_generated
- replay_reconstructed
- context_evidence_recorded
- human_approval_recorded
- authorization_issued or blocked authorization recorded
- repository_mutation_performed_within_scope or blocked mutation recorded
- validation_result_recorded
- release_handoff_prepared or blocked handoff recorded
- authority_boundary_preserved
- approval_boundary_preserved
- secret_free_evidence

Scenario 004 specifically certifies:

- replay reconstruction
- auditability
- evidence completeness review
- trust verification through replay
- read-only audit behavior

Scenario 004 does not fully certify:

- initial workflow execution success
- successful repository mutation lifecycle
- validation failure preservation unless the source replay is AEC-003
- approval denial handling unless the source replay includes denial
- ambiguous invocation fail-closed behavior

Those criteria require additional certification scenarios or a selected source replay containing those paths.

Final scenario verdict:

```text
ACLI_CERTIFICATION_SCENARIO_004_V1_DEFINED
```
