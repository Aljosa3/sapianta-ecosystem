# ACLI_REPOSITORY_CONTEXT_RUNTIME_V1

Status: Defined

Scope: Repository context runtime specification for ACLI-governed development workflows.

Governing artifacts:

- ACLI_END_TO_END_READINESS_REVIEW_V1
- ACLI_GOVERNED_DEVELOPMENT_WORKFLOW_V1
- ACLI_GOVERNED_DEVELOPMENT_READINESS_REVIEW_V1

Final verdict:

ACLI_REPOSITORY_CONTEXT_RUNTIME_V1_DEFINED

## 1. Purpose

This artifact defines how ACLI obtains, maintains, validates, and uses repository context for governed development workflows.

The objective is to remove manual context packaging from the development path:

```text
Human
-> ChatGPT
-> Prompt
-> Codex
-> Copy/Paste
-> Repository
```

and replace it with replay-visible repository awareness:

```text
Human
-> ACLI
-> Repository Context Runtime
-> Governed Development Workflow
-> Replay
```

This is a runtime specification. It does not implement code, redesign ACLI, redesign governance, redesign replay, or create new authority layers.

## 2. Preserved Invariants

The repository context runtime preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Repository context informs governance. It does not authorize mutation, replace human approval, or become an independent authority source.

## 3. Repository Awareness Model

Repository awareness is the ACLI capability to identify the relevant repository state needed to classify, propose, validate, and replay governed development work.

Repository awareness includes:

- file and directory awareness
- changed-file awareness
- governing artifact awareness
- runtime module awareness
- test surface awareness
- certification runtime awareness
- replay artifact awareness
- product artifact awareness
- release discipline awareness
- known limitation awareness

Repository awareness must be bounded to the current repository and approved readable paths.

ACLI must distinguish between:

- observed repository facts
- inferred relationships
- stale or incomplete context
- human-provided claims
- provider-generated proposals

Only observed facts and replay-recorded human approvals may support mutation decisions.

## 4. Artifact Awareness

Artifact awareness is the ability to locate and classify repository artifacts relevant to a development request.

Minimum artifact families:

- governance artifacts
- product lifecycle artifacts
- runtime modules
- provider runtime artifacts
- worker runtime artifacts
- replay artifacts
- certification artifacts
- tests
- release evidence
- README and operator guidance

For each relevant artifact, ACLI context must record:

- artifact path
- artifact family
- artifact role
- last observed state identifier
- relevance rationale
- whether the artifact is governing, supporting, evidence-only, or generated runtime output

ACLI must not treat an artifact as governing unless it is already recognized as a governing artifact by repository convention or explicit certified lineage.

## 5. Workflow Awareness

Workflow awareness is the ability to determine which certified or defined workflows may apply to a development request.

Workflow awareness must include:

- known workflow names
- workflow purpose
- required inputs
- required approvals
- validation expectations
- replay expectations
- fail-closed conditions
- certification status

For ACLI-governed development, minimum workflow classes are:

- DEVELOPMENT_CONTEXT_REVIEW
- DEVELOPMENT_PROPOSAL
- GOVERNANCE_ARTIFACT_CREATION
- RUNTIME_IMPLEMENTATION
- TEST_IMPLEMENTATION
- CERTIFICATION_EXECUTION
- REMEDIATION
- RELEASE_HANDOFF

If no workflow can be selected with sufficient confidence, ACLI must request clarification or escalate semantically without executing mutation.

## 6. Context Acquisition

Context acquisition is the runtime process by which ACLI gathers repository state.

Supported acquisition sources:

- repository scan
- artifact registry
- governance registry
- workflow registry
- certification report index
- replay package index
- test inventory
- runtime module inventory
- current working tree status

Minimum acquisition steps:

1. Capture original human request.
2. Classify the request as development-related or non-development-related.
3. Identify candidate artifact families.
4. Identify candidate workflows.
5. Inspect governing artifacts before implementation artifacts.
6. Inspect runtime and test surfaces relevant to the request.
7. Inspect current working tree state.
8. Record assumptions, omissions, and unresolved context.
9. Produce a replay-safe context summary.

Context acquisition must be deterministic where repository structure is deterministic. When semantic interpretation is required, cognition providers may propose relevance, but ACLI must record provider participation and preserve governance authority.

## 7. Context Freshness

Context freshness determines whether acquired repository context remains valid for workflow selection, approval, mutation, and validation.

Context must be considered stale when:

- relevant files changed after context acquisition
- working tree state changed materially
- approval scope changed
- workflow target changed
- validation target changed
- new evidence or certification output was created
- context age exceeds the active session freshness policy

Minimum freshness evidence:

- context acquisition timestamp
- repository root
- inspected paths
- changed-file summary
- dirty worktree summary
- context version identifier
- invalidation triggers

