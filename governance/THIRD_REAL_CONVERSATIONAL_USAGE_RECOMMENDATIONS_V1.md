# THIRD_REAL_CONVERSATIONAL_USAGE_RECOMMENDATIONS_V1

## Status

Recommendations derived from third epoch evidence.

## Recommendation 1: Align Provider-Assisted Classification Output With Its Contract

Priority:

```text
HIGHEST
```

Evidence:

```text
27 / 44 failures = CLASSIFICATION_FAILURE
dominant reason = suggested_destination is required
```

Recommended next work:

Review the provider-assisted intent classification prompt and normalization
contract so provider assistance returns the required structured classification
fields instead of only explanatory text.

Constraint:

Do not grant provider authority. Provider classification remains advisory and
must remain replay-visible and fail-closed.

## Recommendation 2: Refine Authority-Bearing Text Validation For Explanations

Priority:

```text
HIGH
```

Evidence:

```text
11 / 44 failures = NORMALIZATION_FAILURE
dominant reason = provider conversation response contains authority-bearing text
```

Recommended next work:

Differentiate explanatory statements about governance authority from actual
authority claims, worker invocation, authorization, or execution requests.

Constraint:

The runtime must continue to reject provider outputs that authorize, execute,
mutate replay, invoke workers, or claim governance authority.

## Recommendation 3: Preserve The Minimal Context Capsule

Priority:

```text
HIGH
```

Evidence:

The capsule produced replay-visible AiGOL-specific provider responses for
formerly generic prompts such as `Explain provider boundaries.`

Recommended next work:

Keep the capsule provider-neutral and minimal. Do not expand it into full
constitutional memory or project history.

## Recommendation 4: Add Replay-Backed Evidence Availability For Status Questions

Priority:

```text
MEDIUM
```

Evidence:

Several prompts ask for recent progress, last operation, current status, or
last replay evidence. Provider context alone cannot answer these authoritatively
without replay-backed facts.

Recommended next work:

Analyze how conversational response creation can access already-recorded replay
evidence without changing replay authority or allowing provider-led replay
mutation.

## Recommendation 5: Treat Provider Availability As A Residual Operational Risk

Priority:

```text
MEDIUM
```

Evidence:

Five prompts failed because the OpenAI provider was unavailable during the
epoch.

Recommended next work:

Keep provider unavailability fail-closed and replay-visible. Do not compensate
by inventing responses or weakening governance boundaries.
