# AIGOL_REAL_ELAPSED_TIME_RUNTIME_V1

## Status

Runtime fix and replay-safe certification.

The conversational CLI turn completion summary now reports measured wall-clock execution duration instead of the progress stage count placeholder.

## Executive Finding

The previous elapsed value was not execution time.

It was derived from:

```text
progress_binding_artifact["stage_count"]
```

which is the fixed conversational progress stage count. In ordinary completed turns this rendered as:

```text
elapsed: 8s
```

regardless of actual runtime duration.

## Runtime Change

The interactive conversation loop now records a monotonic timestamp after a non-empty prompt has been accepted and before the turn executes.

At turn completion, it records:

```text
elapsed_seconds = int(time.monotonic() - turn_started_monotonic)
```

The value is clamped to a non-negative integer and passed into the existing turn completion runtime.

## Replay Compatibility

The existing replay artifacts are preserved:

```text
TURN_COMPLETED_ARTIFACT_V1
RESULT_DELIVERED_ARTIFACT_V1
```

The existing replay-visible field is preserved:

```text
elapsed_seconds
```

No new provider authority, dispatch authority, execution authority, worker authority, governance authority, or replay mutation path was introduced.

## Deterministic Test Support

`run_interactive_conversation(...)` accepts an optional `monotonic_func` injection for tests.

Production CLI execution uses:

```text
time.monotonic
```

The deterministic regression test injects a synthetic monotonic sequence:

```text
100.0 -> 103.0
```

and certifies:

```text
elapsed: 3s
elapsed_seconds = 3
```

## Preserved CLI Output Format

The operator-facing completion block format is unchanged:

```text
================================
TURN COMPLETED
turn_id: TURN-000001
providers: NONE
status: COMPLETED
result_delivered: TRUE
elapsed: 3s
============
```

Only the value behind `elapsed` changed from placeholder stage count to measured duration.

## Validation

```bash
python -m pytest tests/test_interactive_conversation_cli_v1.py
python -m pytest tests/test_multiline_prompt_support_runtime_v1.py
```

Both focused suites passed.

## Final Outputs

```text
REAL_ELAPSED_TIME_ACTIVE = TRUE
PLACEHOLDER_ELAPSED_REMOVED = TRUE
REPLAY_COMPATIBLE = TRUE
```
