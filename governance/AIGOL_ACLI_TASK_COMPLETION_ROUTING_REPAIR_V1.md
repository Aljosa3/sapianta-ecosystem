# AIGOL_ACLI_TASK_COMPLETION_ROUTING_REPAIR_V1

## Status

Task-completion routing repair.

This artifact records a minimal ACLI routing repair for the most common task-completion failure identified in `AIGOL_ACLI_TASK_COMPLETION_GAP_ANALYSIS_V1`.

This repair does not redesign ACLI, OCS, PPP, worker lifecycle, replay, authorization, providers, or governance layers.

## Objective

Reduce routing ambiguity by routing real development prompts into existing certified lifecycle entries before generic provider-assisted conversation fallback is selected.

## Files Modified

```text
aigol/runtime/conversational_cli_runtime.py
tests/test_conversational_cli_runtime_v1.py
governance/AIGOL_ACLI_TASK_COMPLETION_ROUTING_REPAIR_V1.md
```

## Routing Changes

Added deterministic task-completion routing predicates for:

- development prompts;
- governance-improvement prompts;
- replay-improvement prompts;
- capability-improvement prompts;
- domain-improvement and domain-proposal prompts;
- Product 1 / AI Decision Validator evidence-presentation prompts;
- provider-boundary improvement prompts;
- approved domain proposal continuation prompts.

The repair maps natural prompts to existing registered workflow entries:

```text
governance validation report -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
replay lineage validation -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
supplier evaluation domain proposal -> CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
platform operator experience improvement -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
AI Decision Validator evidence presentation -> OPERATOR_DECISION_SUPPORT
execution summary boundary check -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
replay governance failure improvement -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
approved domain proposal continuation -> AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
document validation capability candidate -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
provider abstraction / authority boundary improvement -> IMPROVE_PROVIDER_LAYER
```

No workflow registry entries were added. No provider was added. No authority flags were changed.

## Required Review

### Development Prompts

Before:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

After:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

Existing lifecycle entry point:

```text
conversation_native_development_context_integration
```

Minimal routing repair:

Recognize governance report, operator experience, execution-summary boundary, task-completion, and document-validation candidate language as deterministic native-development context prompts.

### Governance-Improvement Prompts

Before:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

After:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

Existing lifecycle entry point:

```text
conversation_native_development_context_integration
```

Minimal routing repair:

Route bounded governance-improvement/report prompts to native-development context before provider fallback.

### Replay-Improvement Prompts

Before:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

After:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

Existing lifecycle entry point:

```text
conversation_native_development_context_integration
```

Minimal routing repair:

Recognize replay lineage, replay-derived improvement, and recurring governance failure language as deterministic task-completion signals.

### Capability-Improvement Prompts

Before:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

After:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

Existing lifecycle entry point:

```text
conversation_native_development_context_integration
```

Minimal routing repair:

Recognize capability candidate and document-validation evidence extraction language as deterministic native-development context.

### Domain-Improvement Prompts

Before:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

or:

```text
OCS_LLM_COGNITION
```

After:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
```

Existing lifecycle entry points:

```text
unknown_domain_clarification_runtime
domain_handoff_review_approval_binding_runtime
```

Minimal routing repair:

Preserve domain clarification for new domain proposal prompts and route approved-domain-proposal continuation language to the existing domain handoff review and approval binding path before OCS cognition fallback.

### Product-Foundation Prompts

Before:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

After:

```text
OPERATOR_DECISION_SUPPORT
```

Existing lifecycle entry point:

```text
operator_decision_support_runtime
```

Minimal routing repair:

Recognize Product 1 / AI Decision Validator evidence-presentation language as governed operator decision support instead of generic provider-assisted conversation.

## Before Behavior

From `AIGOL_ACLI_PRIMARY_INTERFACE_ADOPTION_V1`:

```text
TASKS_EXECUTED = 10
TASKS_PASSED = 0
TASKS_PARTIAL = 10
TASKS_FAILED = 0
MOST_COMMON_FRICTION_POINT = generic provider-assisted routing plus unavailable provider-backed completion
ACLI_PRIMARY_INTERFACE_ADOPTION_READY = NO
```

Eight of ten real development prompts selected:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Representative full prompt submissions failed closed on:

```text
provider-assisted conversation failed closed: OpenAI provider unavailable
```

## After Behavior

The same ten real development prompts now select:

```text
TASK-01 = NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
TASK-02 = NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
TASK-03 = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
TASK-04 = NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
TASK-05 = OPERATOR_DECISION_SUPPORT
TASK-06 = NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
TASK-07 = NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
TASK-08 = AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
TASK-09 = NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
TASK-10 = IMPROVE_PROVIDER_LAYER
```

Generic fallback after repair:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION = 0 / 10
```

