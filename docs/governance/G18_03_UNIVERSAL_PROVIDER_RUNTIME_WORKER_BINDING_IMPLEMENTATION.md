# G18-03 Universal Provider Runtime Worker Binding Implementation

## Executive Summary

G18-03 implements the smallest deterministic binding correction for the G17 Worker provider path.

The Worker continuation path no longer invokes the OpenAI-specific external worker adapter directly. It now declares the external Worker provider consumer as `UNIVERSAL_PROVIDER_WORKER_RUNTIME_V1` and routes execution through `run_universal_provider_worker_runtime(...)`.

The universal Worker runtime performs certified resource selection through the existing Unified Resource Selection Runtime, records replay-visible universal-provider binding and result artifacts, and only then delegates to the selected provider adapter. The currently selected registered provider remains `OPENAI` for the certified Worker task capability, so the existing Certified Provider Attachment and OpenAI adapter remain reused below the universal routing boundary.

Final verdict: `IMPLEMENTED_WITH_OBSERVATIONS`.

## Implementation Scope

This implementation did not redesign Platform Core, Provider Platform, Worker Platform, Governance, Replay, or Human Interface behavior.

The change is limited to:

- replacing the Worker consumer's direct OpenAI adapter call with a universal provider Worker runtime call;
- changing the external Worker capability declaration from an OpenAI-specific interface to the universal Worker provider interface;
- preserving the existing OpenAI adapter as the selected-provider implementation under the universal route;
- exposing universal-provider selection evidence in interactive turn summaries;
- adding focused regression tests and replay-evidence validation.

## Worker Binding Change

Implementation evidence:

- `aigol/cli/aigol_cli.py` imports `UNIVERSAL_PROVIDER_WORKER_INTERFACE` and `run_universal_provider_worker_runtime` from `aigol.runtime.universal_provider_worker_runtime`.
- `_external_worker_capability_declaration()` now emits `worker_interface: UNIVERSAL_PROVIDER_WORKER_INTERFACE` and `worker_family: UNIVERSAL_PROVIDER_EXTERNAL_LLM_WORKER`.
- `_continue_worker_request_to_replay_certification(...)` calls `run_universal_provider_worker_runtime(...)` with the external Worker task package and writes its replay under `universal_provider_worker`.
- The previous direct call to `run_openai_external_worker_provider_adapter(...)` is no longer present inside `_continue_worker_request_to_replay_certification(...)`.

Compatibility evidence:

- The Worker lifecycle stores the universal capture under `universal_provider_worker`.
- The legacy `openai_external_worker_provider` key is preserved as an alias to the same capture so existing downstream replay, validation, and turn-summary consumers continue to resolve OpenAI adapter evidence.
- `accept_external_worker_result_package(...)`, result validation, and replay certification remain unchanged.

## Universal Provider Runtime

New implementation:

- `aigol/runtime/universal_provider_worker_runtime.py`

The runtime performs these deterministic steps:

1. Calls `select_unified_resource(...)` with:
   - `workflow_type="NATIVE_DEVELOPMENT"`;
   - `required_capability="PROPOSAL_GENERATION"`;
   - `requested_role_type=PROVIDER_ROLE`;
   - `domain_id="NATIVE_DEVELOPMENT"`;
   - `provider_necessity_classification=PROVIDER_REQUIRED`;
   - `min_trust_level="STANDARD"`.
2. Requires `RESOURCE_SELECTION_SUCCEEDED`.
3. Records `000_universal_provider_worker_binding_recorded.json`.
4. Delegates to the selected provider through `_invoke_selected_provider(...)`.
5. For the current selected resource `OPENAI`, invokes the existing OpenAI external Worker provider adapter below the universal routing boundary.
6. Records `001_universal_provider_worker_result_recorded.json`.
7. Returns a capture containing `universal_provider_worker_status`, `smart_selection_executed`, `selected_resource_id`, provider replay references, and fail-closed evidence.

The OpenAI adapter remains the selected-provider leaf implementation, not the Worker consumer routing decision.

## Provider Selection Evidence

Runtime evidence:

