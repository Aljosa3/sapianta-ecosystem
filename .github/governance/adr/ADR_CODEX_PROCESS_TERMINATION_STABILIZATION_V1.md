# ADR: CODEX_PROCESS_TERMINATION_STABILIZATION_V1

## Status

Accepted.

## Context

Bounded live Codex execution reached `codex exec <bounded_prompt>` but timed out after producing process output. The governance question is whether the bounded task result was completed before the process failed to terminate, or whether the task itself did not complete before timeout.

## Decision

Introduce deterministic process termination classification for bounded Codex execution.

The bounded prompt includes an explicit `AIGOL_TASK_COMPLETE` marker. The runtime classifies stdout, stderr, exit code, timeout state, process termination state, and output quiescence. If a timeout occurs after a deterministic completion marker and quiescent output, the bounded result may be captured and the single process is terminated safely.

## Boundaries

- No orchestration is introduced.
- No retries are introduced.
- No fallback is introduced.
- No provider routing is introduced.
- No autonomous continuation is introduced.
- No arbitrary command execution is introduced.
- No unrestricted filesystem or shell authority is introduced.

## Consequences

The runtime can distinguish `TIMEOUT_NO_COMPLETION` from `OUTPUT_COMPLETED_PROCESS_RUNNING`. This preserves fail-closed behavior while allowing replay-safe evidence when bounded output completed but Codex did not terminate cleanly.
