# AIGOL_OCS_ROUTING_CONSISTENCY_REVIEW_V1

## Status

Review-only routing assessment.

No runtime code was changed. No provider behavior was changed. No workflow behavior was changed.

## Executive Finding

Prompts that should enter `OCS_LLM_COGNITION` can route into `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` before dispatch.

The divergence is not caused by `SINGLE_PROVIDER_PRIMARY_MODE_V1`. Single-provider mode changes the OCS execution path after OCS dispatch. The observed default-provider route is created earlier by certified conversational routing classification:

```text
aigol/runtime/conversational_cli_runtime.py::_classify_workflow
```

The first failing decision point is:

```text
_classify_workflow(...)
-> _is_ocs_llm_cognition_prompt(...)
-> False
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

## Direct Answers

1. Expected workflow: `OCS_LLM_COGNITION`.

2. Actual workflow: `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` for cognition prompts that do not match the current literal OCS marker list.

3. Routing divergence location: `aigol/runtime/conversational_cli_runtime.py:213-242`, with the specific predicate failure in `aigol/runtime/conversational_cli_runtime.py:291-324`.

4. Minimal safe fix: repair the OCS cognition predicate so question-start detection remains reachable and add explicit certified OCS markers for Sapianta/product cognition prompts such as `first real sapianta product`, `commercial sapianta product`, and `cognition output only`. Add routing regression tests proving the same prompt yields OCS in routing visibility, workflow selection, and dispatch.

## Current Routing Trace

The current ordinary conversational path is:

```text
Human Prompt
-> route_conversational_cli_intent(...)
-> CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1
-> CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1
-> _record_interactive_routing_visibility(..., conversational_routing_capture=...)
-> authoritative_workflow_id
-> dispatch branch
```

`aigol/cli/aigol_cli.py:1761-1772` calls the certified router and reads:

```text
workflow_selection_artifact["workflow_id"]
```

`aigol/cli/aigol_cli.py:1773-1783` then records routing visibility from that same certified routing capture.

`aigol/cli/aigol_cli.py:2779-2813` dispatches OCS only when:

```text
authoritative_workflow_id == OCS_LLM_COGNITION
```

Otherwise, `aigol/cli/aigol_cli.py:2813-2823` dispatches the default provider-assisted conversation path when the selected workflow is:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

## Current Routing Rules

`aigol/runtime/conversational_cli_runtime.py:211-242` currently routes in this priority order:

1. Fail closed for unrestricted autonomous-agent prompts.
2. Domain adaptation reference.
3. OCS LLM cognition.
4. Operator decision support.
5. Create trading domain.
6. Create marketing domain.
7. Create compliance/regulatory domain clarification.
8. Latest replay chain.
9. Audit review.
10. Provider layer improvement.
11. Status.
12. Dashboard.
13. Native development context integration.
14. Default provider-assisted conversation fallback.

## OCS Cognition Trigger Conditions

`aigol/runtime/conversational_cli_runtime.py:298-324` currently admits OCS when:

- prompt does not contain both `unrestricted` and `autonomous agent`;
- prompt does not contain `domain` plus one of `create`, `new`, or `add`;
- prompt contains one of the literal cognition markers:
  - `first real aigol product`
  - `commercialization`
  - `managed services`
  - `license the platform`
  - `sell domains`
  - `should sapianta`
  - `continue the aigol`
  - `continue `
  - `help me decide`
  - `what should`
- or prompt starts with a supported question phrase and ends with `?`.

The question-start path is currently ineffective because callers strip terminal punctuation before calling `_is_ocs_llm_cognition_prompt(...)`.

## Default Provider Trigger Conditions

`DEFAULT_PROVIDER_ASSISTED_CONVERSATION` is selected only after all earlier workflow predicates fail.

Current default selection occurs at:

```text
aigol/runtime/conversational_cli_runtime.py:242
```

with matched terms:

```text
["provider", "conversation", "fallback"]
```

## Divergence Evidence

Classifier probe on representative cognition prompts:

| Prompt Class | OCS Predicate | Selected Workflow |
| --- | ---: | --- |
| `I want to create the first real AiGOL product.` | True | `OCS_LLM_COGNITION` |
| `Can you analyze the first real commercial Sapianta product opportunity?` | False | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |
| `Provide cognition output only.` | False | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` |

This proves the divergence exists before visibility rendering and before dispatch.

## Root Cause

The certified OCS routing predicate is too narrow for current conversational OCS usage.

Two specific defects were found:

1. Question-start detection is unreachable in normal use because the prompt is normalized with `.rstrip(".?!")` before `_is_ocs_llm_cognition_prompt(...)` checks `normalized.endswith("?")`.

2. The OCS marker set recognizes `first real aigol product` but does not recognize analogous Sapianta/product-cognition prompts or explicit `cognition output only` prompts.

## Single Provider Impact

`SINGLE_PROVIDER_PRIMARY_MODE_V1` is not the first failure location.

Single-provider mode is reached only after `authoritative_workflow_id == OCS_LLM_COGNITION`. A prompt routed to `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` never enters the OCS single-provider runtime.

## Minimal Safe Fix

The smallest safe implementation is:

1. Preserve the original prompt punctuation or pass an `ends_with_question` flag into `_is_ocs_llm_cognition_prompt(...)` so question-start cognition prompts can match.

2. Add narrowly scoped certified OCS markers:
   - `first real sapianta product`
   - `commercial sapianta product`
   - `sapianta product opportunity`
   - `cognition output only`

3. Add regression tests proving:
   - routing decision selects `OCS_LLM_COGNITION`;
   - workflow selection selects `OCS_LLM_COGNITION`;
   - routing visibility displays `OCS_LLM_COGNITION`;
   - dispatch enters `_run_conversational_ocs_llm_cognition(...)`;
   - default provider-assisted conversation remains available for non-cognition prompts.

## Final Outputs

```text
EXPECTED_WORKFLOW = OCS_LLM_COGNITION
ACTUAL_WORKFLOW = DEFAULT_PROVIDER_ASSISTED_CONVERSATION
ROUTING_DIVERGENCE_LOCATION = aigol/runtime/conversational_cli_runtime.py::_classify_workflow -> _is_ocs_llm_cognition_prompt
MINIMAL_SAFE_FIX = repair OCS predicate punctuation handling, add narrow Sapianta/cognition markers, and certify routing visibility/workflow selection/dispatch alignment with tests
```
