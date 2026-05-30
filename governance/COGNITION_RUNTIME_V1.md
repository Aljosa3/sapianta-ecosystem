# Cognition Runtime V1

Status: first canonical cognition runtime entrypoint.

This milestone implements:

```text
Human Prompt
-> Cognition Runtime
-> Intent Classification
-> Conversation Runtime or Provider Proposal Runtime
-> Memory-Based Response or Provider Proposal
-> Conversation Response or Provider Proposal Artifact
-> Replay
```

It does not implement provider invocation, worker invocation, execution requests, planning, orchestration, multi-turn memory, governance decisions, or authorization.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/cognition_runtime.py
```

Implemented tests:

```text
tests/test_cognition_runtime_v1.py
```

## Cognition Artifacts

The runtime creates:

- `COGNITION_SESSION_STARTED`
- `COGNITION_RUNTIME_STATE`
- `COGNITION_SESSION_COMPLETED`
- `COGNITION_SESSION_FAILED`

## Responsibility Boundary

Cognition Runtime may coordinate cognition components and expose cognition state.

Cognition Runtime may not:

- invoke providers
- invoke workers
- authorize execution
- perform governance decisions
- dispatch execution

## Supported Paths

V1 supports:

- `CONVERSATION -> CONVERSATION_RUNTIME_V1`
- `PROVIDER_PROPOSAL -> PROVIDER_PROPOSAL_RUNTIME_V1`

Unsupported intents fail closed.

## Final Status

`COGNITION_RUNTIME_STATUS`: `READY`

`COGNITION_RUNTIME_AUTHORITY_STATUS`: `PRESERVED`

`COGNITION_RUNTIME_REPLAY_STATUS`: `READY`
