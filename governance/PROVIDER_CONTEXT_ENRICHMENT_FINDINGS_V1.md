# Provider Context Enrichment Findings V1

Status: review findings.

## Finding 1: Current Provider Prompts Are Under-Contextualized

The current OpenAI adapter sends a single extracted string as `payload.input`.

For AiGOL-specific questions, this preserves the literal prompt but loses the operating domain.

## Finding 2: The Missing Context Is Small

The missing context does not need full constitutional memory, full governance documents, full project history, or a large prompt.

The necessary information is:

- what AiGOL is;
- what providers are allowed to be;
- what providers are not allowed to be;
- what workers are;
- what replay is for;
- which domain the answer should use.

## Finding 3: The Context Can Be Provider-Neutral

The proposed context does not mention OpenAI-specific APIs, model behavior, SDKs, or provider-specific formatting.

It can apply equally to:

- OpenAI;
- Claude;
- Gemini;
- local providers.

## Finding 4: The Context Preserves Authority Separation

The context states that providers are proposal-only sources.

It does not ask providers to govern, authorize, execute, route, mutate replay, or invoke workers.

## Finding 5: The `Explain provider boundaries` Failure Is Context-Sensitive

Without AiGOL context, `provider boundaries` is ambiguous.

The provider cannot know whether `provider` means:

- healthcare provider;
- professional-service provider;
- cloud provider;
- AiGOL LLM provider.

The smallest context that changes the answer is:

```text
AiGOL is a constitutional AI execution governance system. LLM providers are proposal-only and never govern, authorize, execute, mutate replay, or invoke workers.
```

## Finding 6: Context Enrichment Can Improve Several Question Types

Provider-neutral context can plausibly improve:

- governance questions;
- replay questions;
- AiGOL explanation questions;
- architecture questions;
- operational boundary questions.

It cannot be certified as sufficient for:

- current status;
- recent progress;
- last-operation evidence;
- replay ledger summaries.

Those require available evidence, not only semantic framing.

## Finding 7: Significant Coverage Improvement Is Not Yet Proven

The review identifies a likely high-impact improvement, but coverage improvement requires replay-visible measurement after enrichment.

