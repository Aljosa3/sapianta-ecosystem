# PROVIDER_RESPONSE_ACCEPTANCE_CONTRACT_REFINEMENT_ADR_V1

## Status

Accepted.

## Context

`PROVIDER_RESPONSE_ALIGNMENT_FAILURE_ANALYSIS_V1` found that
`THIRD_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` produced 35 replay-visible provider
responses but zero provider-assisted final responses.

Observed rejection causes:

- 27 classification contract mismatches caused by missing
  `suggested_destination`;
- 8 conversation response rejections caused by explanatory authority vocabulary.

Provider responses were mostly AiGOL-relevant and proposal-only.

## Decision

Refine provider response acceptance contracts without transferring authority to
providers.

Provider-assisted classification now accepts either:

- structured provider suggestions with `suggested_destination`,
  `classification_reasoning`, and `confidence`; or
- unambiguous provider explanatory text that AiGOL can deterministically
  normalize into a valid destination.

Conversation response validation now rejects direct authority claims while
allowing explanatory vocabulary about authority boundaries.

## Consequences

Semantically correct, constitutionally safe provider responses can now become
valid AiGOL artifacts.

Ambiguous destination evidence, invalid destinations, authority claims,
authority-bearing fields, worker execution instructions, and replay mutation
requests still fail closed.

This decision does not grant providers governance, routing, execution, worker,
or replay authority.

## Certification

```text
PROVIDER_RESPONSE_ACCEPTANCE_CONTRACT_REFINEMENT_STATUS = READY
```
