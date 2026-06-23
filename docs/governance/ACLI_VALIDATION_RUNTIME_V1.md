# ACLI_VALIDATION_RUNTIME_V1

Status: Defined

Scope: Validation runtime specification for ACLI-governed development workflows.

Governing artifacts:

- ACLI_GOVERNED_DEVELOPMENT_WORKFLOW_V1
- ACLI_REPOSITORY_CONTEXT_RUNTIME_V1
- ACLI_GOVERNED_DEVELOPMENT_READINESS_REVIEW_V1

Final verdict:

ACLI_VALIDATION_RUNTIME_V1_DEFINED

## 1. Purpose

This artifact defines how ACLI performs governed validation after repository mutation and before replay closure or release handoff.

Validation exists to determine whether an approved development change satisfies the approved scope, preserves governance boundaries, and produces evidence sufficient for review.

Validation proves:

- the mutation stayed within approved scope
- required checks were selected
- required checks executed or were explicitly blocked
- validation results are replay-visible
- failures are preserved
- release handoff is not prepared from unvalidated work

Validation does not prove perfect correctness, regulatory compliance, product-market suitability, or absence of all defects.

## 2. Preserved Invariants

The validation runtime preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Validation is a governance checkpoint. It does not replace human authority, approve its own remediation, or authorize release.

## 3. Validation Inputs

Validation requires replay-visible inputs.

Required inputs:

- repository context artifact
- context freshness artifact
- development intent artifact
- mutation proposal artifact
- approval artifact
- authorization artifact
- workflow selection artifact
- mutation record
- changed-file inventory
- governing artifact references
- validation plan

Optional inputs:

- certification report references
- replay package references
- provider participation artifacts
- worker handoff artifacts
- prior failure artifacts
- remediation proposal artifacts

Validation must fail closed when required inputs are missing, stale, contradictory, or not replay-visible.

## 4. Validation Lifecycle

Validation follows:

```text
Mutation
-> Validation
-> Replay
```

Expanded lifecycle:

```text
authorized mutation
-> changed-file inventory
-> validation plan confirmation
-> validation execution
-> result classification
-> evidence capture
-> replay reconstruction check
-> release handoff eligibility decision
```

Validation must occur after mutation and before any claim that the change is ready for release handoff.

If validation requires additional mutation, ACLI must create a remediation proposal and request renewed human approval.

## 5. Validation Families

### 5.1 Syntax Validation

Purpose:

Verify that changed source files, configuration files, and structured artifacts can be parsed or compiled by the relevant local tooling.

Examples:

- Python compilation
- JSON parsing
- Markdown formatting hygiene
- manifest parsing

Trust value:

Confirms basic machine readability. Does not confirm behavior.

### 5.2 Structural Validation

Purpose:

Verify that files are present in expected locations and follow expected repository structure.

Examples:

- required governance artifact path exists
- certification output directories are present
- expected package/module path exists
- generated artifacts use expected family structure

Trust value:

Confirms the repository shape supports downstream review and replay.

### 5.3 Governance Validation

Purpose:

Verify that the change preserves governance constraints.

Examples:

- constitutional invariant block preserved where required
- no authority boundary weakening
- no autonomous mutation path introduced
- no replay bypass introduced
- no secret values included in governance artifacts

Trust value:

Confirms governance compatibility, not functional correctness.

### 5.4 Workflow Validation

Purpose:

Verify that the selected workflow was followed.

Examples:

- approval preceded mutation
- authorization matched approved scope
- mutation stayed within scope
- denied approval blocked execution
- required fail-closed behavior was preserved

Trust value:

Confirms workflow discipline.

### 5.5 Runtime Validation

Purpose:

Verify behavior of changed runtime code.

Examples:

- targeted unit tests
- targeted certification tests
- command-level smoke checks
- fail-closed behavior tests

Trust value:

Confirms observed runtime behavior for selected scenarios.

### 5.6 Replay Validation

Purpose:

Verify that replay reconstructs the governed path.

Examples:

- replay package exists
- evidence package exists
- certification report exists
- replay links to approval, authorization, mutation, and validation evidence
- replay remains secret-free

Trust value:

Confirms audit reconstructability.

### 5.7 Release Handoff Validation

Purpose:

Verify that post-validation handoff evidence is sufficient for commit or release consideration.

Examples:

- changed-file inventory
- validation summary
- known limitations
- evidence references
- replay references
- proposed commit message if requested

Trust value:

Confirms readiness for human release decision, not automatic release.

## 6. Validation Results

Validation result classifications:

### PASS

PASS means:

- required validation inputs were present
- selected validation checks executed
- checks succeeded
- replay evidence was captured
- no blocking governance violation was found

PASS allows release handoff preparation, subject to human review.

### FAIL

FAIL means:

- one or more required validation checks failed
- a governance boundary was violated
- mutation exceeded approved scope
- replay reconstruction failed
- secret-safety check failed
- validation evidence showed a blocking defect

