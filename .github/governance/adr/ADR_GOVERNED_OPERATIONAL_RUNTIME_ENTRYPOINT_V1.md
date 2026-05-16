# ADR_GOVERNED_OPERATIONAL_RUNTIME_ENTRYPOINT_V1

## Decision

Introduce the first formal governed operational runtime ingress boundary.

## Rationale

Persistent channels preserve continuity; they do not define admission. This milestone separates operational enterability from session continuity by requiring deterministic boundary, contract, and admission artifacts.

## Boundary

This is not a session carrier, persistence wrapper, or autonomous activation mechanism. It does not add agents, orchestration, retries, fallback, routing, hidden execution, hidden memory, async runtime behavior, network APIs, `shell=True`, or unrestricted subprocess execution.
