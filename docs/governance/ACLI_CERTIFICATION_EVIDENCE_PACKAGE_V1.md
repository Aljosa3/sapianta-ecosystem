# ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1

Status: Defined

Scope: Canonical evidence package for ACLI-governed development certification review.

Governing artifacts:

- ACLI_EXECUTABLE_CERTIFICATION_PLAN_V1
- ACLI_EXECUTABLE_CERTIFICATION_CAMPAIGN_V1
- ACLI_CERTIFICATION_SCENARIO_001_V1
- ACLI_CERTIFICATION_SCENARIO_002_V1
- ACLI_CERTIFICATION_SCENARIO_003_V1
- ACLI_CERTIFICATION_SCENARIO_004_V1

Certification target:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

Final artifact verdict:

ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1_DEFINED

## 1. Evidence Package Purpose

This artifact defines the standard evidence package produced by ACLI certification scenario execution.

The evidence package exists to provide a single reviewable artifact family for determining whether ACLI-governed development has satisfied the executable readiness criteria.

The evidence package proves, when complete:

- which certification scenarios were executed
- what each scenario attempted to certify
- what human requests initiated execution
- which workflows were invoked
- what repository context was used
- what approvals and authorizations existed
- what mutations occurred or were blocked
- what validation ran and what results were produced
- what replay reconstructed
- what audit review concluded
- whether evidence supports `ACLI_GOVERNED_DEVELOPMENT_READY`

The evidence package does not replace replay, repair missing evidence, certify readiness by assertion, authorize mutation, authorize release, or redesign governance.

## 2. Preserved Invariants

The evidence package preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Evidence packaging must not infer approval, invent missing authorization, hide failed validation, repair replay gaps, treat provider output as authority, or convert incomplete evidence into readiness.

## 3. Evidence Package Structure

The canonical evidence package must include:

### 3.1 Package Manifest

Required contents:

- package id
- campaign id
- scenario ids
- package creation timestamp or ordering marker
- source artifact references
- package status
- reviewer status
- final recommendation status

### 3.2 Scenario Summary

Required contents:

- scenario id
- scenario name
- scenario objective
- expected workflow
- actual workflow
- scenario verdict
- blocking failures
- known limitations

### 3.3 Execution Summary

Required contents:

- execution order
- execution status
- human request summary
- HIRR outcome
- workflow invocation outcome
- repository context outcome
- mutation outcome
- validation outcome
- replay outcome
- release handoff outcome

### 3.4 Approval Evidence

Required contents:

- approval request references
- human approval or denial references
- approved scope
- denied scope when applicable
- approval timestamp or ordering marker
- stale or modified approval evidence when applicable
- approval-to-authorization linkage

### 3.5 Authorization Evidence

Required contents:

- authorization references
- authorized scope
- authorized operation type
- authorization constraints
- authorization-to-mutation linkage
- blocked authorization evidence when applicable

### 3.6 Mutation Evidence

Required contents:

- mutation plan references
- mutation record references
- changed-file inventory
- scope conformance result
- blocked mutation evidence when applicable
- user-owned change preservation evidence

### 3.7 Validation Evidence

Required contents:

- validation plan references
- selected validation families
- executed commands or checks
- skipped checks with reasons
- validation result classification
- validation failure evidence when applicable
- release handoff eligibility

### 3.8 Replay Evidence

Required contents:

- replay package references
- replay artifact indexes
- reconstruction reports
- continuity verdicts
- missing-evidence reports when applicable
- secret-free evidence assessments

### 3.9 Audit Evidence

Required contents:

- audit review references
- evidence completeness matrix
- authority continuity assessment
- approval continuity assessment
- authorization continuity assessment
- mutation scope assessment
- validation continuity assessment
- release handoff assessment
- trust verification verdict

### 3.10 Final Verdict

Required contents:

- package completeness verdict
- scenario aggregate verdict
- blocker list
- known limitations
- certification recommendation
- final reviewer decision

## 4. Evidence Sources

Allowed evidence inputs:

- scenario manifests
- human request artifacts
- HIRR intent and clarification artifacts
- workflow invocation artifacts
- workflow candidate selection artifacts
- repository context artifacts
- context freshness artifacts
- development proposal artifacts
- approval request artifacts
- human approval or denial artifacts
- authorization artifacts
- mutation plan artifacts
- mutation record artifacts
- changed-file inventory artifacts
- scope conformance artifacts
- validation plan artifacts
- validation execution artifacts
- validation result artifacts
- validation failure artifacts
- fail-closed artifacts
- release handoff or blocked-handoff artifacts
- replay packages
- replay reconstruction reports
- audit review artifacts
- trust verification artifacts
- scenario review artifacts
- campaign review artifacts

Disallowed evidence inputs:

- chat-only claims without replay references
- provider summaries without deterministic artifact linkage
- repository diffs without approval and authorization lineage
- validation claims without execution evidence
- release readiness claims without validation and replay closure
- inferred approval
- inferred authorization
- hidden manual substitutions
- artifacts containing secrets, credential values, private keys, authorization headers, or unrelated raw payloads

## 5. Evidence Traceability

Every package-level claim must trace to source evidence.

Minimum traceability links:

| Claim family | Required trace |
| --- | --- |
| Workflow | human request -> HIRR -> workflow invocation -> selected workflow -> rejected candidates |
| Repository context | workflow invocation -> repository context -> context freshness -> target files or artifact families |
| Approval | proposal -> approval request -> human approval or denial -> approved scope |
| Authorization | approval -> authorization -> authorized scope -> execution limits |
| Mutation | authorization -> mutation record -> changed-file inventory -> scope conformance |
| Validation | mutation or blocked mutation -> validation plan -> execution artifact -> validation result |
| Replay | lifecycle artifacts -> replay package -> reconstruction report -> continuity verdict |
| Audit | replay reconstruction -> audit review -> trust verification -> recommendation |

