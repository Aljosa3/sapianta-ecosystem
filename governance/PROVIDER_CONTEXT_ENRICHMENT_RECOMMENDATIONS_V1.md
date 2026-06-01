# Provider Context Enrichment Recommendations V1

Status: review-only recommendations.

## Recommendation 1

Use the minimal context model as the candidate for future measurement.

Do not use full constitutional documents, full governance files, or full project history as provider prompt context.

## Recommendation 2

Measure before and after with the same prompts.

Minimum probe set:

- `Explain provider boundaries.`
- `Explain worker execution.`
- `Explain authorization.`
- `Explain replay.`
- `What can AiGOL do today?`
- `Why should I trust AiGOL results?`

## Recommendation 3

Keep context provider-neutral.

The same context must work for OpenAI, Claude, Gemini, and local providers without provider-specific tuning.

## Recommendation 4

Preserve proposal-only provider semantics.

Any future context must explicitly preserve:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Recommendation 5

Do not claim context enrichment alone solves conversational coverage.

It may improve semantic relevance after provider invocation, but coverage also depends on:

- provider availability;
- classification coverage;
- routing;
- validation;
- replay/evidence access;
- current status evidence.

## Recommendation 6

If implemented later, record context as replay-visible evidence.

Provider context should be reconstructable alongside:

- human prompt;
- intent classification;
- routing destination;
- provider prompt;
- provider response;
- normalized response;
- final AiGOL response.

