# PROMPT_TO_CONVERSATION_INTEGRATION_ADR_V1

## Decision

Connect `aigol prompt submit` to the existing provider-assisted conversation
runtime through a minimal integration wrapper.

## Context

`FIRST_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` showed:

```text
prompt_artifacts_created = 12
conversation_classifications > 0
conversational_responses_returned = 0
```

The missing capability was not new architecture.

The missing capability was connecting existing components:

- Human Prompt Interface;
- Provider-Assisted Intent Classification;
- Intent Routing Attachment;
- Provider-Assisted Conversation Runtime;
- Replay.

## Decision Rationale

The smallest safe integration is:

```text
Prompt Submit
↓
Prompt Artifact and Routing Evidence
↓
Conversation Runtime
↓
Response Artifact
↓
CLI Output
```

The integration keeps `aigol prompt submit` as the operator surface instead of
creating another CLI.

## Rejected Alternatives

### New Conversational CLI

Rejected.

The existing prompt surface is the correct extension point.

### New Provider

Rejected.

The integration uses the existing provider boundary and existing OpenAI
provider attachment when provider assistance is needed.

### New Worker

Rejected.

Conversation response does not require worker execution.

### New Governance Layer

Rejected.

Existing validation, fail-closed, and replay boundaries are sufficient.

## Consequence

AiGOL can now return a conversational response through direct prompt submission
without ChatGPT copy/paste for deterministic self-resolution cases, and with a
provider-assisted path available when a valid provider adapter is supplied.

## Status

`PROMPT_TO_CONVERSATION_INTEGRATION_STATUS = READY`
