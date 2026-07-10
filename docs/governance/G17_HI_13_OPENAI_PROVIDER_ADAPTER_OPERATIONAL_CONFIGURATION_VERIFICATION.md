# G17-HI-13 OpenAI Provider Adapter Operational Configuration Verification

## Executive Summary

G17-HI-12 established that the Central Provider Platform boundary is reached and that the remaining failure is emitted at:

```text
failure_stage = openai_provider_adapter
failure_reason = OpenAI provider unavailable
```

This verification reviews the OpenAI provider adapter operational configuration without changing Platform Core, Worker Runtime, Provider Platform, Governance, Replay, or Human Interface architecture.

Deterministic evidence rules out missing API key, unreadable `OPENAI_API_KEY`, wrong provider identity, wrong credential binding, adapter initialization failure, and provider readiness failure. The adapter reaches the OpenAI invocation path and fails closed during provider adapter execution.

Final verdict: `OPENAI_PROVIDER_ENVIRONMENT_CONFIGURATION_REQUIRED`.

## Adapter Configuration Review

The OpenAI adapter has deterministic configuration defaults:

- `OPENAI_PROVIDER_ID = "openai"`
- `OPENAI_PROVIDER_TYPE = "llm"`
- `OPENAI_PROVIDER_VERSION = "openai-responses-v1"`
- `OPENAI_API_KEY_ENV = "OPENAI_API_KEY"`
- `OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"`
- `DEFAULT_OPENAI_MODEL = "gpt-5.1"`
- `DEFAULT_TIMEOUT_SECONDS = 20`

Implementation evidence:

- `aigol/provider/providers/openai_provider.py` lines 24-30 define provider identity, credential environment variable, endpoint, model, and timeout constants.
- `OpenAIProviderAdapter.__init__(...)` at `aigol/provider/providers/openai_provider.py` lines 51-68 validates provider version, model, endpoint, timeout, optional max tokens, stores the explicit api key, and defaults to `OpenAIHTTPClient()`.
- `aigol/runtime/openai_external_worker_provider_adapter.py` lines 72-99 constructs `OpenAIProviderAdapter(...)` and passes it through `run_certified_provider_attachment(...)`.

Finding:

Adapter initialization is not the failing stage. The runtime reaches provider attachment and records readiness before the adapter invocation failure.

## Credential Resolution Review

Credential resolution is deterministic:

```text
explicit adapter api_key
else OPENAI_API_KEY environment variable
else fail closed with "OPENAI_API_KEY is required"
```

Implementation evidence:

- `_resolve_api_key(...)` at `aigol/provider/providers/openai_provider.py` lines 244-246 uses the explicit adapter key first and falls back to `os.environ.get(OPENAI_API_KEY_ENV)`.
- `_require_string(...)` at `aigol/provider/providers/openai_provider.py` lines 249-252 fail-closes if the credential is not a non-empty string.
- `_openai_api_key_present(...)` at `aigol/provider/provider_runtime.py` lines 589-593 uses the same operational shape for readiness: adapter `_api_key` first, then `OPENAI_API_KEY`.

Replay evidence:

- `000_provider_readiness_recorded.json` records `api_key_present=True`.
- The same readiness artifact records `api_key_presence=READY`.

Finding:

Credential resolution is not failing in the observed runtime evidence.

## Environment Variable Review

Current process environment verification:

```text
OPENAI_API_KEY_PRESENT=True
OPENAI_API_KEY_READABLE_AS_STRING=True
OPENAI_API_KEY_NONEMPTY=True
AIGOL_OPENAI_API_KEY_PRESENT=False
```

Implementation evidence:

- The adapter uses `OPENAI_API_KEY`, not `AIGOL_OPENAI_API_KEY`.
- `OPENAI_API_KEY_ENV = "OPENAI_API_KEY"` is defined in `aigol/provider/providers/openai_provider.py` line 27.
- `_resolve_api_key(...)` reads `OPENAI_API_KEY` at `aigol/provider/providers/openai_provider.py` lines 244-246.

Replay evidence:

- `000_provider_readiness_recorded.json` records `api_key_present=True`.

Finding:

The required environment variable is readable and non-empty in the current process and was observed as present by runtime readiness. `AIGOL_OPENAI_API_KEY` being absent is not relevant to this adapter path because the implementation does not read that variable.

## Provider Identity Review

Provider identity is consistent between the adapter, provider registry, and readiness artifact.

Implementation evidence:

- `OpenAIProviderAdapter.provider_id = OPENAI_PROVIDER_ID` at `aigol/provider/providers/openai_provider.py` lines 46-50.
- `openai_provider_metadata(...)` returns `provider_id=openai`, `provider_type=llm`, and `provider_version=openai-responses-v1` at `aigol/provider/providers/openai_provider.py` lines 161-167.
- `_openai_provider_configuration_valid(...)` requires provider id and provider version to match the adapter at `aigol/provider/provider_runtime.py` lines 605-609.

Replay evidence:

- `000_provider_readiness_recorded.json` records:

```text
provider_id=openai
provider_version=openai-responses-v1
provider_status=AVAILABLE
provider_configuration_valid=True
provider_configuration_validity=READY
```

Finding:

Wrong provider identity is ruled out by implementation and replay evidence.

## Health Check Review

Provider readiness passes all configured health checks.

Implementation evidence:

- `_provider_readiness_artifact(...)` records readiness status and sanitized diagnostics at `aigol/provider/provider_runtime.py` lines 490-525.
- `_provider_readiness_checks(...)` checks api key presence, provider configuration validity, model configuration validity, transport availability, and provider activation readiness at `aigol/provider/provider_runtime.py` lines 528-555.
- `_openai_model_configuration_valid(...)` validates non-empty model, HTTPS endpoint, and positive timeout at `aigol/provider/provider_runtime.py` lines 612-623.
- `_openai_transport_available(...)` validates that the adapter client is callable at `aigol/provider/provider_runtime.py` lines 626-627.

