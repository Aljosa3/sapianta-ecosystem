# AIGOL_OCS_ROUTING_GENERALIZATION_FIX_V1

## Status

Implemented routing generalization fix.

## Goal

Generalize OCS workflow classification so that OCS cognition prompts continue to route to:

```text
OCS_LLM_COGNITION
```

when additional instructions, assumptions, context, formatting requests, or analysis requirements are appended.

## Trace Findings

The authoritative classifier is:

```text
aigol/runtime/conversational_cli_runtime.py::_classify_workflow
```

The OCS predicate is:

```text
aigol/runtime/conversational_cli_runtime.py::is_ocs_llm_cognition_prompt
```

The interactive CLI dispatches by:

```text
workflow_selection_artifact["workflow_id"]
```

The routing visibility path also calls the same public OCS predicate through:

```text
aigol/cli/aigol_cli.py
```

## Matching Model Before Fix

OCS classification depended on:

- phrase markers such as `first real commercial sapianta product`;
- broader keyword markers such as `sapianta`, `aigol`, `commercial`, `architecture`, `governance`, `cognition`, `product`, `analysis`, and `decide`;
- question starts such as `should`, `what should`, and `can you analyze`;
- rule ordering before provider fallback;
- a domain-creation veto that rejected prompts containing `domain` plus `create`, `new`, or `add`.

The classifier did not depend on full-string equality, line count, token count, or punctuation in the target case.

## Why Extended Prompts Failed

The compact prompt contained an OCS phrase marker:

```text
first real commercial Sapianta product
```

Extended prompts could append governance-safe instructions such as:

```text
Assume existing product domains remain read-only evidence.
Do not create a new domain or mutate governance.
```

That appended text introduced `domain` and `create/new`, which activated the broad domain-creation veto before the OCS marker was allowed to classify the prompt.

Result:

```text
OCS intent hidden by domain veto
-> no OCS workflow selected
-> fallback or competing workflow selected
```

## Fix

The OCS predicate now:

- preserves the singular `product domain` operator-support carve-out;
- allows plural `product domains` when used as appended context/evidence;
- checks whether an OCS cognition marker exists before applying the generic domain-creation veto;
- still rejects generic domain creation prompts without an OCS marker.

This preserves existing worker, replay, governance, and provider fallback behavior because those workflow checks remain outside the OCS product-cognition expansion and the fallback remains last.

## Regression Cases

All of the following now route to:

```text
OCS_LLM_COGNITION
```

Case A:

```text
I want to create the first real commercial Sapianta product.
```

Case B:

```text
I want to create the first real commercial Sapianta product.

Use the current AiGOL architecture and repository state.

Assume:

- Existing product domains remain read-only evidence.
- Do not create a new domain or mutate governance.
```

Case C:

```text
I want to create the first real commercial Sapianta product.

Produce:

- Findings
- Assumptions
- Risks
- Uncertainties
- Recommended next milestone
```

Case D:

```text
I want to create the first real commercial Sapianta product.

Context:
Current AiGOL routing, OCS cognition, replay, and governance artifacts exist.
Use repository state as context.
Keep provider output non-authoritative.
```

## Alignment

Validated alignment surfaces:

- routing decision artifact;
- workflow selection artifact;
- routing visibility artifact;
- interactive dispatch;
- OCS end-to-end execution.

## Governance Boundary

This change does not alter provider behavior, replay semantics, execution authority, worker invocation authority, or governance mutation authority.

