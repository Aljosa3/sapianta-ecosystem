# LIVE_REAL_CODEX_EXECUTION_VALIDATION_V1

This package provides a validation-only harness for the first live bounded Codex execution through the governed runtime.

The runner attempts exactly one bounded execution:

```text
codex run <prepared_task_artifact>
```

It uses the existing provider connector, execution gate, bounded Codex runtime, and execution evidence. If Codex CLI is missing or the bounded runtime cannot complete the live run, the validation reports `BLOCKED` with deterministic evidence. It does not fake success.

The harness does not introduce orchestration, retries, fallback, provider routing, adaptive provider selection, hidden prompt rewriting, memory mutation, scheduling, background execution, concurrent execution, arbitrary commands, or unrestricted shell execution.
