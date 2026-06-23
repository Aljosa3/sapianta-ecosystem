# GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1

Status: Defined

Scope: Runtime implementation architecture for the first ACLI governed development workflow.

Governing workflow:

- GOVERNANCE_ARTIFACT_CREATION_WORKFLOW_V1

Runtime dependencies:

- ACLI_WORKFLOW_INVOCATION_RUNTIME_V1
- ACLI_REPOSITORY_CONTEXT_RUNTIME_V1
- ACLI_VALIDATION_RUNTIME_V1
- ACLI_DEVELOPMENT_REPLAY_RUNTIME_V1
- ACLI_EVIDENCE_CONTINUITY_RUNTIME_MAPPING_V1

Runtime verdict:

```text
RUNTIME_DEFINED
```

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1_DEFINED
```

## 1. Runtime Purpose

This runtime defines the implementation architecture for the `GOVERNANCE_ARTIFACT_CREATION` ACLI workflow.

Runtime responsibility:

```text
accept resolved governance artifact creation intent
-> invoke the registered workflow
-> acquire repository context
-> generate a proposal
-> require explicit human approval
-> create only the approved governance artifact
-> run validation
-> persist replay evidence
-> fail closed on missing or invalid evidence
```

This runtime is the narrowest governed development implementation path. It does not implement generic repository mutation, runtime code changes, test changes, release handoff, deployment, or autonomous governance mutation.

## 2. Inputs

Required runtime inputs:

| Input | Requirement |
| --- | --- |
| Original human request | Preserved exactly or by replay-safe reference. |
| HIRR / resolved intent artifact | Must resolve to governance artifact creation. |
| Workflow invocation artifact | Must select `GOVERNANCE_ARTIFACT_CREATION`. |
| Repository context artifact | Must identify target directory, conflicts, and governing constraints. |
| Governance context reference | Must identify applicable governance boundaries. |
| Proposal artifact | Must define target path, title, scope, and validation plan. |
| Human approval artifact | Must explicitly approve path, scope, and mutation. |
| Replay chain reference | Must anchor all runtime evidence. |

Conditionally required inputs:

- clarification artifacts when HIRR required clarification
- existing artifact references when the proposed artifact is related to prior governance lineage
- dirty worktree summary when uncommitted changes exist
- validation policy reference when additional validation beyond `git diff --check` is required

Invalid inputs:

- implied approval
- unresolved intent
- unregistered workflow selection
- target path outside approved governance scope
- proposal without mutation limits
- approval without replay reference
- stale repository context

## 3. Workflow Invocation

The runtime must be reachable only through an explicit ACLI workflow registration.

Required workflow registry entry:

```text
workflow_id: GOVERNANCE_ARTIFACT_CREATION
workflow_class: governed_development
workflow_scope: governance_artifact_creation
mutation_allowed_before_approval: false
approval_required: true
validation_required: true
replay_required: true
```

Invocation requirements:

- workflow selection must be deterministic
- selected workflow must be replay-visible
- rejected candidate workflows must be recorded when available
- invocation must not itself mutate the repository
- invocation must not imply approval
- invocation must fail closed when the resolved intent is broader than governance artifact creation

Minimum runtime entrypoint shape:

```text
invoke_governance_artifact_creation(request, resolved_intent, replay_ref)
```

The runtime may use existing ACLI routing and HIRR components, but it must not redesign them.

## 4. Repository Context

Repository context must be acquired before proposal finalization.

Required context facts:

- repository root
- current working tree status
- target path under `docs/governance/`
- target file existence or absence
- nearby governance artifacts
- naming conflict assessment
- mutation boundary assessment
- validation expectations

Required context artifact fields:

- context id
- acquisition timestamp
- inspected paths
- target path assessment
- conflict status
- dirty worktree status
- governance boundary status
- freshness status
- replay reference

The runtime must not proceed to proposal approval when repository context is missing, stale, contradictory, or insufficient.

## 5. Proposal Generation

The runtime must generate a proposal before mutation.

Proposal generation may use local deterministic templates or cognition-assisted drafting, but generated content is not authority.

Minimum proposal fields:

- proposal id
- original request reference
- resolved intent reference
- selected workflow id
- proposed artifact path
- proposed artifact title
- artifact purpose
- required scope sections
- mutation summary
- validation plan
- replay plan
- known risks
- approval request

Proposal rules:

- proposal must be persisted before approval
- proposal must not write the target artifact
- proposal must identify all files expected to change
- proposal must state that no mutation occurs before approval
- proposal must fail closed if proposed scope exceeds governance artifact creation

## 6. Human Approval

Human approval is mandatory.

Approval integration must record:

- approval id
- proposal id
- approving human/operator reference
- decision
- approved path
- approved scope
- approved mutation limits
- approved validation plan
- timestamp
- replay reference

Allowed approval decisions:

```text
APPROVED
REJECTED
NEEDS_CLARIFICATION
```

Only `APPROVED` permits artifact creation.

The runtime must fail closed when:

- approval is absent
- approval is ambiguous
- approval references a different proposal
- approval scope differs from proposed mutation
- approval is stale after repository context changes

## 7. Repository Mutation

Repository mutation is limited to creation of one approved governance markdown artifact.

Allowed mutation:

```text
create approved file under docs/governance/
```

Mutation preconditions:

- resolved intent exists
- workflow invocation selected `GOVERNANCE_ARTIFACT_CREATION`
- repository context is fresh
- proposal is persisted
- human approval is explicit
- target path matches approval
- replay reference exists

Mutation output:

- mutation id
- target path
- before-state status
- after-state status
- content hash when available
- changed-file summary
- replay reference

Forbidden mutation:

- modifying runtime code
- modifying tests
- modifying release artifacts
- modifying replay history
- deleting files
- editing unrelated files
- writing outside approved path
- broad repository mutation
- server or deployment mutation

Any mutation scope mismatch must produce fail-closed termination.

## 8. Validation

Validation is mandatory after artifact creation.

Minimum validation command:

```bash
git diff --check
```

Validation must record:

- validation id
- command
- execution timestamp
- exit code
- output summary
- changed files
- pass or fail status
- replay reference

Validation behavior:

| Validation status | Runtime behavior |
| --- | --- |
| PASS | Continue to replay completion evidence. |
| FAIL | Fail closed and persist validation failure evidence. |
| NOT_RUN | Fail closed unless explicitly recorded as unavailable for human review. |

Additional validation may be required by governance conformance policy, but the runtime must not silently replace the mandatory minimum validation.

## 9. Replay

Replay persistence is mandatory.

The runtime must persist or link replay evidence for:

- original request
- HIRR / resolved intent
- workflow invocation
- repository context
- proposal
- approval
- mutation
- validation
- final outcome

Minimum replay package shape:

```text
replay/
  manifest.json
  intent_ref.json
  workflow_ref.json
  context_ref.json
  proposal_ref.json
  approval_ref.json
  mutation_ref.json
  validation_ref.json
  outcome.json
