# CODEX_PROCESS_TERMINATION_STABILIZATION_V1

This milestone stabilizes bounded Codex process termination diagnostics for `codex exec <bounded_prompt>`.

It determines whether bounded Codex output contains an explicit completion marker before the process terminates. If bounded output is complete but the process remains running, the runtime may capture the bounded result and terminate that single process safely.

## Boundary

- This is diagnostic and stabilization only.
- It does not introduce orchestration.
- It does not introduce retries.
- It does not introduce fallback.
- It does not introduce provider routing.
- It does not introduce autonomous continuation.
- It does not introduce arbitrary shell execution.

## Completion Marker

The bounded prompt requests the deterministic marker:

```text
AIGOL_TASK_COMPLETE
```

Result availability is not inferred from arbitrary text. A bounded result requires a deterministic marker or structured marker evidence.

## Process States

The process state model distinguishes normal termination, CLI errors, completed output with a still-running process, active output, quiescent output, waits, hanging processes, and timeout without completion.

`UNKNOWN` and `TIMEOUT_NO_COMPLETION` fail closed.

## Stabilization Rule

If the process times out after producing the bounded completion marker and output is quiescent, the bounded result may be captured and the single running process is terminated safely. Evidence records the termination attempt and outcome.
