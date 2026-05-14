# Result Return Loop v1

`RESULT_RETURN_LOOP_V1` establishes the deterministic result return flow from bounded provider invocation back toward interpretation and interaction.

The return loop preserves:

- invocation identity
- provider identity
- envelope identity
- replay identity
- normalized provider result
- invocation evidence references
- deterministic result binding

The return loop does not interpret results, invoke providers, route providers, retry execution, orchestrate follow-up work, generate hidden instructions, or grant execution authority.

## Canonical Flow

```text
InvocationResult
-> validated ResultPayload
-> replay-safe return artifact
-> interpretation-ready payload
```

## Invariants

- `RESULT != INTERPRETATION`
- `RETURN LOOP != ORCHESTRATION`
- `PROVIDER OUTPUT != AUTONOMOUS ACTION`
- `RESULT RETURN != EXECUTION AUTHORITY`
