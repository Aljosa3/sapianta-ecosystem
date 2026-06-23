# ACLI_GOVERNED_DEVELOPMENT_WORKFLOW_V1

Status: Defined

Scope: Governed development workflow executed through ACLI.

Governing review:

- ACLI_END_TO_END_READINESS_REVIEW_V1

Baseline:

- HUMAN_INTENT_RESOLUTION_READY
- ACLI_LIVE_OPERATOR_READY

Final verdict:

ACLI_GOVERNED_DEVELOPMENT_WORKFLOW_V1_DEFINED

## 1. Purpose

This artifact defines the missing workflow required to move future AiGOL development from:

```text
Human
-> ChatGPT
-> Prompt
-> Codex
-> Copy/Paste
-> Repository
```

to:

```text
Human
-> ACLI
-> Governed Development Workflow
-> Replay
```

This is a workflow governance specification. It does not redesign ACLI, governance, replay, workers, providers, transport, release infrastructure, or repository storage.

## 2. Preserved Invariants

The workflow preserves the certified AiGOL invariants:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The development workflow must not introduce autonomous repository mutation, hidden approval bypass, replay gaps, or provider authority.

## 3. Development Intent Entry

Development entry begins with ordinary human language:

```text
Human
-> Natural Language
-> ACLI
```

The human may ask for development work without knowing internal workflow names, artifact naming conventions, certification names, or repository structure.

Supported development intent families:

- implement feature
- fix bug
- create governance artifact
- modify governance artifact
- create runtime certification
- modify workflow behavior
- add or update tests
- run validation
- prepare evidence package
- prepare release handoff
- investigate failure
- remediate certification gap

Example user prompts:

- "Implement the missing provider status command."
- "Fix the workflow routing bug."
- "Create the governance document for this new certification."
- "Add tests for replay reconstruction."
- "Run the validation and prepare the evidence."
- "Prepare this for commit."

ACLI must classify these as development intents rather than generic advisory prompts when the user seeks a repository, artifact, runtime, test, certification, or release change.

## 4. Repository Context Acquisition

ACLI must obtain repository context without requiring the human to manually package it.

Repository context acquisition must include:

- repository awareness
- governance artifact awareness
- runtime module awareness
- test surface awareness
- certification artifact awareness
- replay evidence awareness
- release discipline awareness
- current working tree awareness

Context acquisition must be replay-visible and secret-free.

Minimum context record:

- original human request
- inferred development intent family
- relevant files inspected
- relevant governance artifacts inspected
- relevant runtime modules inspected
- relevant tests inspected
- current repository state summary
- known dirty worktree constraints
- assumptions and unresolved context gaps

Context acquisition must fail closed when required context cannot be accessed or when the system cannot determine whether a change would cross a protected boundary.

The human remains responsible for approving any action that mutates repository state.

## 5. Development Workflow Selection

Development workflow selection follows:

```text
Intent
-> Workflow Classification
-> Governed Development Workflow
```

Required workflow classes:

| Workflow class | Purpose | Mutation allowed before approval |
| --- | --- | --- |
| DEVELOPMENT_CONTEXT_REVIEW | inspect repository and governing artifacts | no |
| DEVELOPMENT_PROPOSAL | prepare a bounded implementation or artifact proposal | no |
| GOVERNANCE_ARTIFACT_CREATION | create or update governance artifact | no |
| RUNTIME_IMPLEMENTATION | modify runtime code | no |
| TEST_IMPLEMENTATION | add or update tests | no |
| CERTIFICATION_EXECUTION | run bounded certification or validation | no, except runtime evidence output when approved |
| REMEDIATION | correct a confirmed defect or gap | no |
| RELEASE_HANDOFF | prepare commit or release evidence | no |

Workflow selection must record:

- selected workflow class
- rejected alternatives
- selection rationale
- confidence
- clarification questions if confidence is insufficient
- escalation to cognition provider if deterministic selection is insufficient

No repository mutation is allowed during classification.

## 6. Development Proposal Lifecycle

Before mutation, ACLI must generate a development proposal.

Minimum proposal contents:

- resolved human intent
- target workflow class
- affected files or artifact families
- proposed change summary
- governance constraints
- replay requirements
- validation requirements
- risk assessment
- expected outputs
- rollback or stop conditions
- approval request

The proposal is not authority. The proposal becomes actionable only after explicit human approval.

The proposal may use cognition providers for analysis or drafting, but provider output remains non-authoritative.

## 7. Approval Continuity

Approvals are required before:

- repository mutation
- governance artifact creation
- runtime code modification
- test modification
- certification execution that writes evidence
- release handoff preparation
- destructive or irreversible operations

Approval continuity must preserve:

```text
development intent
-> proposal
-> approval request
-> human decision
-> authorization
-> mutation or fail-closed stop
```

Approval records must include:

- approval id
- proposal reference
- human decision
- approved scope
- approved files or artifact families
- approved validation plan
- approved execution limits
- timestamp
- replay reference

If the human denies approval, execution must stop and replay must record:

- denial
- reason if provided
- no mutation occurred

