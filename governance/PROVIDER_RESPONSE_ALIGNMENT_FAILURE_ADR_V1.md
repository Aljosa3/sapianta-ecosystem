# PROVIDER_RESPONSE_ALIGNMENT_FAILURE_ADR_V1

## Status

Accepted.

## Context

`THIRD_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` showed no final success-rate
improvement over the second epoch:

```text
Second epoch: 6 / 50
Third epoch: 6 / 50
```

However, the third epoch recorded 35 replay-visible provider responses. Several
responses were AiGOL-specific and semantically relevant.

## Decision

Certify the failure analysis as:

```text
PROVIDER_RESPONSE_ALIGNMENT_FAILURE_STATUS = READY_WITH_GAPS
```

The analysis may claim:

- provider responses were returned and replay-visible;
- most returned provider responses were AiGOL/SAPIANTA relevant;
- the dominant rejection was classification contract mismatch;
- the second rejection class was authority-bearing text detection;
- no returned provider response was observed to invoke workers, request
  execution, mutate replay, or carry authority fields.

The analysis may not claim:

- provider responses are always factually correct;
- current-status answers are authoritative without replay-backed evidence;
- validation should be weakened;
- providers should gain governance or execution authority.

## Consequences

The next highest-impact work should focus on response alignment at validation
boundaries:

- structured provider-assisted classification output;
- safe handling of explanatory authority vocabulary;
- replay-backed evidence for status and history prompts.

Provider replacement is not supported by this evidence as the next bottleneck.
