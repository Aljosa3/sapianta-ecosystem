# Provider Context Construction ADR V1

Status: accepted.

## Context

OpenAI connectivity is proven.

An operator-observed OpenAI Platform Log shows:

```text
Human Prompt: Explain provider boundaries.
Provider Prompt: Explain provider boundaries.
Provider Response: professional/healthcare provider-boundary explanation.
```

This indicates the provider behaved consistently with the prompt it received, but AiGOL did not provide enough AiGOL-specific context.

## Decision

Classify provider context construction as:

```text
PROVIDER_CONTEXT_CONSTRUCTION_STATUS = READY_WITH_GAPS
```

## Basis

The code path proves that structured AiGOL provider request objects are reduced to a single prompt string before OpenAI invocation.

Replay proves that request objects contain some metadata, but live OpenAI payload evidence shows OpenAI receives only `payload.input`.

The repository does not yet contain a full post-connectivity replay chain for `Explain provider boundaries.` from provider response through final AiGOL response.

## Consequence

Current provider usefulness cannot be inferred from connectivity alone.

AiGOL needs measured provider context construction evidence before claiming broad conversational usefulness.

## Rejected Alternatives

Do not replace providers.

Do not redesign governance.

Do not redesign replay.

Do not infer provider failure from irrelevant answers when provider context is missing.

Do not certify context construction as fully ready until post-connectivity conversational replay contains provider prompt, provider response, normalized response, final response, and reconstruction.

