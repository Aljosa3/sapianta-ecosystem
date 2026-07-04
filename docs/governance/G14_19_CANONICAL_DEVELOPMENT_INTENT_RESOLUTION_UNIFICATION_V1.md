# G14-19 Canonical Development Intent Resolution Unification V1

Status: canonical development intent resolution implemented with provider-availability caveat for live external completion.

Final verdict: CANONICAL_DEVELOPMENT_INTENT_RESOLUTION_PARTIALLY_IMPLEMENTED

## 1. Executive Summary

G14-19 implemented the canonical deterministic Development Intent Resolution service identified by G14-18.

The implementation removes the proven fragmentation where:

```text
/send -> governed implementation summary
/approve -> AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
```

could occur for the same request.

The new canonical owner is:

```text
Platform Core Project Services
```

Implementation:

```text
aigol/runtime/platform_core_project_services.py
resolve_development_intent(...)
canonical_development_runtime_prompt(...)
```

Both `/send` and `/approve` now consume the same Platform Core decision artifact:

```text
PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_ARTIFACT_V1
```

ACLI Next remains a thin adapter. It requests the Platform Core decision, renders the governed summary, collects approval, and delegates.

The previously reproduced divergence prompt:

```text
Implement governed policy.
```

now enters runtime binding instead of returning `AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED`.

Live repository runtime validation reached:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
native_development_task_intake
development_context_assembly
post_context_continuation
Provider Platform
```

The live unmocked run then failed closed at provider availability:

```text
failure_reason: OpenAI provider unavailable
operational_failure_classification: PROVIDER_AVAILABILITY
```

Because the live external provider path did not complete to worker execution and Replay certification in this environment, the final verdict is partial rather than full certification.

Final verdict: CANONICAL_DEVELOPMENT_INTENT_RESOLUTION_PARTIALLY_IMPLEMENTED

## 2. Implementation Summary

### 2.1 Canonical Service

Added:

```text
aigol/runtime/platform_core_project_services.py
resolve_development_intent(...)
```

The service returns a deterministic artifact containing:

```text
development_intent_resolution_authority: PLATFORM_CORE
raw_prompt
goal_oriented_request_detected
guided_development_request_detected
clarification_required
goal_mapping
governed_request
refined_message
canonical_runtime_prompt
native_development_prompt_detected
summary_admissible
runtime_binding_admissible
same_decision_for_send_and_approve
```

The key invariant is:

```text
summary_admissible == runtime_binding_admissible
```

for governed summary creation and runtime binding admission.

### 2.2 Canonical Runtime Prompt

Added:

```text
canonical_development_runtime_prompt(...)
```

Purpose:

```text
produce one deterministic Platform Core prompt consumed by both governed summary and runtime binding
```

For prompts already accepted by native task intake, the canonical runtime prompt is unchanged.

For governed but underspecified policy-style implementation prompts, Platform Core normalizes the request into a native development governance workflow prompt, for example:

```text
Implement governed policy.
```

becomes:

```text
Implement governed policy. Implement as a native development governance workflow.
```

This normalization is deterministic and occurs inside Platform Core Project Services, not inside ACLI Next.

### 2.3 ACLI Next Consumer Changes

Updated:

```text
aigol/acli_next/conversational.py
```

Before:

- `/send` used `goal_oriented_request_detected(...)`, `guided_development_request_detected(...)`, and `guided_development_clarification_required(...)` directly;
- `/approve` delegated to runtime binding, which used a different native-development gate.

After:

- `/send` calls `resolve_development_intent(...)`;
- governed summaries are produced only when `summary_admissible` is true;
- ambiguous requests still produce clarification;
- `pending_summary["refined_message"]` is the canonical Platform Core runtime prompt.

### 2.4 Runtime Binding Consumer Changes

Updated:

```text
aigol/cli/aigol_cli.py
_run_acli_next_runtime_bound_session(...)
```

Before:

```text
is_native_development_prompt(prompt)
```

was used directly as the runtime binding gate.

After:

```text
resolve_development_intent(message=prompt)
```

is used by runtime binding. Runtime entry occurs only for prompts whose canonical resolution reports:

```text
runtime_binding_admissible: True
```

The runtime receives the same canonical prompt produced by Platform Core Project Services.

## 3. Responsibility Map

| Capability | Canonical Owner | Implementation | ACLI Next Role |
| --- | --- | --- | --- |
| Development Intent Resolution | Platform Core Project Services | `resolve_development_intent(...)` | Consume and render |
| Goal Mapping | Platform Core Project Services | `goal_mapping_from_workspace(...)` | Consume and render |
| Contextual Task Mapping | Platform Core Project Services | `project_knowledge_context_from_workspace(...)` | Consume and render |
| Clarification Need | Platform Core Project Services | `resolve_development_intent(...)` via existing clarification helpers | Present questions |
| Governed Summary | Platform Core decision, ACLI rendering | `_guided_development_summary(...)` consumes resolution | Render summary |
| Runtime Binding Admission | Platform Core decision consumed by CLI binding | `_run_acli_next_runtime_bound_session(...)` | Delegate |
| Runtime Orchestration | Platform Core / OCS | existing certified runtime | No ownership |
| Governance | Governance | existing authorization runtime | No ownership |
| Replay | Replay | existing evidence runtime | No ownership |
| Worker Execution | Worker Platform | existing worker lifecycle | No ownership |

## 4. Removed Duplicated Responsibility

Removed from ACLI Next summary admission:

```text
direct independent use of goal_oriented_request_detected(...)
direct independent use of guided_development_request_detected(...)
direct independent use of guided_development_clarification_required(...)
```

ACLI Next still imports and renders Platform Core project service results, but it no longer independently decides whether a request should receive a summary that claims runtime continuation.

Runtime binding no longer independently admits approved requests with only:

```text
is_native_development_prompt(...)
```

It now consumes the same Platform Core resolution artifact.

## 5. Regression Evidence

New regression file:

```text
tests/test_g14_19_development_intent_resolution_unification_v1.py
```

Coverage:

| Scenario | Prompt | Expected Result |
| --- | --- | --- |
| A | `Implement a native validation helper for replay evidence summaries.` | summary and runtime binding admissible |
| B | `Improve runtime validation reporting.` | summary and runtime binding admissible |
| C | `Extend runtime binding coverage for native development.` | summary and runtime binding admissible |
| D | `Improve the system.` | clarification required; summary and runtime binding not admissible |
| E | `Implement governed policy.` | summary and runtime binding admissible |

Interactive regression:

```text
Implement governed policy.
/send
/approve
```

with controlled provider and worker adapters now reaches:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND
runtime_entered: True
governance_authorization_reached: True
provider_invocation_reached: True
worker_execution_reached: True
replay_certification_reached: True
```

