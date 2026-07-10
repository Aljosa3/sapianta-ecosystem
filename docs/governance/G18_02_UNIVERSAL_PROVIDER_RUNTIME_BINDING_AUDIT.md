# G18-02 Universal Provider Runtime Binding Audit

## Executive Summary

This audit determines whether the G17 Worker execution path reuses the certified Universal Provider Runtime capabilities established in G18-01.

Finding:

The G17 Worker path does not fully reuse the certified universal provider selection, escalation, or multi-provider cooperation runtime. It reaches the certified provider attachment boundary, but it binds directly to the OpenAI external Worker provider adapter instead of routing through the unified resource selection and multi-provider runtime capabilities.

This is not a Platform Core, Provider Platform, Worker Platform, Governance, or Replay redesign issue. The certified capabilities already exist:

- resource registry and deterministic selection;
- PPP resource-selection integration;
- multi-provider cognition;
- failover and provider isolation;
- replay reconstruction;
- provider governance evidence.

The gap is a provider-consumer binding gap in the G17 Worker continuation path.

Final verdict: `UNIVERSAL_PROVIDER_RUNTIME_REUSE_WITH_MINOR_BINDING`.

## Certified Universal Provider Runtime

The certified universal provider capability is composed of existing Provider Platform runtimes.

Deterministic source evidence:

- `aigol/runtime/unified_resource_selection_runtime.py` defines `default_resource_registry()` at lines 216-231.
- The registry includes multiple resources and records `provider_invoked=False`, `worker_invoked=False`, `execution_requested=False`, `dispatch_requested=False`, and `authorization_created=False`.
- `select_unified_resource(...)` at lines 234-313 evaluates resources and creates replay-visible selection artifacts without invoking providers.
- `reconstruct_unified_resource_selection_replay(...)` at lines 316-357 reconstructs selection status, selected resource, role, capability, domain, rationale, registry hash, and diagnostics hash.
- `aigol/runtime/multi_provider_cognition_runtime.py` defines `run_multi_provider_cognition_runtime(...)` at lines 65-150.
- The multi-provider runtime validates multiple provider contracts, creates request artifacts, processes provider requests, records provider failures, and persists request/result bundles.

Deterministic test evidence:

- `tests/test_unified_resource_selection_runtime_v1.py` verifies provider selection, Worker selection, hybrid role selection, fail-closed prohibited provider selection, and ambiguous selection failure.
- `tests/test_unified_resource_selection_ppp_integration_v1.py` verifies that selected provider resources can be integrated into PPP proposal production while preserving `provider_invoked=False`.
- `tests/test_multi_provider_cognition_runtime_v1.py` verifies multiple provider cognition artifacts and provider failure isolation.
- `tests/test_multi_provider_operational_readiness_certification_v1.py` verifies OpenAI/Claude dual success, OpenAI-to-Claude failover, participation metrics, usage metrics, replay reconstruction, and secret-free evidence.

Conclusion:

Universal provider capabilities exist as certified components. They are replay-safe and non-authoritative.

## G17 Worker Runtime Path

The G17 Worker runtime path proceeds through Worker request, assignment, dispatch, invocation, external task packaging, direct OpenAI provider adapter invocation, result validation, and replay certification.

Implementation evidence:

- `aigol/cli/aigol_cli.py` imports `run_openai_external_worker_provider_adapter` directly at line 353.
- `_external_worker_capability_declaration()` hard-codes `worker_interface="OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"` at lines 934-943.
- `_continue_worker_request_to_replay_certification(...)` performs:
  - Worker assignment at lines 960-968;
  - Worker dispatch at lines 972-979;
  - Worker invocation at lines 983-990;
  - Worker invocation to execution candidate bridge at lines 995-1007;
  - external Worker task package creation at lines 1014-1026;
  - OpenAI external Worker provider invocation at lines 1030-1040;
  - fail-closed if `openai_provider_connected` is not true at lines 1041-1042;
  - result acceptance, validation, and replay certification at lines 1044-1074.

Runtime replay evidence:

The observed Worker continuation path contains:

```text
.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/
  governed_bridge_certified_development_continuation/
  worker_lifecycle_continuation/
    worker_assignment/
    worker_dispatch/
    worker_invocation/
    worker_execution_candidate/
    external_worker_adapter/
    openai_external_worker_provider/
      certified_provider_attachment/
```

