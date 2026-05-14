# Real Provider Transport v1

`REAL_PROVIDER_TRANSPORT_V1` introduces the first bounded real-provider transport connector layer for SAPIANTA / AiGOL.

The milestone supports:

```text
ExecutionEnvelope
-> provider transport request
-> provider-facing task artifact
-> provider result artifact
-> normalized inbound response
-> replay-safe evidence
```

The initial connector is deterministic local file transport only. It does not call real Codex APIs, real Claude APIs, shell commands, network services, routers, retry systems, fallback systems, or orchestration systems.

## Invariants

- `REAL_PROVIDER_TRANSPORT != ORCHESTRATION`
- `TRANSPORT_ARTIFACT != EXECUTION_AUTHORITY`
- `PROVIDER_RESPONSE != GOVERNANCE_DECISION`
- `CONNECTOR != PROVIDER_ROUTER`
- `NO_AUTONOMOUS_EXECUTION`
