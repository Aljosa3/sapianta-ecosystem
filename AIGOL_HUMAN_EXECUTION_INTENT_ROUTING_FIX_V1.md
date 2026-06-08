# AIGOL_HUMAN_EXECUTION_INTENT_ROUTING_FIX_V1

## Status

Compatibility routing fix implemented and regression-tested.

No domain creation runtime was implemented. No execution authority was granted. No approval, authorization, worker assignment, dispatch, invocation, retry, repair, or architectural redesign was implemented.

## Purpose

Fix the gap identified by `AIGOL_HUMAN_TO_EXECUTION_INTENT_AUDIT_V1`:

```text
GENERIC_GOVERNED_DOMAIN_CREATION_INTENT_NOT_BOUND_TO_EXECUTION_ENTRY
```

The motivating prompt was:

```text
Create a new governed domain called PilotDomain.
```

Before this fix, the prompt selected:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

After this fix, the prompt selects:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

and enters the existing governed unknown-domain clarification workflow without provider invocation, worker invocation, authorization, execution, or domain mutation.

## Implemented Change

Added a shared deterministic execution-intent detector:

```text
aigol/runtime/human_execution_intent_detection.py
```

The detector defines canonical generic intent classes:

- `GENERIC_GOVERNED_DOMAIN_CREATION`
- `GENERIC_GOVERNED_ARTIFACT_CREATION`
- `GENERIC_GOVERNED_EXECUTION_REQUEST`
- `NO_EXECUTION_INTENT`

The detector does not grant execution authority. It only classifies human prompt intent for routing.

## Routing Rule

Generic governed domain creation is detected when a prompt contains:

- a domain subject;
- a creation signal such as `create`, `new`, `add`, `build`, or `make`;
- a governance or naming signal such as `governed`, `called`, or `named`.

Example:

```text
Create a new governed domain called PilotDomain.
```

Detection result:

```text
intent_class = GENERIC_GOVERNED_DOMAIN_CREATION
target_kind = DOMAIN
target_name = PilotDomain
requires_clarification = true
execution_authority_granted = false
routing_action = GOVERNED_UNKNOWN_DOMAIN_CLARIFICATION
```

## Authoritative Routing Binding

`aigol/runtime/conversational_cli_runtime.py` now detects generic governed domain creation before the low-confidence provider fallback.

The prompt routes to the existing clarification workflow:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

This preserves the existing workflow registry and avoids adding a new execution path.

## Clarification Binding

`aigol/runtime/unknown_domain_clarification_runtime.py` now accepts generic governed domain creation prompts and emits replay-visible unknown-domain clarification artifacts.

For `PilotDomain`, the clarification artifact records:

```text
originating_intent = CREATE_DOMAIN
requested_domain = PilotDomain
proposed_domain = PilotDomain
clarification_mode = DOMAIN_DETAILS
missing_information = primary purpose, expected capabilities, target users
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
domain_created = false
```

## Fail-Closed Guard

Generic governed artifact creation and generic governed execution requests are now detected but fail closed when no certified workflow mapping exists.

Examples:

```text
Create a governed artifact called PilotArtifact.
Trigger a governed execution workflow.
```

These prompts no longer silently drift into provider-assisted conversation fallback.

They fail closed with:

```text
generic governed execution intent requires a certified workflow mapping
```

## Existing Behavior Preserved

The existing specific-domain routes remain unchanged:

- `Create a trading domain.` routes to `CREATE_DOMAIN_TRADING`;
- `Create a marketing domain.` routes to `CREATE_DOMAIN_MARKETING`;
- `Create a compliance domain.` routes to `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`;
- domain adaptation and OCS cognition routes remain ordered ahead of the provider fallback.

## Authority Boundaries

The fix preserves:

- provider authority: not granted;
- OCS authority: not granted by routing;
- approval authority: not granted;
- execution authority: not granted;
- worker authority: not granted;
- domain creation authority: not granted;
- replay mutation authority: not granted.

The new route produces clarification only. Any later domain creation still requires bounded intent, OCS/handoff processing where applicable, human approval, readiness, authorization, worker selection, dispatch, execution, capture, validation, replay review, and governed termination.

## Regression Coverage

Added coverage in:

```text
tests/test_conversational_cli_runtime_v1.py
tests/test_unknown_domain_and_clarification_ux_v1.py
```

Validated cases:

- generic governed domain creation routes to clarification;
- `PilotDomain` is extracted as the proposed domain;
- interactive ACLI conversation enters unknown-domain clarification without provider fallback;
- generic governed artifact and execution requests fail closed without provider fallback;
- existing trading domain route remains unchanged;
- existing compliance clarification behavior remains unchanged.

## Validation

Executed:

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_unknown_domain_and_clarification_ux_v1.py
```

Result:

```text
33 passed
```

## Final Outputs

```text
EXECUTION_INTENT_DETECTED = TRUE
GENERIC_DOMAIN_CREATION_SUPPORTED = TRUE_AS_GOVERNED_CLARIFICATION_NOT_DIRECT_EXECUTION
ROUTING_GAP_FIXED = TRUE
FAIL_CLOSED_PRESERVED = TRUE
READY_FOR_HUMAN_EXECUTION_WORKFLOW = TRUE_WITH_CLARIFICATION_GATE
```