It does not contain a resource-selection, smart-selection, escalation, or multi-provider runtime subtree inside `worker_lifecycle_continuation`.

Conclusion:

The G17 Worker runtime path reaches the certified provider attachment boundary but uses a direct OpenAI external Worker adapter binding.

## Provider Consumer Binding

The Worker provider consumer is bound directly to OpenAI.

Source evidence:

- `aigol/cli/aigol_cli.py` line 353 imports the OpenAI external Worker adapter.
- `aigol/cli/aigol_cli.py` lines 1030-1040 calls `run_openai_external_worker_provider_adapter(...)`.
- `aigol/runtime/openai_external_worker_provider_adapter.py` lines 72-99 calls `run_certified_provider_attachment(...)` with `provider_id=OPENAI_PROVIDER_ID`, an OpenAI registry, and `OpenAIProviderAdapter(...)`.

Test evidence:

- `tests/test_acli_certified_continuation_orchestration_v1.py` lines 164-214 verifies the certified continuation reaches `openai_external_worker_status == OPENAI_EXTERNAL_WORKER_COMPLETED`.
- The same test asserts `openai_provider_reached is True`.
- `tests/test_openai_external_worker_provider_adapter_v1.py` verifies the OpenAI external Worker adapter path independently.

Conclusion:

The Worker provider consumer is not bound to universal provider routing. It is bound to a provider-specific OpenAI external Worker adapter that then uses Certified Provider Attachment.

## Smart Selection Binding

Smart selection is not executed in the G17 Worker execution path.

Implementation evidence:

- `select_unified_resource(...)` exists in `aigol/runtime/unified_resource_selection_runtime.py`.
- `aigol/cli/aigol_cli.py` does not call `select_unified_resource(...)` in `_continue_worker_request_to_replay_certification(...)`.
- The Worker continuation hard-codes the external Worker capability as `OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1` at lines 934-943.
- The Worker continuation directly calls `run_openai_external_worker_provider_adapter(...)` at lines 1030-1040.

Replay evidence:

- TURN-000019 Worker lifecycle replay contains `openai_external_worker_provider/`.
- TURN-000019 Worker lifecycle replay contains no `resource_selection` or `unified_resource_selection` directory.

Conclusion:

Smart provider/resource selection is certified elsewhere, but it is not bound into this Worker provider consumer path.

## Escalation Binding

Provider escalation is not executed in the G17 Worker execution path.

Certified capability evidence:

- G18-01 records that `run_multi_provider_operational_readiness_certification_v1(...)` verifies OpenAI/Claude dual success and OpenAI-to-Claude failover.
- The multi-provider cognition runtime records provider failure artifacts and continues with remaining provider requests.

Worker path evidence:

- `_continue_worker_request_to_replay_certification(...)` checks only `openai_worker_capture.get("openai_provider_connected")`.
- If OpenAI is not connected, it raises `FailClosedRuntimeError(...)` at `aigol/cli/aigol_cli.py` lines 1041-1042.
- No alternate provider attempt follows.

Runtime replay evidence:

- `openai_external_worker_provider/003_openai_external_worker_returned.json` records `adapter_status=FAILED_CLOSED`, `openai_provider_connected=false`, and `failure_reason=OpenAI provider unavailable`.
- No Claude, Anthropic, fallback, escalation, or multi-provider replay artifact appears under the Worker lifecycle continuation.

Conclusion:

Escalation exists as certified Provider Platform capability, but the G17 Worker consumer does not invoke it.

## Multi-provider Binding

Multi-provider runtime is not reachable from the G17 Worker execution path.

Certified capability evidence:

- `run_multi_provider_cognition_runtime(...)` accepts multiple provider contracts and a transport registry at `aigol/runtime/multi_provider_cognition_runtime.py` lines 65-74.
- It validates provider contracts and creates request artifacts for each contract at lines 80-122.
- It processes provider requests and persists a result bundle at lines 123-141.

Worker path evidence:

- `_continue_worker_request_to_replay_certification(...)` provides a single OpenAI external Worker task package to `run_openai_external_worker_provider_adapter(...)`.
- The direct OpenAI adapter then calls `run_certified_provider_attachment(...)`.
- No `provider_contracts` list or `transport_registry` is passed from the Worker continuation to `run_multi_provider_cognition_runtime(...)`.

