# Conversation Replay Relationship V1

Status: replay relationship for Conversation.

## Replay Classification

`CONVERSATION_REPLAY_RELATIONSHIP`: `REPLAY_VISIBLE`

## Why Replay Is Required

Conversation is a routing destination for Human Prompt handling.

Replay must preserve:

- prompt reference
- route into Conversation
- response artifact
- non-authority guarantees
- termination status

## Replay Boundary

Conversation replay must show that no hidden transition occurred into:

- Memory Consultation
- Provider Proposal
- Execution Request
- authorization
- worker execution
- governance mutation

## Suggested Future Replay Sequence

```text
Human Prompt Evidence
-> Intent Routing Artifact
-> Conversation Response Artifact
-> Conversation Termination Artifact
```

## Replay Gap

No complete Conversation replay artifact exists today.

This is a required gap before Conversation becomes a first-class routing destination.

