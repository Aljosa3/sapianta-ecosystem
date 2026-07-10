# G17-HI-14 OpenAI Provider Adapter Runtime Invocation Trace

## Executive Summary

This audit traces the actual OpenAI provider adapter runtime path after G17-HI-13 confirmed that API key presence, environment readability, provider identity, credential binding, adapter initialization, and health checks succeed.

The runtime reaches the OpenAI adapter invocation path. The recorded failure is not produced by Platform Core, Human Interface, Worker routing, Provider Registry, readiness, or adapter initialization. It is produced after the adapter has a callable client and attempts provider invocation through the OpenAI adapter path.

The deterministic runtime result is:

```text
failure_reason = OpenAI provider unavailable
failure_stage = openai_provider_adapter
```

Final verdict: `ADAPTER_RUNTIME_INVOCATION_EXTERNAL_FAILURE`.

## Runtime Chain

The traced chain is:

```text
Worker continuation
-> _external_worker_openai_client()
-> run_openai_external_worker_provider_adapter(...)
-> _compatibility_client(...)
-> OpenAIProviderAdapter(...)
-> run_certified_provider_attachment(...)
-> run_provider_attachment(...)
-> OpenAIProviderAdapter.generate_proposal(...)
-> OpenAIProviderAdapter._call_openai(...)
-> callable client
-> OpenAIHTTPClient.__call__(...)
-> fail-closed error normalization
-> certified provider attachment replay
-> external worker failed result package
```

Implementation evidence:

- `aigol/cli/aigol_cli.py` lines 863-880 creates `_external_worker_openai_client()`, instantiates `OpenAIHTTPClient()`, and returns a transport callable.
- `aigol/cli/aigol_cli.py` lines 1030-1040 passes that callable into `run_openai_external_worker_provider_adapter(...)`.
- `aigol/runtime/openai_external_worker_provider_adapter.py` lines 72-99 constructs `OpenAIProviderAdapter(...)` and invokes `run_certified_provider_attachment(...)`.
- `aigol/provider/provider_runtime.py` lines 77-81 validates provider and request, then calls `adapter.generate_proposal(...)`.
- `aigol/provider/providers/openai_provider.py` lines 70-75 resolves the key, prepares the request, and calls `_call_openai(...)`.

## Adapter Initialization

Adapter initialization succeeds before the failure is recorded.

Implementation evidence:

- `OpenAIProviderAdapter.__init__(...)` validates provider version, model, endpoint, timeout, optional max output tokens, explicit API key, and client at `aigol/provider/providers/openai_provider.py` lines 51-68.
- If a client is not supplied, the adapter defaults to `OpenAIHTTPClient()` at line 68.
- In this Worker path, a client is supplied through `_compatibility_client(openai_client)` at `aigol/runtime/openai_external_worker_provider_adapter.py` lines 92-97.

Runtime evidence:

- `000_provider_readiness_recorded.json` records `transport_available=True`.
- The same artifact records `model_configuration_valid=True`, `provider_configuration_valid=True`, and `readiness_status=READY`.

Conclusion:

The client can be created and is callable. The failure is not adapter initialization failure.

## Availability Check

The availability/readiness check passes before provider invocation.

Implementation evidence:

- `_provider_readiness_checks(...)` verifies API key presence, provider configuration, model configuration, transport availability, and provider activation readiness at `aigol/provider/provider_runtime.py` lines 528-555.
- `_openai_transport_available(...)` checks `callable(adapter._client)` at `aigol/provider/provider_runtime.py` lines 626-627.

Runtime evidence from `000_provider_readiness_recorded.json`:

```text
provider_id=openai
provider_version=openai-responses-v1
provider_status=AVAILABLE
readiness_status=READY
api_key_present=True
transport_available=True
provider_invocation_allowed=True
```

Conclusion:

Availability is not incorrectly reported as unavailable before invocation. It is reported ready, and the fail-closed state is recorded later.

## Client Creation

