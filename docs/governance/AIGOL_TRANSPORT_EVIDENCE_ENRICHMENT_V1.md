# AIGOL_TRANSPORT_EVIDENCE_ENRICHMENT_V1

Status: evidence enrichment definition.

Purpose: preserve replay-safe transport diagnostics while retaining fail-closed provider execution behavior.

This artifact defines evidence, runtime, replay, and certification requirements. It does not implement runtime changes, invoke providers, retrieve credentials, change ERR, authorize retry, authorize fallback, or alter provider governance.

## 1. Governing Inputs

This enrichment is governed by:

- `CERT-000006`
- `AIGOL_OPENAI_TRANSPORT_ROOT_CAUSE_ANALYSIS_V1`
- `AIGOL_DEPENDENCY_FAILURE_RUNTIME_V1`
- `aigol/runtime/live_provider_runtime_boundary.py`
- `aigol/runtime/live_openai_executor.py`

CERT-000006 established:

```text
provider_invoked = true
provider_response_received = false
failure_reason = live provider boundary failed closed: transport unavailable
error_classification = TRANSPORT_UNAVAILABLE
```

The root-cause analysis determined:

```text
original low-level exception type = NOT_RECORDED
original low-level exception message = NOT_RECORDED
exact DNS/TLS/proxy/firewall/authentication subcause = NOT_YET_DETERMINABLE
```

This enrichment closes that evidence gap without weakening fail-closed behavior.

## 2. Objective

When a governed live provider transport fails, AiGOL must preserve enough diagnostic metadata to distinguish failure classes while never replaying secrets or sensitive request contents.

Required diagnostic questions:

1. What exception type occurred?
2. What exception category occurred?
3. At which transport stage did failure occur?
4. Which endpoint host was targeted?
5. Was DNS resolution attempted?
6. Was TLS handshake attempted?
7. Was HTTP request attempted?
8. Was a response received?

The enriched evidence must remain:

- secret-free;
- replay-safe;
- fail-closed;
- deterministic enough for certification;
- compatible with dependency failure classification;
- non-authoritative for retry or fallback.

## 3. Non-Goals

This enrichment does not:

- store API keys;
- store authorization headers;
- store request payload contents;
- store response body contents in error evidence;
- store secret values;
- hash secret values;
- retry automatically;
- fall back automatically;
- invoke another provider;
- invoke a worker;
- change ERR selection;
- change human approval requirements;
- convert diagnostics into execution authority.

## 4. Evidence Schema

New artifact type:

```text
LIVE_PROVIDER_TRANSPORT_DIAGNOSTIC_ENVELOPE_ARTIFACT_V1
```

Recommended placement:

```text
execution/live_provider_boundary/<index>_live_provider_transport_diagnostic_envelope.json
```

Required fields:

| Field | Type | Required | Secret-safe rule |
| --- | --- | --- | --- |
| `artifact_type` | string | yes | Constant value only |
| `runtime_version` | string | yes | Runtime milestone id |
| `invocation_id` | string | yes | Existing invocation id |
| `provider_id` | string | yes | Provider id only |
| `endpoint_host` | string | yes | Host only, no path query or payload |
| `exception_type` | string | yes | Class name only, no traceback |
| `exception_category` | string | yes | Bounded category |
| `transport_stage` | string | yes | Bounded stage |
| `dns_resolution_attempted` | boolean | yes | Attempt flag only |
| `tls_handshake_attempted` | boolean | yes | Attempt flag only |
| `http_request_attempted` | boolean | yes | Attempt flag only |
| `response_received` | boolean | yes | Response presence only |
| `http_status_code` | integer or null | optional | Status only, no body |
| `timeout_seconds` | integer | yes | Existing timeout value |
| `failure_reason` | string | yes | Existing redacted fail-closed reason |
| `dependency_failure_classification` | string | yes | Dependency Failure Runtime class |
| `credential_secret_replayed` | boolean | yes | Must be false |
| `authorization_header_replayed` | boolean | yes | Must be false |
| `request_payload_replayed` | boolean | yes | Must be false |
| `secret_value_replayed` | boolean | yes | Must be false |
| `retry_attempted` | boolean | yes | Must be false |
| `fallback_attempted` | boolean | yes | Must be false |
| `provider_invoked` | boolean | yes | Mirrors attempted live transport |
| `worker_invoked` | boolean | yes | Must be false |
| `governance_modified` | boolean | yes | Must be false |
| `replay_modified` | boolean | yes | Must be false |
| `replay_visible` | boolean | yes | Must be true |
| `created_at` | string | yes | Timestamp |
| `artifact_hash` | string | yes | Hash of secret-free artifact |

