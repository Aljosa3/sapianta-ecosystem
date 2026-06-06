# AIGOL_OCS_LLM_COGNITION_ROUTE_TRACE_REVIEW_V1

## Status

Review-only route-trace investigation.

No runtime code was changed. No CLI behavior was changed. No provider behavior was changed. No OCS cognition behavior was changed.

## Executive Finding

The observed turn did not execute `OCS_LLM_COGNITION_END_TO_END`.

The CLI displayed a routing visibility artifact with:

```text
workflow: OCS_LLM_COGNITION
```

but the actual workflow dispatch later entered:

```text
OPERATOR_DECISION_SUPPORT
```

The mismatch is caused by two independent routing layers in `aigol/cli/aigol_cli.py`:

1. `CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1`, created by `_record_interactive_routing_visibility(...)`, is replay-visible and operator-facing, but visibility-only.
2. Actual workflow dispatch is still performed by the `run_interactive_conversation(...)` `if/elif` cascade.

For prompts matching both OCS cognition and operator decision-support signals, routing visibility can prefer OCS while the dispatch cascade executes operator decision support first.

## Primary Root Cause

The routing visibility decision is not the source of dispatch authority.

Exact display-only route:

```text
aigol/cli/aigol_cli.py::_record_interactive_routing_visibility
-> _interactive_routing_visibility_analysis
-> _interactive_routing_visibility_candidates
-> _selected_routing_visibility_candidate
-> record_conversational_routing_visibility
-> render_conversational_routing_visibility
```

Exact dispatch route:

```text
aigol/cli/aigol_cli.py::run_interactive_conversation
-> elif is_operator_decision_support_prompt(human_prompt)
-> run_operator_decision_support(...)
-> render_operator_decision_support_summary(...)
```

The dispatch route does not consume the routing visibility artifact.

## Evidence

### Routing Visibility Is Recorded Before Dispatch

`aigol/cli/aigol_cli.py:1640-1650` records routing visibility and appends its operator summary to `turn_progress_buffer`.

`aigol/runtime/conversational_routing_visibility_runtime.py:47-76` persists the artifact with:

- `visibility_only: True`
- `authority_granted: False`
- `provider_authority: False`
- `execution_authority: False`

`aigol/runtime/conversational_routing_visibility_runtime.py:131-151` renders the operator-facing block headed `ROUTING DECISION`.

### Routing Visibility Can Prefer OCS Over Operator Decision Support

`aigol/cli/aigol_cli.py:881-905` adds an `OCS_LLM_COGNITION` routing visibility candidate when OCS cognition markers are detected.

`aigol/cli/aigol_cli.py:906-920` can also add a competing low-confidence `OPERATOR_DECISION_SUPPORT` candidate for the same prompt.

`aigol/cli/aigol_cli.py:924-950` changes the visibility selection order when `is_ocs_llm_cognition_prompt(prompt)` is true by moving `CONVERSATIONAL_OPERATOR_DECISION_SUPPORT` to the end of the visibility order.

Therefore the visibility artifact can select:

```text
workflow_id: OCS_LLM_COGNITION
competing_signals: [OPERATOR_DECISION_SUPPORT]
```

### Actual Dispatch Checks Operator Decision Support Before OCS

`aigol/cli/aigol_cli.py:2173-2230` is the operator decision-support dispatch branch. It calls:

- `route_conversational_cli_intent(...)`
- `run_operator_decision_support(...)`
- `render_operator_decision_support_summary(...)`

`aigol/cli/aigol_cli.py:2654-2687` is the OCS cognition dispatch branch. It is later in the same `if/elif` cascade and calls:

- `route_conversational_cli_intent(...)`
- `_run_conversational_ocs_llm_cognition(...)`
- `render_ocs_llm_cognition_end_to_end_summary(...)`

Because the operator decision-support branch appears first, any prompt matching both predicates dispatches to operator decision support and never reaches the OCS branch.

### Operator Decision Support Explains the Observed Output

`aigol/runtime/operator_decision_support_runtime.py:140-163` renders summaries beginning with:

```text
Recommendation Generated
Category: ...
Recommended: ...
```

`aigol/runtime/operator_decision_support_runtime.py:166-183` classifies prompts containing provider comparison signals as `PROVIDER_COMPARISON`.

The observed prompt contains `Provider disagreements`; because it also contains `first`, the operator decision-support classifier can match the provider comparison rule at `aigol/runtime/operator_decision_support_runtime.py:179-180`.

`aigol/runtime/operator_decision_support_runtime.py:114-137` reconstructs operator decision-support replay with:

- `provider_invoked: False`
- `worker_invoked: False`
- `execution_requested: False`

That matches the observed output exactly.

## Prompt-To-Result Trace