If context is stale, ACLI must refresh context before proposal, approval, mutation, or validation.

ACLI must not rely on stale context to authorize repository mutation.

## 8. Context Boundaries

ACLI may assume:

- facts directly observed from allowed repository reads
- certified verdicts recorded in governing artifacts
- replay evidence explicitly referenced by path
- human clarification answers recorded in the session
- current working tree status observed at context acquisition time

ACLI may not assume:

- unobserved files are irrelevant
- old context remains valid after file changes
- provider suggestions are facts
- human intent implies approval
- approval for one scope authorizes a broader scope
- successful prior certification authorizes new mutation
- generated artifacts are governing unless certified or accepted into governance lineage

When a required assumption is unresolved, ACLI must either clarify, refresh context, escalate to cognition for proposal-only interpretation, or fail closed.

## 9. Workflow Context Requirements

Workflow invocation requires sufficient context to select the correct governed workflow.

Minimum workflow context:

- resolved or clarifying human intent
- candidate workflow classes
- rejected workflow classes
- selection rationale
- governing artifact references
- required approval boundary
- required replay evidence
- required validation category
- known uncertainty

Workflow invocation must not proceed when:

- intent is unresolved
- candidate workflows conflict
- governing artifacts cannot be identified
- approval requirements are unknown
- replay requirements are unknown
- validation requirements are unknown

In these cases, ACLI must request clarification or fail closed.

## 10. Development Context Requirements

Repository mutation workflows require stricter context than workflow invocation.

Minimum development context:

- target files or artifact families
- relevant governing artifacts
- relevant runtime modules
- relevant tests
- current changed-file inventory
- user-owned changes that must be preserved
- mutation scope
- validation plan
- replay evidence plan
- approval scope
- rollback or stop conditions

Development context must explicitly identify:

- what may change
- what must not change
- what evidence must be produced
- what validation must run
- what would cause fail-closed behavior

ACLI must not issue mutation authorization when development context is incomplete.

## 11. Replay Integration

Repository context participates in replay as first-class evidence.

Required replay artifacts:

- repository_context_acquisition_artifact
- artifact_relevance_artifact
- workflow_context_artifact
- context_freshness_artifact
- context_gap_artifact when applicable
- context_refresh_artifact when applicable

Replay must allow a reviewer to reconstruct:

- what repository context ACLI saw
- which artifacts were considered relevant
- which artifacts were rejected as irrelevant
- whether context was fresh at approval time
- whether context was fresh at mutation time
- what context gaps existed
- whether any gaps were resolved, clarified, escalated, or failed closed

Replay must not include secrets, credential values, authorization headers, private keys, or raw payloads that are not necessary for governance reconstruction.

## 12. Approval Integration

Repository context supports human approval by making the proposed development scope understandable.

Approval summaries must include:

- resolved human intent
- relevant repository context
- affected files or artifact families
- proposed mutation scope
- validation plan
- replay plan
- known risks
- unresolved context gaps
- fail-closed conditions

Approval is invalid if the context summary is missing, stale, materially incomplete, or mismatched with the proposed mutation scope.

If context changes after approval and before mutation, ACLI must require renewed approval or explicit human confirmation of the updated scope.

## 13. Failure Handling

Repository context failures must fail closed.

Fail-closed conditions:

- repository root cannot be determined
- governing artifacts cannot be read
- required workflow context is unavailable
- target files cannot be inspected
- working tree state cannot be determined
- context freshness cannot be verified
- user-owned changes cannot be distinguished from proposed changes
- validation requirements cannot be determined
- replay evidence cannot be written
- secret-safety cannot be verified

Failure output must record:

- failure category
- failed context stage
- missing or stale context
- affected workflow
- remediation expectation
- whether human input can resolve the issue
- replay reference

ACLI must not continue with mutation when repository context failure occurs.

## 14. Readiness Criteria

ACLI_REPOSITORY_CONTEXT_READY requires certification that ACLI can:

- detect development intent requiring repository context
- determine repository root
- scan relevant repository surfaces
- identify governing artifacts
- identify relevant runtime modules
- identify relevant tests
- identify current working tree state
- record context freshness
- detect stale context
- refresh stale context
- identify unresolved context gaps
- fail closed on insufficient context
- produce replay-safe context evidence
- support approval with context summary
- preserve secret-free evidence

Minimum certification scenarios:

- governance artifact creation request
- runtime implementation request
- test addition request
- certification rerun request
- dirty worktree request
- stale context before mutation
- missing governing artifact
- incomplete workflow context
- context refresh after file change
- approval denied due to insufficient context

Target readiness verdict:

```text
ACLI_REPOSITORY_CONTEXT_READY
```

This artifact does not certify readiness. It defines the runtime behavior required for certification.

Final artifact verdict:

```text
ACLI_REPOSITORY_CONTEXT_RUNTIME_V1_DEFINED
```
