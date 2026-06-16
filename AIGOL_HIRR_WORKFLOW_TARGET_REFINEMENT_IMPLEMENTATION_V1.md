# AIGOL_HIRR_WORKFLOW_TARGET_REFINEMENT_IMPLEMENTATION_V1

Status: implemented and validated.

## Objective

Implement `HIRR_WORKFLOW_TARGET_REFINEMENT_V1` so ACLI recomputes workflow target selection after a human clarification response instead of preserving the original ambiguous target.

## Architecture Impact

The repair is contained inside the existing Human Intent Resolution clarification-continuity runtime.

No new governance layer was introduced.

Preserved boundaries:

- Universal Intake remains passive;
- governance authority unchanged;
- authorization behavior unchanged;
- worker lifecycle unchanged;
- provider invocation unchanged;
- execution behavior unchanged;
- replay remains append-only and hash-verified;
- fail-closed behavior remains active for malformed state, missing targets, unsupported targets, and replay mismatch.

Updated flow:

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

## Runtime Modifications

Updated runtime:

```text
aigol/runtime/human_intent_clarification_continuity_runtime.py
```

Runtime changes:

- added `HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1`;
- inserted `human_intent_workflow_target_refinement_recorded` as replay step 2;
- recomputed selected workflow from clarification response signals;
- preserved original target in replay;
- recorded clarified/refined intent family in replay;
- recorded refined workflow target in replay;
- updated resolution and workflow-selection artifacts to reference the refinement artifact;
- updated replay reconstruction to verify five ordered replay steps;
- updated rendered summary to expose target refinement status and reason.

## Replay Artifacts

New replay order:

```text
000_human_intent_clarification_reply_binding_recorded.json
001_human_intent_clarification_response_recorded.json
002_human_intent_workflow_target_refinement_recorded.json
003_human_intent_clarification_resolution_recorded.json
004_human_intent_workflow_selection_after_clarification_recorded.json
```

The new refinement artifact preserves:

```text
original_intent_family
original_expected_workflow_targets
clarification_response_signals
refined_intent_family
refined_workflow_targets
selected_workflow_id
refinement_status
refinement_reason
```

Authority fields remain false:

```text
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
governance_mutated = false
replay_mutated = false
```

## Target Refinement Rules

Governed workflow signals select:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

Advisory, planning, no-implementation, or no-execution signals select:

```text
OCS_LLM_COGNITION
```

If no deterministic refinement signal exists, the original target is preserved and replay records:

```text
TARGET_PRESERVED_LOW_CONFIDENCE
```

Unsupported refined targets fail closed.

## Test Plan

Focused certification tests were added to:

```text
tests/test_conversational_cli_runtime_v1.py
```

Coverage includes:

- existing business-goal clarification;
- existing automation clarification;
- existing compliance clarification;
- existing ambiguous-to-governed clarification;
- existing general-improvement advisory clarification;
- four real-world dogfood advisory misrouting cases;
- replay reconstruction of the new target-refinement artifact;
- preservation of no-provider, no-worker, no-execution boundaries.

## Certification Evidence

Focused regression:

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py
109 passed
```

Real-world dogfood rerun:

```text
RESULTS_JSON = /tmp/aigol_hirr_workflow_target_refinement_v1/results.json
TARGET_CORRECT_COUNT = 10
MISROUTINGS = 0
FAILED_CLOSED = 1
```

The remaining failed-closed case is downstream OCS cognition behavior:

```text
cognition comparison failed closed: at least two cognition artifacts are required for comparison
```

It is not a target-refinement failure because `OCS_LLM_COGNITION` was selected correctly.

Whitespace validation:

```text
git diff --check
```

## Implementation Order

Completed order:

1. Added refinement artifact constant and replay step.
2. Inserted target refinement between response binding and resolution.
3. Updated resolution artifact to reference refinement.
4. Updated workflow selection artifact to reference refinement.
5. Updated replay reconstruction for five-step continuity replay.
6. Added deterministic advisory and governed-workflow signal rules.
7. Added dogfood advisory misrouting regression cases.
8. Ran focused test suite and real-world dogfood rerun.

## Acceptance Status

```text
ADVISORY_MISROUTINGS_BEFORE = 4
ADVISORY_MISROUTINGS_AFTER = 0
TARGET_SELECTION_CORRECT = YES
REPLAY_VISIBLE_REFINEMENT = YES
ORIGINAL_TARGET_PRESERVED_IN_REPLAY = YES
CLARIFIED_INTENT_PRESERVED_IN_REPLAY = YES
REFINED_TARGET_PRESERVED_IN_REPLAY = YES
GOVERNANCE_LAYER_ADDED = NO
PROVIDER_INVOCATION_ADDED = NO
WORKER_INVOCATION_ADDED = NO
AUTHORIZATION_CHANGE_ADDED = NO
EXECUTION_CHANGE_ADDED = NO
FAIL_CLOSED_PRESERVED = YES
IMPLEMENTATION_VALIDATED = YES
```
