# Provider Context Construction Failure Analysis V1

Status: failure analysis.

## Failure Classes

| Class | Count in second 50-prompt epoch | Evidence |
| --- | ---: | --- |
| `CONTEXT_LOSS` | 0 proven epoch failures | No provider responses were received in the epoch, so context loss did not produce a replayed failed provider answer there. |
| `PROMPT_AMBIGUITY` | 1 externally observed example | `Explain provider boundaries.` is ambiguous without AiGOL context; operator-supplied Platform Log shows generic professional/healthcare interpretation. |
| `CLASSIFICATION_FAILURE` | 30 | Prompt-level classification failed and provider-assisted classification failed closed. |
| `ROUTING_FAILURE` | 0 primary | Routing failed only where classification had already failed; successful classifications routed. |
| `PROVIDER_FAILURE` | 40 | 30 provider-assisted classification failures plus 10 provider activation failures cite `OpenAI provider unavailable`. |
| `NORMALIZATION_FAILURE` | 3 | Response validation rejected self-resolved authority-related explanations. |

## Poor Answer Cause: `Explain provider boundaries.`

Observed provider prompt:

```text
Explain provider boundaries.
```

Information missing from the provider prompt:

- the product is AiGOL;
- AiGOL is constitutional AI execution governance infrastructure;
- providers are proposal-only;
- providers do not govern;
- providers do not authorize;
- providers do not execute workers;
- replay records provider evidence;
- worker execution requires governed authorization;
- the desired answer concerns AiGOL provider boundaries, not healthcare or professional-service boundaries.

Cause classification:

```text
CONTEXT_LOSS
PROMPT_AMBIGUITY
```

Not supported as cause by available evidence:

```text
PROVIDER_FAILURE
ROUTING_FAILURE
NORMALIZATION_FAILURE
```

## Why Context Loss Happens

`OpenAIProviderAdapter` receives structured request objects but converts them into a minimal OpenAI payload by extracting one text field.

The following fields are lost before provider invocation:

- `semantic_task`;
- `prompt_id`;
- `human_request_reference`;
- `allowed_destinations`;
- `intent_destination`;
- `deterministic_failure_reason`;
- `self_resolution_status`;
- `self_resolution_reason`;
- authority flags;
- replay references;
- constitutional/product context.

## Can The Provider Answer Correctly From Raw Prompt Alone?

For direct generic prompts like the connectivity proof prompt: yes.

For AiGOL-specific prompts that do not explicitly mention AiGOL context: no.

For `Explain provider boundaries.`, the provider cannot infer from the prompt alone that `provider` means AiGOL's bounded LLM provider role.