All route selections preserve:

```text
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
governance_mutated = false
replay_mutated = false
```

## Validation Evidence

Focused test suite:

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py
84 passed
```

Regression spot-checks:

```text
python -m pytest tests/test_acli_certified_continuation_orchestration_v1.py tests/test_acli_end_to_end_human_prompt_certification_v1.py tests/test_conversation_native_development_context_integration_v1.py
11 passed
1 failed
```

The remaining targeted failure is downstream of routing:

```text
test_interactive_conversation_auto_continues_context_assembled_to_ppp
failure_reason = OpenAI provider adapter failed closed
```

The route reached:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
POST_CONTEXT_CONTINUATION_REACHED_PPP
CONVERSATION_PPP_HANDOFF_CREATED
```

The failure occurs after the repaired routing boundary and is not changed by this milestone.

Full repository suite:

```text
python -m pytest tests/
4903 passed
15 failed
1 skipped
```

The full-suite failures include existing browser/preview string assertions, OpenAI comparison attachment expectations, interactive output text expectations, persistent replay JavaScript assertions, and the downstream native-context auto-continuation provider failure above. The focused routing repair suite passed.

Route replay checks:

```text
/tmp/aigol_acli_routing_repair_task_01/AIGOL-ACLI-REPAIR-ROUTE-01 -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
/tmp/aigol_acli_routing_repair_task_02/AIGOL-ACLI-REPAIR-ROUTE-02 -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
/tmp/aigol_acli_routing_repair_task_03/AIGOL-ACLI-REPAIR-ROUTE-03 -> CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
/tmp/aigol_acli_routing_repair_task_04/AIGOL-ACLI-REPAIR-ROUTE-04 -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
/tmp/aigol_acli_routing_repair_task_05/AIGOL-ACLI-REPAIR-ROUTE-05 -> OPERATOR_DECISION_SUPPORT
/tmp/aigol_acli_routing_repair_task_06/AIGOL-ACLI-REPAIR-ROUTE-06 -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
/tmp/aigol_acli_routing_repair_task_07/AIGOL-ACLI-REPAIR-ROUTE-07 -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
/tmp/aigol_acli_routing_repair_task_08/AIGOL-ACLI-REPAIR-ROUTE-08 -> AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
/tmp/aigol_acli_routing_repair_task_09/AIGOL-ACLI-REPAIR-ROUTE-09 -> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
/tmp/aigol_acli_routing_repair_task_10/AIGOL-ACLI-REPAIR-ROUTE-10 -> IMPROVE_PROVIDER_LAYER
```

Documentation validation:

```text
git diff --check
```

## Governance Impact Statement

This repair only changes workflow selection before fallback.

It does not:

- invoke a provider;
- invoke a worker;
- create execution authorization;
- create an execution request;
- dispatch work;
- bypass approval;
- mutate governance;
- mutate replay;
- create a new governance layer;
- add a provider;
- treat provider output as governance authority.

The repair improves the probability that ACLI reaches existing lifecycle entries. Execution, authorization, worker request, worker dispatch, worker invocation, and execution remain governed downstream stages.

## Final Fields

```text
ROUTING_AMBIGUITY_REDUCED = YES
TASK_COMPLETION_ROUTING_FIXED = YES
WORKER_LIFECYCLE_REACHABLE = YES
EXECUTION_REQUEST_REACHABLE = YES
GENERIC_FALLBACK_REDUCED = YES
AUTHORIZATION_BOUNDARY_PRESERVED = YES
FAIL_CLOSED_PRESERVED = YES
ACLI_TASK_COMPLETION_IMPROVED = YES
```

## Completion Boundary

This repair does not claim that all tasks now complete end-to-end.

It claims the identified routing ambiguity is repaired for the real development task families reviewed here, and that existing lifecycle routes are selected before generic provider-assisted conversation fallback.
