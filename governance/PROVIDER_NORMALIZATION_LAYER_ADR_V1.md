# PROVIDER_NORMALIZATION_LAYER_ADR_V1

## Decision

Certify the provider normalization layer as provider-generic.

## Context

`FIRST_REAL_PROVIDER_OPERATION_V1` proved that OpenAI could be reached but
could not initially satisfy the conversation response validation contract.

`PROVIDER_RESPONSE_CONTRACT_ALIGNMENT_V1` added deterministic alignment from
generic provider `response_text` to the existing provider-assisted conversation
contract.

This review determines whether that alignment is OpenAI-specific or suitable
for provider substitution.

## Decision Rationale

The normalization layer reads provider proposal envelope response evidence.

It does not read OpenAI-specific raw response structures.

The same envelope response shape can be produced by:

- OpenAI;
- Claude;
- Gemini;
- Local Provider;
- future providers.

Therefore provider substitution does not require governance, replay, or
conversation runtime changes.

## Constraints

Provider adapters remain responsible for vendor-specific extraction.

The normalization layer begins only after adapter output has become a provider
proposal envelope.

## Rejected Alternatives

### Provider-Specific Runtime Branches

Rejected.

Provider identity must be replay evidence, not hidden runtime behavior.

### Governance Changes Per Provider

Rejected.

Provider output remains proposal-only regardless of provider identity.

### Replay Schema Changes Per Provider

Rejected.

Existing replay records provider identity and provider version.

## Consequence

Provider substitution can proceed through a stable normalization boundary.

Future provider work should focus on adapter-specific extraction and
fail-closed behavior, not core runtime redesign.

## Status

`PROVIDER_NORMALIZATION_LAYER_STATUS = CERTIFIED`