FAIL blocks release handoff.

### INCONCLUSIVE

INCONCLUSIVE means:

- required context was stale
- required validation could not run
- validation tooling was unavailable
- evidence was incomplete
- output could not be interpreted deterministically
- required replay evidence could not be reconstructed

INCONCLUSIVE must be treated as blocking. It is not equivalent to PASS.

## 7. Fail-Closed Requirements

Validation must fail closed when:

- required validation inputs are missing
- approval artifact is missing
- authorization artifact is missing
- mutation record is missing
- changed-file inventory is unavailable
- validation plan is absent
- selected validation cannot execute
- validation result is inconclusive
- replay evidence cannot be written
- replay reconstruction fails
- secret exposure is detected
- mutation exceeds approved scope
- governance invariant is weakened

Fail-closed output must include:

- validation stage
- failure category
- affected artifact or file
- blocking reason
- remediation expectation
- whether human approval is required for remediation
- replay reference

ACLI must not convert FAIL or INCONCLUSIVE into PASS through provider interpretation or advisory text.

## 8. Approval Integration

Approval, authorization, and validation are separate stages.

Approval:

- human approves a bounded proposal
- approval defines permitted scope
- approval does not validate results

Authorization:

- AiGOL issues bounded execution permission based on approval
- authorization constrains mutation
- authorization does not release results

Validation:

- checks the mutation and evidence after execution
- determines whether release handoff may be prepared
- does not approve release

If validation requires remediation, ACLI must route to a new proposal and approval path.

Validation must compare:

- approved scope
- authorized scope
- actual mutation
- validation plan
- observed result

Any mismatch blocks release handoff.

## 9. Replay Integration

Validation participates in replay as a first-class evidence family.

Replay must reconstruct:

- validation inputs
- validation plan
- selected validation families
- commands or checks executed
- validation results
- failures and inconclusive states
- replay reconstruction result
- release handoff eligibility

Validation replay artifacts must reference:

- repository context
- approval
- authorization
- mutation record
- changed-file inventory
- validation evidence
- certification report when applicable

Replay must preserve failed and inconclusive validation results. Failed evidence is governance evidence, not noise.

## 10. Validation Evidence

Required validation evidence artifacts:

- VALIDATION_PLAN_ARTIFACT
- VALIDATION_INPUTS_ARTIFACT
- VALIDATION_EXECUTION_ARTIFACT
- VALIDATION_RESULT_ARTIFACT
- VALIDATION_FAILURE_ARTIFACT when applicable
- VALIDATION_REPLAY_LINKAGE_ARTIFACT
- VALIDATION_RELEASE_HANDOFF_ELIGIBILITY_ARTIFACT

Minimum fields:

- validation_id
- workflow_id
- approval_id
- authorization_id
- mutation_id
- repository_context_id
- validation_families
- checks_selected
- checks_executed
- checks_skipped_with_reason
- result_classification
- blocking_failures
- inconclusive_reasons
- replay_reconstructed
- secret_free_evidence
- release_handoff_eligible

Evidence must not include secret values, provider credentials, authorization headers, private keys, or raw payloads unrelated to validation.

## 11. Validation Selection Rules

Validation must be selected from the touched surface.

Minimum mapping:

| Touched surface | Required validation families |
| --- | --- |
| Governance markdown artifact | syntax, structural, governance |
| Runtime Python module | syntax, runtime, workflow when applicable |
| Test file | syntax, runtime |
| Certification runtime | syntax, runtime, replay |
| Replay artifact model | structural, replay, governance |
| Provider or credential runtime | runtime, governance, replay, secret-safety |
| Worker runtime | runtime, workflow, replay |
| Release handoff artifact | structural, release handoff, governance |

When touched surface cannot be classified, validation must be INCONCLUSIVE and fail closed.

## 12. Readiness Criteria

ACLI_VALIDATION_RUNTIME_READY requires certification that ACLI can:

- consume repository context evidence
- consume proposal, approval, and authorization evidence
- identify changed files
- select validation families from touched surface
- execute required validation checks
- classify PASS, FAIL, and INCONCLUSIVE
- fail closed on missing evidence
- fail closed on failed validation
- fail closed on inconclusive validation
- preserve failed validation evidence
- preserve replay linkage
- block release handoff when validation is not PASS
- generate secret-free validation artifacts

Minimum certification scenarios:

- documentation-only validation PASS
- runtime syntax validation PASS
- runtime test validation PASS
- governance validation FAIL
- replay reconstruction FAIL
- missing approval artifact
- stale repository context
- validation tool unavailable
- inconclusive touched surface
- release handoff blocked after FAIL
- release handoff allowed after PASS

Target readiness verdict:

```text
ACLI_VALIDATION_RUNTIME_READY
```

This artifact does not certify readiness. It defines the runtime behavior required for certification.

Final artifact verdict:

```text
ACLI_VALIDATION_RUNTIME_V1_DEFINED
```
