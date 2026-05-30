# Cognition Runtime V1 ADR

Status: accepted architecture decision record.

## Decision

Implement `COGNITION_RUNTIME_V1` as the canonical deterministic entrypoint for cognition operations.

## Context

AiGOL already had independently operating cognition components:

- Intent Classification
- Intent Routing
- Constitutional Memory Consultation
- Memory-Based Response Runtime
- Conversation Runtime

The missing surface was a single cognition session lifecycle above these components.

## Accepted Approach

The runtime:

- records `COGNITION_SESSION_STARTED`
- invokes Conversation Runtime for `CONVERSATION`
- invokes Provider Proposal Runtime for `PROVIDER_PROPOSAL`
- records `COGNITION_RUNTIME_STATE`
- records `COGNITION_SESSION_COMPLETED` or `COGNITION_SESSION_FAILED`
- preserves deterministic replay

## Rejected Alternatives

Provider invocation: rejected because Provider Proposal is advisory only.

Worker invocation: rejected because V1 is not execution.

Planning or orchestration: rejected because V1 only coordinates the existing bounded cognition flow.

Multi-turn memory: rejected because V1 is single-session and replay-bounded.

## Consequences

Cognition Runtime becomes the canonical entrypoint without adding authority or architecture expansion.

It preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
