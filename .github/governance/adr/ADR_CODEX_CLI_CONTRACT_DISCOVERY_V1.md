# ADR: CODEX_CLI_CONTRACT_DISCOVERY_V1

## Status

Accepted.

## Context

`LIVE_REAL_CODEX_EXECUTION_VALIDATION_V1` was honestly blocked because the installed Codex CLI rejected `codex run <prepared_task_artifact>` with exit code 2. Before changing any runtime behavior, SAPIANTA needs deterministic local discovery of the installed CLI contract.

## Decision

Add a discovery-only harness under `sapianta_bridge/provider_connectors/codex_contract_discovery/`.

The harness may run only safe introspection commands:

- `codex --help`
- `codex -h`
- `codex run --help`
- `codex run -h`
- `codex --version`

It records CLI presence, version, help availability, supported subcommands, non-interactive support, file/stdin input support if discoverable, and a safest bounded invocation candidate.

## Result

The local CLI advertises `exec` as a non-interactive subcommand. File-based input and stdin input support are not confirmed by the allowed probes. The discovery status is therefore `DISCOVERED_PARTIAL`, with candidate vector:

```json
["codex", "exec", "<bounded_prompt>"]
```

## Boundaries

This milestone does not modify runtime execution behavior, governance semantics, provider routing, retries, fallback, orchestration, or autonomous execution.