Optional field:

| Field | Type | Rule |
| --- | --- | --- |
| `exception_message_sanitized` | string | May be included only after removing credentials, authorization headers, request bodies, URLs with query strings, local secret paths, and any provider-returned body text |

Default rule:

```text
exception_message_sanitized SHOULD be omitted unless a strict sanitizer is certified.
```

## 5. Bounded Classifications

`exception_category` values:

- `DNS_FAILURE`
- `TLS_FAILURE`
- `PROXY_FAILURE`
- `FIREWALL_OR_NETWORK_FAILURE`
- `TIMEOUT`
- `RATE_LIMIT`
- `HTTP_STATUS_ERROR`
- `AUTHENTICATION_OR_AUTHORIZATION_FAILURE`
- `MALFORMED_RESPONSE`
- `SDK_CONFIGURATION_FAILURE`
- `TRANSPORT_UNAVAILABLE`
- `UNKNOWN_TRANSPORT_FAILURE`

For the current `urllib.request` implementation, `SDK_CONFIGURATION_FAILURE` is normally `NOT_APPLICABLE`, but the category remains reserved for future SDK-backed transports.

`transport_stage` values:

- `REQUEST_PREPARATION`
- `DNS_RESOLUTION`
- `TLS_HANDSHAKE`
- `HTTP_REQUEST`
- `HTTP_RESPONSE_STATUS`
- `HTTP_RESPONSE_READ`
- `RESPONSE_VALIDATION`
- `BOUNDARY_NORMALIZATION`
- `UNKNOWN`

## 6. Stage Flag Semantics

Stage flags must be conservative:

| Field | Meaning |
| --- | --- |
| `dns_resolution_attempted` | Runtime attempted hostname resolution directly or entered a transport path that necessarily performs it |
| `tls_handshake_attempted` | Runtime attempted TLS socket establishment or entered HTTPS transport after DNS |
| `http_request_attempted` | Runtime attempted to send the HTTPS request |
| `response_received` | Runtime received an HTTP response object or status |

If the runtime cannot distinguish DNS, TLS, or socket stages, it must set:

```text
transport_stage = UNKNOWN
exception_category = TRANSPORT_UNAVAILABLE
dns_resolution_attempted = false
tls_handshake_attempted = false
http_request_attempted = true
response_received = false
```

The evidence must not overclaim precision.

## 7. Runtime Modifications

### 7.1 OpenAI Executor

`aigol/runtime/live_openai_executor.py` should preserve sanitized exception metadata before normalizing to `FailClosedRuntimeError`.

Required behavior:

1. Continue using one governed request only.
2. Continue disabling automatic retry and fallback.
3. Continue preventing credential replay.
4. Capture exception class name before raising fail-closed.
5. Capture HTTP status for `HTTPError` without response body.
6. Classify `URLError.reason` into bounded categories when possible.
7. Return or raise a typed secret-free diagnostic object to the live provider boundary.

Forbidden behavior:

- include `Authorization` header;
- include API key;
- include request payload contents;
- include response body in diagnostic error evidence;
- include traceback with local secret-bearing values;
- include raw exception text unless sanitizer is certified.

### 7.2 Live Provider Runtime Boundary

`aigol/runtime/live_provider_runtime_boundary.py` should create a transport diagnostic envelope when `_invoke_governed_live_transport` fails.

Required behavior:

1. Preserve existing `LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1`.
2. Add diagnostic envelope before or alongside the error envelope.
3. Link diagnostic envelope hash from the error envelope or boundary audit.
4. Preserve existing fail-closed final status.
5. Preserve `provider_invoked = true` when live transport was attempted.
6. Preserve `response_envelope_artifact_hash = null` when no response was received.
7. Preserve no retry, no fallback, no worker invocation.

Minimal linkage:

