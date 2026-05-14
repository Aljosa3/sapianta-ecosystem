# Provider Connectors

`FIRST_REAL_PROVIDER_CONNECTOR_V1` defines the first bounded connector layer between real-provider transport artifacts and a provider-facing interface.

The Codex connector is intentionally `PREPARE_ONLY`. It writes a deterministic Codex-facing task artifact and validates a deterministic provider result artifact. It does not invoke Codex CLI, call provider APIs, execute shell commands, route providers, retry, fallback, or schedule work.

## Boundary

Provider connectors are artifact handoff contracts. They are not governance authorities and do not grant execution authority.

Permanent invariants:

- `CONNECTOR != ORCHESTRATION`
- `CONNECTOR != PROVIDER_ROUTER`
- `CONNECTOR_ARTIFACT != EXECUTION_AUTHORITY`
- `PROVIDER_RESPONSE != GOVERNANCE_DECISION`
- `NO_AUTONOMOUS_EXECUTION`

## Connector Mode

The first connector mode is:

```text
PREPARE_ONLY
```

This mode prepares a bounded task artifact and expects a bounded result artifact to be supplied by the explicit provider-side process. The connector validates identity continuity across provider ID, envelope ID, invocation ID, transport ID, and replay identity.

## Replay Safety

Connector artifacts preserve:

- provider identity
- envelope identity
- invocation identity
- transport identity
- replay identity
- bounded task artifact path
- expected result artifact path

Malformed, identity-mismatched, or authority-expanding connector artifacts fail closed.
