# ADR: FIRST_REAL_PROVIDER_CONNECTOR_V1

## Status

Accepted.

## Context

`REAL_PROVIDER_TRANSPORT_V1` established deterministic outbound and inbound provider transport artifacts. The next bounded step is a connector surface that can prepare provider-facing artifacts without expanding execution authority.

## Decision

Introduce `sapianta_bridge/provider_connectors/` as the first real-provider connector substrate. The first connector target is Codex CLI, but it is implemented in `PREPARE_ONLY` mode.

The connector writes deterministic task artifacts and validates deterministic result artifacts. It does not invoke Codex CLI, execute shell commands, call network APIs, route providers, retry, fallback, or schedule work.

## Rationale

This creates the first concrete provider connector boundary while preserving governance authority. A connector artifact is a handoff contract, not execution authority. Provider output remains evidence for downstream governance interpretation and is not itself a governance decision.

## Invariants

- `CONNECTOR != ORCHESTRATION`
- `CONNECTOR != PROVIDER_ROUTER`
- `CONNECTOR_ARTIFACT != EXECUTION_AUTHORITY`
- `PROVIDER_RESPONSE != GOVERNANCE_DECISION`
- `NO_AUTONOMOUS_EXECUTION`

## Consequences

Future provider connector activation must build on this identity-preserving artifact handoff model. Any transition from `PREPARE_ONLY` to active local invocation requires a separate governance milestone with explicit shell/network authority boundaries.
