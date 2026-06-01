# FOURTH_REAL_CONVERSATIONAL_USAGE_FINDINGS_V1

## Finding 1: Success Increased Beyond The 12% Baseline

The fourth epoch produced:

```text
responses_created = 16
success_rate = 32%
```

This is a material increase from the second and third epoch baseline:

```text
6 / 50 = 12%
```

## Finding 2: Provider-Assisted Final Responses Are Now Working

The fourth epoch created seven provider-assisted final responses.

New provider-assisted successes:

- `Explain authorization.`
- `Explain fail closed behavior.`
- `Summarize recent progress.`
- `Can AiGOL summarize progress?`
- `Explain.`
- `Summarize operation history.`
- `Explain AiGOL in Slovenian.`

Evidence example:

```text
/tmp/aigol_fourth_conversation_epoch/case_13/AIGOL-HUMAN-PROMPT-34260AD00170/conversation_response
```

## Finding 3: Authority Vocabulary Refinement Had Positive Impact

Several prompts that previously failed after provider response creation now
produced final responses.

The prompt:

```text
Explain authorization.
```

returned a provider-assisted response while preserving:

```text
provider_response_authority = False
worker_invoked = False
execution_requested = False
```

## Finding 4: Classification Normalization Has A New Live Evidence Gap

Twenty-nine failures now share the dominant reason:

```text
provider-assisted conversation failed closed: human_prompt is required
```

This occurred after provider responses were returned. The classification
normalization refinement requires human prompt evidence, but the OpenAI adapter
provider capture records an adapter-level request payload instead of the
original structured provider-assisted classification request.

Evidence example:

```text
/tmp/aigol_fourth_conversation_epoch/case_6/AIGOL-HUMAN-PROMPT-EFFB68CCCFC8/conversation_response/intent_classification/000_provider_intent_governance_validation.json
```

## Finding 5: One Authority Example Still Fails Closed

The prompt:

```text
Explain provider boundaries.
```

still failed because the provider response included an explanatory example with
direct forbidden wording:

```text
I authorize X
```

The runtime rejected it as:

```text
provider conversation response contains authority-bearing text
```

Evidence:

```text
/tmp/aigol_fourth_conversation_epoch/case_12/AIGOL-HUMAN-PROMPT-8987B3838E74/conversation_response
```

## Finding 6: Constitutional Boundaries Remained Intact

Across all prompts:

```text
worker_invoked = False
execution_requested = False
```

No provider response became governance, routing, worker, replay, or execution
authority.
