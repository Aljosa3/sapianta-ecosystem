# Conversation Runtime V1 ADR

Status: accepted architecture decision record.

## Decision

Implement Conversation Runtime as a deterministic wrapper over existing AiGOL components.

The first supported path is:

```text
CONVERSATION
-> MEMORY_BASED_RESPONSE
```

## Context

AiGOL already supports intent classification, Constitutional Memory consultation, citation bundle generation, Memory-Based Response generation, and replay recording.

The missing piece was a conversation-level lifecycle artifact that accepts a conversational prompt and returns a bounded response without introducing provider, worker, execution, governance, or authorization authority.

## Accepted Approach

The runtime:

- records conversation start
- classifies the prompt as `CONVERSATION`
- activates the only supported response source: Constitutional Memory evidence
- creates a Memory-Based Response
- wraps it in `CONVERSATION_RESPONSE_ARTIFACT_V1`
- records conversation replay

## Rejected Alternatives

Provider-backed conversation: rejected for V1 because provider calls are explicitly out of scope.

Worker-backed conversation: rejected for V1 because worker dispatch is explicitly out of scope.

Execution planning conversation: rejected because conversation has no execution authority.

Multi-turn memory: rejected because V1 is single-turn and replay-bounded.

## Consequences

Conversation Runtime is intentionally narrow.

It proves a bounded human-facing response path while preserving:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
