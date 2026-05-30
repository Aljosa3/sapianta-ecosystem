# Conversation Runtime V1

Status: first operational Conversation Runtime.

This milestone implements the minimum deterministic conversation path:

```text
Human Prompt
-> Conversation Runtime
-> Intent Classification
-> Constitutional Memory Consultation
-> Memory-Based Response
-> Conversation Response Artifact
-> Replay
```

It does not implement provider calls, worker calls, execution requests, governance decisions, authorization decisions, routing changes, correction loops, multi-turn memory, autonomous planning, or conversation memory.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/conversation_runtime.py
```

Implemented tests:

```text
tests/test_conversation_runtime_v1.py
```

## Supported Path

V1 supports only:

```text
CONVERSATION
-> MEMORY_BASED_RESPONSE
```

No provider path exists in V1.

No execution path exists in V1.

## Conversation Response Artifact

The runtime emits `CONVERSATION_RESPONSE_ARTIFACT_V1` with:

- `conversation_id`
- `prompt_id`
- `intent_id`
- `response_id`
- `response_type`
- `response_text`
- `authority`
- `created_at`
- `replay_visible`

## Replay Events

The runtime records:

- `CONVERSATION_STARTED`
- `CONVERSATION_RESPONSE_CREATED`
- `CONVERSATION_RESPONSE_RETURNED`

## Final Status

`CONVERSATION_RUNTIME_STATUS`: `READY`

`CONVERSATION_RUNTIME_AUTHORITY_STATUS`: `PRESERVED`

`CONVERSATION_RUNTIME_REPLAY_STATUS`: `READY`