Replay evidence from `000_provider_readiness_recorded.json`:

```text
readiness_status=READY
api_key_present=True
provider_configuration_valid=True
model_configuration_valid=True
transport_available=True
provider_activation_ready=True
provider_invocation_allowed=True
api_key_presence=READY
provider_configuration_validity=READY
model_configuration_validity=READY
transport_availability=READY
provider_activation_readiness=READY
```

Finding:

Health check failure is ruled out for the observed runtime path.

## Adapter Invocation Review

The adapter reaches the invocation path and fails closed there.

Implementation evidence:

- `OpenAIProviderAdapter.generate_proposal(...)` resolves the api key, extracts the prompt, creates the Responses API payload, and calls `_call_openai(...)` at `aigol/provider/providers/openai_provider.py` lines 70-75.
- `_call_openai(...)` fails closed with `OpenAI provider client is invalid` only when the client is not callable, then otherwise calls the configured client at `aigol/provider/providers/openai_provider.py` lines 111-120.
- `_call_openai(...)` preserves already certified fail-closed exceptions and converts other exceptions to `FailClosedRuntimeError("OpenAI provider unavailable")` at `aigol/provider/providers/openai_provider.py` lines 121-124.
- `OpenAIHTTPClient.__call__(...)` performs one non-streaming POST to the configured endpoint and converts `URLError`, `TimeoutError`, and JSON decode failures to `OpenAI provider unavailable` at `aigol/provider/providers/openai_provider.py` lines 152-158.

Replay evidence:

- `001_openai_provider_adapter_recorded.json` records:

```text
provider_id=openai
provider_status=FAILED_CLOSED
provider_invoked_inside_adapter=True
failure_reason=OpenAI provider unavailable
```

- `000_provider_proposal_created.json` records:

```text
provider_status=FAILED_CLOSED
provider_invoked=False
failure_reason=OpenAI provider unavailable
failure_stage=openai_provider_adapter
exception_type=FailClosedRuntimeError
http_status=None
transport_failure_category=FAIL_CLOSED
```

- `002_certified_provider_attachment_recorded.json` records the same failure reason and `failure_stage=openai_provider_adapter`.
- `002_openai_external_worker_result_recorded.json` records `execution_status=FAILED_CLOSED`.
- `003_openai_external_worker_returned.json` records `openai_provider_connected=False`.

Finding:

The adapter invocation path is reached. No successful provider proposal envelope is returned. The fail-closed condition occurs during external provider invocation or response handling after local readiness has succeeded.

## Root Cause

The root cause is operational environment/provider availability at the OpenAI adapter invocation boundary.

Ruled out by deterministic evidence:

- missing API key: readiness records `api_key_present=True`;
- unreadable environment variable: current process reads non-empty `OPENAI_API_KEY`;
- wrong credential binding: implementation uses `OPENAI_API_KEY`, and readiness passed the same binding shape;
- wrong provider identity: readiness records `provider_id=openai`, `provider_version=openai-responses-v1`, and `provider_configuration_valid=True`;
- adapter initialization failure: readiness records `transport_available=True` and model/endpoint/timeout validity;
- health check failure: readiness records `readiness_status=READY`;
- Provider Platform routing failure: certified attachment replay reaches provider adapter diagnostics.

Not ruled out by current replay evidence:

- outbound network or DNS/TLS/egress failure;
- OpenAI endpoint reachability failure from the runtime host;
- API key accepted by local presence checks but rejected by OpenAI at invocation time;
- account/project/model entitlement mismatch for `gpt-5.1`;
- provider-side transient unavailability;
- response-shape failure after an HTTP response that did not produce a valid Responses API JSON body.

No deterministic implementation evidence identifies an adapter code defect. The adapter fail-closes exactly at the configured boundary and records sanitized replay diagnostics.

## Required Configuration Action

Preserve the existing adapter and Provider Platform architecture. Verify the operational provider environment:

1. Confirm the runtime host can reach `https://api.openai.com/v1/responses`.
2. Confirm the configured `OPENAI_API_KEY` is valid for the runtime environment.
3. Confirm the key has access to the configured project/account and model `gpt-5.1`.
4. Confirm no proxy, firewall, DNS, TLS, or egress rule blocks the runtime process.
5. Rerun the governed approval path and inspect the same replay directory:

```text
.runtime/aicli/AICLI-REFERENCE-SESSION/<TURN>/governed_bridge_certified_development_continuation/worker_lifecycle_continuation/openai_external_worker_provider/certified_provider_attachment/
```

Expected successful evidence after configuration correction:

```text
provider_status=COMPLETED
provider_invoked=True
openai_provider_connected=True
execution_status=COMPLETED
```

## Final Verdict

`OPENAI_PROVIDER_ENVIRONMENT_CONFIGURATION_REQUIRED`

Deterministic support:

- `OPENAI_API_KEY` is present, readable as a string, and non-empty in the current process.
- Runtime readiness records `api_key_present=True`.
- Runtime readiness records `provider_configuration_valid=True`.
- Runtime readiness records `model_configuration_valid=True`.
- Runtime readiness records `transport_available=True`.
- Runtime readiness records `provider_activation_ready=True`.
- Certified Provider Attachment records `failure_stage=openai_provider_adapter`.
- Certified Provider Attachment records `failure_reason=OpenAI provider unavailable`.
- Worker result replay records `execution_status=FAILED_CLOSED`.

The OpenAI adapter is locally configured and readiness-certified, but the runtime environment is not operationally completing external OpenAI invocation.
