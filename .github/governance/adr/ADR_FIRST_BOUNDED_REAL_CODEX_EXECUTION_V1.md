# ADR: FIRST_BOUNDED_REAL_CODEX_EXECUTION_V1

## Status

Accepted.

## Context

The provider connector substrate can prepare Codex-facing artifacts, and the execution gate can authorize bounded local activation. The next step is a real local Codex runtime path that remains explicit and governance-controlled.

## Decision

Introduce `FIRST_BOUNDED_REAL_CODEX_EXECUTION_V1` under `sapianta_bridge/provider_connectors/`.

The runtime may execute only the fixed command vector:

```text
codex run <prepared_task_artifact>
```

Execution requires a valid execution gate request, `execution_authorized=true`, `approved_by=human`, provider identity `codex_cli`, operation `CODEX_CLI_RUN`, a bounded workspace, and a bounded timeout.

## Rationale

Real local execution must not imply autonomous execution. A single whitelisted Codex command vector preserves provider specificity while avoiding shell freedom, arbitrary command execution, routing, retries, fallback, and orchestration.

## Invariants

- `REAL_EXECUTION != AUTONOMOUS_EXECUTION`
- `CODEX_OUTPUT != GOVERNANCE_DECISION`
- `BOUNDED_EXECUTION != ORCHESTRATION`
- `BOUNDED_EXECUTION != ROUTING`
- `NO_UNRESTRICTED_RUNTIME_AUTHORITY`

## Consequences

Future execution expansion must remain behind explicit gate validation and separate governance milestones. Codex output remains captured result evidence and must flow through governed result return paths before interpretation.
