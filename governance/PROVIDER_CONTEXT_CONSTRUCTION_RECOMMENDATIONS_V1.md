# Provider Context Construction Recommendations V1

Status: analysis-only recommendations.

## Recommendation 1

Rerun a small post-connectivity conversational probe that includes:

- `Explain provider boundaries.`
- `Explain worker execution.`
- `Explain authorization.`
- `Summarize recent progress.`
- `What can AiGOL do today?`

Record provider prompt, provider response, normalized response, final AiGOL response, and replay reconstruction.

## Recommendation 2

Measure provider prompt context explicitly before any fix.

Required fields to measure:

- human prompt;
- provider payload input;
- dropped request keys;
- whether AiGOL identity appears;
- whether governance purpose appears;
- whether provider role appears;
- whether replay purpose appears;
- whether worker authority boundaries appear.

## Recommendation 3

Do not treat irrelevant provider answers as provider malfunction when provider prompt context is minimal.

The Platform Log example shows OpenAI answered the prompt it received. The failure is that the provider did not receive enough AiGOL-specific context.

## Recommendation 4

Separate provider connectivity from provider usefulness.

`REAL_OPENAI_CONNECTIVITY_STATUS = READY` proves API communication. It does not prove AiGOL-specific context construction.

## Recommendation 5

Keep the next action measurement-only until the post-connectivity context probe is captured in replay.

No architecture, governance, replay, worker, or provider redesign is required to certify the current gap.

