# Intent Routing Attachment V1

Status: first minimal intent routing attachment implementation.

This milestone implements:

```text
Intent Classification Artifact
-> Routing Attachment Evidence
-> Replay
```

It does not implement routing engine, provider calls, worker calls, execution, memory retrieval, conversation handling, correction loops, or orchestration.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/intent_routing_attachment.py
```

Implemented tests:

```text
tests/test_intent_routing_attachment_v1.py
```

## Input

The attachment accepts only a valid `INTENT_CLASSIFICATION_ARTIFACT`.

It rejects:

- missing artifact
- corrupt artifact
- ambiguous artifact
- invalid destination
- multiple destinations
- authority-bearing artifact

## Output

The runtime emits `INTENT_ROUTING_ATTACHMENT_RECORD` with:

- routing record id
- artifact reference
- destination
- routing status
- routing version
- routing timestamp
- replay reference
- reconstruction metadata

The record does not contain authority, execution, provider, worker, memory retrieval, or conversation output fields.

## Final Classification

`INTENT_ROUTING_ATTACHMENT_STATUS`: `READY_WITH_CONSTRAINTS`

`INTENT_ROUTING_ATTACHMENT_AUTHORITY_STATUS`: `PRESERVED`

`INTENT_ROUTING_ATTACHMENT_REPLAY_STATUS`: `READY`

