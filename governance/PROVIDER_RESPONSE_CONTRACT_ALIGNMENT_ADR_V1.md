# PROVIDER_RESPONSE_CONTRACT_ALIGNMENT_ADR_V1

## Decision

Add deterministic provider response contract alignment at the existing
provider-assisted conversation validation boundary.

## Context

The real OpenAI provider returned replay-visible provider evidence using the
generic provider envelope field:

```text
response_text
```

The conversation runtime correctly required a validated semantic response
contract:

```text
suggested_response_text
response_reasoning
confidence
```

The mismatch caused `FIRST_REAL_PROVIDER_OPERATION_V1` to certify as
`READY_WITH_GAPS`.

## Decision Rationale

The provider envelope should remain provider-agnostic and proposal-only.

The conversation runtime should remain the validation boundary for responses
returned to humans.

Therefore the smallest safe fix is to align generic provider `response_text`
into the existing conversation contract before validation.

## Rejected Alternatives

### Return Raw Provider Text Directly

Rejected.

Raw provider text is proposal evidence, not AiGOL response authority.

### Relax Conversation Validation

Rejected.

Validation must remain fail-closed and structured.

### Redesign Provider Runtime

Rejected.

Provider runtime already produced replay-visible proposal evidence.

### Add New Governance Layer

Rejected.

The existing AiGOL validation boundary is sufficient.

## Consequences

Real provider responses can now produce validated conversation response
artifacts when the provider returns bounded `response_text`.

Malformed, ambiguous, authority-bearing, or partially structured invalid
responses still fail closed.

## Status

`PROVIDER_RESPONSE_CONTRACT_ALIGNMENT_STATUS = READY`
