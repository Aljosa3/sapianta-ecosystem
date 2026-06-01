# PROVIDER_RESPONSE_ACCEPTANCE_CONTRACT_REFINEMENT_V1

## Status

`PROVIDER_RESPONSE_ACCEPTANCE_CONTRACT_REFINEMENT_STATUS = READY`

## Purpose

This milestone refines provider response acceptance contracts so
semantically-correct and constitutionally-safe provider responses can become
valid AiGOL artifacts.

The refinement preserves the constitutional invariant:

```text
LLM proposes. AiGOL governs. Worker executes. Replay records.
```

## Scope

Implemented refinements:

- provider-assisted intent classification may normalize unambiguous explanatory
  provider text into a validated `suggested_destination`;
- conversation response validation distinguishes actual authority claims from
  explanatory authority vocabulary.

Non-goals:

- no provider authority;
- no provider routing authority;
- no provider execution authority;
- no worker invocation from provider output;
- no replay mutation;
- no weakening of fail-closed behavior.

## Classification Contract Refinement

Structured provider suggestions remain accepted only when they provide:

```text
suggested_destination
classification_reasoning
confidence
```

Generic provider text may now be normalized only when AiGOL can determine one
unambiguous valid destination from replay-visible provider evidence and the
human prompt.

Normalized classification evidence uses:

```text
confidence = PROVIDER_TEXT_NORMALIZED
classification_reasoning = deterministically normalized from provider response_text
provider_suggestion_authority = False
```

Ambiguous or invalid destinations still fail closed.

## Conversation Response Contract Refinement

The response validation gate still rejects:

- authority-bearing response fields;
- direct authorization claims;
- direct worker execution instructions;
- dispatch commands;
- replay or memory mutation requests.

It now allows explanatory authority vocabulary when the text is describing
boundaries rather than claiming authority.

Allowed example:

```text
Providers do not have authority to execute.
```

Forbidden example:

```text
I authorize execution.
```

## Implementation References

| Area | Source |
| --- | --- |
| Provider-assisted classification normalization | `aigol/runtime/provider_assisted_intent_classification.py` |
| Conversation authority text validation | `aigol/runtime/provider_assisted_conversation_runtime.py` |
| Classification tests | `tests/test_provider_assisted_intent_classification_v1.py` |
| Conversation tests | `tests/test_provider_assisted_conversation_runtime_v1.py` |
| Prompt integration tests | `tests/test_prompt_to_conversation_integration_v1.py` |

## Verification

Focused validation:

```text
python -m pytest tests/test_provider_assisted_intent_classification_v1.py tests/test_provider_assisted_conversation_runtime_v1.py tests/test_prompt_to_conversation_integration_v1.py
```

Result:

```text
33 passed
```

## Final Classification

```text
PROVIDER_RESPONSE_ACCEPTANCE_CONTRACT_REFINEMENT_STATUS = READY
```
