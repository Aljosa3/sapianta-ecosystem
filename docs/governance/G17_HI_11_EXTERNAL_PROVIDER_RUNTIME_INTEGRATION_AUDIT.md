# G17-HI-11 - External Provider Runtime Integration Audit

## Executive Summary

The certified Worker runtime reaches the OpenAI external Worker provider adapter. Provider selection is deterministic, the certified provider attachment boundary is used, readiness evidence is recorded, and fail-closed behavior is expected.

The observed failure is not caused by Platform Core, Runtime, Governance, Replay, Worker, or Human Interface ownership. It occurs inside the external provider attachment path after the Worker lifecycle reaches the OpenAI provider boundary. TURN-000019 records provider readiness as `READY`, then records the provider proposal as `FAILED_CLOSED` with `failure_reason = OpenAI provider unavailable`.

The implementation path is operational under deterministic tests with an injected OpenAI client and explicit test key. The live failure therefore requires provider environment/configuration remediation for the governed process and real transport path, not a runtime architecture change.

## Runtime Evidence

Observed replay path:

`.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/governed_bridge_certified_development_continuation/worker_lifecycle_continuation/openai_external_worker_provider`

Replay evidence:

- `000_openai_external_worker_task_recorded.json`: `artifact_type = EXTERNAL_WORKER_TASK_PACKAGE_V1`, `failure_reason = None`, `replay_lineage_preserved = true`.
- `001_openai_provider_adapter_recorded.json`: `artifact_type = OPENAI_EXTERNAL_WORKER_PROVIDER_CAPTURE_ARTIFACT_V1`, `provider_status = FAILED_CLOSED`, `provider_id = openai`, `provider_invoked_inside_adapter = true`, `failure_reason = OpenAI provider unavailable`.
- `002_openai_external_worker_result_recorded.json`: `artifact_type = EXTERNAL_WORKER_RESULT_PACKAGE_V1`, `execution_status = FAILED_CLOSED`, `execution_outcome = FAILED_CLOSED`, `failure_reason = OpenAI provider unavailable`.
- `003_openai_external_worker_returned.json`: `adapter_status = FAILED_CLOSED`, `openai_provider_connected = false`, `failure_reason = OpenAI provider unavailable`, `result_package_generated = true`, `provider_neutrality_above_adapter_preserved = true`.

Certified provider attachment evidence:

- `certified_provider_attachment/000_provider_readiness_recorded.json`: `provider_id = openai`, `provider_version = openai-responses-v1`, `provider_status = AVAILABLE`, `api_key_present = true`, `provider_configuration_valid = true`, `model_configuration_valid = true`, `transport_available = true`, `readiness_status = READY`, `provider_activation_ready = true`.
- `certified_provider_attachment/000_provider_proposal_created.json`: `provider_status = FAILED_CLOSED`, `provider_version = UNKNOWN`, `provider_invoked = false`, `failure_reason = OpenAI provider unavailable`, `failure_stage = openai_provider_adapter`, `transport_failure_category = FAIL_CLOSED`.
- `certified_provider_attachment/002_certified_provider_attachment_recorded.json`: `provider_status = FAILED_CLOSED`, `provider_invoked = false`, `failure_reason = OpenAI provider unavailable`.

Secret-safe environment check in the current process:

- `AIGOL_OPENAI_API_KEY_PRESENT = false`
- `OPENAI_API_KEY_PRESENT = true`

No credential values were printed or inspected.

## Provider Configuration Review

The OpenAI external Worker provider adapter selects OpenAI directly:

- `run_openai_external_worker_provider_adapter(...)` calls `run_certified_provider_attachment(...)` with `provider_id = OPENAI_PROVIDER_ID` (`aigol/runtime/openai_external_worker_provider_adapter.py:72-99`).
- `_openai_provider_registry()` registers OpenAI metadata as `AVAILABLE` (`aigol/runtime/openai_external_worker_provider_adapter.py:324-327`).
- The Provider Registry validates provider metadata and carries no execution, dispatch, or authority (`aigol/provider/provider_registry.py`).

The replay evidence confirms provider configuration was accepted before invocation:

- `provider_configuration_valid = true`
- `model_configuration_valid = true`
- `transport_available = true`
- `provider_activation_ready = true`

Therefore, provider selection and static configuration are valid for the recorded attempt.

## Credential Availability Review

Credential handling has two relevant surfaces:

1. The OpenAI provider adapter resolves an explicit `api_key` first and otherwise reads `OPENAI_API_KEY` (`aigol/provider/providers/openai_provider.py:70-75` and `aigol/provider/providers/openai_provider.py:172-174`).
2. Provider readiness checks `_api_key` first and otherwise reads `OPENAI_API_KEY` (`aigol/provider/provider_runtime.py:589-593`).

In the current process, `OPENAI_API_KEY` is present and `AIGOL_OPENAI_API_KEY` is absent. The operator bootstrap exists to mirror `OPENAI_API_KEY` into `AIGOL_OPENAI_API_KEY` when sourced before process launch (`aigol/runtime/operator_environment_bootstrap.py:25-29`).

TURN-000019 readiness records `api_key_present = true`, so this replay did not fail at missing key detection. The failure occurs later at provider adapter invocation.

## Provider Selection Review

Provider selection is correct:

