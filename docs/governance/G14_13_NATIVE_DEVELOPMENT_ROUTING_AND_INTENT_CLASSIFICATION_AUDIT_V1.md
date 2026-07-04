# G14-13 Native Development Routing and Intent Classification Audit V1

Status: native development routing root cause identified.

Final verdict: NATIVE_DEVELOPMENT_ROUTING_ROOT_CAUSE_IDENTIFIED

## 1. Executive Summary

G14-13 audited why a real Generation 14 acceptance-test request reached a governed implementation summary and human approval, but then remained in Capability Coverage / Existing Capability Audit instead of entering the certified Native Development Runtime.

The observed failure was not architectural.

The root cause was missing deterministic intent coverage for implementation-improvement phrasing:

```text
Improve provider availability handling.
```

The Native Development Intent Classifier existed and was invoked, but the tested request did not match the classifier vocabulary in the failing implementation. Because the runtime binding wrapper gates native runtime entry on that classifier, it returned:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
runtime_entered: False
```

The request therefore remained in the ACLI Next presentation / Platform Core operational dashboard path, whose current workflow stage was:

```text
Classify Capability Coverage
```

Root cause classification:

```text
Missing Intent Classification
```

This means missing deterministic classification coverage for the tested implementation intent, not absence of a classifier.

Final verdict: NATIVE_DEVELOPMENT_ROUTING_ROOT_CAUSE_IDENTIFIED

## 2. Audit Scope

The audit reviewed:

- the Native Development Intent Classifier;
- ACLI Next runtime binding;
- conversational workflow approval transition;
- interactive dispatcher ordering;
- conversational CLI routing;
- Platform Core operational dashboard output;
- native development context integration;
- post-entry continuation to PPP routing;
- provider and worker runtime evidence from the corrected validation path.

No implementation changes were made by this audit.

## 3. Runtime Evidence

Failing evidence root:

```text
/tmp/aigol_g14_12_repro_improve/G14-12-REPRO-IMPROVE/RUN-000001
```

Observed request:

```text
Improve provider availability handling.
```

The failing run produced only ACLI Next conversational presentation, execution-plan preview, and daily dashboard presentation artifacts.

Key evidence:

| Evidence | Finding |
| --- | --- |
| `000_acli_next_conversational_session_presented.json` | `session_status: ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED`; latest prompt was the implementation-improvement request. |
| `dashboard/000_acli_next_daily_dashboard_presented.json` | Platform Core workflow stage was `Classify Capability Coverage`; next operation was `Existing Capability Audit`. |
| `execution_plan/execution_plan/003_acli_next_execution_plan_completed.json` | Provider and worker invocation were false; the plan was descriptive only. |
| Runtime binding output | `runtime_binding_status: AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED`; `runtime_entered: False`. |

The failing replay root did not contain a native runtime turn tree, `post_context_continuation`, provider proposal production, worker lifecycle continuation, or Replay certification artifacts.

This confirms that the stop occurred before native runtime dispatch.

## 4. Native Development Intent Classifier

A deterministic Native Development Intent Classifier exists.

Implementation location:

```text
aigol/runtime/native_development_task_intake_runtime.py
```

Primary functions:

```text
is_native_development_prompt(human_prompt)
is_plain_native_development_prompt(human_prompt)
```

Classifier ownership:

```text
Platform Core native development intake runtime
```

The classifier is deterministic:

- it normalizes the prompt;
- checks milestone identifiers and native development markers;
- checks freeform development subjects;
- rejects unacceptable authority and high-risk external/deployment phrasing;
- returns a boolean gate used by runtime binding and routing visibility.

The classifier is reused by:

- ACLI Next runtime binding in `aigol/cli/aigol_cli.py`;
- interactive conversation dispatch in `aigol/cli/aigol_cli.py`;
- routing visibility candidate generation in `aigol/cli/aigol_cli.py`;
- conversational CLI native development routing in `aigol/runtime/conversational_cli_runtime.py`.

## 5. Runtime Binding Decision Chain

The runtime binding path is implemented in:

```text
aigol/cli/aigol_cli.py
```

Decision chain:

| Step | Input | Decision | Owner | Implementation |
| --- | --- | --- | --- | --- |
| 1 | Approved prompt list | Check `any(is_native_development_prompt(prompt) for prompt in prompts)` | Platform Core runtime binding integration | `_run_acli_next_runtime_bound_session` |
| 2 | Classifier result false | Return presentation-only result | ACLI Next binding adapter delegating to classifier result | `_run_acli_next_runtime_bound_session` |
| 3 | Returned status | Set `AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED` | ACLI Next presentation result | `_run_acli_next_runtime_bound_session` |
| 4 | Dashboard presentation | Show governed development workflow visibility | Platform Core operational exposure | ACLI Next dashboard / operational snapshot |
| 5 | Workflow stage | Present `Classify Capability Coverage` and `Existing Capability Audit` | Platform Core workflow visibility | Dashboard artifact |

The critical gate is:

```text
if not any(is_native_development_prompt(prompt) for prompt in prompts):
    runtime_binding_status = AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
    runtime_entered = False
