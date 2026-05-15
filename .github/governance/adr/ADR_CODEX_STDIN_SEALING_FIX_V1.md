# ADR: CODEX_STDIN_SEALING_FIX_V1

## Status

Accepted.

## Context

`CODEX_PROCESS_TERMINATION_STABILIZATION_V1` showed that bounded Codex execution inherited an open stdin stream and Codex CLI entered supplemental stdin read mode.

## Decision

Seal stdin in the bounded Codex runtime by passing `stdin=subprocess.DEVNULL` to the existing `subprocess.Popen` call.

The invocation contract remains `codex exec <bounded_prompt>`. The bounded prompt is still provided as an explicit argument, not through stdin.

## Consequences

The runtime removes an implicit ambient input path while preserving the existing execution gate, provider identity, bounded workspace, timeout, replay lineage, and fail-closed classifiers.

This does not introduce orchestration, retries, fallback, routing, autonomous continuation, prompt rewriting, or broader execution authority.
