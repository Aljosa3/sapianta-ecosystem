# Real OpenAI Connectivity ADR V1

Status: accepted.

## Context

AiGOL previously had provider architecture, adapter behavior, normalization, fallback, and replay evidence. The remaining question was whether AiGOL had observable proof of actual OpenAI API communication.

This ADR addresses only factual connectivity proof.

## Decision

Certify real OpenAI connectivity as:

```text
REAL_OPENAI_CONNECTIVITY_STATUS = READY
```

## Basis

The decision is based on a live proof run through the existing AiGOL OpenAI provider adapter and provider attachment runtime.

The run observed:

- process environment key presence for `OPENAI_API_KEY`;
- provider initialization through `OpenAIProviderAdapter`;
- real request metadata for `https://api.openai.com/v1/responses`;
- real response metadata with OpenAI response id `resp_02aefc54f17190e6006a1d499ad4dc819cbfde31d6905b008f`;
- replay artifacts for created and returned provider proposal events;
- successful replay reconstruction.

## Rejected Alternatives

Do not certify from architecture alone.

Do not certify from fake-client tests.

Do not certify from provider normalization tests.

Do not certify from fallback behavior.

Do not persist or expose the OpenAI API key.

## Consequences

AiGOL may now claim that, for the observed proof run, OpenAI was truly attached and operational as a real provider source.

The claim remains bounded:

- one request;
- one response;
- proposal-only provider role;
- no execution authority;
- no governance authority;
- no replay mutation authority;
- no future availability guarantee.

