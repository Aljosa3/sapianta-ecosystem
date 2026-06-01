# Minimal Provider Context Capsule V1

Status: implemented with controlled validation.

Final classification:

```text
MINIMAL_PROVIDER_CONTEXT_CAPSULE_STATUS = READY_WITH_GAPS
```

## Purpose

`MINIMAL_PROVIDER_CONTEXT_CAPSULE_V1` adds a provider-neutral AiGOL identity capsule immediately before provider invocation so provider requests carry enough context to interpret AiGOL-specific prompts.

This implementation preserves the existing provider path.

## Scope

Implemented:

- provider-neutral context capsule for provider-assisted intent classification;
- provider-neutral context capsule for provider-assisted conversation response generation;
- provider-facing `prompt` field containing the capsule and original human prompt;
- replay-visible structured `context_capsule`;
- tests comparing raw prompt behavior with capsule-enriched behavior.

Not modified:

- replay architecture;
- governance architecture;
- worker architecture;
- provider selection;
- authorization model;
- provider registry;
- OpenAI-specific behavior.

## Capsule Text

```text
AiGOL context:
AiGOL is a constitutional AI execution governance system.
LLM providers are proposal-only sources; they do not govern, authorize, execute, mutate replay, or invoke workers.
AiGOL governs; workers execute only after governed authorization; replay records evidence.
Answer in the AiGOL/SAPIANTA governance domain unless the user explicitly asks for another domain.
Use the human prompt as the question; provide explanatory text only.

Human prompt:
<original human prompt>
```

## Structured Capsule

The request also carries a replay-visible `context_capsule` object:

```json
{
  "context_capsule_version": "MINIMAL_PROVIDER_CONTEXT_CAPSULE_V1",
  "context_type": "PROVIDER_NEUTRAL_AIGOL_IDENTITY_CAPSULE",
  "provider_neutral": true,
  "authority_transfer": false
}
```

## Implementation Points

The capsule is injected where provider request objects are already constructed:

- `aigol/runtime/provider_assisted_intent_classification.py`
- `aigol/runtime/provider_assisted_conversation_runtime.py`

For OpenAI, the existing adapter already prefers `request["prompt"]`, so the same provider path is used and no OpenAI-specific branch was added.

## Constitutional Preservation

The capsule preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The capsule explicitly states that providers do not govern, authorize, execute, mutate replay, or invoke workers.