Traceability requirements:

- every scenario verdict must link to scenario evidence
- every validation result must link to validation execution evidence
- every release handoff decision must link to validation and replay evidence
- every readiness recommendation must link to scenario verdicts and audit evidence
- every missing item must be explicitly marked as missing evidence

Evidence must not rely on unstated assumptions or undocumented manual steps.

## 6. Replay Requirements

The evidence package must include replay evidence for each executed scenario and for the campaign aggregate.

Scenario replay must reconstruct:

- human request
- HIRR resolution or clarification
- workflow invocation
- repository context
- proposal
- approval or denial
- authorization or blocked authorization
- mutation or blocked mutation
- validation
- release handoff or blocked handoff
- scenario verdict

Campaign replay must reconstruct:

- campaign plan reference
- scenario set
- execution order
- scenario verdicts
- aggregate blockers
- final certification recommendation

Replay package requirements:

- stable replay references
- replay artifact index
- ordered lifecycle records
- missing-evidence markers when applicable
- failed, denied, blocked, and inconclusive evidence preservation
- secret-free evidence assessment
- reconstruction verdict

Replay is the source of truth. The evidence package summarizes and indexes replay; it does not replace replay.

## 7. Review Requirements

Reviewer obligations:

- verify package manifest completeness
- verify every scenario has required evidence
- verify workflow traceability
- verify approval continuity
- verify authorization continuity
- verify mutation scope conformance
- verify validation evidence
- verify validation failure preservation
- verify replay reconstruction
- verify audit and trust verification evidence
- verify secret-free evidence
- record missing evidence
- classify blockers
- produce final recommendation

Reviewer must not:

- infer missing approval
- infer missing authorization
- treat inconclusive evidence as pass
- hide validation failure
- repair replay evidence
- mutate repository state during review
- authorize release from review alone
- treat provider output as authoritative evidence

Review verdicts:

```text
PACKAGE_COMPLETE
PACKAGE_INCOMPLETE
PACKAGE_FAILED
PACKAGE_INCONCLUSIVE
```

## 8. Certification Requirements

The evidence package supports certification decisions by mapping scenario evidence to readiness criteria.

Required readiness mappings:

- development_intent_detected
- development_workflow_selected
- repository_context_acquired
- context_evidence_recorded
- development_proposal_generated
- human_approval_requested
- human_approval_recorded
- authorization_issued or blocked authorization recorded
- repository_mutation_performed_within_scope or blocked mutation recorded
- unauthorized_mutation_blocked when tested
- validation_plan_selected
- validation_executed
- validation_result_recorded
- validation_failure_preserved when tested
- replay_package_generated
- replay_reconstructed
- release_handoff_prepared or blocked handoff recorded
- authority_boundary_preserved
- approval_boundary_preserved
- secret_free_evidence

Certification decision classes:

```text
READY_RECOMMENDED
NOT_READY_RECOMMENDED
INCONCLUSIVE_RECOMMENDATION
```

The package may recommend readiness only when evidence satisfies all mandatory readiness mappings and no blocking failure remains.

## 9. Success Conditions

The evidence package is complete when:

- package manifest exists
- all required scenarios are listed
- every executed scenario has a scenario summary
- every executed scenario has replay references
- every executed scenario has a scenario verdict
- workflow traceability is complete
- approval traceability is complete
- authorization traceability is complete
- mutation traceability is complete for mutation scenarios
- validation traceability is complete
- replay reconstruction is complete
- audit evidence is complete
- secret-free evidence assessment passes
- final certification recommendation is present

The evidence package supports `READY_RECOMMENDED` only when:

- all mandatory scenarios pass
- negative scenarios preserve expected fail-closed behavior
- no mandatory safety failure occurred
- no blocking inconclusive evidence remains
- replay reconstructs all mandatory scenarios
- audit review verifies trust
- all evidence is secret-free

## 10. Failure Conditions

The evidence package is insufficient when:

- package manifest is missing
- scenario summary is missing
- required scenario evidence is missing
- workflow invocation cannot be traced
- approval cannot be traced
- authorization cannot be traced
- mutation cannot be traced when mutation occurred
- changed-file inventory is missing when mutation occurred
- validation execution cannot be traced
- validation result is missing
- validation failure is hidden
- replay package is missing
- replay reconstruction fails
- audit review is missing
- trust verification is missing
- secret-free assessment fails
- release handoff lacks validation and replay support
- evidence relies on provider output as authority
- evidence relies on undocumented manual steps

The evidence package must be classified `PACKAGE_FAILED` when a mandatory safety failure is evidenced.

The evidence package must be classified `PACKAGE_INCONCLUSIVE` when required evidence is unavailable or cannot be interpreted deterministically.

## 11. Certification Recommendation

The evidence package may recommend:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

only when:

- package verdict is `PACKAGE_COMPLETE`
- certification decision class is `READY_RECOMMENDED`
- all mandatory readiness mappings are satisfied
- replay reconstructs all mandatory scenario lifecycles
- audit review verifies trust
- approval and authorization continuity are preserved
- validation lifecycle is preserved
- validation failure behavior is preserved where tested
- release handoff gating is preserved
- evidence is secret-free
- no blocking failure or inconclusive evidence remains

The evidence package must recommend:

```text
ACLI_GOVERNED_DEVELOPMENT_NOT_READY
```

when any mandatory readiness condition remains unproven, failed, or inconclusive.

This artifact defines the canonical evidence package. It does not execute scenarios and does not certify readiness.

Final artifact verdict:

```text
ACLI_CERTIFICATION_EVIDENCE_PACKAGE_V1_DEFINED
```
