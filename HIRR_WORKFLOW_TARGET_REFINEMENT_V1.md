# HIRR_WORKFLOW_TARGET_REFINEMENT_V1

Status: design.

## Objective

When an ambiguous human prompt is clarified by the operator, ACLI must recompute workflow target selection from the clarified intent instead of preserving the first-turn workflow target.

This design uses existing ACLI, Universal Intake, Human Intent Resolution, OCS Cognition, and replay architecture. It does not introduce a new governance layer.

## 1. Root Cause Analysis

Real-world dogfood evidence in `AIGOL_HIRR_REAL_WORLD_DOGFOOD_V1.md` showed:

```text
REAL_PROMPTS_TESTED = 10
MISROUTINGS = 4
FAILED_CLOSED = 1
HIRR_REAL_WORLD_SUCCESS_RATE = 50
```

The advisory misrouting cases had the same shape:

```text
Human prompt
-> HUMAN_INTENT_CLARIFICATION_INTAKE
-> AMBIGUOUS_INTENT
-> expected_workflow_targets = [CREATE_DOMAIN_COMPLIANCE_CLARIFICATION]
-> operator clarification says advisory / planning / no implementation
-> HUMAN_INTENT_CLARIFICATION_CONTINUITY
-> selected workflow remains CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

The implementation cause is localized:

- `human_intent_clarification_intake_runtime.py` assigns `AMBIGUOUS_INTENT` to `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`.
- `human_intent_clarification_continuity_runtime.py` reads `expected_workflow_targets` from the original clarification request.
- `_selected_workflow_id(request)` selects the first stored target and does not inspect the clarification response.
- `HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1` records the preserved target as resolved intent.
- `HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1` records that same target as selected workflow.

This is continuity-safe but not intent-correct after clarification.

The failed-closed OCS case is adjacent but separate:

```text
OCS_LLM_COGNITION selected correctly
-> cognition comparison failed closed: at least two cognition artifacts are required for comparison
```

That is an OCS cognition runtime readiness issue, not the advisory misrouting root cause.

## 2. Proposed Architecture Changes

Add a deterministic target refinement step inside the existing human-intent clarification continuity runtime:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
-> WAITING_FOR_OPERATOR
-> Human clarification response
-> HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1
-> HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1
-> HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1
-> HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1
-> HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1
```

The refinement step should evaluate:

- original prompt intent family;
- original expected workflow targets;
- clarification response text;
- deterministic response signals;
- supported target workflows.

It must output one refined workflow target:

```text
OCS_LLM_COGNITION
```

or:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

The refinement must remain passive. It must not invoke provider, worker, authorization, PPP, execution, governance mutation, or replay mutation.

## 3. Replay-Visible Artifacts Affected

Existing artifacts to preserve:

- `HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1`
- `HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1`
- `HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1`
- `HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1`
- `UNIVERSAL_INTAKE_ARTIFACT_V1`
- `CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1`

New replay-visible artifact:

```text
HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1
```

Required fields:

```text
artifact_type
runtime_version
refinement_id
clarification_request_reference
clarification_request_hash
clarification_response_reference
clarification_response_hash
original_intent_family
original_expected_workflow_targets
clarification_response_signals
refined_intent_family
refined_workflow_targets
selected_workflow_id
refinement_status
refinement_reason
canonical_chain_id
created_at
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
governance_mutated = false
replay_mutated = false
failure_reason
artifact_hash
```

Replay step insertion:

```text
000_human_intent_clarification_reply_binding_recorded.json
001_human_intent_clarification_response_recorded.json
002_human_intent_workflow_target_refinement_recorded.json
003_human_intent_clarification_resolution_recorded.json
004_human_intent_workflow_selection_after_clarification_recorded.json
```

The reconstruction function should verify all five wrappers in order.

## 4. Required Runtime Modifications

### `aigol/runtime/human_intent_clarification_continuity_runtime.py`

Add constants:

```text
HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1
WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION
```

Add a refinement function:

```text
_refined_workflow_target(request, clarification_response) -> refinement decision
```

Use the refinement decision in:

- `_resolution_artifact(...)`
- `_selection_artifact(...)`
- `_capture(...)`
- `render_human_intent_clarification_continuity_summary(...)`
- `reconstruct_human_intent_clarification_continuity_replay(...)`

Replace current selection flow:

```text
_selected_workflow_id(request)
```

with:

```text
_selected_workflow_id(refinement)
```

Keep `_selected_workflow_id(request)` only as validation of original target availability, or rename it to `_initial_workflow_target(request)`.

### Deterministic Signal Rules

Advisory / OCS refinement signals:

```text
advisory
guidance
planning
recommend
recommendation
analyze
how should we
reduce risk
safer
understand
explain
wording
before implementation
do not start implementation
no implementation
without execution
first step
next safest
```

Governed workflow signals:

```text
governed workflow
workflow proposal
implementation proposal
evidence model
collect evidence
audit evidence
approval criteria
review before use
controlled workflow
create a governed
start with a governed
```

Refinement priority:

1. If governed workflow signals are present, select `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`.
2. If advisory / OCS signals are present and no governed workflow signal is present, select `OCS_LLM_COGNITION`.
3. If both signal groups are present, select `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` unless explicit no-execution language is present.
4. If no refinement signal is present, preserve the original first-turn target.
5. If the refined target is not in `SUPPORTED_TARGET_WORKFLOWS`, fail closed.

### Universal Intake

No Universal Intake redesign is required.

Universal Intake should continue to record a passive artifact after the selected workflow is known. Once the continuity runtime emits the refined selected workflow, the existing Universal Intake classification should naturally classify:

```text
OCS_LLM_COGNITION -> OCS_COGNITION_INTAKE
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION -> DOMAIN_INTAKE
```

If the current ACLI dispatch does not attach Universal Intake to clarification-continuation turns after refinement, the implementation should only wire the existing `record_universal_intake(...)` call to the refined workflow selection. It should not add new intake authority.

### OCS Cognition

This design does not repair OCS cognition fail-closed behavior.

The direct OCS failure should remain visible as a separate downstream blocker:

```text
cognition comparison failed closed: at least two cognition artifacts are required for comparison
```

Target refinement success means ACLI selected `OCS_LLM_COGNITION` correctly. OCS runtime completion is a separate certification question.

## 5. Acceptance Criteria

Functional acceptance:

- ambiguous first-turn prompts still return `CLARIFICATION_REQUIRED`;
- clarification state remains persisted;
- next human response is bound as clarification response;
- workflow target is recomputed from original prompt plus clarification response;
- ambiguous-to-advisory clarification selects `OCS_LLM_COGNITION`;
- ambiguous-to-governed-workflow clarification selects `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`;
- advisory first-turn prompts continue to select `OCS_LLM_COGNITION`;
- governed implementation/evidence prompts continue to select `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`;
- no provider invocation is introduced by target refinement;
- no worker invocation is introduced by target refinement;
- no authorization is created by target refinement;
- no execution is requested by target refinement.

Evidence acceptance:

- target refinement artifact is present in replay;
- resolution artifact references the refinement artifact and hash;
- workflow selection artifact references the refinement artifact and hash;
- replay reconstruction verifies the new step ordering;
- rendered summary includes the refined workflow target and refinement reason.

Dogfood acceptance:

- the four advisory misrouting cases from `AIGOL_HIRR_REAL_WORLD_DOGFOOD_V1` select `OCS_LLM_COGNITION`;
- the five governed workflow cases still select `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`;
- `FAILED_CLOSED` count for target refinement is zero for the dogfood set;
- human corrections required for advisory misrouting cases drop from 4 to 0.

## 6. Certification Criteria

Required tests:

- unit test for advisory refinement from `AMBIGUOUS_INTENT`;
- unit test for governed workflow refinement from `AMBIGUOUS_INTENT`;
- regression test for `GENERAL_IMPROVEMENT_INTENT` first-turn advisory target;
- regression test for existing business goal, automation, compliance, and ambiguous governed-flow cases;
- replay reconstruction test for five-step HIRR continuity replay;
- fail-closed test for unsupported refined target;
- fail-closed test for missing clarification response;
- fail-closed test for missing original expected workflow targets.

Required dogfood certification:

```text
REAL_PROMPTS_TESTED >= 10
ADVISORY_MISROUTINGS = 0
FAILED_CLOSED_IN_REFINEMENT = 0
HUMAN_CORRECTIONS_REQUIRED <= 1
HIRR_REAL_WORLD_SUCCESS_RATE >= 90
```

Required validation commands:

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py
git diff --check
```

If OCS cognition completion is also evaluated, OCS fail-closed behavior must be reported separately from target refinement.

## 7. Fail-Closed Behavior Requirements

The refinement runtime must fail closed when:

- active clarification state is missing;
- active clarification belongs to a different workflow;
- chain identity mismatches;
- clarification request artifact is missing or malformed;
- clarification response is missing or blank;
- original expected workflow targets are missing;
- refined workflow target is unsupported;
- artifact hash verification fails;
- replay step already exists;
- replay reconstruction order mismatches;
- replay reconstruction hash verification fails.

The refinement runtime must not fail closed merely because the response is low confidence. Low-confidence response behavior should preserve the original target and record:

```text
refinement_status = TARGET_PRESERVED_LOW_CONFIDENCE
```

Policy or safety violations remain eligible for existing fail-closed behavior, but this design does not introduce new policy authority.

## 8. Minimal Implementation Plan

1. Add `HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1` to `human_intent_clarification_continuity_runtime.py`.
2. Insert a new replay step between response and resolution.
3. Implement deterministic `_target_refinement_artifact(...)` using existing string-signal helpers or local helpers.
4. Update `_resolution_artifact(...)` to reference refinement and record `selected_workflow_id` from refinement.
5. Update `_selection_artifact(...)` to reference refinement and record `workflow_id` from refinement.
6. Update replay reconstruction to verify five steps.
7. Update rendered summary to include:

```text
Selected Workflow: <workflow>
Workflow Target Refinement: <status>
Refinement Reason: <reason>
```

8. Add focused tests for the dogfood failures and existing HIRR successes.
9. Re-run the ten real-world dogfood prompts and record `HIRR_WORKFLOW_TARGET_REFINEMENT_CERTIFICATION_V1`.

## Non-Goals

- No governance redesign.
- No Universal Intake redesign.
- No OCS cognition runtime repair.
- No provider invocation changes.
- No worker lifecycle changes.
- No authorization changes.
- No execution changes.
- No new routing authority outside existing HIRR clarification continuity.

## Final Design Fields

```text
ROOT_CAUSE_IDENTIFIED = YES
TARGET_REFINEMENT_DEFINED = YES
REPLAY_ARTIFACT_DEFINED = YES
UNIVERSAL_INTAKE_REDESIGN_REQUIRED = NO
GOVERNANCE_LAYER_ADDED = NO
FAIL_CLOSED_REQUIREMENTS_DEFINED = YES
IMPLEMENTATION_READY = YES
NEXT_ARTIFACT = AIGOL_HIRR_WORKFLOW_TARGET_REFINEMENT_IMPLEMENTATION_V1
```
