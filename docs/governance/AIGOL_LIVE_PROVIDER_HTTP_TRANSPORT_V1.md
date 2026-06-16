# AIGOL Live Provider HTTP Transport V1

Status: implemented governed HTTP transport boundary.

Purpose: implement the minimal HTTP transport evidence layer needed for first OpenAI invocation readiness while keeping live provider dispatch disabled by default.

This milestone implements request, response, error, and audit artifact generation.

It does not perform a real OpenAI request by default.

It does not store or replay secrets.

It does not broaden ERR or OCS.

## Context

Inputs:

```text
HIRR certification
ERR_ROLE = UNIVERSAL_RESOURCE_REGISTRY
AIGOL_CANONICAL_PROVIDER_CONTRACT_V1
AIGOL_CANONICAL_PROVIDER_CONTRACT_ADAPTERS_V1
AIGOL_LIVE_PROVIDER_INVOCATION_GOVERNANCE_V1
AIGOL_LIVE_PROVIDER_CREDENTIAL_BOUNDARY_V1
AIGOL_LIVE_PROVIDER_TRANSPORT_BOUNDARY_V1
AIGOL_LIVE_PROVIDER_RUNTIME_BOUNDARY_V1
AIGOL_FIRST_LIVE_PROVIDER_INVOCATION_FINAL_READINESS_AUDIT_V1
```

Audit verdict entering this milestone:

```text
ONLY_OPERATIONAL_IMPLEMENTATION_REMAINS = YES
```

## Architecture Summary

Implemented transport path:

```text
live approval artifact
-> credential policy artifact
-> ERR openai metadata selection
-> canonical provider contract view
-> replay-safe HTTP request artifact
-> injected/mock HTTP transport
-> replay-safe HTTP response artifact
   or replay-safe HTTP error artifact
-> HTTP transport audit artifact
-> replay reconstruction
```

The transport boundary supports injected/mock transport for validation.

The transport boundary refuses live HTTP enablement in this milestone.

## Runtime Changes

Added:

- `aigol/runtime/live_provider_http_transport.py`

The runtime provides:

- `run_live_provider_http_transport`;
- `create_live_http_request_artifact`;
- `create_failed_live_http_request_artifact`;
- `create_live_http_response_artifact`;
- `create_live_http_error_artifact`;
- `create_live_http_transport_audit`;
- `reconstruct_live_provider_http_transport_replay`.

## Replay Evidence Model

Successful injected transport validation writes:

```text
000_live_provider_http_request.json
001_live_provider_http_response.json
002_live_provider_http_transport_audit.json
```

Fail-closed validation writes:

```text
000_live_provider_http_request.json
001_live_provider_http_error.json
002_live_provider_http_transport_audit.json
```

Nested ERR selection evidence remains in:

```text
err_openai_selection/
```

Replay reconstruction verifies:

- wrapper ordering;
- wrapper hashes;
- artifact hashes;
- request-to-response or request-to-error references;
- audit references;
- final status;
- no live HTTP dispatch;
- no provider invocation flag;
- no worker invocation;
- no governance mutation;
- no replay mutation;
- no credential secret replay.

## Transport Artifacts

Implemented artifact types:

| Artifact | Purpose |
| --- | --- |
| `LIVE_PROVIDER_HTTP_REQUEST_ARTIFACT_V1` | Records a redacted HTTP request envelope for OpenAI Responses API readiness. |
| `LIVE_PROVIDER_HTTP_RESPONSE_ARTIFACT_V1` | Records injected/mock HTTP response evidence as untrusted, non-authoritative output. |
| `LIVE_PROVIDER_HTTP_ERROR_ARTIFACT_V1` | Records timeout, rate-limit, malformed-response, authority-boundary, credential, and transport failures. |
| `LIVE_PROVIDER_HTTP_TRANSPORT_AUDIT_ARTIFACT_V1` | Records transport audit status and governance preservation flags. |

## Credential Boundary

The HTTP request artifact records:

- authorization header redacted;
- credential secret not replayed;
- credential reference not replayed;
- credential policy artifact hash;
- no live HTTP dispatch.

No secret material is persisted in replay.

## Fail-Closed Handling

Implemented fail-closed conditions:

1. missing approval;
2. malformed approval;
3. unapproved approval;
4. unauthorized provider;
5. missing credential policy;
6. unsupported credential policy;
7. ERR selection does not select `openai`;
8. live HTTP enablement is attempted;
9. injected transport is missing;
10. injected transport raises timeout;
11. injected transport raises rate-limit;
12. injected transport returns HTTP 429;
13. malformed response;
14. authority-bearing response;
15. injected transport claims a real OpenAI call occurred;
16. replay collision;
17. replay tampering.

Implemented error classifications:

- `AUTHENTICATION_UNAVAILABLE`;
- `CREDENTIAL_POLICY_INVALID`;
- `MALFORMED_RESPONSE`;
- `RATE_LIMIT`;
- `TIMEOUT`;
- `TRANSPORT_UNAVAILABLE`;
- `AUTHORITY_BOUNDARY_VIOLATION`.

## Governance Boundary Preservation

Preserved:

- ERR remains passive;
- OCS architecture is not modified;
- canonical provider contract is preserved;
- adapter strategy is preserved through canonical contract conversion;
- replay evidence is append-only;
- live OpenAI request is not executed by default;
- credentials are not replayed;
- workers are not invoked;
- provider output is non-authoritative;
- governance is not modified;
- replay is not mutated.

Runtime invariant:

```text
live_http_dispatch_performed = false
provider_invoked = false
worker_invoked = false
credential_secret_replayed = false
authorization_header_replayed = false
governance_modified = false
replay_modified = false
```

## Tests Added

Added:

- `tests/test_live_provider_http_transport_v1.py`

Coverage:

- injected HTTP transport success without live OpenAI call;
- ordered replay evidence;
- no secret material in replay;
- missing injected transport fail-closed;
- live HTTP enablement refusal;
- missing approval fail-closed;
- missing credential policy fail-closed;
- non-OpenAI ERR selection fail-closed;
- timeout classification;
- rate-limit exception classification;
- HTTP 429 classification;
- malformed-response classification;
- authority-bearing response classification;
- transport claiming real OpenAI call fail-closed;
- replay tampering detection;
- static check that the module has no default network client.

## Validation Results

Focused validation:

```text
python -m pytest tests/test_live_provider_http_transport_v1.py
16 passed
```

Broader live-provider regression validation:

```text
python -m pytest tests/test_live_provider_http_transport_v1.py tests/test_live_provider_runtime_boundary_v1.py tests/test_live_provider_invocation_prerequisites_v1.py tests/test_first_real_provider_runtime_v1.py tests/test_real_provider_registration_v1.py tests/test_external_resource_registry_runtime_v0.py tests/test_llm_cognition_provider_runtime_v1.py tests/test_cognition_artifact_runtime_v1.py
85 passed
```

## Remaining Gaps

Remaining operational gaps after this milestone:

- real OpenAI dispatch remains disabled by default;
- live authentication header construction with real secret material is not replayed or activated;
- live response normalization into final production cognition artifacts remains governed by future live-call approval;
- provider invocation approval instance must still be supplied for any future live call.

## Recommendation

`AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1` should be treated as the governed HTTP evidence layer, not as live dispatch authorization.

The milestone removes the HTTP artifact and failure-classification blocker, while preserving the requirement that first live OpenAI invocation still needs explicit operational approval and a separately governed live-dispatch activation.
