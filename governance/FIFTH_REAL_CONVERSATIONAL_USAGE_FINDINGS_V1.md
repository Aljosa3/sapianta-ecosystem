# FIFTH_REAL_CONVERSATIONAL_USAGE_FINDINGS_V1

## Finding 1: Prompt Continuity Restoration Had Material Impact

The fifth epoch increased conversational coverage from 32% to 82%.

```text
Fourth epoch responses_created = 16
Fifth epoch responses_created = 41
delta = +25 responses
```

The prior dominant failure:

```text
human_prompt is required
```

did not recur in fifth-epoch observations.

## Finding 2: Provider-Assisted Responses Became The Main Success Path

Final response source distribution:

| Source | Count |
| --- | ---: |
| Provider-assisted final responses | 27 |
| Self-resolution responses | 14 |
| Unavailable | 9 |

Provider-assisted final responses rose from 7 in the fourth epoch to 27 in the
fifth epoch.

## Finding 3: Replay Visibility Was Preserved

Forty prompts produced replay-visible provider responses, and 28 reached
conversation-stage provider response generation.

For accepted provider-assisted responses, replay contains:

- self-resolution attempt evidence;
- provider-assisted conversation start evidence;
- provider response validation evidence;
- provider-assisted conversation response artifact;
- provider-assisted response return evidence.

## Finding 4: Constitutional Boundaries Remained Intact

Across the epoch:

```text
worker_invoked = False
execution_requested = False
provider_response_authority = False
```

Provider output remained proposal evidence only. AiGOL still governed whether
provider output became an accepted conversation response.

## Finding 5: Remaining Failures Are No Longer Dominated By Prompt Evidence Loss

The fifth epoch had 9 unsuccessful outcomes:

| Failure class | Count |
| --- | ---: |
| CLASSIFICATION_FAILURE | 5 |
| NORMALIZATION_FAILURE | 1 |
| PROVIDER_FAILURE | 1 |
| OTHER | 2 |

This is a different bottleneck profile than the fourth epoch, where 29 failures
were caused by missing structured `human_prompt` evidence.

## Finding 6: One Regression Was Observed

`Explain fail closed behavior.` succeeded in the fourth epoch but failed in the
fifth epoch because validation rejected the provider response for
authority-bearing text.

This does not falsify the prompt continuity improvement, but it shows provider
response validation remains sensitive to provider wording.