Replay evidence:

- Worker lifecycle replay records the OpenAI provider path only.
- No multi-provider request bundle or result bundle is recorded in the Worker lifecycle continuation.

Conclusion:

The certified multi-provider runtime is reachable in its own cognition/runtime paths, but not from the G17 Worker execution provider consumer.

## Divergence Analysis

The execution path diverges from universal provider runtime reuse at this point:

```text
aigol/cli/aigol_cli.py
_continue_worker_request_to_replay_certification(...)
-> _external_worker_capability_declaration()
-> create_external_worker_task_package(...)
-> run_openai_external_worker_provider_adapter(...)
```

The expected universal-provider-reuse path would include a replay-visible selection/binding step before provider-specific invocation:

```text
Worker
-> provider consumer binding
-> select_unified_resource(...)
-> selected provider or provider set
-> escalation/multi-provider policy when needed
-> certified provider attachment or multi-provider runtime
-> provider result
-> Worker result validation/replay certification
```

The actual G17 Worker path is:

```text
Worker
-> external Worker task package
-> OpenAI external Worker provider adapter
-> Certified Provider Attachment
-> OpenAI Provider Adapter
-> OpenAI provider result or fail-closed result
-> Worker result validation/replay certification on success
```

The path preserves certified attachment and fail-closed replay behavior, but bypasses universal selection, escalation, and multi-provider cooperation.

## Minimal Binding Recommendation

No Provider Platform redesign is required.

Minimal binding recommendation:

Introduce a governed provider-consumer binding step in the Worker continuation before provider-specific adapter invocation:

1. Build a replay-visible provider-consumer request from the external Worker task package.
2. Call existing `select_unified_resource(...)` with required Worker/provider capability and domain.
3. Persist the selection replay reference alongside the Worker lifecycle replay.
4. If the selected route is a single provider, invoke the existing certified provider attachment path through the selected provider adapter.
5. If policy requires failover or cooperation, invoke existing multi-provider runtime capabilities.
6. Preserve current authority rules: provider outputs remain non-authoritative, no provider gains Governance, Replay, Worker, execution, or approval authority.

This is a binding of existing certified capabilities, not a new Provider Platform.

## Architectural Conclusions

1. Platform Core remains certified.
2. Worker Runtime remains certified.
3. Central Provider Platform remains certified.
4. Certified Provider Attachment is reused by the G17 Worker path.
5. Universal resource selection is not reused by the G17 Worker provider consumer.
6. Smart selection does not execute in the G17 Worker provider path.
7. Provider escalation does not execute in the G17 Worker provider path.
8. Multi-provider runtime is not reachable from the G17 Worker provider path.
9. The divergence is a provider-consumer binding gap.
10. Existing certified capabilities are sufficient for the next integration step.

This audit does not identify an architectural defect in Platform Core, Worker Runtime, Provider Platform, Governance, or Replay.

## Final Recommendation

Certify the current state as a reuse-with-binding gap.

Do not redesign the Provider Platform.

Reuse:

- `default_resource_registry()`;
- `select_unified_resource(...)`;
- `run_multi_provider_cognition_runtime(...)`;
- existing provider readiness and Certified Provider Attachment;
- existing provider governance metrics;
- existing replay reconstruction primitives.

Bind these capabilities into the Worker provider consumer path before the OpenAI-specific adapter is selected.

## Final Verdict

`UNIVERSAL_PROVIDER_RUNTIME_REUSE_WITH_MINOR_BINDING`

Deterministic support:

- The G17 Worker path directly imports and invokes `run_openai_external_worker_provider_adapter(...)`.
- The Worker capability declaration hard-codes `OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1`.
- The OpenAI adapter reuses Certified Provider Attachment.
- The Worker path does not call `select_unified_resource(...)`.
- The Worker path does not call `run_multi_provider_cognition_runtime(...)`.
- The Worker path fails closed when OpenAI is unavailable rather than escalating to another provider.
- Worker replay contains `openai_external_worker_provider/certified_provider_attachment`.
- Worker replay contains no resource-selection, escalation, or multi-provider subtree.
- Existing certified Provider Platform capabilities are available and replay-safe.
- The remaining work is provider-consumer binding, not Provider Platform implementation.
