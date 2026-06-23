# DEVELOPMENT_INTENT_TO_GOVERNED_DEVELOPMENT_ROUTING_V1

Status: Defined

Scope: Natural development intent routing into the existing governed development workflow.

Target behavior:

```text
Human natural development request
-> HIRR classification: DEVELOPMENT_INTENT
-> ACLI workflow selection: GOVERNED_DEVELOPMENT_WORKFLOW
```

Examples:

- `Add replay validation`
- `Implement worker authorization`
- `Create comparison runtime`
- `Add audit export`

Runtime target:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

Final routing verdict:

```text
NATURAL_DEVELOPMENT_INTENT_ROUTING_READY
```

## 1. HIRR Classification

HIRR exposes a concrete `DEVELOPMENT_INTENT` classification only for narrow implementation-style requests with deterministic development subjects.

The classification does not grant approval, authorization, worker execution, provider authority, repository mutation, or validation execution.

## 2. Routing Behavior

ACLI routes resolved `DEVELOPMENT_INTENT` to:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

Routing remains replay-visible and non-mutating. Workflow selection does not execute the governed development workflow.

## 3. Preserved Boundaries

This routing preserves:

- fail-closed behavior
- replay as source of truth
- explicit approval boundaries
- repository mutation worker protections
- validation allowlists
- proposal hash binding

## 4. Validation Plan

Required validation:

```bash
python -m py_compile aigol/runtime/conversational_cli_runtime.py aigol/runtime/human_intent_clarification_intake_runtime.py
python -m pytest tests/test_conversational_cli_runtime_v1.py -k "natural_development_intent or governed_development_workflow"
python -m pytest tests/test_governed_development_workflow_runtime_v1.py
git diff --check
```

## 5. Final Verdict

```text
NATURAL_DEVELOPMENT_INTENT_ROUTING_READY
```
