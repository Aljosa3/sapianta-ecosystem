# Minimal Provider Context Capsule Findings V1

Status: controlled validation findings.

## Finding 1: Provider Requests Now Carry Context

Provider-assisted request objects now include:

- `prompt`: capsule-enriched provider-facing text;
- `context_capsule`: structured replay-visible capsule;
- original `human_prompt`;
- existing semantic task and authority fields.

## Finding 2: The Existing OpenAI Path Is Preserved

The OpenAI adapter already extracts `request["prompt"]` when present.

No OpenAI-specific behavior was introduced.

## Finding 3: Same-Prompt Controlled Comparison Improved Relevance

Controlled prompt set:

- `Explain provider boundaries.`
- `Explain worker execution.`
- `Explain authorization.`
- `Explain fail closed behavior.`
- `Summarize operation history.`
- `Explain AiGOL in Slovenian.`

Measured in the local context-sensitive provider harness:

| Metric | Without capsule | With capsule |
| --- | ---: | ---: |
| Prompt set size | 6 | 6 |
| Generic/non-AiGOL interpretation | 6 | 0 |
| AiGOL-specific interpretation | 0 | 6 |
| Provider-assisted response created | 0 measured in raw baseline harness | 6 |
| Provider authority introduced | 0 | 0 |
| Worker invoked | 0 | 0 |
| Execution requested | 0 | 0 |

## Finding 4: `Explain provider boundaries.` Is Disambiguated

Without capsule, the controlled provider returns a professional/provider-boundary style response.

With capsule, the same prompt returns an AiGOL-specific provider-boundary response.

## Finding 5: Live A/B Evidence Remains A Gap

This milestone validates the capsule through deterministic tests and controlled provider comparison.

It does not yet include a live OpenAI same-prompt A/B replay suite.

Therefore the status is `READY_WITH_GAPS`.

