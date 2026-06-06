# AIGOL_REAL_OPENAI_PROVIDER_AVAILABILITY_TRACE_REVIEW_V1

## Status

Review-only investigation.

No implementation was performed. No runtime code was changed. No provider code was changed. No governance model was changed.

## Executive Finding

The OpenAI provider is registered correctly, provider lookup succeeds, adapter initialization succeeds, and the current process environment contains `OPENAI_API_KEY`.

The observed `OpenAI provider unavailable` failure occurs after those gates, at the outbound OpenAI client call / HTTP transport boundary.

The exact low-level exception is not persisted in the replay. Repository code shows the message can be produced by:

- `aigol/provider/providers/openai_provider.py::OpenAIHTTPClient.__call__` when `urllib` raises `URLError`, `TimeoutError`, or `JSONDecodeError`;
- `aigol/provider/providers/openai_provider.py::OpenAIProviderAdapter._call_openai` when a non-`FailClosedRuntimeError` escapes the configured client.

Because the default conversational adapter uses `OpenAIHTTPClient`, and because missing credentials, provider registration failure, provider lookup failure, and adapter validation failure would produce different failure strings, the fail-closed classification is:

```text
ROOT_CAUSE = outbound OpenAI transport unavailable after successful provider registration, lookup, adapter initialization, and credential lookup
```

## Required Outputs

```text
REAL_OPENAI_PROVIDER_REGISTERED = true
REAL_OPENAI_PROVIDER_CREDENTIAL_FOUND = true
REAL_OPENAI_PROVIDER_AVAILABLE = false
FAILURE_LOCATION = aigol/provider/providers/openai_provider.py::OpenAIHTTPClient.__call__ outbound request boundary, surfaced through OpenAIProviderAdapter.generate_proposal and run_provider_attachment
ROOT_CAUSE = OpenAI outbound transport unavailable; exact underlying network/timeout/response-decoding cause is not replay-persisted
```

## Direct Answers

1. `OpenAIProviderAdapter` reports unavailable because its client call fails before a successful provider proposal envelope is created. The failure is surfaced as `OpenAI provider unavailable`.

2. `OpenAIProviderAdapter` is registered correctly through `_conversation_openai_provider_registry()`, which registers `openai_provider_metadata()` with status `AVAILABLE`.

3. Provider lookup succeeds. Local inspection returned:

```text
LOOKUP_PROVIDER_ID=openai
LOOKUP_PROVIDER_STATUS=AVAILABLE
```

4. Credential lookup succeeds for the current process environment. Local inspection found:

```text
OPENAI_API_KEY_PRESENT=True
AIGOL_OPENAI_API_KEY_PRESENT=False
```

The adapter used by this path reads `OPENAI_API_KEY`, not `AIGOL_OPENAI_API_KEY`.

5. The failing availability check is not provider registry availability. The registry status is `AVAILABLE`. The failure occurs at provider invocation availability: `OpenAIHTTPClient.__call__` / `OpenAIProviderAdapter._call_openai`.

6. Cause classification:

| Candidate | Finding |
| --- | --- |
| missing API key | Not supported by evidence. Missing key would report `OPENAI_API_KEY is required`; current environment has `OPENAI_API_KEY`. |
| wrong environment variable | Not supported. This adapter uses `OPENAI_API_KEY`, which is present. |
| provider registration | Not supported. Provider lookup returns `AVAILABLE`. |
| adapter initialization | Not supported. Adapter class is `OpenAIProviderAdapter`, provider id is `openai`. |
| transport configuration | Plausible boundary. Endpoint is `https://api.openai.com/v1/responses`; outbound call failed. |
| runtime guard | Not supported. Runtime reached `adapter.generate_proposal(...)`. |
| policy restriction | Not supported by observed failure string. |
| network restriction | Plausible and consistent with `OpenAI provider unavailable`, but exact low-level exception is not replay-persisted. |

## Trace

```text
conversational CLI
-> _conversation_ocs_cognition_provider_contracts(...)
-> _conversation_ocs_cognition_transports(...)
-> run_provider_attachment(provider_id="openai", ...)
-> ProviderRegistry.lookup_provider("openai")
-> provider_status == AVAILABLE
-> _validate_adapter(...)
-> OpenAIProviderAdapter.generate_proposal(...)
-> _resolve_api_key(...)
-> _call_openai(...)
-> OpenAIHTTPClient.__call__(...)
-> FAILED_CLOSED: OpenAI provider unavailable
```

## Evidence Details

### Conversational Binding

`aigol/cli/aigol_cli.py::_conversation_ocs_cognition_transports` binds both `openai` and `openai-comparison` to the same transport helper. That helper calls:

```text
run_provider_attachment(provider_id=OPENAI_PROVIDER_ID, ...)
```

with:

```text
registry=_conversation_openai_provider_registry()
adapter=_conversation_openai_provider_adapter()
```

### Provider Registration

`aigol/cli/aigol_cli.py::_conversation_openai_provider_registry` registers:

```text
openai_provider_metadata()
```

`aigol/provider/providers/openai_provider.py::openai_provider_metadata` creates metadata with:

```text
provider_id = openai
provider_type = llm
provider_version = openai-responses-v1
provider_status = AVAILABLE
```

### Provider Attachment

`aigol/provider/provider_runtime.py::run_provider_attachment` performs:

```text
provider = registry.lookup_provider(provider_id)
if provider["provider_status"] != AVAILABLE:
    raise FailClosedRuntimeError("provider is unavailable")
_validate_adapter(...)
_validate_request(...)
envelope = adapter.generate_proposal(...)
```

The observed failure string is not `provider is unavailable`, so registry availability is not the failing check.

### Credential Lookup

`aigol/provider/providers/openai_provider.py::OpenAIProviderAdapter.generate_proposal` calls:

```text
api_key = _resolve_api_key(self._api_key)
```

`_resolve_api_key` reads:

```text
OPENAI_API_KEY
```

If the key were missing, the failure string would be:

```text
OPENAI_API_KEY is required
```

The observed failure string is:

```text
OpenAI provider unavailable
```

### Failure Point

The adapter then calls:

```text
raw_response = self._call_openai(payload=payload, api_key=api_key)
```

`OpenAIProviderAdapter._call_openai` maps non-runtime client exceptions to:

```text
OpenAI provider unavailable
```

The default `OpenAIHTTPClient.__call__` maps:

```text
URLError
TimeoutError
JSONDecodeError
```

to:

```text
OpenAI provider unavailable
```

The observed provider attachment replay recorded:

```text
event_type: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
provider_invoked: false
provider_status: FAILED_CLOSED
provider_version: UNKNOWN
response: null
```

## Conclusion

OpenAI provider availability failed after provider registration, provider lookup, adapter initialization, and credential lookup.

The exact low-level network or response failure is not retained in replay, so the review cannot honestly distinguish DNS failure, sandbox/network restriction, timeout, or malformed response decoding from replay alone.

The repository-backed answer is:

```text
REAL_OPENAI_PROVIDER_AVAILABLE = false
FAILURE_LOCATION = OpenAIProviderAdapter outbound client call / OpenAIHTTPClient transport
ROOT_CAUSE = outbound OpenAI transport unavailable; low-level exception not replay-visible
```
