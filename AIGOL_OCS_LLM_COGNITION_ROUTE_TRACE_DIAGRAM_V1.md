# AIGOL_OCS_LLM_COGNITION_ROUTE_TRACE_DIAGRAM_V1

## Observed Mismatch Diagram

```text
Human Prompt
  |
  v
Prompt Capture
  |
  v
_record_interactive_routing_visibility(...)
  |
  v
_interactive_routing_visibility_candidates(...)
  |        \
  |         +-- OPERATOR_DECISION_SUPPORT candidate
  |
  +-- OCS_LLM_COGNITION candidate
  |
  v
_selected_routing_visibility_candidate(...)
  |
  v
CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1
  |
  v
Operator Display
  |
  +-- ROUTING DECISION
      workflow: OCS_LLM_COGNITION
      competing: OPERATOR_DECISION_SUPPORT

  DISPLAY-ONLY BOUNDARY
  routing visibility is not dispatch authority

  |
  v
run_interactive_conversation(...) if/elif cascade
  |
  +-- earlier branch:
  |   elif is_operator_decision_support_prompt(human_prompt):
  |       run_operator_decision_support(...)
  |       render_operator_decision_support_summary(...)
  |       STOP CASCADE
  |
  +-- later branch not reached:
      elif is_ocs_llm_cognition_prompt(human_prompt):
          _run_conversational_ocs_llm_cognition(...)
          render_ocs_llm_cognition_end_to_end_summary(...)

  |
  v
Final Output
  |
  +-- Recommendation Generated
  +-- Category: PROVIDER_COMPARISON
  +-- provider_invoked: False
  +-- replay_reference: .../operator_decision_support
  +-- TURN COMPLETED
```

## Expected OCS Path

```text
Human Prompt
  |
  v
Workflow Dispatch: OCS_LLM_COGNITION
  |
  v
_run_conversational_ocs_llm_cognition(...)
  |
  v
run_ocs_llm_cognition_end_to_end(...)
  |
  +-- source context assembly
  +-- provider contracts
  +-- provider transports
  +-- provider responses
  +-- comparison
  +-- continuity
  +-- clarification
  |
  v
render_ocs_llm_cognition_end_to_end_summary(...)
  |
  v
OCS_LLM_COGNITION_END_TO_END
```

## Actual Observed Path

```text
Human Prompt
  |
  v
Routing Visibility: OCS_LLM_COGNITION
  |
  v
Dispatch: OPERATOR_DECISION_SUPPORT
  |
  v
run_operator_decision_support(...)
  |
  v
OPERATOR_DECISION_SUPPORT_ARTIFACT_V1
  |
  v
Recommendation Generated
```

## Boundary Finding

```text
ROUTING DECISION != WORKFLOW DISPATCH
```

The displayed routing decision is a replay-visible explanation artifact. The executed workflow is selected later by a separate CLI branch cascade.