The Worker path creates a callable client wrapper around the OpenAI HTTP client.

Implementation evidence:

- `_external_worker_openai_client()` creates `http_client = OpenAIHTTPClient()` at `aigol/cli/aigol_cli.py` line 864.
- The returned `_transport(...)` function calls that HTTP client with `api_key=os.environ.get(OPENAI_API_KEY_ENV, "")`, `endpoint=OPENAI_RESPONSES_ENDPOINT`, and the configured timeout at `aigol/cli/aigol_cli.py` lines 873-878.
- `_compatibility_client(...)` wraps the Worker transport so it can satisfy the OpenAI provider adapter callable interface at `aigol/runtime/openai_external_worker_provider_adapter.py` lines 347-364.

Conclusion:

The client is created. The API call is not blocked by missing client construction.

## API Invocation

The adapter attempts invocation through `_call_openai(...)`.

Implementation evidence:

- `OpenAIProviderAdapter.generate_proposal(...)` calls `_call_openai(...)` at `aigol/provider/providers/openai_provider.py` line 75.
- `_call_openai(...)` first checks `callable(self._client)` at lines 111-113.
- If callable, `_call_openai(...)` invokes the client at lines 115-120.
- `OpenAIHTTPClient.__call__(...)` builds a POST request to the configured endpoint at lines 142-150.
- `OpenAIHTTPClient.__call__(...)` executes `request.urlopen(...)` and decodes JSON at lines 152-154.

Runtime evidence:

- `001_openai_provider_adapter_recorded.json` records `provider_invoked_inside_adapter=True`.
- The certified provider attachment artifacts record `failure_stage=openai_provider_adapter`, not readiness failure.

Conclusion:

The API invocation path is reached. Runtime replay does not prove a successful HTTP round trip; it proves the adapter boundary was entered and failed before a successful provider proposal envelope was created.

## Response Handling

Successful response handling would require a raw OpenAI response and a valid bounded response text.

Implementation evidence:

- After `_call_openai(...)`, `generate_proposal(...)` calls `_extract_response_text(raw_response)` at `aigol/provider/providers/openai_provider.py` line 76.
- A successful provider proposal envelope is created only after response text extraction at lines 77-109.

Runtime evidence:

- `000_provider_proposal_created.json` records `provider_status=FAILED_CLOSED`, `provider_invoked=False`, and `provider_version=UNKNOWN`.
- `002_certified_provider_attachment_recorded.json` records `provider_status=FAILED_CLOSED`.
- No successful provider proposal envelope is recorded.

Conclusion:

The runtime does not reach successful response handling. It fails before a completed provider proposal can be persisted.

## Error Handling

There are two implementation locations that can produce the exact string `OpenAI provider unavailable`:

1. HTTP-client transport/response normalization:

```text
aigol/provider/providers/openai_provider.py line 158
```

`OpenAIHTTPClient.__call__(...)` raises `FailClosedRuntimeError("OpenAI provider unavailable")` for:

- `URLError`;
- `TimeoutError`;
- `json.JSONDecodeError`.

2. Adapter-level client exception normalization:

```text
aigol/provider/providers/openai_provider.py line 124
```

`OpenAIProviderAdapter._call_openai(...)` raises `FailClosedRuntimeError("OpenAI provider unavailable")` for non-`FailClosedRuntimeError` exceptions raised by the callable client.

The adapter preserves already fail-closed exceptions:

```text
aigol/provider/providers/openai_provider.py lines 121-122
```

Provider Attachment then records diagnostics:

- `_failure_diagnostics(...)` builds diagnostics at `aigol/provider/provider_runtime.py` lines 429-439.
- `_diagnostic_exception(...)` unwraps direct HTTP, URL, timeout, or JSON causes at lines 442-446.
- `_failure_stage(...)` records `openai_provider_adapter` when the failure is a `FailClosedRuntimeError` whose message starts with `OpenAI provider` at lines 449-454.

Runtime evidence:

