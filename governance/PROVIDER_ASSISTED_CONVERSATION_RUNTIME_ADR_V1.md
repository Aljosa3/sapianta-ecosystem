# PROVIDER_ASSISTED_CONVERSATION_RUNTIME_ADR_V1

## Decision

Implement provider-assisted conversation response as a bounded runtime that
emits replay-visible AiGOL response artifacts.

## Context

`PROVIDER_ASSISTED_INTENT_CLASSIFICATION_V1` allows natural-language prompts
such as:

```text
Kaj je namen AiGOL?
```

to classify as `CONVERSATION`.

The missing step was a response path after classification and routing.

## Decision Rationale

The smallest safe implementation is:

```text
Conversation Intent
↓
Self-resolution attempt
↓
Provider response suggestion only if unresolved
↓
AiGOL validation
↓
Final response artifact
```

This preserves AiGOL-first resolution and keeps provider output as proposal
evidence.

## Rejected Alternatives

### Provider Direct Response To Human

Rejected.

Provider text must not bypass AiGOL validation or replay.

### Provider-First Conversation

Rejected.

AiGOL must attempt deterministic self-resolution first.

### Worker Or Execution Activation

Rejected.

Conversation response does not authorize or invoke workers.

### New Governance Model

Rejected.

The runtime uses existing provider runtime, provider-assisted intent
classification, replay hashing, and fail-closed semantics.

## Consequences

AiGOL can now return a response for conversation prompts without ChatGPT
copy/paste transport.

Provider assistance is used only when deterministic self-resolution is
insufficient.

## Status

`PROVIDER_ASSISTED_CONVERSATION_RUNTIME_STATUS = READY`
