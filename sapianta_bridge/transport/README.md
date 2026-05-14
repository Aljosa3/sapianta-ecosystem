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

---

# TRANSPORT BRIDGE v1

`TRANSPORT_BRIDGE_V1` adds bounded envelope transport semantics on top of the provider and runtime adapter substrate.

The bridge flow is:

```text
ExecutionEnvelope
-> validated transport request
-> explicit provider transport binding
-> bounded adapter runtime delivery
-> normalized runtime response
-> replay-safe transport evidence
```

## Envelope-First Transport

Transport may deliver only validated execution envelopes. Invalid envelopes are blocked before transport execution.

## Provider Binding

Transport binds to one explicit provider identity. It does not select, route, optimize, retry, or fall back to another provider.

## Bounded Transport Guarantees

Transport preserves:

- provider identity;
- envelope identity;
- replay identity;
- runtime binding;
- authority scope;
- workspace scope;
- normalized runtime result semantics.

## Transport vs Runtime vs Orchestration

Transport delivers the validated request to a bounded runtime adapter. Runtime invokes the explicit adapter. Orchestration would choose, schedule, retry, coordinate, or chain execution. This milestone does none of that.

## Non-Goals

`TRANSPORT_BRIDGE_V1` does not add autonomous orchestration, planning, provider routing intelligence, dynamic optimization, retries, fallback, hidden execution, multi-agent coordination, unrestricted provider execution, autonomous scheduling, or production bridge behavior.
