# PROVIDER_FALLBACK_ACTIVATION_FINDINGS_V1

## Findings Summary

Provider fallback is connected.

Provider fallback is reachable.

Provider fallback did not produce successful usage in the second conversational
epoch because the default real provider was unavailable.

## Finding 1: Self-Resolution Correctly Skips Provider

Prompt:

```text
What is AiGOL?
```

Result:

```text
response_status = PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED
response_source = SELF_RESOLUTION
provider_used = False
```

This is correct behavior. Provider fallback should not activate when
self-resolution succeeds.

## Finding 2: Conversation Response Fallback Is Reached

Prompt:

```text
Explain worker execution.
```

Result:

```text
classification_destination = CONVERSATION
routing_destination = CONVERSATION
response_status = FAILED_CLOSED
failure_reason = OpenAI provider unavailable
```

Replay contained provider conversation response evidence under:

```text
conversation_response/provider_conversation_response/
```

This proves fallback was reached.

## Finding 3: Intent Fallback Is Reached For Unclassified Prompts

Prompt:

```text
Kaj je namen AiGOL?
```

Result:

```text
classification_destination = None
routing_destination = None
response_status = FAILED_CLOSED
failure_reason = provider-assisted conversation failed closed: OpenAI provider unavailable
```

This indicates deterministic classification failed and provider-assisted intent
classification attempted fallback, but could not complete because the provider
was unavailable.

## Finding 4: Provider Availability Is The Main Activation Blocker

The default provider path uses:

```text
OpenAIProviderAdapter()
```

The adapter requires a real OpenAI API key and successful HTTP response.

In the reviewed environment, provider calls failed closed with:

```text
OpenAI provider unavailable
```

## Finding 5: Top-Level Provider Usage Is A Success Indicator, Not Attempt Indicator

The current prompt output uses:

```text
provider_used = False
provider_invoked = False
```

for failed provider fallback.

This is not wrong under the existing provider runtime semantics, but it is
operator-confusing because it hides whether fallback was attempted.

## Finding 6: No Authority Boundary Was Violated

Failed provider fallback did not:

- execute;
- authorize;
- invoke workers;
- mutate memory;
- mutate replay outside append-only evidence.

Fail-closed behavior preserved the constitutional invariant.

## Final Finding

Provider fallback is not `NOT_CONNECTED`.

It is connected but operationally blocked by provider availability and by weak
operator visibility into failed provider attempts.
