# ACLI_WORKFLOW_INVOCATION_RUNTIME_V1

Status: Defined

Scope: Workflow invocation runtime specification for ACLI-governed workflows.

Governing artifacts:

- ACLI_GOVERNED_DEVELOPMENT_WORKFLOW_V1
- ACLI_REPOSITORY_CONTEXT_RUNTIME_V1
- ACLI_VALIDATION_RUNTIME_V1
- ACLI_DEVELOPMENT_REPLAY_RUNTIME_V1
- AIGOL_ACLI_WORKFLOW_SELECTION_FAILURE_ANALYSIS_V1
- AIGOL_ACLI_WORKFLOW_SELECTION_REMEDIATION_V1

Baseline:

- HUMAN_INTENT_RESOLUTION_READY
- ACLI_LIVE_OPERATOR_READY
- ACLI_GOVERNED_DEVELOPMENT_WORKFLOW_V1_DEFINED
- ACLI_REPOSITORY_CONTEXT_RUNTIME_V1_DEFINED
- ACLI_VALIDATION_RUNTIME_V1_DEFINED
- ACLI_DEVELOPMENT_REPLAY_RUNTIME_V1_DEFINED

Final verdict:

ACLI_WORKFLOW_INVOCATION_RUNTIME_V1_DEFINED

## 1. Purpose

This artifact defines how ACLI deterministically invokes the correct governed workflow from resolved human intent.

Workflow invocation exists to close the operational gap between:

```text
Natural Language
-> Intent Resolution
```

and:

```text
Governed Workflow Invocation
-> Governed Workflow
```

The human should not need to know internal workflow names, certification identifiers, routing terms, repository structure, or governance implementation details before entering a governed workflow.

Workflow invocation proves:

- resolved intent was mapped to a known governed workflow
- the selected workflow is admissible for the resolved intent
- rejected workflow candidates were recorded
- ambiguity was clarified, escalated, or failed closed
- no worker execution occurred merely because invocation selected a workflow
- invocation evidence is replay-visible

Invocation is downstream of intent resolution. HIRR resolves or clarifies what the human is asking for. Workflow Invocation determines which governed workflow may receive that resolved intent.

Invocation is not approval, authorization, mutation, validation, release handoff, or worker execution.

## 2. Preserved Invariants

Workflow invocation preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Invocation must not introduce autonomous repository mutation, hidden approval bypass, provider authority, worker execution from intake, or replay gaps.

## 3. Invocation Inputs

Workflow invocation requires replay-visible inputs.

Mandatory inputs:

- resolved intent artifact
- original human request reference
- workflow registry or certified workflow catalog reference
- governance context reference
- invocation policy reference
- replay chain reference

Conditionally mandatory inputs:

- clarification artifacts when HIRR required clarification
- repository context artifacts for development, repository, runtime, test, governance, certification, replay, or release requests
- context freshness artifacts when repository context is required
- prior workflow continuity artifacts when the request resumes an existing workflow
- provider participation artifacts when cognition assisted intent interpretation
- denial or fail-closed artifacts when invocation cannot proceed

Governance context must include:

- allowed workflow classes
- workflow preconditions
- approval requirements
- authorization requirements
- mutation boundaries
- replay requirements
- validation expectations
- fail-closed conditions

Workflow invocation must fail closed when required inputs are missing, stale, contradictory, not replay-visible, or outside governance boundaries.

## 4. Invocation Lifecycle

The canonical lifecycle is:

```text
Intent
-> Resolution
-> Invocation
-> Workflow
```

Expanded lifecycle:

```text
human natural language
-> HIRR intake
-> clarification if required
-> resolved intent
-> invocation input assembly
-> candidate workflow identification
-> deterministic selection or fail-closed stop
-> invocation artifact recorded
-> governed workflow entered
```

Invocation may enter a workflow stage that later requests approval, authorization, mutation, validation, or release handoff. Invocation itself does not satisfy those later stages.

The invocation output must include:

