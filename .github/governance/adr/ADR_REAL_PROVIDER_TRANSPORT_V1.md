# ADR: Real Provider Transport v1

## Context

SAPIANTA / AiGOL now has deterministic no-copy/paste continuity across ingress, governed sessions, active invocation, and result return. The next step toward reducing manual ChatGPT to Codex to ChatGPT transfer is a bounded provider transport substrate.

## Decision

Introduce `REAL_PROVIDER_TRANSPORT_V1` as an explicit provider transport request/response artifact layer with a deterministic local file connector.

The connector writes a provider-facing task artifact, reads a provider result artifact, validates identity continuity, normalizes the inbound response, and emits replay-safe evidence.

## Consequences

Positive:

- governed execution requests can be serialized into provider-facing artifacts
- provider result artifacts can be read back through deterministic validation
- replay identity, provider identity, and envelope identity remain visible
- no-copy/paste continuity can move toward real provider interfaces without adding orchestration

Tradeoffs:

- no real Codex API calls
- no real Claude API calls
- no shell or network execution
- no routing, retries, or fallback behavior

## Invariants

- `REAL_PROVIDER_TRANSPORT != ORCHESTRATION`
- `TRANSPORT_ARTIFACT != EXECUTION_AUTHORITY`
- `PROVIDER_RESPONSE != GOVERNANCE_DECISION`
- `CONNECTOR != PROVIDER_ROUTER`
- `NO_AUTONOMOUS_EXECUTION`