```text
failure_reason=OpenAI provider unavailable
failure_stage=openai_provider_adapter
exception_type=FailClosedRuntimeError
transport_failure_category=FAIL_CLOSED
http_status=None
```

Conclusion:

The persisted runtime result is produced by fail-closed error normalization inside the OpenAI adapter path. The replay artifact preserves the normalized provider failure, but it does not preserve enough original exception detail to distinguish line 124 from line 158 for this specific run.

## Runtime Evidence

Observed replay path:

```text
.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/
  governed_bridge_certified_development_continuation/
  worker_lifecycle_continuation/
  openai_external_worker_provider/
```

Key artifacts:

- `certified_provider_attachment/000_provider_readiness_recorded.json`
  - `readiness_status=READY`
  - `api_key_present=True`
  - `transport_available=True`
  - `provider_invocation_allowed=True`

- `certified_provider_attachment/000_provider_proposal_created.json`
  - `provider_status=FAILED_CLOSED`
  - `provider_invoked=False`
  - `failure_reason=OpenAI provider unavailable`
  - `failure_stage=openai_provider_adapter`
  - `exception_type=FailClosedRuntimeError`
  - `transport_failure_category=FAIL_CLOSED`
  - `http_status=None`

- `certified_provider_attachment/002_certified_provider_attachment_recorded.json`
  - `provider_status=FAILED_CLOSED`
  - `provider_invoked=False`
  - `failure_reason=OpenAI provider unavailable`
  - `failure_stage=openai_provider_adapter`

- `001_openai_provider_adapter_recorded.json`
  - `provider_status=FAILED_CLOSED`
  - `provider_invoked_inside_adapter=True`
  - `failure_reason=OpenAI provider unavailable`

- `003_openai_external_worker_returned.json`
  - `openai_provider_connected=False`
  - `failure_reason=OpenAI provider unavailable`

## Investigation Answers

API call is never attempted:

Not supported. The callable client is created, readiness records transport availability, `generate_proposal(...)` reaches `_call_openai(...)`, and adapter replay records `provider_invoked_inside_adapter=True`.

Client cannot be created:

Ruled out. `_external_worker_openai_client()` creates `OpenAIHTTPClient()`, the adapter receives a callable compatibility client, and readiness records `transport_available=True`.

Adapter catches an exception and rewrites it:

Supported as the persisted fail-closed mechanism. Either `OpenAIHTTPClient.__call__(...)` raises `FailClosedRuntimeError("OpenAI provider unavailable")` at line 158 for URL/timeout/JSON failures, or `_call_openai(...)` raises the same message at line 124 for non-fail-closed client exceptions. The certified replay records the normalized fail-closed result.

Availability incorrectly reported:

Not supported. Availability/readiness is a pre-invocation local readiness signal. It records the adapter as locally invocable, not that the external OpenAI service will successfully respond.

Fail-closed path triggered before invocation:

Not supported by replay. Readiness succeeds and adapter replay records `provider_invoked_inside_adapter=True`. The fail-closed path is triggered during adapter invocation before a successful provider proposal envelope is created.

## Final Verdict

`ADAPTER_RUNTIME_INVOCATION_EXTERNAL_FAILURE`

Deterministic support:

- Worker creates a callable OpenAI HTTP transport.
- Provider readiness records `READY`.
- Transport availability records `True`.
- The adapter invocation path reaches `_call_openai(...)`.
- Adapter replay records `provider_invoked_inside_adapter=True`.
- Certified Provider Attachment records `failure_reason=OpenAI provider unavailable`.
- Certified Provider Attachment records `failure_stage=openai_provider_adapter`.
- No successful provider proposal envelope is created.

The exact persisted runtime result is produced by fail-closed normalization in the OpenAI adapter invocation path, with implementation emitters at `aigol/provider/providers/openai_provider.py` line 158 or line 124 depending on the underlying client exception. The replay evidence for the observed run certifies external adapter invocation failure, not an implementation defect in Platform Core, Provider Platform, Worker Runtime, Governance, or Replay.
