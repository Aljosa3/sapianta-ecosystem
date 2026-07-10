# G17-HI-12 Central Provider Platform Runtime Path Audit

## Executive Summary

This audit verifies the provider failure as a Central Provider Platform runtime-path question, not as a direct OpenAI-only question.

The observed Worker continuation does not call OpenAI directly from the Human Interface, Platform Core conversation layer, or governed development bridge. It enters the certified provider boundary through:

```text
Worker continuation
-> run_openai_external_worker_provider_adapter(...)
-> run_certified_provider_attachment(...)
-> run_provider_attachment(...)
-> OpenAIProviderAdapter.generate_proposal(...)
-> OpenAIHTTPClient
```

The deterministic replay evidence shows that Provider Registry lookup, provider identity, credential presence, provider configuration, model configuration, transport availability, and provider activation readiness all succeed. The runtime records `OpenAI provider unavailable` after readiness, at the provider adapter invocation stage.

Final verdict: `PROVIDER_PLATFORM_OPERATIONAL_CONFIGURATION_REQUIRED`.

## Central Provider Platform Runtime Chain

The audited runtime chain is:

```text
Governed Worker continuation
-> external worker task package
-> OpenAI external worker provider adapter
-> Certified Provider Attachment
-> Provider Attachment Runtime
-> Provider Registry lookup
-> Provider readiness checks
-> Provider adapter validation
-> OpenAI provider adapter invocation
-> OpenAI HTTP client
-> fail-closed provider result
-> external worker failed result package
```

Implementation evidence:

- `aigol/cli/aigol_cli.py` lines 1030-1042 call `run_openai_external_worker_provider_adapter(...)` from the Worker continuation and fail closed if `openai_provider_connected` is not true.
- `aigol/runtime/openai_external_worker_provider_adapter.py` lines 72-99 call `run_certified_provider_attachment(...)`, passing `provider_id=OPENAI_PROVIDER_ID`, `_openai_provider_registry()`, and `OpenAIProviderAdapter(...)`.
- `aigol/provider/certified_provider_attachment.py` lines 26-61 define the stable certified provider boundary and delegate to `run_provider_attachment(...)`.
- `aigol/provider/provider_runtime.py` lines 63-91 perform replay availability, registry lookup, readiness, adapter validation, request validation, adapter invocation, and provider proposal replay capture.

This confirms that the Worker enters the Central Provider Platform boundary before external provider use.

## Provider Registry Validation

Provider Registry is reached.

Implementation evidence:

- `run_provider_attachment(...)` calls `registry.lookup_provider(provider_id)` at `aigol/provider/provider_runtime.py` line 66.
- `ProviderRegistry.lookup_provider(...)` validates provider identity and returns canonical metadata at `aigol/provider/provider_registry.py` lines 63-69.
- `ProviderRegistry` is explicitly metadata-only and does not dispatch or execute providers at `aigol/provider/provider_registry.py` lines 49-50.

Replay evidence:

- `.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/.../certified_provider_attachment/000_provider_readiness_recorded.json`
  records `provider_id=openai`, `provider_version=openai-responses-v1`, `provider_status=AVAILABLE`, and a provider identity hash.

Registry validation succeeds.

## Provider Selection Validation

Provider selection is deterministic and single-provider for this Worker path.

Implementation evidence:

- `run_openai_external_worker_provider_adapter(...)` passes `provider_id=OPENAI_PROVIDER_ID` to `run_certified_provider_attachment(...)`.
- `_openai_provider_registry()` supplies the OpenAI provider metadata for that deterministic provider path.
- `docs/governance/G14_20_PROVIDER_PLATFORM_CANONICAL_RUNTIME_AUDIT_V1.md` lines 145-162 previously certified that this runtime path selects `provider_id: openai` deterministically and does not demonstrate dynamic multi-provider selection.

The selected provider becomes unavailable after deterministic selection, not during selection.

## Smart Selection Validation

Smart or dynamic multi-provider selection is not executed in the observed Worker continuation path.

Implementation evidence:

