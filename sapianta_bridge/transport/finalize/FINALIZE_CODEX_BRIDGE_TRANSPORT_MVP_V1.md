# Finalize CODEX_BRIDGE_TRANSPORT_MVP_V1

## Finalized Scope

`CODEX_BRIDGE_TRANSPORT_MVP_V1` finalizes the first bounded Codex execution transport layer for SAPIANTA.

Finalized capabilities include:

- Task queue transport.
- Single-task atomic lock handling.
- Protocol enforcement before processing.
- Bounded Codex subprocess execution.
- Canonical `result.json` generation.
- Result validation through the protocol validator.
- Terminal movement to `completed/` or `failed/`.
- Append-only replay logging.

## Locked Behaviors

The following behaviors are locked for this milestone:

- Tasks originate from validated `task.json` artifacts.
- Invalid tasks are blocked before execution.
- One task is processed per listener invocation.
- Lock uncertainty blocks execution.
- Codex runs through bounded subprocess execution only.
- `shell=False` is required.
- Timeout is enforced.
- Stdout and stderr are captured.
- Result artifacts are generated deterministically.
- Generated results must pass protocol validation.
- Replay log append occurs before terminal task movement.
- Failed or malformed results move to `failed/`.
- Quarantine isolates malformed governance-unsafe artifacts.
- No recursive task generation occurs.

## Validation Summary

Finalization acceptance evidence records successful validation for:

- `pytest tests/test_protocol_validator.py tests/test_lifecycle.py tests/test_hashing.py tests/test_lineage.py tests/test_enforcement.py tests/test_cli_validation.py tests/test_quarantine.py tests/test_bridge_listener.py tests/test_codex_runner.py tests/test_task_queue.py tests/test_task_lock.py tests/test_replay_log.py`
- `python -m py_compile` over protocol and transport modules.
- `git diff --check`.
- `git -C sapianta_system diff --check`.

## Replay Guarantees

The transport appends runtime evidence to `sapianta_bridge/runtime/logs/replay_log.jsonl`.

Replay entries include:

- Task ID.
- Execution timestamp.
- Codex exit code.
- Task hash.
- Result hash.
- Processing duration.
- Final state.

## Deterministic Guarantees

The transport lifecycle is deterministic and single-task:

```text
tasks/ -> processing/ -> completed/ or failed/
```

The listener does not daemonize, recurse, spawn follow-up tasks, or chain autonomous work.

## Fail-Closed Guarantees

The transport fails closed on:

- Invalid task artifacts.
- Lifecycle validation failure.
- Lock uncertainty.
- Workspace uncertainty.
- Target paths outside configured workspace.
- Codex timeout.
- Subprocess error.
- Malformed result artifact.
- Result validation failure.
- Replay log append failure.
- Unknown exception.

## Excluded Capabilities

This milestone excludes:

- Recursive execution.
- Automatic next-task generation.
- Reflection orchestration.
- Auto-repair.
- Auto-merge.
- Auto-push.
- Systemd daemonization.
- Distributed orchestration.
- Multi-agent planning.
- Self-modifying governance.
- Runtime authority escalation.

## Runtime Authority Boundaries

Codex is a bounded execution subprocess. It is not an authority layer. It cannot approve work, create follow-up tasks, merge work, push work, mutate governance, bypass protocol validation, or continue after quarantine.

The governance substrate remains authoritative.

## Future Milestone Dependency Chain

```text
BRIDGE_PROTOCOL_V0_1_FINAL
-> BRIDGE_SCHEMA_VALIDATOR_INTEGRATION_V1
-> CODEX_BRIDGE_TRANSPORT_MVP_V1
-> EXECUTION_OBSERVABILITY_V1
-> REFLECTION_LAYER_V1
-> HUMAN_APPROVAL_QUEUE_V1
-> BOUNDED_AUTONOMY_V1
```

Future milestones must preserve bounded transport guarantees unless a new explicitly governed milestone reopens the transport behavior.

