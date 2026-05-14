# ADR: CODEX_EXEC_COMPLETION_STABILIZATION_V1

## Status

Accepted.

## Context

`LIVE_REAL_CODEX_EXECUTION_VALIDATION_V2` reached real `codex exec <bounded_prompt>` execution with bounded writable state but ended blocked due to timeout. The runtime needs deterministic completion classification so blocked executions can be interpreted without retries or behavior changes.

## Decision

Add completion state, classifier, and timeout telemetry modules under `sapianta_bridge/provider_connectors/`.

The classifier uses only stdout, stderr, exit code, timeout flag, and duration. It emits deterministic states such as `COMPLETED`, `TIMEOUT`, `AUTH_WAIT`, `APP_SERVER_WAIT`, and `CLI_ERROR`.

## Boundaries

This milestone is diagnostic and stabilization only. It does not introduce orchestration, retries, fallback, provider routing, adaptive selection, autonomous continuation, hidden prompt rewriting, memory mutation, scheduling, background execution, concurrent execution, unrestricted shell execution, arbitrary commands, unrestricted filesystem access, or new provider types.