```text
LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1.transport_diagnostic_artifact_hash
LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1.transport_diagnostic_artifact_hash
```

### 7.3 Dependency Failure Runtime

Transport diagnostic evidence should map to dependency failure classifications:

| Transport category | Dependency failure classification |
| --- | --- |
| `DNS_FAILURE` | `UNREACHABLE_SERVICE` |
| `TLS_FAILURE` | `UNREACHABLE_SERVICE` |
| `PROXY_FAILURE` | `UNREACHABLE_SERVICE` |
| `FIREWALL_OR_NETWORK_FAILURE` | `UNREACHABLE_SERVICE` |
| `TIMEOUT` | `UNREACHABLE_SERVICE` |
| `RATE_LIMIT` | `UNREACHABLE_SERVICE` |
| `HTTP_STATUS_ERROR` | `UNREACHABLE_SERVICE` |
| `AUTHENTICATION_OR_AUTHORIZATION_FAILURE` | `AUTHORIZATION_FAILURE` |
| `MALFORMED_RESPONSE` | `DEPENDENCY_UNAVAILABLE` |
| `SDK_CONFIGURATION_FAILURE` | `MISSING_CONFIGURATION` |
| `TRANSPORT_UNAVAILABLE` | `UNREACHABLE_SERVICE` |
| `UNKNOWN_TRANSPORT_FAILURE` | `UNKNOWN_DEPENDENCY_FAILURE` |

Dependency failure runtime must use the diagnostic envelope to explain:

- what dependency failed;
- what capability was stopped;
- why execution was stopped;
- whether the operator should check DNS, TLS, proxy, firewall, credential authorization, or service availability;
- how to retry after remediation through a governed entrypoint.

It must not authorize retry automatically.

## 8. Replay Modifications

Existing error replay sequence:

```text
live_provider_credential_retrieval_attempt
live_provider_request_envelope
live_provider_error_envelope
live_provider_runtime_boundary_audit
```

Enriched error replay sequence:

```text
live_provider_credential_retrieval_attempt
live_provider_request_envelope
live_provider_transport_diagnostic_envelope
live_provider_error_envelope
live_provider_runtime_boundary_audit
```

Replay reconstruction must verify:

- diagnostic envelope ordering;
- diagnostic envelope hash;
- request envelope reference;
- error envelope diagnostic reference;
- no secret replay flags;
- no authorization header replay;
- no request payload contents in diagnostic envelope;
- no worker invocation;
- no retry;
- no fallback;
- final status remains `FAILED_CLOSED`.

The request envelope may continue to contain the existing replay-safe request payload according to the current provider boundary. The diagnostic envelope itself must not duplicate request payload contents.

## 9. Example Diagnostic Envelope

```json
{
  "artifact_type": "LIVE_PROVIDER_TRANSPORT_DIAGNOSTIC_ENVELOPE_ARTIFACT_V1",
  "runtime_version": "AIGOL_LIVE_PROVIDER_RUNTIME_BOUNDARY_V1",
  "invocation_id": "FIRST-LIVE-COGNITION-PROVIDER-OPERATOR-DISPATCH-000006:EXECUTION:OPENAI_DISPATCH_ATTEMPT_1",
  "provider_id": "openai",
  "endpoint_host": "api.openai.com",
  "exception_type": "URLError",
  "exception_category": "DNS_FAILURE",
  "transport_stage": "DNS_RESOLUTION",
  "dns_resolution_attempted": true,
  "tls_handshake_attempted": false,
  "http_request_attempted": false,
  "response_received": false,
  "http_status_code": null,
  "timeout_seconds": 20,
  "failure_reason": "live provider boundary failed closed: transport unavailable",
  "dependency_failure_classification": "UNREACHABLE_SERVICE",
  "credential_secret_replayed": false,
  "authorization_header_replayed": false,
  "request_payload_replayed": false,
  "secret_value_replayed": false,
  "retry_attempted": false,
  "fallback_attempted": false,
  "provider_invoked": true,
  "worker_invoked": false,
  "governance_modified": false,
  "replay_modified": false,
  "replay_visible": true,
  "created_at": "2026-06-17T00:00:00+00:00"
}
```

This example is illustrative only. CERT-000006 did not record the low-level exception type, so this artifact must not be backfilled into CERT-000006 as historical fact.

