# Active Provider Invocation v1

`ACTIVE_PROVIDER_INVOCATION_V1` introduces the first active, bounded provider invocation layer for SAPIANTA / AiGOL.

The layer performs exactly one explicit provider invocation through a validated `ExecutionEnvelope`, then records deterministic replay evidence.

## Boundary

Provider invocation is not orchestration.

The active invocation layer does not select providers, route requests, retry execution, schedule work, run concurrent execution, or adaptively optimize provider choice.

## Flow

```text
ExecutionEnvelope
-> InvocationRequest
-> InvocationValidator
-> bounded adapter runtime
-> InvocationResult
-> InvocationEvidence
```

## Invariants

- `PROVIDER != GOVERNANCE`
- `INVOCATION != ORCHESTRATION`
- `EXECUTION_ENVELOPE REMAINS AUTHORITATIVE`
- `REPLAY MUST REMAIN DETERMINISTIC`
- `ONE INVOCATION != AUTONOMOUS EXECUTION`

## Fail-Closed Behavior

Invocation is blocked if the envelope, provider identity, replay binding, runtime binding, invocation binding, or lifecycle is invalid.

Blocked invocations produce deterministic evidence and do not call provider runtime delivery.
