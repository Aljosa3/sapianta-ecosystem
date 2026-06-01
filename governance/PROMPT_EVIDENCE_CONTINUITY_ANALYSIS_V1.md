# PROMPT_EVIDENCE_CONTINUITY_ANALYSIS_V1

## Status

`PROMPT_EVIDENCE_CONTINUITY_STATUS = READY_WITH_GAPS`

## Purpose

This artifact traces `human_prompt` evidence continuity for failed operations
in `FOURTH_REAL_CONVERSATIONAL_USAGE_EPOCH_V1`.

This is an evidence-only analysis. It does not modify runtime, providers,
governance, replay, routing, or workers.

## Evidence Scope

Replay root:

```text
/tmp/aigol_fourth_conversation_epoch/
```

Failed or non-conversation outcomes analyzed:

```text
34
```

Dominant fourth-epoch failure:

```text
provider-assisted conversation failed closed: human_prompt is required
```

## Primary Finding

`human_prompt` evidence is not lost from replay.

For all 34 failed or non-conversation outcomes, the original human prompt is
available in:

```text
000_human_prompt_artifact.json
```

For the 29 `human_prompt is required` failures, the prompt is also visible
inside the OpenAI adapter payload:

```text
request.payload.input
```

However, the structured field expected by provider-assisted classification:

```text
request.human_prompt
```

is absent from the provider proposal envelope captured after OpenAI adapter
request transformation.

## Exact Loss Point

The loss point is:

```text
OpenAI adapter provider proposal envelope request construction
```

The original provider-assisted classification request contains structured
AiGOL fields, including `human_prompt`. The OpenAI adapter extracts the prompt,
creates an OpenAI Responses API payload, and records the provider proposal
envelope request as:

```text
provider
model
endpoint
payload
api_key_captured
single_request
streaming
tool_use
function_calling
memory
```

That replay-visible adapter request does not retain:

```text
human_prompt
semantic_task
human_request_reference
allowed_destinations
```

The fourth-epoch classification normalization path then reads the provider
proposal envelope request and fails closed because `human_prompt` is not
available as a structured field.

## Source Evidence

Human prompt creation:

```text
/tmp/aigol_fourth_conversation_epoch/case_6/AIGOL-HUMAN-PROMPT-EFFB68CCCFC8/000_human_prompt_artifact.json
```

Conversation start:

```text
/tmp/aigol_fourth_conversation_epoch/case_6/AIGOL-HUMAN-PROMPT-EFFB68CCCFC8/conversation_response/000_provider_assisted_conversation_started.json
```

Provider proposal request after OpenAI adapter transformation:

```text
/tmp/aigol_fourth_conversation_epoch/case_6/AIGOL-HUMAN-PROMPT-EFFB68CCCFC8/conversation_response/intent_classification/provider_semantic_assistance/000_provider_proposal_created.json
```

Validation failure:

```text
/tmp/aigol_fourth_conversation_epoch/case_6/AIGOL-HUMAN-PROMPT-EFFB68CCCFC8/conversation_response/intent_classification/000_provider_intent_governance_validation.json
```

Implementation source:

```text
aigol/provider/providers/openai_provider.py
aigol/runtime/provider_assisted_intent_classification.py
```

## Reconstructability

The missing prompt can be deterministically reconstructed from existing replay
evidence in all 34 analyzed failed or non-conversation outcomes.

Reconstruction sources:

- `000_human_prompt_artifact.json.artifact.prompt_text`;
- `conversation_response/000_provider_assisted_conversation_started.json.artifact.prompt_text` when conversation path was entered;
- `provider_semantic_assistance/000_provider_proposal_created.json.artifact.request.payload.input` for the 29 classification-normalization failures.

## Final Classification

```text
PROMPT_EVIDENCE_CONTINUITY_STATUS = READY_WITH_GAPS
```

The continuity gap is identified precisely. The prompt remains replay-visible
and reconstructable, but structured prompt evidence is not preserved across the
OpenAI adapter request envelope boundary.
