# SECOND_REAL_CONVERSATIONAL_USAGE_RECOMMENDATIONS_V1

## Primary Recommendation

Prioritize conversational answer coverage before adding new workers or new
architecture.

## Recommended Next Step

Implement a governed conversational self-resolution expansion for:

- current status;
- recent progress;
- last operation;
- replay ledger/report;
- failure explanation;
- component explanation;
- provider requirement explanation;
- unsupported prompt explanation.

This should reuse existing replay, reporting, and explanation surfaces.

## Provider Recommendation

Provider fallback should be tested with a live, configured provider or a
governed local provider harness.

The epoch shows provider fallback is necessary for broad natural-language and
multilingual coverage, but unavailable provider behavior currently dominates
failures.

## Validation Recommendation

Refine response validation so safe explanatory text containing words like
`authority`, `authorized`, or `worker` is not blocked merely because the words
appear.

The validator should reject imperative authority-bearing claims, not all
authority-related explanations.

## Replay Recommendation

Connect conversation prompts to replay-backed operation explanation for prompts
such as:

- `What happened in the last operation?`
- `Why did an operation fail?`
- `What evidence supports the last result?`

## Do Not Prioritize

This epoch does not justify:

- new workers;
- new governance layers;
- orchestration;
- planning;
- autonomous dispatch;
- broad architecture redesign.

## Final Recommendation

The next bottleneck is:

```text
Conversational evidence coverage
```

with provider availability as the second bottleneck.
