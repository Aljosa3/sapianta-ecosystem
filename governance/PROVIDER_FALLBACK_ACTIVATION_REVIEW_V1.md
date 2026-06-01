# PROVIDER_FALLBACK_ACTIVATION_REVIEW_V1

## Status

`PROVIDER_FALLBACK_ACTIVATION_STATUS = READY_WITH_GAPS`

## Purpose

This milestone reviews why `SECOND_REAL_CONVERSATIONAL_USAGE_EPOCH_V1`
reported:

```text
provider_used = 0
success_rate = 12%
unclassified_prompts = 30
```

even though provider-assisted intent classification and provider-assisted
conversation runtime already exist.

This is review-only.

It introduces no runtime changes, providers, workers, governance layers,
orchestration, planning, or authority.

## Reviewed Runtime Surfaces

Reviewed:

- `aigol/runtime/prompt_to_conversation_integration.py`
- `aigol/runtime/provider_assisted_intent_classification.py`
- `aigol/runtime/provider_assisted_conversation_runtime.py`
- `aigol/provider/provider_runtime.py`
- `aigol/provider/providers/openai_provider.py`
- `aigol/cli/aigol_cli.py`

## Review Evidence

Controlled prompts executed:

```text
What is AiGOL?
Explain worker execution.
Kaj je namen AiGOL?
```

Observed:

- `What is AiGOL?` resolved through self-resolution and correctly skipped
  provider fallback.
- `Explain worker execution.` classified as `CONVERSATION`, reached provider
  conversation fallback, and failed closed with `OpenAI provider unavailable`.
- `Kaj je namen AiGOL?` failed deterministic prompt classification, entered the
  provider-assisted conversation path, and failed closed with
  `OpenAI provider unavailable`.

## Question Answers

### 1. Why Was `provider_used = 0`?

Because successful results were all self-resolution results, and provider
fallback attempts failed closed before a successful provider-assisted response
could be validated.

The CLI reports `provider_used = True` only when a provider suggestion becomes a
validated successful response. Failed provider attempts currently surface as:

```text
provider_used = False
provider_invoked = False
response_status = FAILED_CLOSED
```

### 2. Was Provider Fallback Reached?

Yes.

Provider fallback was reached for at least two paths:

- unresolved conversation response after a successful `CONVERSATION`
  classification;
- provider-assisted intent classification after deterministic classification
  failed.

### 3. If Reached, Why Was Provider Not Invoked?

The provider runtime attempted to create provider evidence but failed closed.

Replay for `Explain worker execution.` includes:

```text
conversation_response/provider_conversation_response/000_provider_proposal_created.json
```

with:

```text
event_type = FAILED_CLOSED
failure_reason = OpenAI provider unavailable
provider_invoked = false
```

The provider boundary records failed provider availability as not invoked.

### 4. Is Provider Configured?

Partially.

`prompt_to_conversation_integration.py` creates a default OpenAI provider
registry and adapter:

```text
openai_provider_metadata(status=AVAILABLE)
OpenAIProviderAdapter()
```

The adapter expects `OPENAI_API_KEY` or an explicitly injected API key/client.

### 5. Is Provider Available?

Operationally, no.

The reviewed epoch and controlled prompt showed:

```text
OpenAI provider unavailable
```

Therefore the fallback path exists, but the real provider was not available in
the current runtime environment.

### 6. Is Provider Invocation Gated By A Condition That Never Becomes True?

No.

The provider fallback condition can become true.

Provider fallback is gated by:

- deterministic intent classification failure, for provider-assisted intent;
- unresolved self-resolution, for provider-assisted conversation response.

Both conditions occurred during review.

### 7. Is Provider Fallback Connected To Human Prompt Flow?

Yes, but with reporting gaps.

`aigol prompt submit` calls `submit_prompt_to_conversation(...)`, which calls
`run_provider_assisted_conversation(...)`, which calls
`classify_intent_with_provider_assistance(...)`.

The connection exists.

The top-level output currently hides attempted provider fallback when provider
failure occurs.

### 8. Can An Unclassified Prompt Ever Trigger Provider Invocation?

Yes, by entering provider-assisted intent classification.

However, if the real provider is unavailable, the unclassified prompt fails
closed before a validated final classification exists.

## Final Classification

```text
PROVIDER_FALLBACK_ACTIVATION_STATUS = READY_WITH_GAPS
```

Provider fallback is connected and reachable.

The gap is operational provider availability and top-level visibility of failed
provider fallback attempts.