- invocation id
- resolved intent reference
- selected workflow id
- selected workflow class
- rejected candidate workflows
- selection rationale
- confidence or determinism classification
- required next lifecycle stage
- approval awareness status
- repository context status when applicable
- replay reference
- fail-closed status when applicable

## 5. Workflow Selection Requirements

Workflow selection must be deterministic whenever resolved intent and context are sufficient.

Deterministic selection requires:

- a known workflow registry entry
- a resolved intent family
- satisfied workflow preconditions
- no unresolved competing workflow with equal or higher priority
- governance context confirming admissibility
- repository context when workflow choice depends on repository state
- replay-visible selection rationale

Minimum development workflow classes:

| Workflow class | Invocation purpose |
| --- | --- |
| DEVELOPMENT_CONTEXT_REVIEW | inspect repository and governing artifacts |
| DEVELOPMENT_PROPOSAL | prepare a bounded development proposal |
| GOVERNANCE_ARTIFACT_CREATION | create or update a governance artifact after approval |
| RUNTIME_IMPLEMENTATION | modify runtime code after approval |
| TEST_IMPLEMENTATION | add or update tests after approval |
| CERTIFICATION_EXECUTION | run bounded certification or validation after approval when evidence writes occur |
| REMEDIATION | correct a confirmed defect or gap after approval |
| RELEASE_HANDOFF | prepare commit or release evidence after validation |

Selection must record:

- selected workflow
- candidate workflows considered
- rejected alternatives
- reason for rejection
- required approval boundary
- required validation family
- required replay evidence

Ambiguity handling:

- unresolved intent must return to HIRR clarification
- multiple admissible workflows must request clarification or record an explicit human workflow choice
- governance-sensitive ambiguity must escalate to governance review or fail closed
- provider-assisted interpretation may propose a workflow but must not become authoritative

ACLI must not select a workflow by guessing when deterministic selection cannot be established.

## 6. Clarification Integration

The relationship is:

```text
HIRR
-> Workflow Invocation
```

HIRR supplies resolved intent, clarification history, ambiguity status, and any remaining uncertainty. Workflow Invocation consumes that evidence and attempts deterministic workflow selection.

Clarification artifacts must preserve:

- original prompt
- clarification questions
- human clarification responses
- resolved intent family
- unresolved ambiguity if any
- workflow target candidates if HIRR identified them
- provider participation when escalation occurred
- confirmation that no approval or execution was implied by clarification alone

Workflow Invocation must return to HIRR when:

- intent remains unresolved
- the human response only confirms a missing or unclear object
- the response could mean approval or clarification but the scope is not explicit
- the target workflow depends on a missing object, file, artifact, or repository state
- the request contains contradictory constraints

Clarification may make invocation possible. Clarification does not authorize mutation.

## 7. Repository Context Integration

Repository-aware invocation is required for development workflows and any workflow whose admissibility depends on repository state.

Required repository-awareness inputs:

- repository root
- current working tree summary
- relevant governance artifacts
- relevant runtime modules
- relevant tests
- relevant certification artifacts
- relevant replay artifacts
- target files or artifact families when known
- protected boundary indicators
- context freshness status
- unresolved context gaps

Repository context supports invocation by identifying which workflow class applies. For example, a request to create a governance specification requires governance artifact awareness, while a request to change runtime behavior requires runtime and test awareness.

Repository context does not approve mutation, authorize execution, or certify readiness.

Invocation must fail closed when repository context is required but:

- the repository root cannot be determined
- governing artifacts cannot be inspected
- target artifact family cannot be classified
- protected boundary status is unknown
- working tree state cannot be determined
- context freshness cannot be verified

## 8. Approval Integration

Invocation requires approval awareness when the selected workflow may later mutate repository state, write certification evidence, prepare release handoff, or cross a governance-sensitive boundary.

Approval awareness means invocation must record:

- whether the selected workflow requires later human approval
- what stage requires approval
- what scope approval must cover
- whether approval is already present, absent, denied, stale, or out of scope
- whether invocation must stop at proposal, approval request, or context review

