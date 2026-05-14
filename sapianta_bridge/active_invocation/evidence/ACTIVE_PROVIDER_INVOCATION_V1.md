# Active Provider Invocation v1

`ACTIVE_PROVIDER_INVOCATION_V1` establishes the first active bounded provider invocation layer for SAPIANTA / AiGOL.

The milestone supports:

- explicit provider invocation
- deterministic invocation identity
- bounded adapter runtime delivery
- normalized execution result binding
- replay-safe invocation evidence
- fail-closed validation

It does not introduce orchestration, retries, fallback logic, autonomous routing, adaptive provider choice, scheduling, background workers, concurrent execution, unrestricted shell execution, or unrestricted network execution.

## Canonical Flow

```text
ExecutionEnvelope
-> explicit InvocationRequest
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
