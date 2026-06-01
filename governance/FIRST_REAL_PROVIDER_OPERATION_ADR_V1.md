# FIRST_REAL_PROVIDER_OPERATION_ADR_V1

## Decision

Certify the first real provider operation as `READY_WITH_GAPS`.

## Context

`PROVIDER_FALLBACK_ACTIVATION_REVIEW_V1` found that provider fallback was
connected but provider availability was the remaining unknown.

This milestone tested the real OpenAI provider path with network access and an
available API key.

## Observed Reality

OpenAI was reached.

OpenAI returned a replay-visible provider response.

AiGOL failed closed during conversation validation because the response shape
was generic provider output rather than provider-assisted conversation
suggestion output.

## Decision Rationale

The result is not `READY` because the full target flow did not produce a final
conversation response.

The result is not `NOT_READY` because the real provider request/response/replay
boundary succeeded.

The accurate status is:

```text
READY_WITH_GAPS
```

## Rejected Alternatives

### Treat Raw Provider Text As Final Response

Rejected.

Provider response is proposal evidence only. AiGOL must validate structured
response suggestions before returning a response.

### Loosen Validation To Accept Any `response_text`

Rejected.

That would blur provider output and AiGOL response authority.

### Redesign Provider Runtime

Rejected.

The provider runtime successfully created replay-visible provider evidence.

## Consequence

Future work should add a structured semantic response contract or adapter-local
normalization layer while preserving provider substitutability and
non-authority.

## Status

`FIRST_REAL_PROVIDER_OPERATION_STATUS = READY_WITH_GAPS`
