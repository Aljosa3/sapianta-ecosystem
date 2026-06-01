# PROVIDER_FALLBACK_ACTIVATION_RECOMMENDATIONS_V1

## Recommendation

Do not redesign the provider fallback architecture.

The current architecture is connected and reachable.

## Priority 1: Improve Fallback Visibility

Add operator-visible fields in a future implementation:

- `provider_fallback_attempted`
- `provider_fallback_stage`
- `provider_failure_reason`
- `provider_replay_reference`

This should not change provider authority.

It should only expose existing replay-visible evidence.

## Priority 2: Validate Provider Configuration

Before additional conversational usage epochs, add or run a provider readiness
check that answers:

- Is `OPENAI_API_KEY` present?
- Can the provider adapter return a valid proposal envelope?
- Does provider response shape match the semantic suggestion model?
- Is the provider replay evidence reconstructable?

## Priority 3: Use A Governed Test Provider Harness For Local Epochs

For local usage epochs without network or credentials, use an injected
proposal-only test adapter or certified local provider harness.

This would allow provider fallback behavior to be evaluated without weakening
authority boundaries.

## Priority 4: Preserve Fail-Closed Semantics

Provider unavailability must continue to fail closed.

Do not introduce:

- silent fallback generation;
- raw provider response to human;
- provider authority;
- worker invocation;
- retries;
- orchestration.

## Priority 5: Improve Failure Explanation

Prompt output should explain:

```text
Provider fallback was attempted but failed because the provider was unavailable.
```

This is materially better than only:

```text
provider_used = False
```

## Final Recommendation

Next milestone should be a compatibility hardening milestone:

```text
PROVIDER_FALLBACK_VISIBILITY_AND_CONFIGURATION_CHECK_V1
```

not a new provider architecture.
