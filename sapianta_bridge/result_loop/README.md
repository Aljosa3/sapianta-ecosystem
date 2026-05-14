# Result Return Loop v1

`RESULT_RETURN_LOOP_V1` returns bounded provider invocation results toward the interpretation and interaction layers.

The return loop is deterministic, replay-safe, provider-independent, and fail-closed. It does not interpret results, invoke providers, retry execution, route providers, or create autonomous follow-up work.

## Flow

```text
InvocationResult
-> ResultPayload
-> ResultValidation
-> ResultEvidence
-> interpretation-ready payload
```

## Invariants

- `RESULT != INTERPRETATION`
- `RETURN LOOP != ORCHESTRATION`
- `PROVIDER OUTPUT != AUTONOMOUS ACTION`
- `RESULT RETURN != EXECUTION AUTHORITY`

## Fail-Closed Behavior

Malformed invocation results, missing lineage, provider mismatches, invalid replay bindings, missing evidence, and invalid lifecycle references are blocked before a return payload is accepted.
