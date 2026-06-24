# GOVERNANCE_ARTIFACT_UNIFICATION_V1

Status: Ready

Purpose: Determine how standard operator governance-artifact requests should enter the complete ACLI governed development lifecycle.

Target verdict:

```text
GOVERNANCE_ARTIFACT_UNIFICATION_READY
```

## 1. Context

`CONVERSATIONAL_WORKFLOW_COVERAGE_AUDIT_V1` found that `GOVERNED_DEVELOPMENT_WORKFLOW` is the only complete operator-facing ACLI lifecycle.

It supports:

- routing;
- proposal;
- approval;
- human-friendly explanation;
- execution;
- validation;
- replay.

The same audit found that `GOVERNANCE_ARTIFACT_CREATION` routes successfully but fails before proposal in the interactive ACLI loop:

```text
unsupported conversational workflow selection: GOVERNANCE_ARTIFACT_CREATION
```

## 2. Routing Analysis

Governance-artifact routing is currently detected in:

```text
aigol/runtime/conversational_cli_runtime.py:906
```

The classifier recognizes phrases such as:

```text
create governance artifact
add governance artifact
draft governance artifact
prepare certification artifact
create governance doc
```

When matched, routing selects:

```text
GOVERNANCE_ARTIFACT_CREATION
```

Selection occurs before the generic governed-development classifier:

```text
aigol/runtime/conversational_cli_runtime.py:557
GOVERNANCE_ARTIFACT_CREATION

aigol/runtime/conversational_cli_runtime.py:571
GOVERNED_DEVELOPMENT_WORKFLOW
```

Existing routing tests intentionally assert route-only behavior:

```text
tests/test_conversational_cli_runtime_v1.py:158
test_governance_artifact_creation_prompt_routes_without_execution

tests/test_conversational_cli_runtime_v1.py:171
test_audited_governance_artifact_prompt_routes_to_governance_artifact_creation

tests/test_conversational_cli_runtime_v1.py:191
test_governance_artifact_phrase_expansion_routes_without_execution
```

Those tests matched the earlier architecture, where `GOVERNANCE_ARTIFACT_CREATION` was a certified workflow selection but not an operator-facing execution bridge.

## 3. Lifecycle Analysis

### 3.1 Current Governance Artifact Lifecycle

Current operator prompt:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices for using ACLI as the primary development interface.
```

Current ACLI lifecycle:

```text
Human Prompt
-> HIRR / routing
-> GOVERNANCE_ARTIFACT_CREATION
-> unsupported interactive branch
-> fail closed
```

Current support:

- routing: yes;
- proposal: no;
- approval: no;
- human-friendly explanation: no;
- execution: no;
- validation: no;
- replay: routing/intake replay only.

### 3.2 Complete Governed Development Lifecycle

Current governed-development lifecycle:

```text
Human Prompt
-> HIRR / routing
-> GOVERNED_DEVELOPMENT_WORKFLOW
-> proposal
-> human-friendly explanation
-> approval
-> execution
-> repository mutation
-> validation
-> replay
```

Current support:

- routing: yes;
- proposal: yes;
- approval: yes;
- human-friendly explanation: yes;
- execution: yes;
- validation: yes;
- replay: yes.

### 3.3 Lifecycle Mismatch

The operator phrase "create governance artifact" implies repository artifact creation.

In the current interactive ACLI runtime, direct `GOVERNANCE_ARTIFACT_CREATION` selection cannot satisfy that implication.

Therefore standard operator-facing governance-artifact requests should not remain routed to a branch that fails before proposal.

## 4. Decision

Standard operator governance-artifact creation requests should be normalized into:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

This unifies the operator experience under the only complete certified lifecycle while preserving existing governance boundaries.

## 5. Rationale

### 5.1 Avoid Duplicate Conversational Bridges

Creating a dedicated `GOVERNANCE_ARTIFACT_CREATION` conversational bridge would duplicate:

- proposal generation;
- approval capture;
- explanation rendering;
- replay binding;
- validation;
- fail-closed behavior.

Those behaviors already exist in the governed development bridge.

### 5.2 Preserve Approval Boundaries

`GOVERNED_DEVELOPMENT_WORKFLOW` already requires explicit approval before mutation.

It preserves:

- proposal hash binding;
- `APPROVE` boundary;
- rejection without mutation;
- no worker invocation before approval.

### 5.3 Preserve Replay Lineage

The governed-development bridge already records:

- routing replay;
- proposal replay;
- approval replay;
- governed workflow replay;
- validation replay;
- replay reconstruction evidence.

### 5.4 Preserve Validation

The governed-development path already invokes allowlisted validation.

### 5.5 Preserve Explanation Layer

The human-friendly explanation layer is already integrated at the governed-development proposal point.

Routing governance-artifact operator requests into this lifecycle immediately gives the operator:

- what ACLI understood;
- what will happen;
- what will not happen;
- why approval is required;
- what to type next;
- replay visibility.

## 6. Boundary Conditions

This unification applies to standard operator-facing ACLI prompts such as:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices for using ACLI as the primary development interface.
Add governance artifact TEST_ACLI_BRIDGE_V1 documenting that ACLI execution bridge was successfully tested.
Write governance artifact TEST_ACLI_BRIDGE_V1.
```

