# AIGOL_CONVERSATIONAL_DISPATCH_AUTHORITY_UNIFICATION_REVIEW_V1

## Status

Review-only architecture assessment.

No runtime code was changed. No CLI behavior was changed. No provider behavior was changed. No workflow behavior was changed.

## Executive Finding

AiGOL conversational CLI can safely move toward:

```text
Routing Decision = Dispatch Authority
```

but not by promoting `CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1` directly.

The correct authority candidate is the existing certified routing pair:

```text
CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1
CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1
```

implemented by:

```text
aigol/runtime/conversational_cli_runtime.py::route_conversational_cli_intent
```

The visibility artifact should become a rendered projection of the authoritative routing decision and workflow selection, not the source of dispatch authority.

## Direct Answers

1. The artifact that should become dispatch authority is `CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1`, bound to `CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1` by routing decision hash.

2. `CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1` should not become dispatch authority as currently designed. It declares `visibility_only: True`, `authority_granted: False`, and lacks the existing runtime, CLI command, workflow selection hash binding, and coverage fields needed for authoritative dispatch.

3. The existing `if/elif` cascade currently owns dispatch for approval resume, recommendation approval, recommendation follow-up, read-only workflows, domain adaptation reference, operator decision support, unknown-domain clarification, native development intent, native development context integration, OCS cognition, and default provider-assisted conversation fallback.

4. Moving dispatch authority directly to routing selection would break workflows whose stateful preconditions are not represented by the current routing runtime, especially pending approval decisions, recommendation decisions, recommendation follow-ups, native development context integration, and legacy default fallback.

5. Minimal migration path: keep stateful resume branches before generic routing, call `route_conversational_cli_intent(...)` once for all ordinary prompts, dispatch by `workflow_selection_artifact["workflow_id"]`, and render routing visibility from the same authoritative capture.

6. Affected files are listed in the evidence artifact. The primary files are `aigol/cli/aigol_cli.py`, `aigol/runtime/conversational_cli_runtime.py`, `aigol/runtime/conversational_routing_visibility_runtime.py`, and the interactive/routing tests.

7. Estimated implementation complexity is medium-high. The conceptual change is small, but regression risk is real because many certified branches have branch-local side effects and turn-summary builders.

## Current Architecture

### Visibility Path

`aigol/cli/aigol_cli.py:1640-1650` records routing visibility before execution:

```text
_record_interactive_routing_visibility(...)
-> operator_routing_summary
-> turn_progress_buffer
```

`aigol/runtime/conversational_routing_visibility_runtime.py:47-76` creates a visibility artifact with:

- `visibility_only: True`
- `authority_granted: False`
- `provider_authority: False`
- `execution_authority: False`

This artifact is replay-visible, but intentionally non-authoritative.

### Existing Certified Routing Path

`aigol/runtime/conversational_cli_runtime.py:42-79` creates:

- `CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1`
- `CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1`
- `CONVERSATIONAL_CLI_ROUTING_RETURNED`

`aigol/runtime/conversational_cli_runtime.py:311-346` defines the routing decision artifact.

`aigol/runtime/conversational_cli_runtime.py:349-389` defines the workflow selection artifact and binds it to the routing decision by hash.

This is the right shape for dispatch authority because it already records:

- `workflow_id`
- `routing_status`
- `existing_runtime`
- `existing_cli_command`
- coverage
- replay references
- downstream control preservation fields

### Actual Dispatch Path

`aigol/cli/aigol_cli.py::run_interactive_conversation` still performs dispatch with an `if/elif` cascade.

Key branches:

| Branch | Line Region | Current Dependency |
| --- | ---: | --- |
| recommendation approval | 2051-2079 | pending recommendation state |
| recommendation follow-up | 2080-2106 | pending recommendation approval state |
| read-only workflows | 2107-2138 | `_is_conversational_cli_readonly_candidate` |
| domain reference adaptation | 2139-2172 | `is_domain_reference_adaptation_prompt` |
| operator decision support | 2173-2230 | `is_operator_decision_support_prompt` |
| unknown-domain clarification | 2231-2264 | `is_unknown_domain_clarification_eligible` |
| native development intent | 2265-2620 | `is_conversation_native_development_intent` plus approval/handoff execution chain |
| native development context | 2621-2653 | `is_native_development_prompt` |
| OCS cognition | 2654-2687 | `is_ocs_llm_cognition_prompt` |
| default fallback | 2688 onward | provider-assisted conversation fallback |

The certified router is called inside several of these branches after the branch has already been selected. That means the routing artifact currently records branch-local evidence, but does not control the branch choice.

## Why Visibility Must Not Become Authority

`CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1` exists to explain routing to the operator. Its current contract explicitly denies authority:

```text
visibility_only: True
authority_granted: False
provider_authority: False
approval_authority: False
execution_authority: False
worker_authority: False
governance_authority: False
```

Promoting it directly would invert its certified semantics. It would also create a governance ambiguity: an artifact named and certified as visibility-only would suddenly select execution paths.

The safer model is:

```text
CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1
-> CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1
-> dispatch
-> CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1 rendered from the same selection
```

## What Would Break If Routing Immediately Owned Dispatch

### Stateful Resume Flows

Approval and recommendation flows are not ordinary prompt classification. They depend on in-memory session state:

- `pending_approval_required`
- `recommendation_continuity_artifact`
- `recommendation_approval_artifact`

Moving all prompts directly into `route_conversational_cli_intent(...)` would fail to preserve these state checks unless the router accepts session state or a pre-routing stateful-resume layer remains in front.

### Native Development Context Integration

`is_native_development_prompt(human_prompt)` currently dispatches to `run_conversation_native_development_context_integration(...)`, but `workflow_registry()` in `conversational_cli_runtime.py` does not register a corresponding `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` workflow. Routing visibility knows about it, but the certified router does not.

This branch would be unreachable under pure certified-router dispatch until the workflow is registered.

### Default Provider-Assisted Conversation Fallback

The final `else` path calls `submit_prompt_to_conversation(...)`. The current certified router fails closed on unmapped prompts. Moving to authoritative routing would remove or change the legacy default behavior unless an explicit `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` workflow is registered or the fallback remains outside unified dispatch.

### Priority Behavior Changes

The existing dispatch cascade and `conversational_cli_runtime._classify_workflow(...)` do not have identical scope to routing visibility. Moving authority to routing selection would fix the OCS/operator mismatch only if classifier priority is intentionally aligned and regression tested.

## Minimal Migration Path

### Phase 1: Declare Authority Boundary

Define:

```text
CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1 is dispatch authority.
CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1 is display evidence only.
```

No behavior change in this phase.

### Phase 2: Add A Dispatcher Function

Add a single internal dispatcher in `aigol/cli/aigol_cli.py`, for example:

```text
_dispatch_conversational_workflow(selection.workflow_id, context)
```

Initially it should call the same branch bodies that the cascade calls today.

### Phase 3: Preserve Stateful Pre-Routing Branches

Keep these checks before generic routing:

- pending implementation approval decisions
- recommendation approval decisions
- recommendation follow-ups

They are state transitions, not ordinary workflow routing.

### Phase 4: Route Once For Ordinary Prompts

For ordinary prompts:

```text
conversational_routing_capture = route_conversational_cli_intent(...)
workflow_id = conversational_routing_capture["workflow_selection_artifact"]["workflow_id"]
dispatch(workflow_id)
```

Do not re-run prompt predicates inside dispatch.

### Phase 5: Render Visibility From Authority

Create routing visibility from the authoritative routing capture rather than from a parallel classifier. This removes the display/dispatch split.

### Phase 6: Register Missing Workflows Or Keep Explicit Exceptions

Before making routing authority total, either:

- register `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`;
- register default provider-assisted conversation fallback;
- or keep those branches as explicit, documented exceptions.

### Phase 7: Regression Certification

Add tests proving:

- OCS prompt displays OCS and dispatches OCS;
- operator-support prompt displays operator support and dispatches operator support;
- ambiguous prompt has one authoritative workflow;
- routing visibility matches workflow selection;
- stateful approval and recommendation follow-up still work;
- unknown prompts fail closed or route to an explicitly registered fallback by design.

## Complexity Estimate

Implementation complexity: `MEDIUM_HIGH`.

Reason:

- The authoritative routing runtime already exists.
- The main work is extracting branch bodies into dispatchable handlers.
- Regression surface is broad because branch-local summaries, replay directories, pending approval state, chain IDs, fail-closed handling, and output rendering are currently interleaved in one loop.

Expected implementation footprint:

- 1 primary CLI refactor.
- 1 routing runtime extension for missing workflows or documented exceptions.
- 1 visibility runtime projection update.
- 8-12 focused regression tests.
- governance certification artifacts.

## Recommendation

Move to:

```text
Routing Decision = Dispatch Authority
```

only through `CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1`, not through `CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1`.

The safe final architecture is:

```text
Human Prompt
-> Stateful Resume Gate
-> route_conversational_cli_intent(...)
-> CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1
-> CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1
-> dispatch by workflow_id
-> render visibility from the same workflow selection
-> workflow runtime
-> result
-> TURN_COMPLETED
```

## Final Answer

Yes, AiGOL conversational CLI can safely move to `Routing Decision = Dispatch Authority` without breaking existing certified workflows, but only as a staged migration with stateful resume branches preserved and missing workflows explicitly registered or documented as exceptions.

It is not safe to make `CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1` the dispatch authority in its current form.
