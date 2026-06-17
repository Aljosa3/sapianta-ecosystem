# AIGOL Live OpenAI Executor V1

Status: implemented runtime milestone.

Purpose: close the governed live OpenAI transport implementation gap while preserving existing provider governance boundaries.

This milestone implements one live HTTPS executor for `openai`.

It does not add provider routing.

It does not add retries.

It does not add fallback.

It does not expand ERR.

It does not disclose credentials.

## Context

Upstream audit:

```text
AIGOL_LIVE_TRANSPORT_ACTIVATION_AUDIT_V1
LIVE_TRANSPORT_IMPLEMENTATION_GAP
```

Required implementation:

```text
AIGOL_LIVE_OPENAI_EXECUTOR_V1
```

The executor exists only behind the already governed operator and execution path:

```text
operator entrypoint
-> first live provider execution runtime
-> live provider runtime boundary
-> governed live OpenAI executor
-> OpenAI HTTPS endpoint
```

## Runtime Implementation

Runtime file:

```text
aigol/runtime/live_openai_executor.py
```

Integration points:

```text
aigol/runtime/live_provider_runtime_boundary.py
aigol/runtime/first_live_provider_execution_runtime.py
```

Focused tests:

```text
tests/test_live_openai_executor_v1.py
tests/test_live_provider_runtime_boundary_v1.py
tests/test_first_live_provider_execution_runtime_v1.py
tests/test_first_live_provider_operator_entrypoint_v1.py
```

## Executor Responsibilities

The executor:

- consumes an approved live execution payload from the live provider runtime boundary;
- accepts credential material only in process memory through boundary metadata;
- constructs a real OpenAI HTTPS request for the Responses endpoint;
- performs exactly one request when explicitly enabled by the governed boundary;
- parses the provider response;
- returns secret-free response evidence;
- reports `real_openai_called = true`;
- reports `live_provider_call_performed = true`;
- fails closed on timeout, rate limit, transport failure, malformed request, and malformed response.

## Request Boundary

Allowed request shape:

```text
provider = openai
endpoint = https://api.openai.com/v1/responses
method = POST
stream = false
automatic_retries = false
fallback = false
```

The executor requires:

```text
metadata.provider_id = openai
metadata.credential_secret_replayed = false
metadata._credential_secret present in memory
payload.model present
payload.input present
payload.stream = false
```

The `_credential_secret` field is an internal transport handoff and is stripped before replay-visible evidence is produced.

## Replay Evidence

Replay-visible evidence remains owned by the existing runtime path:

```text
LIVE_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1
LIVE_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1
LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1
LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1
FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1
LLM_COGNITION_ARTIFACT_V1
```

Secret-free replay invariants:

```text
CREDENTIAL_SECRET_REPLAYED = false
AUTHORIZATION_HEADER_REPLAYED = false
SECRET_VALUE_OMITTED = true
```

Live execution evidence is now truthful:

```text
live_provider_call_performed = true
provider_invoked = true
deterministic_or_injected_transport_used = false
worker_invoked = false
```

## Fail-Closed Conditions

The executor fails closed when:

- provider is not `openai`;
- credential is unavailable;
- credential replay flag is not explicitly false;
- request payload is malformed;
- streaming is requested;
- timeout is invalid;
- HTTPS transport fails;
- OpenAI returns rate limit status `429`;
- response body is missing;
- response body is not JSON;
- response body does not contain extractable cognition text.

The live provider runtime boundary also fails closed if live transport is enabled without the governed executor marker:

```text
aigol_governed_live_openai_executor_v1 = true
```

## Governance Validation

Preserved invariants:

```text
ERR_PASSIVE = true
OCS_ARCHITECTURE_PRESERVED = true
PROVIDER = openai
PROVIDER_RESOURCE_TYPE = COGNITION_PROVIDER
MULTI_PROVIDER_ROUTING = false
PROVIDER_COMPARISON = false
AUTOMATIC_RETRY = false
FALLBACK = false
WORKER_INVOCATION = false
GOVERNANCE_MUTATION = false
REPLAY_MUTATION = false
SECRET_REPLAY = false
AUTHORIZATION_HEADER_REPLAY = false
```

Provider output remains:

```text
UNTRUSTED = true
NON_AUTHORITATIVE = true
HUMAN_REVIEW_REQUIRED = true
```

## Validation Results

Focused validation:

```text
python -m pytest tests/test_live_openai_executor_v1.py tests/test_live_provider_runtime_boundary_v1.py tests/test_first_live_provider_execution_runtime_v1.py tests/test_first_live_provider_operator_entrypoint_v1.py
33 passed
```

Validated behaviors:

- real OpenAI HTTPS request construction;
- Authorization header built only inside executor;
- secret-free executor result;
- governed live executor marker required;
- full operator-to-execution path can use the live executor with an injected HTTPS opener;
- request replay evidence is recorded;
- response replay evidence is recorded;
- canonical cognition artifact is produced;
- live provider invocation evidence is truthful;
- unmarked live transport fails closed;
- timeout fails closed;
- rate limit fails closed;
- malformed response fails closed;
- no worker invocation occurs;
- ERR remains passive.

## Remaining Operational Requirements

Real dispatch still requires:

- operator execution through `AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1`;
- fresh one-attempt dispatch authorization;
- `AIGOL_OPENAI_API_KEY` available in the governed process environment;
- explicit `live_transport_enabled = true`;
- post-dispatch audit and recertification review of the resulting replay evidence.

## Final Verdict

```text
AIGOL_LIVE_OPENAI_EXECUTOR_V1_IMPLEMENTED
```

## Recommendation

Treat the live OpenAI executor as the single approved transport implementation for the first governed dispatch attempt.

Do not add retries, fallback, provider routing, or additional providers until the first live dispatch replay packet has been audited and recertified.
