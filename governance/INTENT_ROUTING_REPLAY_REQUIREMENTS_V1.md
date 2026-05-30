# Intent Routing Replay Requirements V1

Status: replay requirements for intent routing.

## Replay Visibility Classification

`INTENT_ROUTING_REPLAY_VISIBILITY`: `MANDATORY`

## Why Replay Is Mandatory

Routing affects which governed destination receives a Human Prompt.

Therefore replay must preserve:

- the original Human Prompt reference
- routing artifact identity
- candidate destination
- final routing status
- ambiguity status
- failure reason if failed
- lineage from prompt to destination boundary

## Replay Sequence

A future routing sequence should record:

```text
Human Prompt Evidence
-> Intent Routing Artifact
-> Destination Boundary Entry
```

The routing artifact must be created before destination execution, provider invocation, memory retrieval, or authorization.

## Reconstructability

Replay reconstruction must answer:

- which prompt was routed
- which destination was selected
- why routing succeeded or failed
- whether ambiguity was present
- which downstream boundary received the prompt

## Fail-Closed Replay

Missing, corrupted, ambiguous, or unordered routing replay must fail closed.

No route may be considered valid without replay evidence.

