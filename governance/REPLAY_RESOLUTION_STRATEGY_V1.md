# Replay Resolution Strategy V1

Status: first replay-backed answer resolution strategy.

Final classification:

```text
REPLAY_RESOLUTION_STRATEGY_STATUS = CERTIFIED
```

## Scope

`REPLAY_RESOLUTION_STRATEGY_V1` implements replay-based answer resolution for replay-oriented human prompts.

It extends Resolution Strategy Runtime to support:

```text
REPLAY
```

It does not implement worker execution, provider authority, approval changes, proposal mutation, provider invocation, or execution requests.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/replay_resolution_strategy.py
```

Updated runtime file:

```text
aigol/runtime/resolution_strategy_runtime.py
```

Implemented tests:

```text
tests/test_replay_resolution_strategy_v1.py
tests/test_resolution_strategy_runtime_v1.py
```

## Replay-Oriented Prompt Detection

The runtime detects prompts including:

- `What happened recently?`
- `What changed?`
- `Show latest proposal.`
- `Show latest approval.`
- `What was the last operation?`
- `Summarize recent activity.`

Detected replay-oriented prompts select:

```text
selected_strategy = REPLAY
```

## Replay Answer Artifact

The runtime emits:

```text
REPLAY_RESOLUTION_ARTIFACT_V1
```

It records:

- resolution id;
- strategy id and hash;
- selected strategy;
- human prompt reference;
- replay source reference;
- evidence count;
- latest replay event;
- replay-backed answer text;
- non-authority and non-execution flags;
- artifact hash.

## Replay Events

The runtime records:

```text
REPLAY_RESOLUTION_CREATED
REPLAY_RESOLUTION_RETURNED
```

The nested strategy selection records:

```text
RESOLUTION_STRATEGY_SELECTED
RESOLUTION_STRATEGY_RETURNED
```

## Fail-Closed Cases

The runtime fails closed on:

- non-replay-oriented prompt;
- replay unavailable;
- empty replay source;
- corrupt replay JSON;
- replay hash mismatch;
- artifact hash mismatch;
- invalid replay resolution references;
- replay ordering corruption.

## Boundary Guarantees

The runtime preserves:

```text
authority = false
provider_used = false
worker_invoked = false
execution_requested = false
```

No provider inference is used for replay truth.

No worker is invoked.

No approval is changed.

No proposal is mutated.

## Constitutional Invariant

The runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Runtime mapping:

| Role | Runtime meaning |
| --- | --- |
| LLM proposes | No provider inference is required for replay truth |
| AiGOL governs | AiGOL selects REPLAY and validates replay evidence |
| Worker executes | Worker execution is absent |
| Replay records | Replay records strategy selection and replay answer evidence |

## Validation

Focused validation:

```text
python -m pytest tests/test_resolution_strategy_runtime_v1.py tests/test_replay_resolution_strategy_v1.py
```

Result:

```text
30 passed
```

## Final Result

AiGOL can answer replay-oriented questions from replay evidence rather than provider inference.

```text
REPLAY_RESOLUTION_STRATEGY_STATUS = CERTIFIED
```
