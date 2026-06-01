# MINIMAL_HUMAN_PROMPT_INTERFACE_ADR_V1

## Decision

Implement the first minimal Human Prompt Interface.

## Context

`HUMAN_PROMPT_INTERFACE_REVIEW_V1` concluded that the Human Prompt Interface needs implementation, not new architecture.

AiGOL already has:

- intent classifier;
- intent routing attachment;
- replay verification;
- replay reporting;
- replay-backed explanations.

## Decision Rationale

The smallest useful implementation is:

```text
Human Prompt
↓
Prompt Artifact
↓
Intent Classification
↓
Intent Routing Attachment
↓
Prompt Lineage
↓
Replay
```

This gives the human a direct entrypoint into AiGOL while preserving all downstream boundaries.

## Rejected Alternatives

### Provider Activation

Rejected for this milestone.

The prompt interface must first prove replay-visible prompt ingress before activating provider paths.

### Worker Activation

Rejected.

Workers may execute only after governed authorization. The prompt interface does not authorize or dispatch.

### New Replay Model

Rejected.

The implementation uses the existing immutable replay wrapper pattern.

### Orchestration Or Planning

Rejected.

This milestone only records prompt ingress and cognition path entry.

## Consequence

Humans can submit prompts directly to AiGOL through:

```text
aigol prompt submit
```

The prompt becomes replay-visible and enters existing intent/routing cognition evidence without ChatGPT copy/paste transport.
