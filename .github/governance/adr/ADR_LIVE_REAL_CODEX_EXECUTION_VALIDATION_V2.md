# ADR: LIVE_REAL_CODEX_EXECUTION_VALIDATION_V2

## Status

Accepted.

## Context

`CODEX_CLI_CONTRACT_DISCOVERY_V1` discovered that the installed Codex CLI advertises `exec` as the non-interactive command. `LIVE_REAL_CODEX_EXECUTION_VALIDATION_V1` was blocked because `codex run <prepared_task_artifact>` was not accepted.

## Decision

Update the bounded Codex runtime contract to:

```text
codex exec <bounded_prompt>
```

The bounded prompt is generated deterministically from the prepared task artifact content. The runtime does not assume file-based artifact input.

## Result

The V2 live validation detected and invoked Codex CLI through the bounded runtime. Execution remained blocked because this environment could not initialize Codex local state/app-server components due to read-only filesystem errors. The milestone records `BLOCKED` honestly and preserves stdout, stderr, and exit-code evidence.

## Boundaries

This milestone does not introduce orchestration, retries, fallback, routing, adaptive provider selection, autonomous continuation, hidden prompt rewriting, memory mutation, scheduling, background execution, concurrent execution, unrestricted shell execution, arbitrary command execution, unrestricted filesystem access, or new provider types.