## 10. Certification Plan

Certification suite:

```text
AIGOL_TRANSPORT_EVIDENCE_ENRICHMENT_CERTIFICATION_V1
```

Required tests:

1. `URLError` with DNS-like reason produces `exception_type = URLError`, `exception_category = DNS_FAILURE`, and `transport_stage = DNS_RESOLUTION`.
2. TLS certificate failure produces `TLS_FAILURE` and `transport_stage = TLS_HANDSHAKE`.
3. Proxy failure produces `PROXY_FAILURE`.
4. Socket timeout produces `TIMEOUT`.
5. HTTP 429 produces `RATE_LIMIT` and records `http_status_code = 429`.
6. HTTP 401 or 403 produces `AUTHENTICATION_OR_AUTHORIZATION_FAILURE` and maps to `AUTHORIZATION_FAILURE`.
7. Generic `OSError` produces `FIREWALL_OR_NETWORK_FAILURE` or `TRANSPORT_UNAVAILABLE` without overclaiming.
8. Unknown exception produces `UNKNOWN_TRANSPORT_FAILURE`.
9. Malformed provider response still produces `MALFORMED_RESPONSE`.
10. Diagnostic envelope contains no API key.
11. Diagnostic envelope contains no authorization header.
12. Diagnostic envelope contains no request payload contents.
13. Diagnostic envelope contains no response body text.
14. Error envelope links to diagnostic envelope hash.
15. Boundary audit links to diagnostic envelope hash.
16. Replay reconstruction validates enriched error sequence.
17. Existing fail-closed final status is preserved.
18. No automatic retry is performed.
19. No fallback is performed.
20. No worker is invoked.
21. Dependency Failure Runtime receives `UNREACHABLE_SERVICE` for transport failures.
22. Dependency Failure Runtime receives `AUTHORIZATION_FAILURE` for HTTP 401/403.
23. Existing CERT-000006 interpretation remains unchanged and is not retroactively altered.

Pass criteria:

```text
LOW_LEVEL_EXCEPTION_METADATA_REPLAY_SAFE = TRUE
NO_SECRET_REPLAY = TRUE
NO_AUTHORIZATION_HEADER_REPLAY = TRUE
NO_REQUEST_PAYLOAD_DUPLICATION_IN_DIAGNOSTIC = TRUE
FAIL_CLOSED_PRESERVED = TRUE
DEPENDENCY_FAILURE_INTEGRATION_DEFINED = TRUE
REPLAY_RECONSTRUCTION_PASSES = TRUE
```

Failure criteria:

- any API key is recorded;
- any authorization header is recorded;
- any request payload contents are duplicated into diagnostic evidence;
- any response body text is recorded in diagnostic error evidence;
- transport diagnostics trigger retry or fallback;
- diagnostics invoke another provider;
- diagnostics invoke a worker;
- diagnostics mutate ERR;
- diagnostics overclaim DNS/TLS/proxy stage without evidence;
- replay reconstruction cannot validate the diagnostic envelope.

## 11. Smallest Implementation Scope

Smallest conformant implementation:

1. Add a secret-free transport diagnostic dataclass or dictionary helper.
2. Add exception-to-category mapping in `live_openai_executor.py`.
3. Pass sanitized diagnostic metadata through the fail-closed exception path.
4. Extend `create_live_error_envelope` or adjacent boundary logic to persist `LIVE_PROVIDER_TRANSPORT_DIAGNOSTIC_ENVELOPE_ARTIFACT_V1`.
5. Link diagnostic artifact hash from error envelope and boundary audit.
6. Extend replay reconstruction to accept and verify the enriched error sequence.
7. Add focused unit tests with injected fake transports and fake exceptions only.

Out of scope:

- live OpenAI request execution;
- provider registry changes;
- credential registry changes;
- multi-provider transport;
- automatic retry;
- fallback;
- worker execution.

## 12. Final Verdict

`TRANSPORT_EVIDENCE_ENRICHMENT_DEFINED`

The enrichment can be implemented as a replay-safe diagnostic envelope that records bounded low-level transport metadata, integrates with Dependency Failure Runtime, preserves fail-closed behavior, and maintains no-secret replay invariants.
