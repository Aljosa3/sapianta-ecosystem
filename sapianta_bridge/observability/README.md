# Execution Observability v1

This package provides read-only observability for SAPIANTA bounded bridge transport.

It introduces deterministic runtime inspection, queue visibility, replay log reading, execution summaries, and transition visibility before any reflection or recursive orchestration exists.

## Architecture

- `runtime_status.py`: deterministic runtime snapshot.
- `queue_inspector.py`: read-only task directory inspection.
- `replay_reader.py`: append-only replay log reader.
- `execution_summary.py`: deterministic summaries derived from replay evidence.
- `state_transitions.py`: readable lifecycle transition visibility.
- `observability_cli.py`: read-only CLI entrypoint.

## CLI

```bash
python -m sapianta_bridge.observability.observability_cli status
python -m sapianta_bridge.observability.observability_cli queue
python -m sapianta_bridge.observability.observability_cli replay --latest
python -m sapianta_bridge.observability.observability_cli replay --task-id TASK-001
python -m sapianta_bridge.observability.observability_cli summary
python -m sapianta_bridge.observability.observability_cli transitions --task-id TASK-001
```

The CLI is deterministic and read-only. It never starts transport, invokes Codex, creates tasks, edits replay logs, retries failed tasks, or generates reflections.

## Replay Inspection Philosophy

Replay history is treated as immutable evidence. Malformed replay lines, missing replay fields, unknown execution states, or corrupted entries fail closed with explicit errors and a quarantine recommendation.

## Read-Only Guarantees

Observability reads runtime directories and replay logs only. It does not mutate queue state, transport locks, completed artifacts, failed artifacts, quarantine records, or replay history.

## Why Observability Precedes Reflection

SAPIANTA must first see runtime state, inspect replay evidence, validate transitions, and expose deterministic execution history before strategic interpretation, reflection, orchestration, or bounded autonomy can be introduced.

This milestone introduces visibility, not intelligence.