```

Replay reconstruction must answer:

- what was requested
- what intent was resolved
- why the workflow was selected
- what context was inspected
- what was proposed
- what was approved
- what file was created
- what validation ran
- whether the workflow completed or failed closed

Replay failure prevents successful workflow completion.

## 10. Failure Handling

The runtime is fail-closed.

Required fail-closed conditions:

| Condition | Required status |
| --- | --- |
| Intent unresolved | `FAIL_CLOSED_UNRESOLVED_INTENT` |
| Workflow not selected | `FAIL_CLOSED_NO_WORKFLOW_SELECTION` |
| Workflow not registered | `FAIL_CLOSED_WORKFLOW_NOT_REGISTERED` |
| Context missing or stale | `FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT` |
| Proposal missing | `FAIL_CLOSED_NO_PROPOSAL` |
| Approval missing or rejected | `FAIL_CLOSED_NO_APPROVAL` |
| Approval scope mismatch | `FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH` |
| Target path outside scope | `FAIL_CLOSED_SCOPE_VIOLATION` |
| Mutation error | `FAIL_CLOSED_MUTATION_FAILED` |
| Validation failure | `FAIL_CLOSED_VALIDATION_FAILED` |
| Replay incomplete | `FAIL_CLOSED_REPLAY_INCOMPLETE` |

Failure records must include:

- failure id
- failed stage
- reason
- evidence references available at failure time
- whether mutation occurred
- replay reference
- required human review status

Failure must not be hidden, retried silently, or reframed as success.

## 11. Runtime Boundaries

This runtime may not:

- redesign HIRR
- redesign replay
- create generic governed development execution
- infer approval from intent
- mutate before approval
- write outside the approved governance artifact path
- modify runtime code
- modify tests
- mutate release artifacts
- mutate replay history
- perform deployment or server changes
- claim `ACLI_GOVERNED_DEVELOPMENT_READY`
- fabricate evidence

This runtime may:

- register a narrow workflow entry
- consume resolved HIRR evidence
- acquire repository context
- generate and persist a proposal
- record explicit approval
- create one approved governance artifact
- run validation
- persist replay evidence
- produce reviewable completion or fail-closed evidence

Implementation footprint should remain minimal:

```text
workflow registry entry
workflow selection mapping
governance artifact creation runtime module
evidence persistence helpers
validation runner integration
replay manifest integration
focused tests
```

## 12. Final Verdict

Final runtime verdict:

```text
RUNTIME_DEFINED
```

Rationale:

The runtime architecture defines the minimal executable bridge from ACLI workflow invocation to bounded governance artifact creation. It uses existing ACLI concepts, preserves HIRR and replay boundaries, requires explicit human approval, limits mutation to one approved governance artifact, requires validation, and fails closed on missing evidence or scope mismatch.

This artifact defines runtime architecture only. It does not claim implementation exists or that ACLI governed development is ready.

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1_DEFINED
```