- The Worker provider adapter is OpenAI-specific by design.
- It passes `provider_id = OPENAI_PROVIDER_ID`.
- Certified provider attachment records `provider_id = openai`.
- Provider readiness records `provider_version = openai-responses-v1`, matching the adapter runtime.

No evidence shows provider discovery failure or incorrect provider routing.

## Provider Health Detection Review

Provider health detection is split into readiness and actual invocation:

- Readiness checks are static/local checks: key presence, provider configuration, model/endpoint/timeout validity, callable transport, and provider metadata status (`aigol/provider/provider_runtime.py:528-555`).
- `_openai_transport_available(...)` checks whether the adapter client is callable (`aigol/provider/provider_runtime.py:626-627`).
- Actual OpenAI invocation occurs later in `OpenAIProviderAdapter.generate_proposal(...)`, which resolves the key, creates payload, calls `_call_openai(...)`, and extracts response text (`aigol/provider/providers/openai_provider.py:70-88`).

TURN-000019 shows readiness detection worked as implemented: local readiness passed, then actual provider invocation failed closed.

## Fail-Closed Behavior Review

Fail-closed behavior is expected and correctly recorded.

Implementation evidence:

- `run_openai_external_worker_provider_adapter(...)` raises fail-closed when the provider artifact is not `COMPLETED` (`aigol/runtime/openai_external_worker_provider_adapter.py:100-107`).
- The adapter catches exceptions, records a failed external Worker result package, and returns a failed capture instead of continuing as if provider output existed (`aigol/runtime/openai_external_worker_provider_adapter.py:134-146`).
- `OpenAIProviderAdapter._call_openai(...)` normalizes non-`FailClosedRuntimeError` provider call exceptions to `OpenAI provider unavailable` (`aigol/provider/providers/openai_provider.py:111-123`).
- The underlying HTTP client normalizes URL, timeout, and JSON decode failures to `OpenAI provider unavailable` and HTTP errors to `OpenAI provider HTTP failure` (`aigol/provider/providers/openai_provider.py:125-145`).

Replay evidence:

- `openai_provider_connected = false`
- `execution_status = FAILED_CLOSED`
- `result_package_generated = true`
- `provider_neutrality_above_adapter_preserved = true`

The runtime did not bypass fail-closed semantics.

## Implementation Readiness Evidence

Existing tests prove the implementation path is operational with controlled provider input:

- `test_openai_external_worker_provider_adapter_connects_task_to_result_package` injects a fake OpenAI client and explicit key, then asserts `worker_status = OPENAI_EXTERNAL_WORKER_COMPLETED`, `openai_provider_connected = true`, `result_package_generated = true`, and replay readiness true (`tests/test_openai_external_worker_provider_adapter_v1.py:97-123`).
- `test_openai_external_worker_routes_through_adapter_validation_and_replay_certification` uses the same adapter path, accepts the external Worker result package, validates the result, and certifies replay (`tests/test_openai_external_worker_provider_adapter_v1.py:126-164`).
- `test_openai_external_worker_fails_closed_on_provider_failure` injects a failing client and verifies fail-closed behavior (`tests/test_openai_external_worker_provider_adapter_v1.py:167-186`).

This evidence supports that the implementation path exists and behaves deterministically for both success and provider-failure cases.

## Root Cause Classification

Classification: provider environment/configuration required.

Reasoning:

- Provider selection is correct.
- Static provider configuration is valid in TURN-000019.
- Credential presence check passed in TURN-000019.
- The Worker provider adapter reached certified provider attachment.
- Actual provider invocation failed closed with `OpenAI provider unavailable`.
- Positive tests demonstrate the adapter can complete and reach replay certification when a callable provider client returns a valid response.

The unresolved operational dependency is the real governed process/provider transport environment: the runtime needs a usable OpenAI credential in the process environment used by the provider adapter and successful HTTPS access to the OpenAI Responses endpoint.

## Required Action

No runtime implementation change is recommended.

Required operational action:

1. Ensure the governed process environment that launches `./aicli` contains usable provider credentials. Prefer canonical `AIGOL_OPENAI_API_KEY`; the current OpenAI provider adapter also reads `OPENAI_API_KEY`.
2. If only `OPENAI_API_KEY` is configured, source or apply the operator bootstrap before launching the governed process so `AIGOL_OPENAI_API_KEY` is also available where required by adjacent provider tooling.
3. Verify network/HTTPS access from the same governed process environment to the OpenAI Responses endpoint.
4. Re-run the governed Human Interface path and inspect the certified provider attachment replay for `provider_invoked = true`, `provider_status = AVAILABLE` on success artifacts, `openai_provider_connected = true`, and downstream replay certification.

## Architectural Impact Assessment

No Platform Core redesign is required.

No Runtime redesign is required.

No Governance redesign is required.

No Replay redesign is required.

No Worker architecture redesign is required.

No Human Interface redesign is required.

The current fail-closed behavior is architecturally correct: provider output is not synthesized, replay certification is not forged, and Worker continuation stops when the external provider cannot produce governed evidence.

## Final Recommendation

Treat G17-HI-11 as an operational provider-environment remediation item, not as a certified runtime implementation gap.

After provisioning credentials and confirming real transport access in the governed process, rerun the same Human Interface approval path. If readiness remains `READY` but provider invocation still fails, collect the new certified provider attachment replay and classify by the recorded `failure_diagnostics` category.

## Final Verdict

PROVIDER_ENVIRONMENT_CONFIGURATION_REQUIRED

