# ADR: Active Provider Invocation v1

## Context

SAPIANTA / AiGOL now has provider abstraction, bounded execution envelopes, adapter runtime delivery, transport semantics, natural-language ingress, and a finalized ChatGPT ingress boundary.

The next structural step is active provider invocation: a governed layer that can activate one explicit provider through one validated envelope and record replay-safe evidence.

## Decision

Introduce `ACTIVE_PROVIDER_INVOCATION_V1` as the first active bounded provider invocation layer.

Invocation is defined as:

```text
ExecutionEnvelope
-> explicit provider invocation
-> bounded adapter runtime
-> normalized execution result
-> replay-safe invocation evidence
```

The layer uses deterministic invocation identities, a fixed lifecycle, explicit provider binding, fail-closed validation, and normalized result binding.

## Consequences

Positive:

- active provider invocation becomes explicit and replay-visible
- provider identity remains deterministic
- execution envelopes remain authoritative
- invocation evidence can be audited independently
- future result-return and governed session milestones have a bounded base

Tradeoffs:

- no provider routing
- no retries
- no fallback behavior
- no orchestration
- no autonomous provider choice

## Explicit Non-Goals

- orchestration
- retries
- fallback logic
- autonomous routing
- adaptive optimization
- hidden provider selection
- background agents
- continuous loops
- scheduling
- autonomous planning
- memory mutation
- concurrent execution
- unrestricted shell or network authority

## Invariants

- `PROVIDER != GOVERNANCE`
- `INVOCATION != ORCHESTRATION`
- `EXECUTION_ENVELOPE REMAINS AUTHORITATIVE`
- `REPLAY MUST REMAIN DETERMINISTIC`
- `ONE INVOCATION != AUTONOMOUS EXECUTION`
