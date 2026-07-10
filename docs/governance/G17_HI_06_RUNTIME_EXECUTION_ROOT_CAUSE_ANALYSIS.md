# G17-HI-06 - Governed Development Runtime Execution Root-Cause Analysis

Status: deterministic implementation RCA  
Date: 2026-07-10  
Scope: root-cause analysis only; no implementation change  
Final verdict: EXISTING_RUNTIME_NOT_INVOKED

## Executive Summary

After `/approve`, `./aicli` successfully delegates to `run_human_interface_runtime_entry(...)`. The canonical Human Interface Runtime Entry Service successfully invokes the injected governed runtime runner, `run_interactive_conversation(...)`.

The execution does not stop in `./aicli`, and it does not fail before entering the runtime runner.

The first divergence occurs inside `run_interactive_conversation(...)`: the approved prompt is processed as a normal conversation prompt and routes to `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`, not to the existing governed-development execution bridge. In the reproduced trace, that native-development branch fails closed with `OpenAI provider unavailable`, producing:

- `runtime_response_source: NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY`
- `runtime_response_status: CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED`
- `runtime_failed_turns: 1`
- `provider_invocation_reached: False`
- `worker_execution_reached: False`
- `replay_certification_reached: False`
- `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND`

Existing governed-development execution capability does exist. The repository contains an implemented bridge path that can continue a governed-development proposal into certified runtime and worker lifecycle replay. That path is not invoked by the current canonical UHI approval delegation.

Root cause: the UHI approval handoff enters the generic conversation runtime with a canonical prompt, but does not bind that approved prompt to the existing governed-development execution bridge path. The existing runtime is present, but the approved UHI execution path routes around it.

## Observed Runtime Evidence

Operational sequence reproduced through `./aicli`:

1. User submits a governed development request.
2. Platform Core prepares a governed implementation summary.
3. User enters `/approve`.
4. `./aicli` prints `Human approval recorded. Delegating to certified Platform Core runtime.`
5. Runtime returns `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND`.
6. Runtime result reports no provider, worker, or replay certification reached.
7. No governed development artifact is created.

Local implementation trace of a representative approved request produced:

```text
canonical_runtime_entry_status: CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND
runtime_entered: True
runtime_turn_count: 1
runtime_failed_turns: 1
runtime_response_source: NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY
runtime_response_status: CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
auto_continue_enabled: True
auto_continue_stop_reason: FAILED_CLOSED
manual_chatgpt_codex_transfer_required: True
governance_authorization_reached: False
provider_invocation_reached: False
worker_execution_reached: False
replay_certification_reached: False
```

The conversation output tail included:

```text
workflow: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
FAILED_CLOSED: OpenAI provider unavailable
```

This confirms that the runtime runner is reached, but the governed-development bridge and worker lifecycle are not reached.

## Execution Trace

The approval path begins in `./aicli`.

`run_reference_uhi_session(...)` handles `/approve`, extracts `pending_summary["canonical_runtime_prompt"]`, and calls `run_human_interface_runtime_entry(...)` with:

- `interface_name="aicli"`
- `human_requests=[prompt]`
- `governed_runtime_runner=run_interactive_conversation`
- `operator_context="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"`

Implementation evidence: `aigol/cli/aicli.py:306-329`.

`run_human_interface_runtime_entry(...)` then:

1. Re-resolves the supplied human request through `prepare_unified_human_interface_project_context(...)`.
2. Extracts `runtime_prompts` from admissible development intent.
3. Builds `conversation_args` with `auto_continue=True`.
4. Invokes `governed_runtime_runner(conversation_args, input_func=_input_sequence([*runtime_prompts, "exit"]), output_func=...)`.

Implementation evidence: `aigol/runtime/human_interface_runtime_entry_service.py:63-152`.

The service then reads the latest turn from the conversation result and determines canonical binding status using `_runtime_bound(...)`.

Implementation evidence: `aigol/runtime/human_interface_runtime_entry_service.py:153-204`.

`_runtime_bound(...)` requires:

- `failed_turns == 0`
- latest turn has `worker_invoked is True`
- latest turn has `replay_certification_reached is True`

Implementation evidence: `aigol/runtime/human_interface_runtime_entry_service.py:243-248`.

Because the actual latest turn is a failed native-development context turn with no worker invocation or replay certification, the service returns `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND`, which `./aicli` maps to `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND`.

Implementation evidence: `aigol/cli/aicli.py:673-680`.

## Runtime Control Flow

`run_interactive_conversation(...)` initializes session state and reads the approved prompt supplied by the canonical runtime entry service.

Implementation evidence: `aigol/cli/aigol_cli.py:3348-3422`.

It then routes the prompt through conversational routing unless a stateful gate is active.

Implementation evidence: `aigol/cli/aigol_cli.py:3460-3578`.

The observed routed workflow is `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`. That branch executes `run_conversation_native_development_intent_routing(...)`, then may continue into conversation-to-PPP handoff and worker execution if the branch reaches the proper conditions.

Implementation evidence: `aigol/cli/aigol_cli.py:5360-5515`.

In the reproduced UHI approval path, the branch fails closed before worker execution with provider unavailability. The native-development context integration runtime records native context assembly and returns `CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED`.

Implementation evidence:

- native context integration assembles context and returns integration status: `aigol/runtime/conversation_native_development_context_integration.py:67-96`
- native-development turn summaries expose `NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY`: `aigol/cli/aigol_cli.py:8376-8428`
- native context restore assigns `response_source: NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY`: `aigol/cli/aigol_cli.py:8644-8660`
- provider-unavailable failure marker is explicitly recognized: `aigol/runtime/conversation_provider_unavailable_clarification_fallback.py:28-32`

