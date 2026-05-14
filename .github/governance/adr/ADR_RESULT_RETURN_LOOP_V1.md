# ADR: Result Return Loop v1

## Context

`ACTIVE_PROVIDER_INVOCATION_V1` introduced the first active bounded provider invocation layer. The next required boundary is a deterministic return path that carries normalized invocation results back toward interpretation and interaction without turning provider output into autonomous action.

## Decision

Introduce `RESULT_RETURN_LOOP_V1` as a replay-safe result return layer.

The return loop accepts an `InvocationResult` and invocation evidence, validates lineage, binds normalized provider output to deterministic replay evidence, and produces an interpretation-ready payload.

## Consequences

Positive:

- provider results become replay-visible return artifacts
- invocation, provider, envelope, and replay identities are preserved
- interpretation-facing payloads are deterministic
- malformed or lineage-incomplete results fail closed

Tradeoffs:

- the return loop does not summarize or interpret results
- autonomous follow-up execution remains excluded
- retry and orchestration behavior remain unavailable

## Explicit Non-Goals

- autonomous interpretation
- provider invocation
- retries
- fallback logic
- provider selection
- provider switching
- scheduling
- hidden memory mutation
- background task execution
- recursive self-invocation
- autonomous next-step execution
- multi-provider coordination
- runtime authority escalation

## Invariants

- `RESULT != INTERPRETATION`
- `RETURN LOOP != ORCHESTRATION`
- `PROVIDER OUTPUT != AUTONOMOUS ACTION`
- `RESULT RETURN != EXECUTION AUTHORITY`