| Step | Runtime | File / Function | Evidence | Result |
| --- | --- | --- | --- | --- |
| 1 | Prompt capture | `aigol/cli/aigol_cli.py::run_interactive_conversation` | prompt assembled before line 1640 | One human prompt enters the turn |
| 2 | Routing visibility | `_record_interactive_routing_visibility` | lines 1640-1650, 714-743 | Visibility artifact created |
| 3 | Visibility candidate analysis | `_interactive_routing_visibility_candidates` | lines 852-920 | OCS and operator-support candidates can both be present |
| 4 | Visibility selection | `_selected_routing_visibility_candidate` | lines 924-950 | OCS can be displayed as selected |
| 5 | Source router | `route_source_of_truth(...)` | lines 1659-1665 | Source routing artifact recorded |
| 6 | Workflow dispatch | `run_interactive_conversation` cascade | lines 2173-2230 before 2654-2687 | Operator support branch wins |
| 7 | Runtime execution | `run_operator_decision_support` | `operator_decision_support_runtime.py:42-75` | Recommendation artifact generated |
| 8 | Rendering | `render_operator_decision_support_summary` | `operator_decision_support_runtime.py:140-163` | `Recommendation Generated` printed |
| 9 | Completion | turn completion block | `aigol/cli/aigol_cli.py:2740-2778` | `TURN COMPLETED` printed after operator-support result |

## Review Question Answers

1. Execution did not enter `OCS_LLM_COGNITION_END_TO_END` on the observed path. The CLI displayed a routing visibility artifact only.

2. No dispatch function receives the routing visibility decision as authority. The artifact is created in `aigol/cli/aigol_cli.py::_record_interactive_routing_visibility`, lines 714-743, and rendered from `aigol/runtime/conversational_routing_visibility_runtime.py::render_conversational_routing_visibility`, lines 131-151.

3. Workflow dispatch is performed by `aigol/cli/aigol_cli.py::run_interactive_conversation`. The relevant branches are `elif is_operator_decision_support_prompt(human_prompt)` at lines 2173-2230 and `elif is_ocs_llm_cognition_prompt(human_prompt)` at lines 2654-2687.

4. The routing visibility artifact does not influence dispatch. It is visibility-only evidence.

5. Yes. Visibility can show `workflow = OCS_LLM_COGNITION` while dispatch executes `OPERATOR_DECISION_SUPPORT` because `_selected_routing_visibility_candidate(...)` can prefer OCS at lines 942-945, while the dispatch cascade checks operator decision support first at line 2173.

6. The full transition is: human prompt -> multiline/single-line prompt capture -> routing visibility analysis -> routing visibility artifact -> source router -> independent dispatch cascade -> operator decision-support runtime -> recommendation continuity -> operator-support summary -> turn completion.

7. `ROUTING_DECISION` from `CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1` is display-only. The actual dispatch source is the `run_interactive_conversation(...)` branch cascade.

8. `provider_invoked: False` appears because the executed runtime was `operator_decision_support_runtime`, whose replay reconstruction explicitly returns `provider_invoked: False`.

9. In the observed path, `providers: NONE` is evidence that OCS cognition did not execute. It is not the sole proof by itself, because provider projection gaps exist elsewhere, but combined with `operator_decision_support` replay and `Recommendation Generated`, it confirms non-OCS execution.

10. The exact root cause is divergent routing authority: the displayed routing visibility artifact uses one selection priority, while actual dispatch uses a separate `if/elif` cascade where operator decision support precedes OCS cognition.

## Findings

### F-1: Displayed Workflow Is Not Dispatch Authority

Classification: `DISPATCH_BUG`

The CLI displays `workflow: OCS_LLM_COGNITION` from a visibility-only artifact, then dispatches using an independent branch cascade. This creates an operator-visible mismatch between displayed workflow and executed workflow.

### F-2: Visibility Selection Priority Diverges From Dispatch Priority

Classification: `ROUTING_BUG`

Routing visibility moves operator decision support behind OCS when an OCS prompt is detected. Actual dispatch checks operator decision support before OCS cognition.

### F-3: Operator Decision-Support Output Is Correct For The Executed Branch

Classification: `FALSE_POSITIVE`

The `Recommendation Generated`, `PROVIDER_COMPARISON`, `provider_invoked: False`, and `operator_decision_support` replay reference are not malformed OCS output. They are correct output for the branch that actually executed.

### F-4: OCS Cognition Runtime Is Not The Failing Component

Classification: `FALSE_POSITIVE`

The OCS cognition end-to-end runtime is not implicated by this trace because `_run_conversational_ocs_llm_cognition(...)` was not reached.

### F-5: Routing Visibility Label Overstates Execution Selection

Classification: `VISIBILITY_BUG`

The heading `ROUTING DECISION` reads like an execution decision, but the artifact has `visibility_only: True` and is not consumed by dispatch.

## Conclusion

The CLI displayed `workflow: OCS_LLM_COGNITION` because routing visibility selected OCS for operator explanation. The CLI produced `operator_decision_support` output because actual dispatch ignored that visibility artifact and entered the earlier `is_operator_decision_support_prompt(human_prompt)` branch.

The defect is in the boundary between routing visibility and workflow dispatch, not in OCS cognition execution.
