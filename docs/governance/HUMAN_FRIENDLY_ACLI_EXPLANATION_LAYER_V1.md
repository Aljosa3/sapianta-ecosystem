# HUMAN_FRIENDLY_ACLI_EXPLANATION_LAYER_V1

Status: Ready

Purpose: Define a human-friendly ACLI explanation layer that helps operators understand certified routing and approval state without changing governance behavior.

Target verdict:

```text
HUMAN_FRIENDLY_ACLI_EXPLANATION_READY
```

## 1. Problem Statement

ACLI now understands human prompts well enough to route, propose, approve, execute, validate, and persist replay evidence through certified governed development paths.

The remaining usability gap is operator comprehension.

Current ACLI output can be technically correct while still difficult for a normal operator to interpret:

```text
ROUTING DECISION
workflow: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
confidence: HIGH

Intent Family: GENERAL_IMPROVEMENT_INTENT
Selected Workflow: OCS_LLM_COGNITION

Current Lifecycle Stage: APPROVAL
```

The operator needs a plain-language explanation of what ACLI understood, what will happen if approval is granted, what will not happen before approval, and where replay evidence will be visible.

## 2. Architecture Review

The explanation layer belongs after deterministic routing and before any approval decision is requested.

It must consume already-created runtime artifacts:

- human prompt capture;
- HIRR or routing decision artifacts;
- workflow selection artifacts;
- routing visibility artifacts;
- universal intake artifacts;
- proposal artifacts when available;
- replay references already created for the turn.

It must not:

- classify intent;
- select workflows;
- override workflow selection;
- approve execution;
- trigger providers;
- invoke workers;
- mutate repository state;
- mutate governance artifacts;
- bypass fail-closed checks.

The explanation is an operator-facing derived view over certified artifacts. It is not an authority layer.

## 3. Runtime Design

The proposed runtime component is:

```text
aigol/runtime/acli_human_friendly_explanation_runtime.py
```

The runtime should expose:

```text
create_acli_human_friendly_explanation(...)
render_acli_human_friendly_explanation(...)
reconstruct_acli_human_friendly_explanation_replay(...)
```

The explanation artifact should be recorded under each turn:

```text
TURN-000001/human_friendly_explanation/
```

The CLI should render this explanation after routing visibility and before proposal approval instructions.

For governed development proposal turns, the output order should be:

```text
ROUTING DECISION
HUMAN-FRIENDLY EXPLANATION
Governed Development Proposal
```

For clarification turns, the output order should be:

```text
ROUTING DECISION
HUMAN-FRIENDLY EXPLANATION
Clarification Questions
```

For fail-closed turns, the explanation may render only if enough certified context exists. It must not invent missing intent or imply that execution is available.

## 4. Determinism Requirement

The explanation must be deterministic by default.

Inputs should be structured artifact fields, not freeform model completion:

- `workflow_id`;
- `intent_family`;
- `selected_workflow`;
- `approval_required`;
- `target_paths`;
- `provider_invoked`;
- `worker_invoked`;
- `mutation_performed`;
- `validation_executed`;
- `replay_reference`;
- proposal title or artifact name when available.

If a field is unavailable, the explanation must say that the detail is not yet available rather than guessing.

## 5. OCS Cognition Provider Role

OCS cognition may be used only as an optional explanation refinement provider after deterministic explanation generation exists.

Provider-backed explanation must be constrained:

- provider output is advisory text only;
- provider output cannot alter routing;
- provider output cannot alter approval state;
- provider output cannot alter proposal content;
- provider output cannot trigger execution;
- provider output must be replayed if displayed;
- malformed provider explanation fails closed to the deterministic explanation.

The initial implementation should not require OCS cognition. Deterministic explanation is sufficient for Product 1 demo readiness.

## 6. Required Explanation Sections

### 6.1 What I Understood

Purpose: translate routing and proposal fields into plain language.

Example:

```text
WHAT I UNDERSTOOD

I understood that you want to create or update governed repository artifacts related to:

Add replay validation

Selected workflow:

GOVERNED_DEVELOPMENT_WORKFLOW
```

When a governance artifact name is available:

```text
I understood that you want to create a governance artifact named:

ACLI_USAGE_GUIDELINES_V1

Purpose:

Document recommended operator practices for using ACLI as the primary development interface.
```

### 6.2 What Will Happen

Purpose: explain approved next effects.

Example:

```text
WHAT WILL HAPPEN

If approved:

- a governed proposal will be used
- repository artifacts may be created or modified
- validation will run
- replay evidence will be recorded
```

### 6.3 What Will Not Happen

Purpose: make boundaries visible.

Example:

```text
WHAT WILL NOT HAPPEN

- no worker will execute before approval
- no repository mutation will occur before approval
- no provider will be invoked unless required by the selected workflow
- ACLI will not treat provider output as authority
```

### 6.4 What Requires Your Approval

Purpose: explain why the operator must act.

Example:

```text
WHAT REQUIRES YOUR APPROVAL

Approval is required because the selected workflow may create or modify repository artifacts.

Approval binds to the proposal hash. A changed proposal requires a new approval.
```