This unification does not remove the lower-level `governance_artifact_creation_runtime`.

The lower-level runtime remains usable as an internal component of governed development and direct runtime tests.

## 7. Implementation Plan

### 7.1 Routing Change

Update `aigol/runtime/conversational_cli_runtime.py`.

Change standard governance-artifact creation prompt classification from:

```text
GOVERNANCE_ARTIFACT_CREATION
```

to:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

Preserve matched signal evidence such as:

```text
create
governance
artifact
```

Recommended operator summary:

```text
Route governance artifact creation through the governed development workflow so proposal, approval, validation, explanation, and replay are preserved.
```

### 7.2 Optional Internal Workflow Preservation

Keep `GOVERNANCE_ARTIFACT_CREATION` in `workflow_registry()` as an internal component workflow.

Do not present it as the standard interactive operator route unless a dedicated conversational bridge is added later.

### 7.3 Test Updates

Update routing tests that currently assert:

```text
workflow_id == GOVERNANCE_ARTIFACT_CREATION
```

for standard operator prompts.

Expected new assertion:

```text
workflow_id == GOVERNED_DEVELOPMENT_WORKFLOW
```

Preserve registry test proving `GOVERNANCE_ARTIFACT_CREATION` remains registered.

### 7.4 End-To-End Regression

Add or update an interactive ACLI test for:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices for using ACLI as the primary development interface.
```

Expected:

- routes to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- renders human-friendly explanation;
- requires approval;
- `APPROVE` executes;
- validation runs;
- replay reconstructs;
- no `unsupported conversational workflow selection` appears.

## 8. Regression Plan

Required tests:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py -q
python -m pytest tests/test_acli_governed_development_execution_bridge_v1.py -q
python -m pytest tests/test_acli_human_friendly_explanation_runtime_v1.py -q
git diff --check
```

Regression assertions:

- standard governance-artifact operator prompts route to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- `GOVERNANCE_ARTIFACT_CREATION` remains registered;
- no provider is invoked during routing;
- no worker is invoked before approval;
- no execution is requested during routing;
- approval is required before mutation;
- human-friendly explanation renders before approval;
- replay reconstructs after execution.

## 9. Risk Assessment

### Risk 1: Requested Artifact Name Preservation

The existing governed-development bridge may generate bounded artifact names rather than preserving exact requested artifact names such as:

```text
ACLI_USAGE_GUIDELINES_V1
```

This is a proposal-generation quality issue, not a routing unification blocker.

Mitigation:

- preserve the original prompt in the request artifact;
- improve proposal generation in a later scoped change if exact artifact naming becomes required.

### Risk 2: Internal Runtime Visibility

Keeping `GOVERNANCE_ARTIFACT_CREATION` registered while not routing standard operator prompts to it may confuse audits.

Mitigation:

- document it as an internal component workflow unless a dedicated bridge is added.

### Risk 3: Regression In Existing Route-Only Tests

Existing route-only tests will need to change.

Mitigation:

- preserve one registry-level test for `GOVERNANCE_ARTIFACT_CREATION`;
- update operator prompt tests to assert the complete governed-development lifecycle.

## 10. Final Recommendation

Do not create a duplicate conversational bridge for `GOVERNANCE_ARTIFACT_CREATION` at this time.

Normalize standard operator governance-artifact prompts into:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

Use the existing complete lifecycle to preserve:

- approval boundaries;
- replay lineage;
- validation;
- fail-closed behavior;
- human-friendly explanation.

## 11. Final Verdict

```text
GOVERNANCE_ARTIFACT_UNIFICATION_READY
```
