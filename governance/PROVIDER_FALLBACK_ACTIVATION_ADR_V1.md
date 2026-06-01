# PROVIDER_FALLBACK_ACTIVATION_ADR_V1

## Decision

Certify provider fallback activation as connected but ready with gaps.

## Context

`SECOND_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` reported:

```text
provider_used = 0
success_rate = 12%
unclassified_prompts = 30
```

This raised the question whether provider fallback was connected to the Human
Prompt flow.

## Reviewed Evidence

Review showed:

- `prompt_to_conversation_integration.py` calls provider-assisted conversation;
- provider-assisted conversation calls provider-assisted intent classification;
- provider-assisted intent classification calls provider runtime on
  deterministic failure;
- provider-assisted conversation calls provider runtime on unresolved
  self-resolution.

Controlled replay evidence showed provider fallback artifacts were created for
an unresolved conversation prompt.

## Decision Rationale

The correct classification is not `NOT_CONNECTED`.

Fallback is connected.

The practical gaps are:

- real provider unavailable;
- top-level CLI does not distinguish provider fallback attempted from provider
  fallback succeeded;
- no explicit provider configuration readiness check is surfaced to operator.

## Rejected Alternatives

### Redesign Provider Fallback

Rejected.

The fallback path is already connected and replay-visible.

### Treat Provider Failure As Successful Provider Usage

Rejected.

Provider usage should remain reserved for validated provider-assisted results.

### Bypass Provider Availability Failure

Rejected.

Provider unavailability must fail closed.

## Consequence

Future work should improve observability and configuration checks, not
architecture.

## Status

`PROVIDER_FALLBACK_ACTIVATION_STATUS = READY_WITH_GAPS`