## Execution Bridge Analysis

The existing governed-development bridge path is implemented.

When `authoritative_workflow_id == CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW`, `run_interactive_conversation(...)` calls `propose_acli_governed_development_execution(...)`.

Implementation evidence: `aigol/cli/aigol_cli.py:5242-5253`.

If the bridge proposal requires approval and the runtime entry context has `auto_continue=True`, the code calls `_continue_governed_development_bridge_to_certified_runtime(...)`.

Implementation evidence: `aigol/cli/aigol_cli.py:5254-5346`.

The continuation helper is explicitly designed to continue an already-approved UHI governed-development bridge into certified runtime.

Implementation evidence: `aigol/cli/aigol_cli.py:1188-1202`.

That helper performs:

- native development context integration;
- post-context PPP routing;
- worker request continuation;
- worker assignment;
- worker dispatch;
- worker invocation;
- worker execution candidate;
- external task package;
- provider reachability;
- result validation;
- replay certification.

Implementation evidence: `aigol/cli/aigol_cli.py:1203-1268`.

The actual UHI approval trace does not enter this bridge branch. Therefore the execution bridge capability exists, but is not invoked for the approved UHI prompt.

## Artifact Generation Analysis

Artifact generation is not intentionally skipped at the worker layer. The worker/replay artifact path exists behind `_continue_ppp_handoff_to_worker_request(...)`.

That helper creates:

- implementation handoff visibility;
- governed implementation dry run;
- execution authorization;
- worker invocation request;
- worker lifecycle continuation.

Implementation evidence: `aigol/cli/aigol_cli.py:1097-1180`.

The full runtime also contains direct approval-resume execution logic that can prepare dry run, authorize execution, create worker invocation request, assign worker, dispatch worker, invoke worker, start execution, capture result, validate result, and continue to executable bundle handling.

Implementation evidence: `aigol/cli/aigol_cli.py:4068-4325`.

The current UHI approval path does not create the expected governed development artifact because it does not reach either of those execution-producing branches. It reaches native context assembly and fails closed before the continuation conditions are satisfied.

## Root Cause

The root cause is not a failure of `/approve` handling in `./aicli`.

The root cause is not that `run_human_interface_runtime_entry(...)` refuses to invoke the runtime.

The root cause is that the approved UHI runtime prompt is handed to `run_interactive_conversation(...)` as a normal prompt, without a binding that forces or constructs the existing governed-development execution bridge for the already-approved Platform Core implementation summary.

As a result:

1. `run_human_interface_runtime_entry(...)` invokes `run_interactive_conversation(...)`.
2. `run_interactive_conversation(...)` routes the prompt through normal conversational routing.
3. The prompt routes to `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`.
4. Native development context assembly fails closed with `OpenAI provider unavailable`.
5. The existing governed-development bridge continuation is not invoked.
6. No worker lifecycle or governed development artifact is created.
7. The canonical entry service correctly reports partial binding because `_runtime_bound(...)` is false.

## Existing Reuse Opportunities

Existing reusable implementation is present:

- `propose_acli_governed_development_execution(...)` branch in `run_interactive_conversation(...)`.
- `_continue_governed_development_bridge_to_certified_runtime(...)`.
- `_continue_ppp_handoff_to_worker_request(...)`.
- worker lifecycle continuation and replay certification fields consumed by `_interactive_acli_governed_development_bridge_turn_summary(...)`.

The minimal reuse path should bind the approved UHI implementation summary to the existing governed-development bridge continuation path instead of introducing a new runtime or new artifact-generation concept.

## Minimal Corrective Action

The minimal corrective action is to add or repair the execution bridge binding between canonical UHI approval and the existing governed-development bridge.

The binding should ensure that when Platform Core approval summary says:

```text
runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME
```

and `/approve` delegates through `run_human_interface_runtime_entry(...)`, the runtime runner receives enough deterministic state to enter the existing governed-development bridge continuation path rather than normal native-development conversational routing.

This can be achieved by reusing existing code paths:

- preserve `run_human_interface_runtime_entry(...)` as the shared entry;
- preserve `run_interactive_conversation(...)` as the governed runtime runner;
- preserve `_continue_governed_development_bridge_to_certified_runtime(...)` as the certified continuation;
- bind UHI approval to the governed-development bridge state or workflow selection before generic routing can divert the prompt to native context assembly.

No new governance, replay, PCCL, or Human Interface architecture is required.

## Architectural Impact Assessment

The architecture remains valid:

- Platform Core owns approval and runtime continuation.
- Human Interfaces only collect approval and delegate.
- Existing governed runtime and worker lifecycle capabilities are implemented.
- The observed failure is localized to execution-path binding.

The impact is implementation-level:

- canonical UHI approval reaches runtime entry;
- runtime entry invokes the runner;
- runner uses generic routing;
- generic routing does not reliably select the existing governed-development bridge for an already-approved UHI summary.

This is a binding defect, not a need to redesign Platform Core.

## Final Recommendation

Repair the canonical UHI approval-to-runtime binding so approved Platform Core implementation summaries enter the existing governed-development bridge continuation path.

Do not introduce a new execution runtime.

Do not move execution logic into `./aicli`.

Do not bypass approval, governance, replay, or worker lifecycle certification.

Reuse the existing bridge and worker lifecycle implementation already present in `aigol/cli/aigol_cli.py`.

## Final Verdict

EXISTING_RUNTIME_NOT_INVOKED

The canonical runtime entry is reached, but the existing governed-development execution bridge and worker lifecycle runtime are not invoked. The approved UHI prompt is processed through normal conversation routing, routes to native development context assembly, fails closed on provider unavailability, and returns partial binding before governed development artifact generation can occur.
