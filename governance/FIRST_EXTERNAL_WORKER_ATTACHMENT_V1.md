# First External Worker Attachment V1

Status: first implemented external Worker attachment.

This milestone implements `EXTERNAL_RUNTIME_INSPECTION_WORKER_V1` as a narrow read-only, inspection-only Worker attachment.

It proves Worker substitutability as implementation reality without introducing worker registry, worker discovery, worker selection, worker orchestration, worker memory, worker autonomy, filesystem mutation, shell execution, network execution, API execution, or multi-worker runtime.

## Constitutional Invariant

The frozen operational invariant remains:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The Worker is an execution participant only.

The Worker does not possess proposal authority, authorization authority, governance authority, replay authority, or capability expansion authority.

## Implemented Worker

Worker identity:

```text
EXTERNAL_RUNTIME_INSPECTION_WORKER
```

Worker type:

```text
READ_ONLY_INSPECTION_WORKER
```

The Worker may:

- inspect bounded runtime metadata
- return inspection evidence
- emit replay-visible execution records
- terminate deterministically

The Worker may not:

- write, delete, move, or modify files
- execute shell commands
- perform network execution
- perform API execution
- authorize itself
- mutate replay
- mutate governance
- continue autonomously

## Attachment Flow

The implemented path is:

```text
Human
-> Provider
-> AiGOL
-> Authorization
-> External Worker
-> Worker Evidence
-> Replay
-> Governed Result
```

The Worker receives only `AUTHORIZED_EXECUTION_REQUEST` evidence. There is no direct provider-to-worker path, no direct human-to-worker path, and no replay bypass.

## Runtime Files

Implemented runtime evidence:

- `aigol/runtime/external_runtime_inspection_worker.py`
- `tests/test_external_runtime_inspection_worker_v1.py`

## Success Condition

Success is practical evidence that a real external Worker attachment can execute a bounded read-only inspection request while preserving:

- proposal-only provider semantics
- AiGOL governance authority
- worker execution-only participation
- mandatory replay recording
- fail-closed boundary enforcement

