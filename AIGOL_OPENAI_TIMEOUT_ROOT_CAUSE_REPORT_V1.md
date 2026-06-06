# AIGOL_OPENAI_TIMEOUT_ROOT_CAUSE_REPORT_V1

## Status

Review-only timeout root-cause investigation.

No runtime code was changed. No provider behavior was changed. No governance semantics were changed.

## Executive Finding

The conversational OCS OpenAI provider path times out because it uses `OpenAIProviderAdapter()` with the default fixed timeout:

```text
REQUEST_TIMEOUT_SECONDS = 20
```

The same replayed OCS provider request failed at:

```text
ACTUAL_ELAPSED_SECONDS = 20.142
exception_chain:
FailClosedRuntimeError("OpenAI provider unavailable")
-> TimeoutError("The read operation timed out")
```

The timeout is reached inside:

```text
aigol/provider/providers/openai_provider.py::OpenAIHTTPClient.__call__
```

at the `urllib.request.urlopen(..., timeout=timeout_seconds)` read boundary.

## Determined Configuration

| Field | Value |
| --- | --- |
| `REQUEST_TIMEOUT_SECONDS` | `20` |
| `ACTUAL_ELAPSED_SECONDS` | `20.142` for same replayed request |
| `OPENAI_MODEL_USED` | `gpt-5.1` |
| `OPENAI_ENDPOINT_USED` | `https://api.openai.com/v1/responses` |
| `STREAMING` | `false` |
| `PAYLOAD_KEYS` | `input`, `model`, `stream` |
| `PROMPT_CHARS` | `3059` for `openai`; `3070` for `openai-comparison` |

## Source Trace

1. Conversational OCS binding creates two contracts:

```text
aigol/cli/aigol_cli.py::_conversation_ocs_cognition_provider_contracts
```

Providers:

- `openai`
- `openai-comparison`

2. Conversational OCS transport calls:

```text
aigol/cli/aigol_cli.py::_conversation_ocs_cognition_transports
-> run_provider_attachment(...)
```

3. The provider adapter is constructed without a timeout override:

```text
aigol/cli/aigol_cli.py::_conversation_openai_provider_adapter
-> OpenAIProviderAdapter()
```

4. The adapter default is:

```text
aigol/provider/providers/openai_provider.py
DEFAULT_TIMEOUT_SECONDS = 20
```

5. The HTTP client performs one non-streaming request:

```text
request.urlopen(http_request, timeout=timeout_seconds)
```

6. `TimeoutError` is collapsed into:

```text
FailClosedRuntimeError("OpenAI provider unavailable")
```

## Verification Matrix

| Question | Determination | Evidence |
| --- | --- | --- |
| Timeout value too low | `TRUE` | 20s replayed request fails at 20.142s; 60s probe passes the timeout boundary |
| Request payload malformed | `FALSE` | Prompt JSON valid; payload keys are `input`, `model`, `stream` |
| Model name mismatch | `NO EVIDENCE` | Same request reaches response extraction with 60s timeout |
| Endpoint mismatch | `FALSE` | Endpoint is `/v1/responses`; 60s probe reaches response extraction |
| Streaming mismatch | `FALSE` | Both binding and payload use non-streaming mode |
| Transport wrapper blocks response parsing | `FALSE_FOR_TIMEOUT` | 60s probe reaches response text bound check |

## Second Blocking Condition

The 60 second probe did not time out. It failed later with:

```text
FailClosedRuntimeError("OpenAI provider response exceeds bounded size")
```

This identifies a second downstream blocker:

```text
MAX_OPENAI_RESPONSE_CHARS = 8192
```

Therefore increasing the timeout alone is expected to remove the `TimeoutError`, but not necessarily make the full conversational OCS run complete. The next fail-closed condition is likely the bounded response size guard unless output length is constrained or the bound is deliberately revised.

## Root Cause

The immediate timeout root cause is an OCS workload mismatch with the provider attachment default:

```text
Conversational OCS prompt
-> gpt-5.1 Responses API
-> non-streaming request
-> fixed 20 second timeout
-> read timeout before model response completes
```

The configured timeout is adequate for small connectivity probes but too low for the larger OCS cognition prompt and requested analysis structure.

## Fix Required

`TRUE`.

## Minimal Safe Fix

Make the conversational OCS OpenAI provider timeout explicitly configurable or OCS-specific, and set it above the observed completion boundary.

Recommended minimal safe direction:

```text
_conversation_openai_provider_adapter()
-> OpenAIProviderAdapter(timeout_seconds=<bounded OCS timeout>)
```

The bound should remain deterministic, replay-visible, and fail-closed.

To achieve end-to-end success rather than only replacing the timeout failure, also constrain output length at the request level or revise the bounded response policy deliberately:

```text
OpenAI response length must fit MAX_OPENAI_RESPONSE_CHARS
```

## Expected Result After Fix

After increasing the OCS provider timeout, the current `TimeoutError` should stop occurring for the observed prompt.

If no output-size change is made, the expected next failure is:

```text
OpenAI provider response exceeds bounded size
```

after the model response is received.

