# Real Provider Transport v1

`REAL_PROVIDER_TRANSPORT_V1` introduces a bounded real-provider transport substrate.

The first connector is deterministic local file transport only:

```text
ExecutionEnvelope
-> provider transport request
-> provider-facing task artifact
-> provider result artifact
-> normalized inbound response
-> replay-safe evidence
```

It does not call Codex APIs, Claude APIs, shell commands, network services, provider routers, retries, fallback handlers, or orchestration systems.

## Invariants

- `REAL_PROVIDER_TRANSPORT != ORCHESTRATION`
- `TRANSPORT_ARTIFACT != EXECUTION_AUTHORITY`
- `PROVIDER_RESPONSE != GOVERNANCE_DECISION`
- `CONNECTOR != PROVIDER_ROUTER`
- `NO_AUTONOMOUS_EXECUTION`