If the human modifies scope, ACLI must update the proposal and request confirmation again before mutation.

## 8. Repository Mutation Lifecycle

Repository mutation follows:

```text
Proposal
-> Approval
-> Authorization
-> Mutation
-> Validation
-> Replay
```

Required mutation rules:

- mutation must be bounded to approved scope
- mutation must use existing repository patterns
- unrelated files must not be changed
- user changes must not be reverted without explicit request
- generated evidence must remain secret-free
- protected governance boundaries must be preserved

Mutation records must include:

- authorization id
- changed files
- change type
- mutation worker or execution path
- scope conformance result
- rejected out-of-scope actions
- replay reference

Any mutation attempt outside the approved scope must fail closed.

## 9. Validation Continuity

Validation continuity follows:

```text
Development
-> Validation
-> Certification
```

Validation must be selected according to the touched surface:

| Touched surface | Minimum validation |
| --- | --- |
| documentation-only governance artifact | `git diff --check` |
| runtime Python module | targeted pytest and `py_compile` |
| certification runtime | targeted certification tests and artifact checks |
| replay model | replay reconstruction tests |
| provider or credential runtime | secret-safety and fail-closed tests |
| release handoff | changed-file and evidence summary checks |

Validation evidence must record:

- validation plan
- commands or checks selected
- command results
- failures
- skipped checks with reason
- certification verdict if applicable

Failed validation must not be hidden. ACLI may propose remediation, but it must not autonomously approve or execute remediation.

## 10. Replay Continuity

Replay must reconstruct the full development lifecycle:

```text
human request
-> clarification
-> repository context
-> workflow selection
-> proposal
-> approval
-> authorization
-> mutation
-> validation
-> outcome
-> release handoff if applicable
```

Replay evidence families:

- intent evidence
- clarification evidence
- repository context evidence
- workflow selection evidence
- proposal evidence
- approval evidence
- authorization evidence
- mutation evidence
- validation evidence
- outcome evidence
- release handoff evidence

Replay must be sufficient for a reviewer to answer:

- what did the human ask for?
- what context was used?
- why was this workflow selected?
- what was proposed?
- who approved it?
- what was authorized?
- what changed?
- what validation ran?
- what failed or passed?
- what evidence supports the result?

Replay remains the source of truth. Chat logs, provider responses, or local assumptions are not substitutes for replay records.

## 11. Git And Release Handoff

Git and release handoff occurs only after validation.

The handoff must produce:

- changed-file inventory
- approved scope comparison
- validation result summary
- known limitations
- evidence package references
- replay package references
- proposed commit message if requested
- release readiness status

The handoff must not imply automatic release or deployment.

Human approval remains required for:

- commit
- push
- release tagging
- deployment handoff
- publication of governed release artifacts

Release handoff must preserve existing release discipline:

```text
Local PC
-> innovation layer

GitHub
-> governed release registry

Server
-> stable governed runtime
```

## 12. Remaining Human Responsibilities

Humans remain responsible for:

- defining desired outcomes
- answering clarification questions
- approving proposals
- approving repository mutation
- approving destructive operations
- reviewing validation failures
- approving remediation scope
- approving release handoff
- deciding whether evidence is sufficient

Humans are not required to:

- know internal workflow identifiers
- manually package repository context
- write certification names
- select validation commands without assistance
- construct replay evidence manually

ACLI reduces orchestration burden. It does not remove human authority.

## 13. Fail-Closed Conditions

The governed development workflow must fail closed when:

- intent cannot be resolved
- repository context is insufficient
- workflow selection is ambiguous and unconfirmed
- proposed mutation lacks approval
- mutation exceeds approved scope
- validation plan is missing
- validation fails and no remediation is approved
- replay evidence cannot be recorded
- secret leakage is detected
- protected governance boundaries would be crossed
- release handoff lacks required evidence

Fail-closed output must explain:

- what stopped
- why it stopped
- what evidence exists
- what human decision is required next

## 14. Readiness Criteria

ACLI_GOVERNED_DEVELOPMENT_READY requires certification that ACLI can complete:

```text
Human development request
-> ACLI intake
-> clarification if needed
-> repository context acquisition
-> workflow selection
-> development proposal
-> human approval
-> authorization
-> repository mutation
-> validation
-> replay reconstruction
-> git/release handoff
```

Required certification assertions:

- development_intent_detected
- repository_context_acquired
- workflow_selected
- development_proposal_generated
- human_approval_requested
- human_approval_recorded
- authorization_issued
- mutation_scope_preserved
- validation_executed
- validation_result_recorded
- replay_reconstructed
- release_handoff_prepared
- authority_boundary_preserved
- secret_free_evidence

Minimum scenario coverage:

- documentation-only governance artifact creation
- runtime code change
- test addition
- certification execution
- failed validation
- remediation proposal
- approval denial
- approval scope modification
- git handoff preparation

## 15. Certification Target

The future certification target is:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

This artifact does not claim readiness. It defines the workflow required to certify readiness.

Final verdict:

```text
ACLI_GOVERNED_DEVELOPMENT_WORKFLOW_V1_DEFINED
```
