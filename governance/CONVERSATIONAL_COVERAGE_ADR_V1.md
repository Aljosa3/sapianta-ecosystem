# Conversational Coverage ADR V1

Status: accepted.

## Context

`REAL_OPENAI_CONNECTIVITY_PROOF_V1` proves that AiGOL can communicate with the OpenAI API.

`SECOND_REAL_CONVERSATIONAL_USAGE_EPOCH_V1` measured 50 real prompts through `aigol prompt submit` and produced only 6 responses.

The question is why conversational coverage remained low.

## Decision

Classify conversational coverage analysis as:

```text
CONVERSATIONAL_COVERAGE_STATUS = READY_WITH_GAPS
```

## Basis

Replay evidence is sufficient to explain the second epoch:

- 30 prompts stopped at intent classification;
- 10 prompts stopped at provider activation;
- 3 prompts stopped at response validation;
- 1 prompt was classified as non-conversation;
- 6 prompts succeeded by deterministic self-resolution.

Replay evidence is not sufficient to certify post-connectivity conversational coverage, because the same 50 prompts have not been rerun after real OpenAI connectivity was proven.

## Consequence

The correct next step is measurement, not redesign.

The same 50-prompt suite should be rerun with live OpenAI available, and the resulting stop-point distribution should be compared to this analysis.

## Rejected Alternatives

Do not infer broad conversational readiness from one successful OpenAI connectivity proof.

Do not infer provider failure from architecture now that OpenAI connectivity is proven.

Do not redesign providers, governance, replay, routing, or workers based on the second epoch alone.

Do not hide the fact that the measured epoch had zero provider invocations and zero provider responses.