Invocation may proceed into non-mutating workflow stages without approval when the workflow permits inspection, clarification, proposal drafting, or advisory review.

Invocation must not treat any of the following as approval:

- intent resolution
- clarification response
- workflow selection
- provider recommendation
- prior approval for a different scope
- successful prior validation
- replay-derived improvement proposal

When approval is required but absent, invocation may enter the workflow only up to the approval-request boundary.

## 9. Replay Integration

Workflow invocation becomes replay evidence as a first-class evidence family.

Required invocation replay artifacts:

- WORKFLOW_INVOCATION_INPUTS_ARTIFACT
- WORKFLOW_CANDIDATE_SELECTION_ARTIFACT
- WORKFLOW_INVOCATION_DECISION_ARTIFACT
- WORKFLOW_INVOCATION_REJECTION_ARTIFACT when applicable
- WORKFLOW_INVOCATION_FAIL_CLOSED_ARTIFACT when applicable
- WORKFLOW_INVOCATION_REPLAY_LINKAGE_ARTIFACT

Replay must reconstruct:

- original human request
- resolved intent
- clarification path when applicable
- repository context used when applicable
- governance context used
- candidate workflows
- selected workflow
- rejected workflows
- ambiguity or escalation handling
- approval awareness status
- next workflow stage
- whether provider or worker participation occurred

Invocation replay evidence must explicitly record:

```text
worker_invoked = false
mutation_performed = false
authorization_created = false unless a separate authorization stage exists
approval_bypassed = false
```

Replay remains the source of truth for why a workflow was invoked.

## 10. Fail-Closed Requirements

Workflow invocation must fail closed when:

- no workflow matches
- multiple workflows match without deterministic priority
- resolved intent is missing
- clarification evidence is required but missing
- repository context is required but insufficient
- governance context is unavailable
- workflow registry is unavailable
- workflow preconditions cannot be verified
- selected workflow would cross a protected boundary without approval path
- approval status is ambiguous for a workflow stage requiring approval
- provider output is the only basis for selection
- replay evidence cannot be recorded

Fail-closed output must include:

- invocation stage
- failure category
- unresolved intent or context gap
- candidate workflows if any
- reason no deterministic selection was possible
- required human clarification or governance review
- replay reference

Fail-closed invocation must not enter mutation, worker execution, validation, release handoff, or authorization stages.

## 11. Readiness Criteria

ACLI_WORKFLOW_INVOCATION_READY requires certification that ACLI can:

- consume resolved human intent
- consume clarification artifacts
- consume repository context when required
- consume governance context
- identify candidate workflows
- deterministically select one workflow when evidence is sufficient
- record rejected candidate workflows
- return unresolved intent to HIRR clarification
- fail closed when no workflow matches
- fail closed when multiple workflows match without deterministic priority
- fail closed when repository context is insufficient
- preserve approval awareness without treating invocation as approval
- enter only the allowed initial workflow stage
- prevent worker invocation during workflow invocation
- prevent mutation during workflow invocation
- produce replay-safe invocation evidence
- reconstruct invocation from replay

Minimum certification scenarios:

- resolved development intent invokes DEVELOPMENT_PROPOSAL
- governance artifact request invokes GOVERNANCE_ARTIFACT_CREATION
- runtime change request invokes RUNTIME_IMPLEMENTATION
- test request invokes TEST_IMPLEMENTATION
- validation request invokes CERTIFICATION_EXECUTION or validation workflow
- release handoff request invokes RELEASE_HANDOFF only after validation context
- ambiguous request returns to HIRR clarification
- no matching workflow fails closed
- multiple matching workflows fail closed or require human selection
- missing repository context fails closed
- approval-required workflow stops at approval boundary
- replay reconstructs selected and rejected workflows

Target readiness verdict:

```text
ACLI_WORKFLOW_INVOCATION_READY
```

This artifact does not certify readiness. It defines the runtime behavior required for certification.

Final artifact verdict:

```text
ACLI_WORKFLOW_INVOCATION_RUNTIME_V1_DEFINED
```