- `run_universal_provider_worker_runtime(...)` writes Unified Resource Selection replay under `universal_provider_worker/universal_resource_selection`.
- The selection result is copied into the universal-provider Worker capture as `resource_selection`.
- The selected resource id is exposed as `selected_resource_id`.
- Interactive turn summaries expose:
  - `universal_provider_worker_status`;
  - `universal_provider_worker_replay_reference`;
  - `selected_provider_resource_id`;
  - `smart_provider_selection_executed`.

Test evidence:

- `tests/test_universal_provider_worker_runtime_v1.py::test_universal_provider_worker_selects_provider_then_delegates_to_certified_attachment` proves the universal runtime executes smart selection, selects `OPENAI`, reaches the OpenAI provider adapter below the universal boundary, and writes Certified Provider Attachment replay.
- `tests/test_acli_certified_continuation_orchestration_v1.py::test_worker_continuation_routes_through_universal_provider_runtime` proves `_continue_worker_request_to_replay_certification(...)` contains `run_universal_provider_worker_runtime(...)` and does not contain `run_openai_external_worker_provider_adapter(...)`.
- `tests/test_acli_certified_continuation_orchestration_v1.py::test_development_acli_auto_continue_reaches_replay_certification` proves the full interactive certified continuation reaches replay certification while exposing universal-provider status, selected provider id `OPENAI`, and smart-selection evidence.

## Certified Provider Attachment Reuse

The universal Worker runtime does not replace the Certified Provider Attachment.

When selection returns `OPENAI`, `_invoke_selected_provider(...)` calls the existing `run_openai_external_worker_provider_adapter(...)`. That adapter still owns OpenAI request construction, Certified Provider Attachment invocation, adapter replay, result-package creation, and fail-closed provider handling.

The new regression test verifies the selected provider path writes:

`universal_provider_worker/selected_provider_openai/certified_provider_attachment/002_certified_provider_attachment_recorded.json`

This proves the Worker path now uses universal provider routing before reaching the certified OpenAI attachment path.

## Replay Evidence

Replay evidence added by G18-03:

- `000_universal_provider_worker_binding_recorded.json`
- `001_universal_provider_worker_result_recorded.json`
- nested `universal_resource_selection` replay
- nested selected-provider OpenAI replay
- nested Certified Provider Attachment replay

Replay evidence preserved:

- external Worker task package replay;
- external Worker result acceptance replay;
- governed result validation replay;
- replay certification replay;
- OpenAI adapter replay under the selected-provider route.

The continuation path preserves `replay_lineage_preserved` by including the universal provider capture in the existing replay-lineage check.

## Validation

Executed:

```bash
python -m pytest tests/test_acli_certified_continuation_orchestration_v1.py tests/test_universal_provider_worker_runtime_v1.py tests/test_openai_external_worker_provider_adapter_v1.py
```

Result:

```text
10 passed
```

## Observations

The binding correction is intentionally minimal.

The Worker path now reaches the certified Universal Provider Runtime selection layer before selected-provider invocation. However, the selected-provider dispatch table currently binds only `OPENAI` for this external Worker result-package contract. Additional provider-specific Worker result-package adapters would be required before Claude, Codex, Anthropic, or cooperative multi-provider execution can complete the same Worker contract.

The universal selection, replay, and provider-consumer boundary are implemented. Broad multi-provider cooperation for Worker result package generation remains an extension of selected-provider adapter coverage, not a redesign of the certified routing layer.

## Architectural Conclusions

- Platform Core remains unchanged.
- Human Interface remains unchanged.
- Worker lifecycle and authorization order remain unchanged.
- Governance authorization remains upstream of Worker continuation.
- Replay certification remains downstream of Worker result validation.
- Provider Platform selection is now reused by the Worker provider path.
- The direct OpenAI Worker consumer bypass identified in G18-02 is corrected.
- Existing OpenAI adapter and Certified Provider Attachment capabilities are reused below the universal-provider route.

## Final Recommendation

Accept G18-03 as the deterministic Worker binding implementation.

Next provider-runtime work should add selected-provider Worker adapters for additional registered providers and then expand the universal runtime's selected-provider dispatch table. That work should remain adapter-level integration, not a redesign of Worker, Governance, Replay, or Platform Core.

## Final Verdict

`IMPLEMENTED_WITH_OBSERVATIONS`
