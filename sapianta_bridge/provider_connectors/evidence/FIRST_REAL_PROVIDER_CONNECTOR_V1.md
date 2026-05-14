# FIRST_REAL_PROVIDER_CONNECTOR_V1

This milestone introduces the first bounded real provider connector substrate for SAPIANTA / AiGOL.

The connector target is Codex CLI, but the connector is frozen in `PREPARE_ONLY` mode for this milestone. It prepares deterministic provider-facing task artifacts and validates deterministic provider result artifacts without invoking Codex CLI.

## Scope

The connector layer provides:

- deterministic connector identity
- bounded connector request artifacts
- bounded connector response artifacts
- replay-safe connector binding
- fail-closed connector validation
- connector evidence
- Codex CLI prepare-only artifact handoff

## Explicit Non-Goals

This milestone does not introduce:

- provider routing
- retries
- fallback logic
- orchestration
- autonomous execution
- provider auto-selection
- multi-provider coordination
- unrestricted shell execution
- unrestricted network execution
- hidden prompt rewriting
- scheduling
- memory mutation

## Connector Mode

The canonical mode for this milestone is:

```text
PREPARE_ONLY
```

In `PREPARE_ONLY` mode, the connector writes a task artifact and validates an expected result artifact. The provider-side execution remains outside this connector and is not invoked by the connector.

## Boundary Invariants

- `CONNECTOR != ORCHESTRATION`
- `CONNECTOR != PROVIDER_ROUTER`
- `CONNECTOR_ARTIFACT != EXECUTION_AUTHORITY`
- `PROVIDER_RESPONSE != GOVERNANCE_DECISION`
- `NO_AUTONOMOUS_EXECUTION`

## Replay Safety

Connector artifacts preserve provider identity, envelope identity, invocation identity, transport identity, replay identity, and artifact paths. Any missing or mismatched identity fails validation.