### 6.5 What To Type Next

Purpose: reduce command uncertainty.

Example:

```text
WHAT TO TYPE NEXT

Type:

APPROVE

to continue.

Type:

REJECT

to cancel.
```

When modifications are supported:

```text
Type:

REQUEST_MODIFICATION

to stop execution and request changes.
```

### 6.6 Replay Visibility

Purpose: show where evidence will be found.

Example:

```text
REPLAY VISIBILITY

Replay evidence will be available after execution.

Replay location:

runtime/demo/SESSION/TURN-000001/acli_governed_development_execution_bridge/
```

If replay exists at explanation time:

```text
Replay evidence already recorded for this turn:

runtime/demo/SESSION/TURN-000001/human_friendly_explanation/
```

## 7. Replay Impact

The explanation layer should persist a visibility-only artifact.

Required artifact properties:

- `artifact_type`: `ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1`
- `visibility_only`: `true`
- `authority_granted`: `false`
- `provider_authority`: `false`
- `approval_authority`: `false`
- `execution_authority`: `false`
- `worker_authority`: `false`
- source artifact references and hashes
- rendered explanation hash
- replay reference

Replay reconstruction must verify:

- wrapper hash;
- artifact hash;
- source artifact references;
- source artifact hashes when available;
- rendered explanation hash.

Replay remains source of truth. The explanation is review evidence, not execution evidence.

## 8. Approval Impact

The explanation layer must make approval clearer without changing approval.

It may say:

- approval is required;
- approval binds to the current proposal hash;
- mutation will not occur before approval;
- `APPROVE`, `REJECT`, and `REQUEST_MODIFICATION` are valid next actions where supported.

It must not:

- approve on behalf of the human;
- infer approval from conversational tone;
- weaken exact approval token requirements;
- change approval artifacts;
- change proposal hash binding;
- execute after explanation alone.

Human remains the authority layer.

## 9. Fail-Closed Behavior

The explanation layer fails closed as a presentation component.

If explanation generation cannot validate its inputs:

- execution must not be authorized by the explanation;
- routing and workflow behavior must remain unchanged;
- the CLI may render a compact technical fallback if existing artifacts are valid;
- malformed explanation artifacts must not be replayed as valid evidence.

If explanation rendering fails after the governed proposal exists, ACLI should either:

- omit the explanation and continue showing the existing certified proposal summary; or
- fail closed only if the implementation treats explanation replay as mandatory for that workflow.

The recommended initial behavior is non-blocking visibility: explanation failure must not create authority, and must not hide existing governance summaries.

## 10. Implementation Plan

### P0 Runtime

Create `aigol/runtime/acli_human_friendly_explanation_runtime.py`.

Implement:

- artifact creation;
- deterministic section generation;
- renderer;
- replay persistence;
- replay reconstruction;
- strict validation of source references.

### P0 CLI Integration

Update `aigol/cli/aigol_cli.py`.

Insert explanation rendering after routing visibility is recorded and after enough workflow/proposal context exists.

Minimum first integration:

- governed development proposal turns;
- governed development approval-continuation turns;
- clarification turns where workflow selection is visible.

### P0 Tests

Add focused tests:

- deterministic artifact creation;
- rendering includes all required sections;
- explanation is visibility-only and non-authoritative;
- replay reconstruction detects tampering;
- governed development proposal output includes explanation before approval prompt;
- explanation failure does not bypass approval.

### P1 Coverage

Extend explanation support to:

- OCS cognition turns;
- domain clarification turns;
- fail-closed routing turns;
- replay inspection summaries.

### P2 Optional Provider Refinement

Add optional provider-assisted wording refinement only after deterministic explanation is stable.

Provider refinement must remain advisory and replayed.

## 11. Regression Plan

Required regression commands:

```bash
python -m pytest tests/test_acli_human_friendly_explanation_runtime_v1.py -q
python -m pytest tests/test_acli_governed_development_execution_bridge_v1.py -q
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_human_execution_intent_detection_v1.py -q
git diff --check
```

Regression assertions:

- explanation renders `WHAT I UNDERSTOOD`;
- explanation renders `WHAT WILL HAPPEN`;
- explanation renders `WHAT WILL NOT HAPPEN`;
- explanation renders `WHAT REQUIRES YOUR APPROVAL`;
- explanation renders `WHAT TO TYPE NEXT`;
- explanation renders `REPLAY VISIBILITY`;
- explanation has no authority fields set to true;
- approval is still required before mutation;
- worker is not invoked before approval;
- repository mutation is not performed before approval;
- replay evidence is persisted and reconstructable.

## 12. Constitutional Preservation

This design preserves:

- HIRR;
- deterministic routing;
- governance boundaries;
- approval boundaries;
- replay;
- fail-closed behavior;
- proposal hash binding;
- worker protections;
- validation allowlists;
- Human = Authority;
- Replay = Source Of Truth;
- LLM proposes. AiGOL governs. Worker executes. Replay records.

## 13. Final Verdict

```text
HUMAN_FRIENDLY_ACLI_EXPLANATION_READY
```