- `aigol/provider/provider_runtime.py` lines 304-313 record provider metadata with `metadata_routing_enabled=False`, `metadata_selection_enabled=False`, and `metadata_execution_enabled=False`.
- `aigol/provider/provider_registry.py` lines 49-50 states that the registry is metadata-only and does not dispatch or execute providers.
- The observed call chain supplies the selected provider id directly to `run_certified_provider_attachment(...)`.

Architectural interpretation:

The absence of smart selection is not the source of `OpenAI provider unavailable` in this trace. The failure is emitted after direct deterministic provider selection and after readiness succeeds. Dynamic smart selection remains outside this audited single-provider Worker continuation path.

## Credential Resolution Validation

Credential presence succeeds for the observed replay.

Implementation evidence:

- `_provider_readiness_checks(...)` includes `api_key_presence` at `aigol/provider/provider_runtime.py` lines 528-535.
- `_openai_api_key_present(...)` checks the adapter api key first and then `OPENAI_API_KEY` at `aigol/provider/provider_runtime.py` lines 589-593.
- `OpenAIProviderAdapter.generate_proposal(...)` resolves the api key before creating the OpenAI payload at `aigol/provider/providers/openai_provider.py` lines 70-75.

Replay evidence:

- `000_provider_readiness_recorded.json` records `api_key_present=True`.
- Current process verification records `OPENAI_API_KEY_PRESENT=True` and `AIGOL_OPENAI_API_KEY_PRESENT=False`.

Credential presence is not the failing stage in the observed runtime artifact.

## Health Detection Validation

Provider health and readiness detection succeeds.

Implementation evidence:

- `_provider_readiness_artifact(...)` records readiness fields at `aigol/provider/provider_runtime.py` lines 490-525.
- `_provider_readiness_checks(...)` validates api key presence, provider configuration, model configuration, transport availability, and provider activation readiness at `aigol/provider/provider_runtime.py` lines 528-555.

Replay evidence from `000_provider_readiness_recorded.json`:

```text
readiness_status: READY
api_key_present: True
provider_configuration_valid: True
model_configuration_valid: True
transport_available: True
provider_activation_ready: True
provider_invocation_allowed: True
readiness_checks:
  api_key_presence=READY
  provider_configuration_validity=READY
  model_configuration_validity=READY
  transport_availability=READY
  provider_activation_readiness=READY
```

Health detection does not record provider unavailability.

## Provider Adapter Validation

Provider adapter initialization and validation are reached after readiness.

Implementation evidence:

- `run_provider_attachment(...)` calls `_validate_adapter(...)` and `_validate_request(...)` before `adapter.generate_proposal(...)` at `aigol/provider/provider_runtime.py` lines 77-81.
- `OpenAIProviderAdapter.generate_proposal(...)` creates the request payload and calls `_call_openai(...)` at `aigol/provider/providers/openai_provider.py` lines 70-75.

Replay evidence:

- `001_openai_provider_adapter_recorded.json` records `provider_id=openai`, `provider_status=FAILED_CLOSED`, `provider_invoked_inside_adapter=True`, and `failure_reason=OpenAI provider unavailable`.
- Certified provider attachment records the failure as `failure_stage=openai_provider_adapter`.

The adapter boundary is reached and is the stage where the fail-closed provider unavailable condition is normalized.

## External Invocation Validation

External invocation is attempted through the provider adapter path, but no successful provider proposal envelope is produced.

Implementation evidence:

- `OpenAIProviderAdapter._call_openai(...)` calls its configured client and normalizes non-certified exceptions to `FailClosedRuntimeError("OpenAI provider unavailable")` at `aigol/provider/providers/openai_provider.py` lines 111-124.
- `OpenAIHTTPClient.__call__(...)` performs the non-streaming HTTP POST and normalizes `URLError`, `TimeoutError`, and JSON decode failures to `OpenAI provider unavailable` at `aigol/provider/providers/openai_provider.py` lines 152-158.
- `run_provider_attachment(...)` catches that exception and persists failed provider proposal artifacts at `aigol/provider/provider_runtime.py` lines 92-112.

Replay evidence:

