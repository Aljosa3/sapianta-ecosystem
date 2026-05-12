# Reflection Layer v1

This package provides the first advisory-only reflection layer for SAPIANTA bounded execution evidence.

Reflection derives interpretation from replay logs, execution summaries, runtime status, and lifecycle transition visibility. It does not execute work, enqueue tasks, trigger Codex, mutate queue state, or modify replay history.

## Architecture

- `reflection_engine.py`: builds and stores deterministic reflection artifacts.
- `capability_delta.py`: conservatively summarizes replay-derived capability deltas.
- `governance_risk.py`: interprets bounded governance risk from execution evidence.
- `advisory_proposals.py`: emits non-authoritative recommendations.
- `reflection_reader.py`: reads immutable reflection history.
- `reflection_cli.py`: exposes read-only and generate-only reflection commands.

## CLI

```bash
python -m sapianta_bridge.reflection.reflection_cli latest
python -m sapianta_bridge.reflection.reflection_cli summary
python -m sapianta_bridge.reflection.reflection_cli task --task-id TASK-001
python -m sapianta_bridge.reflection.reflection_cli generate --task-id TASK-001
```

`generate` creates only a reflection artifact under `sapianta_bridge/runtime/reflections/`. It does not create tasks, modify transport state, invoke Codex, or trigger follow-up execution.

## Advisory-Only Principles

Every reflection artifact sets `advisory_only` to `true` and `allowed_to_execute_automatically` to `false`. Advisory proposals require human approval and remain non-authoritative.

## Governance Boundaries

Reflection is replay-derived and fail-closed. Malformed replay evidence, invalid lifecycle evidence, missing source task evidence, or malformed reflection artifacts stop interpretation with explicit errors.

## Why Reflection Is Separate From Execution

Observability must precede interpretation, and interpretation must remain separate from execution authority. This layer adds strategic visibility without autonomy, orchestration, recursive execution, auto-repair, auto-merge, or auto-push.
