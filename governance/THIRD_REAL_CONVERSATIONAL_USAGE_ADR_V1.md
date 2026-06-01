# THIRD_REAL_CONVERSATIONAL_USAGE_ADR_V1

## Status

Accepted.

## Context

`SECOND_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` measured 50 prompts and produced:

```text
responses_created = 6
fail_closed_responses = 44
success_rate = 12%
```

Since that epoch, AiGOL has proven real OpenAI connectivity and implemented a
minimal provider context capsule.

The question for this epoch is whether the capsule materially improved real
conversational usefulness through the normal CLI path.

## Decision

Certify `THIRD_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` as an evidence-complete
operational measurement with gaps:

```text
THIRD_REAL_CONVERSATIONAL_USAGE_STATUS = READY_WITH_GAPS
```

The epoch may claim:

- OpenAI provider responses were replay-visible in the third epoch;
- the minimal context capsule improved provider-side AiGOL relevance;
- final conversational coverage did not improve over the 12% baseline;
- fail-closed constitutional boundaries remained intact.

The epoch may not claim:

- conversational coverage is improved;
- provider-assisted final responses are working;
- classification and normalization gaps are solved;
- providers have any governance, worker, execution, or replay authority.

## Consequences

The next improvement should focus on provider output contract alignment and
safe response validation, not on provider replacement or broad architecture
redesign.

The minimal context capsule remains useful, but context enrichment alone is not
sufficient to improve final conversational success.
