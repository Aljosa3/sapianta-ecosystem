# G17-HI-07 Runtime Invocation Environment Verification

Status: deterministic implementation pre-check.

Final verdict: `EXECUTION_BRIDGE_SELECTION_FIX_REQUIRED`.

## Executive Summary

The observed runtime failure is not caused solely by local development environment configuration or missing provider configuration.

The approved Human Interface path reaches `run_human_interface_runtime_entry(...)`, which invokes `run_interactive_conversation(...)` with `auto_continue=True`. The runtime then routes the approved Platform Core prompt into the native development provider path, where OpenAI proposal production fails closed with `OpenAI provider unavailable`.

That provider failure is real for the selected path, but it is not the first implementation divergence. The first divergence is that the existing governed-development bridge continuation path is not selected for the already-approved canonical Human Interface runtime entry.

Root cause classification: `D) Execution bridge selection defect`.

## Observed Runtime Evidence

Reproduced runtime result after `/approve`:

- `runtime_entered`: `True`
- `runtime_status`: `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND`
- `canonical_runtime_entry_status`: `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND`
- `runtime_turn_count`: `1`
- `runtime_failed_turns`: `1`
- `runtime_response_source`: `NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY`
- `runtime_response_status`: `CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED`
- `auto_continue_enabled`: `True`
- `auto_continue_stop_reason`: `FAILED_CLOSED`
- `manual_chatgpt_codex_transfer_required`: `True`
- `governance_authorization_reached`: `False`
- `provider_invocation_reached`: `False`
- `worker_execution_reached`: `False`
- `replay_certification_reached`: `False`

The output tail includes:

```text
ROUTING DECISION
workflow: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
FAILED_CLOSED: OpenAI provider unavailable
Workflow Name: NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY
Workflow State: FAILED_CLOSED
```

This proves that Human Interface approval reached runtime entry, but the governed-development worker lifecycle was not reached.

## Execution Trace Review

The approved `./aicli` path calls `run_human_interface_runtime_entry(...)` with `governed_runtime_runner=run_interactive_conversation` and `operator_context="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"` from `aigol/cli/aicli.py`.

Inside `run_human_interface_runtime_entry(...)`, the service constructs `conversation_args` with `auto_continue=True`, then invokes the injected runner with the prepared runtime prompts and a trailing `exit` input. Evidence: `aigol/runtime/human_interface_runtime_entry_service.py:137`.

The service then derives the binding status from the latest conversation turn. It only considers the runtime bound when there are zero failed turns, the worker was invoked, and replay certification was reached. Evidence: `aigol/runtime/human_interface_runtime_entry_service.py:243`.

The reproduced runtime has one failed turn and neither worker invocation nor replay certification, so `PARTIALLY_BOUND` is the expected status for the observed turn.

## Provider Resolution Review

The selected runtime path uses the OpenAI provider adapter imported by `aigol/cli/aigol_cli.py` from `aigol.provider.providers.openai_provider`. Evidence: `aigol/cli/aigol_cli.py:481`.

That adapter resolves credentials from `OPENAI_API_KEY`, not `AIGOL_OPENAI_API_KEY`. Evidence: `aigol/provider/providers/openai_provider.py:244`.

The provider runtime has a deterministic readiness failure reason for missing credentials: `OPENAI_API_KEY is required`. Evidence: `aigol/provider/provider_runtime.py:418`.

The observed failure is instead `OpenAI provider unavailable`. The adapter emits that message when the client call raises an exception or when the HTTP transport raises `URLError`, `TimeoutError`, or JSON decode failure. Evidence: `aigol/provider/providers/openai_provider.py:111` and `aigol/provider/providers/openai_provider.py:152`.

Therefore, the selected provider path fails closed during provider invocation availability, not at deterministic missing-credential detection.

## Environment Verification

Current environment presence check:

- `OPENAI_API_KEY_PRESENT=True`
- `AIGOL_OPENAI_API_KEY_PRESENT=False`

For this selected `aigol_cli` provider path, `OPENAI_API_KEY` is the relevant credential. The missing `AIGOL_OPENAI_API_KEY` belongs to a separate runtime provider implementation and is not the deterministic cause of the observed `OpenAI provider unavailable` message in this path.

The evidence does not support classifying the primary root cause as development environment configuration or provider configuration. Provider availability remains a live runtime dependency for the native provider path, but that path is not the intended terminal explanation for why the already-approved governed-development bridge is not reached.

## Routing Verification

