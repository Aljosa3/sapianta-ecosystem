# ADR: BOUNDED_RUNTIME_WRITABLE_STATE_V1

## Status

Accepted.

## Context

`LIVE_REAL_CODEX_EXECUTION_VALIDATION_V2` reached real `codex exec <bounded_prompt>` execution but was blocked because Codex CLI attempted local state/app-server initialization in a read-only filesystem environment.

## Decision

Introduce a bounded runtime-state directory under `/tmp/sapianta_codex_runtime/<session_id>` and pass only approved state containment environment variables to Codex:

- `HOME`
- `XDG_CACHE_HOME`
- `XDG_CONFIG_HOME`
- `TMPDIR`

The state path is deterministic, provider-bound, invocation-bound, replay-bound, and validated to remain inside the approved runtime-state root.

## Boundaries

This does not grant unrestricted filesystem access, workspace escape, orchestration, retries, fallback, provider routing, autonomous execution, background execution, network expansion, arbitrary shell execution, hidden prompt rewriting, memory mutation, home directory mutation, repo-root app state, or global config mutation.

## Consequences

Live Codex validation can now be retried with local state/app-server initialization contained inside the bounded runtime-state directory.
