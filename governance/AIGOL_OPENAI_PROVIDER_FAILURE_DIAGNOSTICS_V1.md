# AIGOL_OPENAI_PROVIDER_FAILURE_DIAGNOSTICS_V1

## Status

Implemented.

Classification:

```text
CERTIFIED_OPENAI_PROVIDER_FAILURE_DIAGNOSTICS
```

## Objective

Add minimal, sanitized, fail-closed diagnostics for OpenAI provider failures while preserving existing provider attachment semantics.

## Scope

Changed runtime surface:

```text
aigol/provider/provider_runtime.py
```

Added test surface:

```text
tests/test_openai_provider_failure_diagnostics_v1.py
```

No new provider runtime was created. No new OpenAI adapter was created. No cognition runtime, replay model, governance model, comparison runtime, continuity runtime, or clarification runtime was introduced.

## Runtime Change

Provider attachment failures still persist the existing `failure_reason` field unchanged.

Failed provider proposal artifacts now also include:

```text
failure_diagnostics:
  failure_stage
  exception_type
  transport_failure_category
  http_status
```

The diagnostics are derived from the fail-closed exception chain and are intentionally bounded.

## Sanitization Boundary

Allowed diagnostic fields:

- `exception_type`
- `transport_failure_category`
- `http_status`
- `failure_stage`

Disallowed diagnostic content:

- API keys
- Authorization headers
- request bodies
- raw response bodies
- stack traces
- raw transport exception messages

## Diagnostic Categories

Implemented transport categories:

| Source exception | Category |
| --- | --- |
| `urllib.error.HTTPError` | `HTTP_ERROR` |
| `urllib.error.URLError` | `URL_ERROR` |
| `TimeoutError` | `TIMEOUT` |
| `json.JSONDecodeError` | `JSON_DECODE` |
| `FailClosedRuntimeError` | `FAIL_CLOSED` |
| other exception | `CLIENT_EXCEPTION` |

## Replay Evidence

Both failed replay steps contain the same sanitized diagnostics:

```text
000_provider_proposal_created.json
001_provider_proposal_returned.json
```

This preserves replay reconstruction while making the failure reason operationally diagnosable.

## Boundary Guarantees

- Provider failures remain fail-closed.
- Provider authority remains false.
- Execution capability remains false.
- Worker invocation remains false.
- Existing `failure_reason` remains present.
- Sensitive values are not serialized into diagnostics.

## Tests

Added coverage verifies:

- DNS-style `URLError` diagnostics.
- Timeout diagnostics.
- HTTP status diagnostics for `HTTPError`.
- Replay-visible diagnostics on created and returned failure artifacts.
- Exclusion of API key, Authorization header, bearer token, raw exception message, and stack trace.

## Conclusion

The OpenAI provider failure path now answers why a provider failed at a bounded diagnostic level without exposing credentials or expanding provider authority.
