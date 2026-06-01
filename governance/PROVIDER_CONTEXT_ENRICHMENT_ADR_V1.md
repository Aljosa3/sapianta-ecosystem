# Provider Context Enrichment ADR V1

Status: accepted as review decision.

## Context

OpenAI connectivity is proven, but provider context construction is incomplete.

AiGOL currently sends the literal extracted human prompt as provider `payload.input`. For `Explain provider boundaries.`, this leaves the provider without enough information to know that the intended domain is AiGOL provider authority boundaries.

## Decision

Classify provider context enrichment review as:

```text
PROVIDER_CONTEXT_ENRICHMENT_STATUS = READY_WITH_GAPS
```

Adopt a review-level minimal context model for future measurement, not implementation in this milestone.

## Minimal Model

The smallest useful context is:

```text
AiGOL is a constitutional AI execution governance system.
LLM providers are proposal-only sources; they do not govern, authorize, execute, mutate replay, or invoke workers.
AiGOL governs; workers execute only after governed authorization; replay records evidence.
Answer in the AiGOL/SAPIANTA governance domain unless the user explicitly asks for another domain.
Use the human prompt as the question; provide explanatory text only.
```

## Rationale

This context is sufficient to disambiguate AiGOL terms such as provider, worker, replay, governance, and authorization without embedding full governance documents or transferring authority to the provider.

## Consequences

Provider-neutral enrichment is possible.

Conversational relevance is likely to improve for AiGOL-specific explanatory prompts.

Coverage improvement is not yet proven and requires replay-visible measurement.

## Rejected Alternatives

Do not send full constitutional memory.

Do not send full governance documents.

Do not send provider-specific prompts.

Do not give the provider governance, authorization, execution, replay, worker, or routing authority.

Do not implement enrichment in this review milestone.

