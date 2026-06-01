# Conversational Coverage Recommendations V1

Status: evidence-based recommendations.

## Recommendation 1

Rerun the same 50-prompt epoch with the now-proven OpenAI provider available.

Rationale: 40 of 44 failures in the measured epoch cite `OpenAI provider unavailable`. The repository now has `REAL_OPENAI_CONNECTIVITY_STATUS = READY`, but the 50-prompt coverage rate has not been remeasured under that condition.

Expected evidence output:

- prompt-level classification count;
- routing count;
- provider invocation count;
- provider response count;
- response validation failures;
- final response count;
- replay reconstruction result.

## Recommendation 2

Measure response validation separately for authority/worker-isolation explanatory prompts.

Rationale: cases 5, 41, and 42 were self-resolved but blocked by validation. This is a proven coverage loss independent of provider connectivity.

## Recommendation 3

Add a replay-visible coverage report for prompt categories.

Rationale: project status, replay history, last-result evidence, component explanations, and multilingual prompts failed, but the current operator-facing failure explanation compresses many cases into provider-unavailable status.

## Recommendation 4

Prioritize conversational evidence availability for current status, recent progress, replay history, and last-result evidence.

Rationale: those prompt categories are central to daily usefulness and repeatedly failed in the epoch.

## Recommendation 5

Do not expand workers, execution surfaces, or autonomous behavior to solve this coverage problem.

Rationale: the epoch failed before worker or execution boundaries. Evidence shows:

```text
worker_invoked = 0
execution_requested = 0
```

The bottleneck is conversational classification, provider availability during the epoch, response validation, and evidence-backed answer availability.