`run_interactive_conversation(...)` restores or detects stateful gates before normal routing. It only forces `CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW` when `pending_governed_development_bridge is not None` and the human prompt is an approve/reject/modify decision. Evidence: `aigol/cli/aigol_cli.py:3572`.

If no stateful governed-development bridge is present, the runtime uses normal conversational routing. Evidence: `aigol/cli/aigol_cli.py:3558`.

The observed approved Platform Core runtime prompt did not restore or create a pending governed-development bridge before routing. It therefore entered `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`, not the governed-development bridge workflow.

The native development branch then runs native development routing and handoff behavior. Evidence: `aigol/cli/aigol_cli.py:5360`.

For runtime, worker, or CLI task kinds, development context assembly marks provider proposal as required. Evidence: `aigol/runtime/development_context_assembly_runtime.py:571`.

The post-context PPP continuation requires `PROVIDER_REQUIRED`, builds a provider request handoff, and calls `produce_provider_development_proposal(...)`. Evidence: `aigol/runtime/conversation_ppp_routing_integration.py:117` and `aigol/runtime/conversation_ppp_routing_integration.py:163`.

This explains the observed provider fail-closed path without treating it as the first divergence.

## Execution Bridge Selection Review

An existing bridge continuation implementation already exists:

- `_continue_governed_development_bridge_to_certified_runtime(...)` is explicitly documented as continuing an already-approved UHI governed-development bridge into certified runtime. Evidence: `aigol/cli/aigol_cli.py:1188`.
- It performs native context integration, PPP continuation, worker request continuation, and returns worker/replay lifecycle fields. Evidence: `aigol/cli/aigol_cli.py:1203`.
- The governed-development workflow branch proposes `propose_acli_governed_development_execution(...)`. Evidence: `aigol/cli/aigol_cli.py:5242`.
- In canonical Human Interface runtime entry context, with `auto_continue=True`, that branch calls `_continue_governed_development_bridge_to_certified_runtime(...)`. Evidence: `aigol/cli/aigol_cli.py:5306`.
- On success, it sets `worker_invoked`, `replay_certification_reached`, `approval_granted`, and `execution_authorized`. Evidence: `aigol/cli/aigol_cli.py:5327`.

The bridge continuation is therefore implemented and reusable. The defect is selection: the already-approved Platform Core runtime prompt does not enter the governed-development bridge workflow before normal native provider routing.

## Root Cause Classification

Classification: `D) Execution bridge selection defect`.

Rejected classifications:

- `A) Development environment configuration`: rejected because runtime entry and the selected provider path both execute; the first divergence is workflow selection before environment-dependent provider failure.
- `B) Provider configuration`: rejected because `OPENAI_API_KEY` is present for the selected adapter, and missing-key failure has a distinct deterministic message.
- `C) Implementation routing defect`: partially descriptive, but less precise than the observed defect. Normal routing is functioning; the missing behavior is canonical UHI selection of the existing execution bridge.
- `E) Expected reference-runtime behavior`: rejected because an existing canonical UHI auto-continuation bridge exists and is not selected.

## Required Action

No code change is proposed for provider configuration, provider discovery, governance architecture, replay, PCCL, or runtime architecture.

The smallest corrective action is to bind canonical Human Interface approval runtime entry to the existing governed-development bridge selection path before native provider routing. The correction should reuse the existing bridge continuation implementation and should not introduce a new execution concept.

The implementation should ensure that an already-approved Platform Core governed implementation summary is represented to `run_interactive_conversation(...)` as a governed-development bridge continuation, or otherwise forces the existing `CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW` branch under `operator_context="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"` when the runtime prompt is an approved canonical governed-development prompt.

## Architectural Impact Assessment

No Platform Core architecture change is required.

No Governance redesign is required.

No Replay redesign is required.

No PCCL redesign is required.

No provider architecture change is required.

The required action is a Human Interface runtime-entry binding correction that selects an existing certified bridge path earlier and avoids misrouting approved governed-development execution into the generic native provider proposal path.

## Final Recommendation

Implement a minimal execution bridge selection fix in the canonical Human Interface runtime-entry path.

The fix should preserve the current thin Human Interface adapter model:

- Human Interface collects approval.
- Platform Core prepares the canonical runtime prompt.
- Runtime entry invokes the certified runtime.
- Certified runtime selects the existing governed-development bridge continuation.
- Worker lifecycle and replay certification determine bound status.

Provider availability should remain fail-closed for provider-dependent workflows, but it should not mask the bridge-selection requirement for already-approved governed-development execution.

## Final Verdict

`EXECUTION_BRIDGE_SELECTION_FIX_REQUIRED`

