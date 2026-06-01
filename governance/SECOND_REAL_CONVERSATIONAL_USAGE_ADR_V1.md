# SECOND_REAL_CONVERSATIONAL_USAGE_ADR_V1

## Decision

Record the second conversational usage epoch as evidence that direct
prompt-to-response is operational but coverage remains narrow.

## Context

`PROMPT_TO_CONVERSATION_INTEGRATION_V1` connected:

```text
Human Prompt
↓
AiGOL
↓
Conversational Response
↓
Replay
```

The next question was whether AiGOL could be used directly for real
conversational project work.

## Observed Reality

AiGOL answered 6 of 50 prompts.

All successful answers used deterministic self-resolution.

Provider fallback did not produce successful real responses in this epoch.

## Decision Rationale

The correct next priority is not more architecture.

The correct next priority is expanding replay-backed and governance-backed
answer coverage through existing surfaces.

## Rejected Alternatives

### New Worker

Rejected.

The bottleneck is conversational response coverage, not execution.

### New Governance Layer

Rejected.

Existing governance constraints remain sufficient.

### New CLI

Rejected.

`aigol prompt submit` is the correct operator surface.

### Architecture Redesign

Rejected.

The prompt-to-response path works; it needs evidence coverage and provider
availability.

## Consequence

Future work should use observed prompt failures as the backlog for self-resolution
coverage and replay-backed explanation integration.