## 6. Runtime Evidence

Live repository runtime command:

```text
python -m aigol.cli.aigol_cli next \
  --session-id G14-19-REAL-RUNTIME \
  --runtime-root /tmp/aigol_g14_19_real_runtime \
  --workspace /home/pisarna/work/sapianta \
  --created-at 2026-07-04T00:00:00Z
```

Interactive input:

```text
Implement governed policy.
/send
/approve
exit
```

Observed output:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_PARTIALLY_BOUND
runtime_entered: True
prompt: Implement governed policy. Implement as a native development governance workflow.
```

The previous failure state is no longer observed:

```text
AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
```

Runtime evidence root:

```text
/tmp/aigol_g14_19_real_runtime/G14-19-REAL-RUNTIME
```

Representative evidence:

```text
TURN-000001/conversational_cli_routing/001_conversational_workflow_selection_recorded.json
workflow_id: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
routing_status: WORKFLOW_SELECTED
```

```text
TURN-000001/native_development_task_intake/000_native_development_task_intake_recorded.json
```

```text
TURN-000001/development_context_assembly/004_development_context_assembly_returned.json
```

Provider availability evidence:

```text
TURN-000001/post_context_continuation/001_post_context_continuation_returned.json
continuation_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
operational_failure_classification: PROVIDER_AVAILABILITY
provider_resilience_status: PROVIDER_UNAVAILABLE_FAIL_CLOSED
```

## 7. Architectural Assessment

Ownership boundaries remain preserved:

- ACLI Next remains a thin adapter.
- Platform Core Project Services own Development Intent Resolution.
- Platform Core / OCS continue to own runtime coordination.
- Governance remains authorization authority.
- Replay remains evidence authority.
- Worker Platform remains execution authority.
- Provider Platform remains provider boundary.

No new authority layer was introduced.

No probabilistic classifier was introduced.

No additional parallel classifier was introduced.

## 8. Remaining Gap

The Development Intent Resolution fragmentation is fixed for the covered path.

Full operational certification remains blocked by an external provider availability condition in the live unmocked runtime environment:

```text
OpenAI provider unavailable
```

This is not an intent-resolution defect and not an architectural ownership defect.

## 9. Validation Evidence

Validation performed:

```text
python -m py_compile aigol/runtime/platform_core_project_services.py aigol/acli_next/conversational.py aigol/cli/aigol_cli.py tests/test_g14_19_development_intent_resolution_unification_v1.py
python -m pytest tests/test_g14_19_development_intent_resolution_unification_v1.py -q
python -m pytest tests/test_native_development_task_intake_and_session_resume_v1.py::test_native_development_prompt_detection_is_conservative tests/test_g14_04_conversational_development_workflow_v1.py tests/test_g14_08a_platform_core_project_services_extraction_v1.py -q
python -m pytest tests/test_conversational_cli_runtime_v1.py::test_task_completion_repair_routes_real_development_prompts_before_provider_fallback -q
git diff --check
```

Validation result:

```text
clean
```

Final verdict: CANONICAL_DEVELOPMENT_INTENT_RESOLUTION_PARTIALLY_IMPLEMENTED
