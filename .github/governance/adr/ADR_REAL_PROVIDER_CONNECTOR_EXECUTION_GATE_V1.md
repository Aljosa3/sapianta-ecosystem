# ADR: REAL_PROVIDER_CONNECTOR_EXECUTION_GATE_V1

## Status

Accepted.

## Context

`FIRST_REAL_PROVIDER_CONNECTOR_V1` established deterministic provider-facing task artifacts in `PREPARE_ONLY` mode. A prepared artifact must not become execution authority by implication. A separate, explicit gate is required before any bounded local execution activation.

## Decision

Introduce `REAL_PROVIDER_CONNECTOR_EXECUTION_GATE_V1` under `sapianta_bridge/provider_connectors/`.

The gate requires explicit human authorization, provider identity continuity, workspace boundary validation, bounded timeout validation, and replay-safe lineage before the single supported bounded operation may run.

The first operation is `CAPTURE_CONNECTOR_TASK`. It reads the prepared connector task artifact inside an authorized workspace and returns deterministic stdout, stderr, exit code, timestamps, and metadata. It does not invoke a shell, run arbitrary commands, call networks, route providers, retry, fallback, or schedule work.

## Rationale

Execution activation must be separate from provider preparation. This preserves the invariant that prepared provider artifacts are not execution authority and gives future local connector activation a replay-safe authorization boundary.

## Invariants

- `PREPARED PROVIDER ARTIFACT != EXECUTION AUTHORITY`
- `EXECUTION_GATE != ORCHESTRATION`
- `EXECUTION_GATE != PROVIDER_ROUTER`
- `EXECUTION_GATE != SHELL FREEDOM`
- `NO_AUTONOMOUS_EXECUTION`

## Consequences

Any future expansion from artifact capture to actual provider CLI invocation must pass through this gate and define explicit command, workspace, timeout, and authority constraints in a separate governance milestone.
