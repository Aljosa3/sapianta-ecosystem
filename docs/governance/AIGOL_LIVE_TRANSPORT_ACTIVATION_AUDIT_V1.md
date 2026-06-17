# AIGOL Live Transport Activation Audit V1

Status: live transport activation audit.

Purpose: determine why live provider transport remains disabled and whether activation requires new implementation.

This artifact is audit only.

It does not invoke OpenAI.

It does not disclose credentials.

It does not modify runtime behavior.

## Context

Current upstream readiness:

```text
EXECUTION_PATH_COMPLETE
READY_FOR_FIRST_LIVE_DISPATCH
```

Remaining blocker report:

```text
LIVE_OPENAI_NETWORK_TRANSPORT_DISABLED = BLOCKER
AIGOL_OPENAI_API_KEY_NOT_PRESENT_IN_CURRENT_DISPATCH_ENVIRONMENT = BLOCKER
FIRST_REAL_LIVE_DISPATCH_REPLAY_EVIDENCE_NOT_CREATED = BLOCKER
```

This audit evaluates why the live network transport remains disabled.

## 1. Responsible Files

Primary files:

```text
aigol/runtime/live_provider_runtime_boundary.py
aigol/runtime/live_provider_http_transport.py
```

Calling path:

```text
aigol/runtime/first_live_provider_operator_entrypoint.py
aigol/runtime/first_live_provider_execution_runtime.py
```

Protective tests:

```text
tests/test_live_provider_runtime_boundary_v1.py
tests/test_live_provider_http_transport_v1.py
tests/test_first_live_provider_execution_runtime_v1.py
tests/test_first_live_provider_operator_entrypoint_v1.py
```

## 2. Runtime Conditions

### Live Provider Runtime Boundary

Condition:

```text
live_transport_enabled is True
```

File:

```text
aigol/runtime/live_provider_runtime_boundary.py
```

Effect:

```text
FailClosedRuntimeError("live provider boundary failed closed: live OpenAI transport is not implemented")
```

### Live Provider HTTP Transport Boundary

Condition:

```text
live_http_enabled is True
```

File:

```text
aigol/runtime/live_provider_http_transport.py
```

Effect:

```text
FailClosedRuntimeError("live provider HTTP transport failed closed: live HTTP dispatch is not enabled")
```

### Injected Transport Real-Call Claim

Condition:

```text
response["real_openai_called"] is True
```

Files:

```text
aigol/runtime/live_provider_runtime_boundary.py
aigol/runtime/live_provider_http_transport.py
```

Effects:

```text
FailClosedRuntimeError("live provider boundary failed closed: live OpenAI call is prohibited")
FailClosedRuntimeError("live provider HTTP transport failed closed: live OpenAI call is prohibited")
```

## 3. Fail-Closed Triggers

Current fail-closed triggers that disable live activation:

- `live_transport_enabled = true`;
- `live_http_enabled = true`;
- injected transport reports `real_openai_called = true`;
- missing injected transport;
- missing credential;
- timeout;
- rate limit;
- malformed response;
- authority-bearing output;
- replay artifact already exists.

The first three are activation blockers. The remaining triggers are expected runtime safety behavior.

## 4. Disablement Classification

Governance policy:

```text
PARTIAL
```

Reason:

Governance requires one-attempt authorization, no-secret replay, no retry, no fallback, no routing, and fail-closed behavior. Governance does not require live transport to remain permanently disabled.

Implementation gap:

```text
YES
```

Reason:

No governed external OpenAI HTTP executor is implemented behind the live transport boundary. The current boundary executes injected/mock transport only.

Configuration requirement:

```text
YES
```

Reason:

`AIGOL_OPENAI_API_KEY` must be present in the governed dispatch environment. This process currently cannot verify that the key is present.

Safety lock:

```text
YES
```

Reason:

The code intentionally fails closed when live activation flags are enabled and rejects transport outputs claiming a real OpenAI call. Tests protect this non-live behavior.

## 5. Activation Procedure

Live transport activation requires a new implementation milestone.

Required procedure:

1. Implement a governed OpenAI HTTP executor behind the existing transport boundary.
2. Keep the operator entrypoint as the only first-dispatch activation path.
3. Require fresh one-attempt dispatch authorization.
4. Require `AIGOL_OPENAI_API_KEY` in the governed dispatch environment.
5. Build the Authorization header only inside the transport boundary.
6. Never write credential value or Authorization header to replay.
7. Write request replay evidence before the external request crosses the boundary.
8. Execute exactly one HTTP request.
9. Write response replay evidence or error replay evidence.
10. Normalize successful response into canonical cognition output and `LLM_COGNITION_ARTIFACT_V1`.
11. Execute post-dispatch audit.
12. Execute post-dispatch recertification.
13. Execute rollback evidence on failure.
14. Refuse retry, fallback, routing, worker invocation, governance mutation, and replay mutation.

Required tests:

- live transport remains disabled unless the governed executor is explicitly selected;
- missing credential fails closed;
- credential value is never replayed;
- Authorization header is never replayed;
- exactly one request is attempted;
- timeout fails closed;
- rate limit fails closed;
- malformed response fails closed;
- authority-bearing output fails closed;
- response evidence is replay-visible;
- error evidence is replay-visible;
- post-dispatch audit and recertification execute;
- rollback executes on failure.

## 6. Does Activation Require New Implementation?

```text
YES
```

Reason:

Activation cannot be achieved by configuration alone. The existing live boundary explicitly rejects live enablement and rejects real-call evidence. A new governed transport executor and truthful real-call evidence model must be implemented.

## Remaining Risks

Residual risks after implementation:

- credential leaks outside AiGOL replay through external process logging;
- provider timeout;
- provider rate limit;
- malformed provider response;
- provider response shape drift;
- authority-bearing provider output;
- replay write failure after request preparation;
- accidental second attempt if operator bypasses entrypoint;
- mismatch between mock validation and live OpenAI response behavior.

Required mitigations:

- use only `AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1`;
- preserve one-attempt execution packet;
- write pre-request replay evidence;
- keep credentials out of replay;
- keep Authorization headers out of replay;
- fail closed on every transport anomaly;
- audit and recertify every attempt;
- require new authorization for any later attempt.

## Final Verdict

```text
LIVE_TRANSPORT_IMPLEMENTATION_GAP
```

## Final Recommendation

Implement:

```text
AIGOL_GOVERNED_LIVE_OPENAI_HTTP_TRANSPORT_EXECUTOR_V1
```

Minimum implementation scope:

- one OpenAI HTTP request executor;
- no retry;
- no fallback;
- no provider routing;
- no worker invocation;
- no credential replay;
- truthful real-call evidence;
- replay-visible request evidence;
- replay-visible response or error evidence;
- timeout, rate-limit, malformed-response, and authority-output fail-closed handling;
- integration only through `AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1`.