- `000_provider_proposal_created.json` records `provider_status=FAILED_CLOSED`, `provider_invoked=False`, `failure_reason=OpenAI provider unavailable`, and diagnostics `failure_stage=openai_provider_adapter`.
- `001_provider_proposal_returned.json` records the same failure reason and diagnostics.
- `002_certified_provider_attachment_recorded.json` records `provider_status=FAILED_CLOSED`, `provider_invoked=False`, and `failure_reason=OpenAI provider unavailable`.
- `002_openai_external_worker_result_recorded.json` records `execution_status=FAILED_CLOSED`, `execution_outcome=FAILED_CLOSED`, and `failure_reason=OpenAI provider unavailable`.
- `003_openai_external_worker_returned.json` records `openai_provider_connected=False`.

The exact deterministic stage returning provider unavailable is the OpenAI provider adapter invocation path, normalized by Certified Provider Attachment replay.

## Root Cause

The root cause is operational provider execution failure after Central Provider Platform readiness has succeeded.

This is not caused by:

- Human Interface routing;
- Platform Core conversation ownership;
- governed bridge selection;
- Worker continuation ownership;
- Provider Registry lookup;
- deterministic provider selection;
- credential presence;
- provider configuration validity;
- model configuration validity;
- transport callable availability;
- provider activation readiness.

The runtime records provider unavailable at:

```text
Certified Provider Attachment
-> Provider Attachment Runtime
-> OpenAIProviderAdapter.generate_proposal(...)
-> OpenAIProviderAdapter._call_openai(...)
-> OpenAIHTTPClient / configured client
-> FailClosedRuntimeError("OpenAI provider unavailable")
```

The failure remains replay-safe and fail-closed.

## Existing Capability Reuse

The observed runtime reuses existing certified capabilities:

- Worker continuation from governed development execution;
- OpenAI external worker provider adapter;
- Certified Provider Attachment boundary;
- Provider Registry metadata validation;
- Provider health and readiness runtime;
- provider adapter validation;
- fail-closed provider diagnostics;
- immutable replay artifacts.

No new Provider Platform, Registry, Selection engine, Worker architecture, Cognition architecture, Runtime architecture, Governance model, or Replay model is required for this audit finding.

## Architectural Conclusions

1. The Central Provider Platform boundary is reached.

2. Provider Registry is reached and succeeds.

3. Provider selection is deterministic for this Worker path and selects `openai`.

4. Smart or dynamic multi-provider selection is not executed in this single-provider Worker path; the replayed failure occurs after deterministic provider selection and readiness.

5. Credential presence succeeds in the observed readiness artifact.

6. Health detection succeeds and records `readiness_status=READY`.

7. Provider adapter invocation is reached and records `OpenAI provider unavailable`.

8. External provider success is not achieved; the provider result remains fail-closed and replay-visible.

9. The failure is operational/configuration/transport at the provider adapter invocation boundary, not a Platform Core or Human Interface routing defect.

## Final Recommendation

Preserve the existing Central Provider Platform architecture and investigate the operational provider execution environment at the adapter invocation boundary:

- verify live OpenAI endpoint reachability from the runtime host;
- verify the configured key is accepted by the OpenAI Responses API;
- verify model entitlement for the configured model;
- verify no network policy, proxy, DNS, TLS, or egress constraint blocks `https://api.openai.com/v1/responses`;
- rerun the same governed approval path and inspect `certified_provider_attachment` replay artifacts.

Do not redesign Provider Platform, Registry, Selection, Worker, Cognition, Runtime, Governance, Replay, or Human Interface architecture.

## Final Verdict

`PROVIDER_PLATFORM_OPERATIONAL_CONFIGURATION_REQUIRED`

Deterministic support:

- Provider Platform boundary is reached through `run_certified_provider_attachment(...)`.
- Registry lookup is implemented and reached through `registry.lookup_provider(provider_id)`.
- Readiness replay records `READY` for api key presence, provider configuration, model configuration, transport availability, and provider activation.
- The fail-closed provider artifacts record `failure_reason=OpenAI provider unavailable`.
- Provider diagnostics record `failure_stage=openai_provider_adapter`.
- Worker result replay records `execution_status=FAILED_CLOSED`.

The selected external provider becomes unavailable at the provider adapter invocation stage after Central Provider Platform readiness succeeds.
