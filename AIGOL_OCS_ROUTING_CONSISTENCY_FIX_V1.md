# AIGOL_OCS_ROUTING_CONSISTENCY_FIX_V1

## Status

Runtime routing fix implemented.

Provider behavior was not changed. OCS execution behavior was not changed. Default provider fallback remains available.

## Executive Finding

Conversational OCS routing now classifies:

```text
I want to create the first real commercial Sapianta product.
```

as:

```text
OCS_LLM_COGNITION
```

The divergence was caused by an OCS predicate that recognized `first real aigol product`, but not the equivalent Sapianta product cognition prompt. The question-path predicate was also ineffective because terminal punctuation was stripped before checking whether the prompt ended with `?`.

## What Changed

`aigol/runtime/conversational_cli_runtime.py` now preserves whether the original normalized prompt ended with a question mark before stripping punctuation for the rest of routing.

The OCS predicate now recognizes narrow governed-cognition signals:

- `sapianta`
- `aigol`
- `commercialization` / `commercial`
- `architecture`
- `governance`
- `cognition`

The broad signal path is bounded by subject, scope, and analysis intent:

```text
(sapianta or aigol)
and (commercialization/commercial/architecture/governance/cognition)
and (first real/product/opportunity/analyze/analysis/evaluate/decide)
```

Explicit markers were also added for:

- `first real commercial sapianta product`
- `first real sapianta product`
- `commercial sapianta product`
- `sapianta product opportunity`
- `cognition output only`

## Preservation

Unrelated workflow priority remains preserved.

The explicit domain-creation exclusion remains before OCS matching:

```text
domain + create/new/add -> not OCS
```

That preserves domain creation and operator decision-support behavior for prompts such as:

```text
I want to create the first real AiGOL product domain.
```

which still routes to:

```text
OPERATOR_DECISION_SUPPORT
```

## Validation Coverage

### Workflow Selection

`tests/test_conversational_cli_runtime_v1.py` now proves:

```text
I want to create the first real commercial Sapianta product.
-> OCS_LLM_COGNITION
```

It also proves question-based cognition routing:

```text
Can you analyze the first real commercial Sapianta product opportunity?
-> OCS_LLM_COGNITION
```

### Routing Visibility

`tests/test_conversational_routing_visibility_runtime_v1.py` now proves the interactive visibility artifact displays:

```text
workflow: OCS_LLM_COGNITION
```

for the exact Sapianta commercial product prompt.

### Dispatch

`tests/test_conversational_ocs_cognition_binding_v1.py` now uses the exact Sapianta commercial product prompt and proves dispatch reaches:

```text
OCS_LLM_COGNITION_END_TO_END
```

with:

```text
conversational_workflow_id = OCS_LLM_COGNITION
```

## Validation Commands

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_conversational_routing_visibility_runtime_v1.py tests/test_conversational_ocs_cognition_binding_v1.py
```

Result:

```text
25 passed
```

## Final Outputs

```text
EXPECTED_WORKFLOW = OCS_LLM_COGNITION
ACTUAL_WORKFLOW = OCS_LLM_COGNITION
ROUTING_ALIGNMENT = TRUE
DISPATCH_ALIGNMENT = TRUE
REGRESSION_TEST_STATUS = PASSED
```
