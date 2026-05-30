# Conversation Gaps V1

Status: genuine gaps before Conversation becomes a first-class routing destination.

## Critical Gaps

Before implementation, AiGOL needs:

- conversation-only lifecycle
- conversation replay artifact
- non-authoritative response boundary
- explicit termination semantics
- fail-closed handling for conversation attempting execution, authorization, provider invocation, memory retrieval, or governance mutation

## Important Gaps

Useful but not strictly blocking for model definition:

- operator-facing conversation summary format
- distinction rules for conversation vs memory consultation
- distinction rules for conversation vs provider proposal
- distinction rules for conversation vs execution request
- pressure validation plan for conversation ambiguity

## Optional Gaps

Should not drive architecture yet:

- conversational memory
- multi-turn dialogue management
- provider-backed conversation
- conversation correction loops
- strategic planning mode

## Readiness

`CONVERSATION_INTENT_READINESS`: `READY_WITH_GAPS`

Conversation can be modeled as a routing destination, but should not be implemented until lifecycle and replay boundaries are defined.

