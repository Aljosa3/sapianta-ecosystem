# Human Prompt To Governed Readonly Result V1

Status: first minimal end-to-end operator flow.

This artifact defines the bounded path from human prompt to governed read-only result using existing runtime components only.

## Permanent Invariant

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## End-To-End Flow

```text
Human prompt
-> cognition proposal
-> AiGOL proposal normalization
-> AiGOL validation
-> AiGOL authorization
-> governed execution request
-> deterministic worker/runtime execution
-> read-only capability result
-> replay-visible evidence
-> governed return
```

## Supported Capabilities

The operator flow may target only existing read-only capabilities:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

No new capability class or capability surface is introduced.

## Boundary Status

The flow does not introduce:

- LLM execution
- worker self-authorization
- filesystem mutation
- shell execution
- network execution
- orchestration runtime
- agent runtime
- new capabilities
