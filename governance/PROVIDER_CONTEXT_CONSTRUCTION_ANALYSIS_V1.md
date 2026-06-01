# Provider Context Construction Analysis V1

Status: evidence-based provider context construction analysis.

Final classification:

```text
PROVIDER_CONTEXT_CONSTRUCTION_STATUS = READY_WITH_GAPS
```

## Scope

This analysis determines what AiGOL sends to providers and what semantic context is lost before provider invocation.

It does not redesign architecture, governance, replay, providers, workers, routing, or normalization.

## Evidence Sources

- `aigol/runtime/provider_assisted_conversation_runtime.py`
- `aigol/runtime/provider_assisted_intent_classification.py`
- `aigol/provider/providers/openai_provider.py`
- Replay root: `/tmp/aigol_second_conversation_epoch`
- Replay root: `/tmp/real_openai_connectivity_sfnhm8np`
- Operator-supplied OpenAI Platform Log observation for `Explain provider boundaries.`

## Primary Finding

AiGOL builds structured provider request objects containing some governance metadata, but `OpenAIProviderAdapter` sends only a single extracted string as the OpenAI `input`.

The adapter extraction rule is:

```text
use request["prompt"], request["human_prompt"], or request["request"]
```

The provider payload is then:

```json
{
  "model": "gpt-5.1",
  "input": "<extracted prompt string>",
  "stream": false
}
```

Therefore provider-side context construction is currently minimal. The original human prompt survives, but AiGOL-specific context usually does not.

## Context Preservation Classification

| Surface | Context survival | Evidence |
| --- | --- | --- |
| Human prompt text | `FULL_CONTEXT` | `human_prompt` is preserved and extracted as provider `input`. |
| Prompt id / replay id | `NO_CONTEXT` to OpenAI | Present in AiGOL request object, not included in OpenAI payload. |
| Intent destination | `NO_CONTEXT` to OpenAI | Present in conversation provider request object, not included in OpenAI payload. |
| Self-resolution status/reason | `NO_CONTEXT` to OpenAI | Present in conversation provider request object, not included in OpenAI payload. |
| Allowed destinations | `NO_CONTEXT` to OpenAI | Present in provider-assisted classification request, not included in OpenAI payload. |
| Provider authority flags | `NO_CONTEXT` to OpenAI | Present in AiGOL request object, not included in OpenAI payload. |
| AiGOL identity | `NO_CONTEXT` unless human prompt says it | Not added by adapter. |
| Governance purpose | `NO_CONTEXT` unless human prompt says it | Not added by adapter. |
| Replay purpose | `NO_CONTEXT` unless human prompt says it | Not added by adapter. |
| Constitutional constraints | `NO_CONTEXT` | Not added by adapter. |
| Worker authority boundaries | `NO_CONTEXT` unless human prompt says it | Not added by adapter. |
| Project/domain context | `NO_CONTEXT` unless human prompt says it | Not added by adapter. |

## Example: Explain Provider Boundaries

Replay evidence from `/tmp/aigol_second_conversation_epoch/case_12`:

```text
Human Prompt:
Explain provider boundaries.

Intent Classification:
CONVERSATION

Routing Destination:
CONVERSATION

AiGOL provider request object:
semantic_task = conversation_response_suggestion
human_prompt = Explain provider boundaries.
intent_destination = CONVERSATION
self_resolution_status = UNRESOLVED
self_resolution_reason = deterministic self-resolution insufficient
provider_authority = false
response_authority = false
execution_authority = false

Provider Prompt if OpenAI adapter is invoked:
Explain provider boundaries.

Provider Response in replay:
None. The epoch failed closed before provider invocation.

Final AiGOL Response in replay:
FAILED_CLOSED: OpenAI provider unavailable
```

Operator-supplied OpenAI Platform Log observation:

```text
Human Prompt:
Explain provider boundaries.

Provider Prompt:
Explain provider boundaries.

Provider Response:
Explanation of professional/healthcare provider boundaries.
```

This observation is consistent with the adapter source: the provider receives the raw prompt without AiGOL context.

## Is Context Construction The Primary Bottleneck?

For the second 50-prompt epoch: not proven as the primary bottleneck.

Measured epoch bottlenecks were:

- `PROVIDER_FAILURE`: 40 prompts;
- `NORMALIZATION_FAILURE`: 3 prompts;
- non-conversation routing boundary: 1 prompt;
- successful self-resolution: 6 prompts.

For post-connectivity provider quality: context construction is a proven risk and a plausible cause of irrelevant provider answers, because real provider prompts are raw or near-raw strings.

## Classification Rationale

`READY_WITH_GAPS` because:

- code proves the transformation rule;
- replay proves the provider request objects;
- live connectivity replay proves OpenAI payload shape;
- operator-supplied Platform Log observation supports raw prompt forwarding;
- repository replay does not contain a full successful `Explain provider boundaries` provider-response-to-final-response chain after connectivity was fixed.

