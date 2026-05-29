# Operator Quickstart V1

Status: minimal quickstart for first useful AiGOL.

## 1. Submit A Runtime Inspection Request

```python
from aigol.runtime.minimal_operator_entrypoint import run_minimal_operator_entrypoint

result = run_minimal_operator_entrypoint(
    operator_flow_id="OPERATOR-FLOW-000001",
    human_request="Inspect bounded runtime metadata.",
    target_capability="READ_ONLY_RUNTIME_INSPECTION",
    created_at="2026-05-29T00:00:00+00:00",
    replay_dir=".runtime/operator_replay/OPERATOR-FLOW-000001",
)
```

## 2. Read The Governed Result

```python
summary = result["operator_result_summary"]

print(summary["status"])
print(summary["reason"])
print(summary["capability_used"])
print(summary["replay_reference"])
print(summary["recommended_next_action"])
```

## 3. Inspect Replay Summary

```python
from aigol.runtime.replay_summary_command import summarize_operator_replay, render_replay_summary

replay = summarize_operator_replay(
    replay_dir=summary["replay_reference"],
)

print(render_replay_summary(replay))
```

## 4. Interpret Status

`ACCEPTED` means AiGOL validated, authorized, executed a bounded read-only worker capability, recorded replay, and returned a governed result.

`REJECTED` means AiGOL failed closed. Read the reason, then either stop or submit a corrected new bounded request.

## 5. Remember The Invariant

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## 6. Stay Inside Boundaries

Allowed:

- read-only runtime inspection
- allowlisted filesystem read-only inspection
- replay summary inspection

Not allowed:

- mutation
- shell
- network
- agents
- orchestration
- hidden continuation