```

Because the tested implementation-improvement phrase did not match the classifier in the failing implementation, the native runtime was never called.

## 6. Complete Routing Trace After Approval

The tested approval path was:

```text
Human approval
-> ACLI Next runtime binding wrapper
-> Native Development Intent Classifier
-> classifier returned false for the approved request
-> runtime binding returned AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
-> ACLI Next presented Platform Core dashboard state
-> dashboard current stage: Classify Capability Coverage
-> dashboard next operation: Existing Capability Audit
```

What did not occur in the failing run:

- interactive native development dispatch;
- `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`;
- post-entry continuation gate;
- PPP routing continuation;
- provider invocation;
- execution authorization;
- worker invocation;
- result validation;
- Replay certification.

## 7. Capability Coverage Selection

Capability Coverage was selected as the visible workflow stage because the runtime binding path did not enter native execution.

It was not selected by Governance, Provider Platform, Worker Platform, or Replay.

It was not caused by provider availability.

It was not caused by missing Platform Core runtime capability.

It was caused by the binding wrapper concluding that native development runtime binding was not required after the deterministic classifier failed to recognize the approved implementation request.

Capability Coverage therefore represented the presentation fallback state of the governed development workflow, not a successful implementation dispatcher decision.

## 8. Native Development Runtime Reachability

The Native Development Runtime already exists and is reachable.

Implementation evidence:

| Capability | Evidence |
| --- | --- |
| Native task intake | `aigol/runtime/native_development_task_intake_runtime.py` |
| Native context integration | `aigol/runtime/conversation_native_development_context_integration.py` |
| Post-entry continuation gate | `aigol/runtime/post_entry_continuation_gate_runtime.py` |
| PPP routing continuation | `aigol/runtime/context_assembled_to_ppp_routing_continuation.py` |
| Worker continuation | `aigol/cli/aigol_cli.py` continuation into worker request, authorization, dispatch, invocation, result validation, and Replay certification |

Corrected runtime evidence root:

```text
/tmp/aigol_g14_12_approval_routing_validation_escalated/G14-12-APPROVAL-ROUTING-VALIDATION-ESCALATED/TURN-000001
```

Corrected evidence showed:

- `conversational_cli_routing/000_conversational_routing_decision_recorded.json` selected `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`;
- `post_entry_continuation_gate/000_post_entry_continuation_gate_recorded.json` recorded `CONTINUATION_ALLOWED`;
- `post_context_continuation/001_post_context_continuation_returned.json` recorded `POST_CONTEXT_CONTINUATION_REACHED_PPP`;
- `execution_authorization/003_authorization_result_recorded.json` recorded `EXECUTION_AUTHORIZED`;
- `worker_invocation/003_invocation_result_recorded.json` recorded `WORKER_INVOKED`;
- `result_validation/002_result_validation_returned.json` recorded `RESULT_VALIDATION_COMPLETED`;
- `replay_certification/001_replay_certification_returned.json` recorded `REPLAY_CERTIFICATION_COMPLETED`.

Therefore the Native Development Runtime was reachable; it was bypassed by the initial classifier gate in the failing path.

## 9. Intent Classification Analysis

Deterministic intent classification exists, but it is distributed across specialized deterministic classifiers rather than one universal enum classifier.

Observed supported intent families include:

| Intent Family | Evidence |
| --- | --- |
| Native development | `is_native_development_prompt` and `is_plain_native_development_prompt` |
| Conversational workflow routing | `route_conversational_cli_intent` and workflow constants in `conversational_cli_runtime.py` |
| Human decisions | `normalize_human_decision` and approval/reject/modify handling |
| Lifecycle commands | `_is_lifecycle_command_prompt` |
| OCS cognition | `is_ocs_llm_cognition_prompt` |
| Governance/domain lifecycle | domain proposal, approval, authorization, worker lifecycle workflow selectors |
| Dashboard/status/replay requests | conversational route candidates and workflow constants |

The implementation does not contain a single reusable universal classifier that returns a canonical enum such as:

```text
IMPLEMENT
ANALYZE
AUDIT
CERTIFY
QUESTION
EXECUTE
REPLAY
STATUS
```

Instead, it uses deterministic specialized classifiers and route candidates. This is sufficient for the certified architecture when coverage is complete, but the failing request exposed a vocabulary gap in the native development implementation-intent branch.

## 10. Dispatcher and Routing Priority Analysis

Dispatcher ordering did not directly cause the original `AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED` result because native runtime binding returned before the interactive dispatcher ran.

However, a secondary routing hazard existed in conversational CLI task-completion routing:

- broad `improve provider` phrasing could be classified as provider-layer review;
- provider-layer routing appears before native development context integration in routing visibility candidate ordering;
- this could divert genuine provider implementation requests toward read-only provider-layer audit behavior.

That hazard explains why capability audit/provider-layer behavior could be observed after partial correction, but the primary failing evidence with `runtime_entered: False` occurred earlier at the runtime binding classifier gate.

## 11. Ownership Analysis

| Routing Decision | Owner | Location | Assessment |
| --- | --- | --- | --- |
| Human input capture and `/approve` collection | AiGOL Next | `aigol/acli_next/conversational.py` | Correct thin-interface behavior. |
| Native development prompt detection | Platform Core native development intake runtime | `aigol/runtime/native_development_task_intake_runtime.py` | Correct ownership; coverage gap in failing implementation. |
| Runtime binding dispatch | ACLI Next binding adapter delegating into Platform Core runtime | `aigol/cli/aigol_cli.py` | Correct ownership; relies on classifier result. |
| Conversational route selection | PGSP/UBTR/CSA-compatible conversational runtime path | `aigol/runtime/conversational_cli_runtime.py` | Correct ownership pattern; secondary provider-layer overmatch risk existed. |
| Workflow stage presentation | Platform Core operational exposure | ACLI Next dashboard artifacts | Correct presentation-only behavior. |
| Governance authorization | Governance | execution authorization runtime | Not reached in failing run. |
| Worker execution | Worker Platform | worker lifecycle continuation | Not reached in failing run. |

No routing responsibility was proven to be incorrectly owned.

The problem was incomplete deterministic intent coverage for the tested implementation request.

## 12. Root Cause Classification

Required classification:

```text
Missing Intent Classification
```

Meaning:

```text
The Native Development Intent Classifier existed and was invoked, but the tested implementation-improvement request was outside its deterministic vocabulary in the failing implementation.
```

Rejected classifications:

| Classification | Reason Rejected |
| --- | --- |
| Routing Priority | Secondary risk only; failing runtime evidence stopped before dispatcher priority mattered. |
| Existing Intent Classifier Not Used | Rejected because `_run_acli_next_runtime_bound_session` explicitly invoked `is_native_development_prompt`. |
| Dispatcher Ordering | Rejected as primary cause because the failing result returned before interactive native dispatch. |
| Runtime Binding Defect | Rejected as primary cause because binding behaved according to its classifier gate. |
| Platform Core Integration Gap | Rejected because the native runtime was reachable once the classifier selected it. |
| UBTR Integration Gap | Rejected because UBTR evidence exists in corrected native route; failing run never reached it. |
| Configuration Gap | Rejected because provider configuration was not reached in the failing path. |
| Documentation Gap | Rejected because implementation evidence identifies the classifier vocabulary gap. |
| No Defect Detected | Rejected because runtime evidence proves unexpected presentation-only behavior for an implementation request. |

## 13. Architectural Assessment

The certified architecture remains valid.

The evidence confirms:

- AiGOL Next remained a thin human interface;
- Platform Core remained responsible for workflow state and native development runtime coordination;
- Governance did not authorize because the runtime did not enter the execution path;
- Worker Platform did not execute because dispatch was never reached;
- Replay preserved the presentation-only evidence;
- no authority moved into AiGOL Next.

The defect was implementation coverage in deterministic intent classification, not architectural responsibility leakage.

## 14. Certification Summary

G14-13 explains the observed Generation 14 acceptance-test failure:

```text
implementation request
-> governed summary
-> /approve
-> native classifier did not recognize the request
-> runtime binding returned NOT_REQUIRED
-> ACLI Next displayed Platform Core Capability Coverage state
-> native runtime was not entered
```

The audit is complete because it identifies:

- where the Native Development Intent Classifier exists;
- where it is invoked;
- why the failing request did not enter native execution;
- why Capability Coverage was displayed;
- why Governance, Provider, Worker, and Replay certification were not reached;
- why the issue is implementation classification coverage rather than architecture.

Final verdict: NATIVE_DEVELOPMENT_ROUTING_ROOT_CAUSE_IDENTIFIED

## 15. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: NATIVE_DEVELOPMENT_ROUTING_ROOT_CAUSE_IDENTIFIED
