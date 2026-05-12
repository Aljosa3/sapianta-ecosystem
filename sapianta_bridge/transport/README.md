# CODEX BRIDGE TRANSPORT MVP v1

This package introduces the first bounded execution transport layer for governed Codex execution.

The transport lifecycle is:

```text
task.json
-> protocol enforcement gate
-> atomic processing lock
-> processing/
-> bounded Codex subprocess execution
-> result.json generation
-> result validation
-> completed/ or failed/
-> append replay log
```

## Bounded Execution Model

The listener processes at most one task per invocation. Codex execution uses `subprocess.run` with `shell=False`, a configured workspace, captured stdout/stderr, and an enforced timeout.

Codex remains non-authoritative. It receives a validated task and returns process output. Protocol validation, lifecycle enforcement, result validation, replay logging, and quarantine remain the governing authority.

## Fail-Closed Behavior

The transport fails closed when a task is invalid, lifecycle validation fails, lock state is uncertain, target paths escape the workspace, Codex times out, subprocess execution fails, generated results are malformed, result validation fails, replay logging fails, or an unknown exception occurs.

## Replay Guarantees

Each execution appends a JSONL replay ledger entry to:

```text
sapianta_bridge/runtime/logs/replay_log.jsonl
```

Entries include task ID, execution timestamp, Codex exit code, task hash, result hash, duration, and final state.

## Lock Semantics

`task_lock.py` uses atomic lock file creation. If the lock exists or cannot be acquired, execution is blocked. v1 does not remove stale locks automatically because uncertain lock state must not continue.

## No Recursion

v1 does not generate new tasks, process follow-up proposals, call reflection generators, retry automatically, self-trigger execution, or run autonomous loops.

One task enters. One result exits. Nothing more.

