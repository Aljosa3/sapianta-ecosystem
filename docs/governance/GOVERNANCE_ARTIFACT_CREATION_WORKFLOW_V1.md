# GOVERNANCE_ARTIFACT_CREATION_WORKFLOW_V1

Status: Defined

Scope: First narrow ACLI governed development workflow for governance artifact creation.

Strategic basis:

- ACLI_GOVERNED_DEVELOPMENT_STRATEGIC_DECISION_V1
- ACLI_GOVERNED_DEVELOPMENT_GAP_ANALYSIS_V1
- ACLI_WORKFLOW_INVOCATION_RUNTIME_V1
- ACLI_REPOSITORY_CONTEXT_RUNTIME_V1
- ACLI_VALIDATION_RUNTIME_V1
- ACLI_DEVELOPMENT_REPLAY_RUNTIME_V1

Workflow id:

```text
GOVERNANCE_ARTIFACT_CREATION
```

Final workflow verdict:

```text
WORKFLOW_DEFINED
```

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_WORKFLOW_V1_DEFINED
```

## 1. Workflow Purpose

This workflow defines the first narrow ACLI governed development workflow.

It exists to allow a human to request creation of a governance artifact through ACLI without manually selecting an internal workflow name or bypassing governance controls.

The workflow transforms:

```text
Natural Language
-> HIRR
-> Workflow Selection
-> Governance Artifact Proposal
-> Human Approval
-> Artifact Creation
-> Validation
-> Replay
```

This workflow does not create a generic autonomous development executor. It is limited to governance artifact creation after intent resolution, repository context acquisition, proposal generation, explicit human approval, bounded mutation, validation, and replay capture.

## 2. Workflow Inputs

Supported human intents:

- create a new governance artifact
- define a new governance review artifact
- define a new governance workflow artifact
- define a new certification artifact
- define a new governance analysis artifact
- create a bounded governance markdown document under `docs/governance/`

Examples of supported requests:

- "Create a governance artifact defining the next certification scenario."
- "Implement the governance review document for this readiness gate."
- "Create a workflow definition for governance artifact creation."

Unsupported inputs:

- runtime code mutation
- test creation or modification
- release handoff
- deployment action
- direct server mutation
- hidden or automatic constitutional mutation
- broad repository refactoring
- creation of artifacts outside the approved governance scope
- mutation without explicit approval

Mandatory workflow inputs:

- original human request
- HIRR or resolved intent artifact
- workflow invocation artifact
- repository context artifact
- governance context reference
- proposed artifact path
- proposed artifact title
- proposed artifact scope
- approval decision artifact
- replay chain reference

The workflow must fail closed when the request cannot be resolved to a governance artifact creation intent.

## 3. Workflow Lifecycle

The canonical lifecycle is:

```text
Human Request
-> HIRR
-> Workflow Selection
-> Repository Context
-> Governance Artifact Proposal
-> Human Approval
-> Bounded Artifact Creation
-> Validation
-> Replay Capture
-> Reviewable Completion
```

Lifecycle requirements:

| Stage | Requirement |
| --- | --- |
| Human Request | Preserve original human language. |
| HIRR | Resolve artifact creation intent or request clarification. |
| Workflow Selection | Select `GOVERNANCE_ARTIFACT_CREATION` deterministically. |
| Repository Context | Confirm target directory, existing artifact names, and relevant governing docs. |
| Proposal | Produce proposed artifact path, purpose, scope, and mutation summary. |
| Approval | Require explicit human approval before writing. |
| Artifact Creation | Create only the approved governance artifact. |
| Validation | Run mandatory documentation validation. |
| Replay | Persist lifecycle evidence and reconstruction references. |
| Reviewable Completion | Produce an outcome that can be reviewed by certification or audit process. |

No repository mutation may occur before approval.

## 4. Repository Context

Repository context is required before proposal finalization.

Minimum repository awareness:

- repository root
- current working tree status
- target artifact directory
- existing artifact with same or conflicting name
- relevant governance artifacts
- applicable mutation boundaries
- validation commands required for documentation-only governance changes

Minimum context evidence:

- files inspected
- target path assessed
- conflict check result
- governance boundary assessment
- dirty worktree awareness
- assumptions and unresolved context gaps

The workflow must fail closed when repository context is unavailable, stale, or insufficient to determine the safety of artifact creation.

## 5. Proposal Generation

The proposal stage defines the artifact before mutation.

Minimum proposal contents:

- proposal id
- original human request reference
- resolved intent reference
- selected workflow id
- proposed artifact path
- proposed artifact title
- artifact purpose
- required scope coverage
- non-goals
- governance constraints
- expected validation commands
- replay requirements
- mutation summary
- approval request

Proposal constraints:

- proposal is not authority
- proposal does not permit mutation by itself
- proposal must be replay-visible
- proposal must identify any uncertainty
- proposal must identify if the target artifact would affect protected constitutional semantics

If proposal scope is ambiguous or broader than governance artifact creation, the workflow must request clarification or fail closed.

## 6. Approval Stage

Human approval is mandatory before artifact creation.

Approval evidence must include:

- approval id
- approving human or operator identity reference
- proposal reference
- approved artifact path
- approved artifact scope
- approved mutation limits
- approved validation requirements
- approval timestamp
- replay reference

Approval must be explicit. Silence, implied continuation, workflow selection, HIRR completion, or proposal generation do not constitute approval.

Approval denial or absence produces:

```text
FAIL_CLOSED_NO_APPROVAL
```

The workflow must preserve:

```text
Human = Authority
```

## 7. Artifact Creation

Artifact creation is the only repository mutation allowed by this workflow.

Allowed mutation scope:

- create one approved markdown artifact under `docs/governance/`
- write content consistent with the approved proposal
- avoid modifying unrelated files
- avoid changing runtime code
- avoid changing tests
- avoid changing release artifacts
- avoid mutating replay history

Artifact creation must be bounded by:

- approved path
- approved scope
- repository context evidence
- validation requirements
- replay linkage

Forbidden mutation:

- unapproved file creation
- unapproved file edit
- deletion
- broad rename
- runtime code modification
- hidden constitutional reinterpretation
- replay artifact mutation
- server or deployment mutation

If artifact creation cannot be limited to approved scope, the workflow must fail closed.

## 8. Validation

Validation is mandatory after artifact creation.

Minimum validation:

```bash
git diff --check
```

Additional validation is required when governance conformance rules, certification rules, or repository policy demand it.

Validation evidence must include:

- validation command
- timestamp
- exit status
- summarized output
- changed files
- pass or fail status
- replay reference

Validation outcomes:

| Outcome | Behavior |
| --- | --- |
| PASS | Continue to replay capture and reviewable completion. |
| FAIL | Fail closed and preserve failure evidence. |
| NOT_RUN | Fail closed unless explicitly justified as unavailable and accepted by human review. |

Validation failure must not be hidden or reframed as success.

## 9. Replay Integration

Replay is mandatory and is the source of truth for workflow evidence.

Replay must record:

- original human request
- HIRR / resolved intent artifact
- workflow selection artifact
- repository context artifact
- proposal artifact
- approval artifact
- mutation artifact
- validation artifact
- final workflow outcome

Replay reconstruction must show:

```text
what was requested
what workflow was selected
what context was inspected
what artifact was proposed
what the human approved
what file was created
what validation ran
what final outcome occurred
```

Replay gaps are workflow failures.

If replay persistence or reconstruction fails, final workflow completion must be withheld.

## 10. Success Criteria

The workflow is complete only when all of the following are true:

- original human request is preserved
- intent is resolved through HIRR or equivalent certified intake
- `GOVERNANCE_ARTIFACT_CREATION` is selected deterministically
- repository context is captured
- proposal is recorded
- explicit human approval is recorded
- only the approved governance artifact is created
- validation runs and passes
- replay evidence is persisted
- workflow outcome is reviewable
- no unsupported mutation occurs

Measurable completion status:

```text
GOVERNANCE_ARTIFACT_CREATION_COMPLETED
```

Fail-closed statuses:

```text
FAIL_CLOSED_UNRESOLVED_INTENT
FAIL_CLOSED_NO_WORKFLOW_SELECTION
FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT
FAIL_CLOSED_NO_PROPOSAL
FAIL_CLOSED_NO_APPROVAL
FAIL_CLOSED_SCOPE_VIOLATION
FAIL_CLOSED_VALIDATION_FAILED
FAIL_CLOSED_REPLAY_INCOMPLETE
```

## 11. Final Verdict

Final workflow verdict:

```text
WORKFLOW_DEFINED
```

Rationale:

The workflow defines the narrowest viable ACLI governed development path: governance artifact creation only. It uses existing ACLI runtime architecture concepts, preserves HIRR and replay boundaries, requires human approval before mutation, limits mutation to the approved governance artifact, requires validation, and makes replay evidence mandatory.

This workflow does not by itself prove runtime implementation or certification readiness. It defines the required workflow boundary for later implementation and execution evidence.

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_WORKFLOW_V1_DEFINED
```
