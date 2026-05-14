# ADR: LIVE_REAL_CODEX_EXECUTION_VALIDATION_V1

## Status

Accepted.

## Context

The bounded Codex execution runtime exists and permits only the fixed command vector `codex run <prepared_task_artifact>` through a human-authorized execution gate. A live validation milestone is needed to test the current environment honestly without expanding authority.

## Decision

Add a validation-only live Codex harness under `sapianta_bridge/provider_connectors/live_validation/`.

The harness detects Codex CLI, builds a minimal governed validation case, prepares a bounded task artifact, activates the execution gate, invokes the existing bounded Codex runtime, captures stdout, stderr, and exit code, and emits deterministic evidence.

## Result

In this environment, Codex CLI was detected and executed, but the installed CLI rejected the fixed `codex run <prepared_task_artifact>` command vector. The validation is therefore recorded as `BLOCKED`, not `PASSED`.

## Boundaries

This milestone does not introduce orchestration, retries, fallback, provider routing, adaptive provider selection, autonomous continuation, hidden prompt rewriting, memory mutation, scheduling, background execution, concurrent execution, arbitrary commands, unrestricted shell execution, network expansion, external APIs, or new provider types.
