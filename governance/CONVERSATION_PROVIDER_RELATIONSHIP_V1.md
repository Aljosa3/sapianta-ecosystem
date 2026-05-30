# Conversation Provider Relationship V1

Status: relationship between Conversation and Provider Proposal.

## Provider Requirement

`CONVERSATION_PROVIDER_REQUIREMENT`: `OPTIONAL`

Conversation does not constitutionally require a provider.

## Distinction

Conversation is a human-facing response destination.

Provider Proposal is a proposal-source destination where provider output is captured, normalized, and governed as untrusted proposal input.

## When To Use Conversation

Use Conversation when:

- no external proposal is required
- no provider output is required
- the response can remain non-authoritative and bounded

## When To Use Provider Proposal

Use Provider Proposal when:

- external LLM contribution is needed
- provider identity and raw response must be captured
- output must enter proposal normalization
- downstream governance or execution may be involved

## Provider Boundary

Conversation must not silently call a provider.

If a provider is used, the route is no longer pure Conversation. It becomes `PROVIDER_PROPOSAL` or a separately governed provider-backed conversation model not yet defined.

## Distinction Classification

`CONVERSATION_VS_PROVIDER_PROPOSAL`: `PARTIAL`

The distinction is constitutionally clear, but no classifier currently enforces it.

