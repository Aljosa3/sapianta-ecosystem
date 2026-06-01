# FOURTH_REAL_CONVERSATIONAL_USAGE_COMPARISON_V1

## Quantitative Comparison

| Metric | Second epoch | Third epoch | Fourth epoch |
| --- | ---: | ---: | ---: |
| Total prompts | 50 | 50 | 50 |
| Successful responses | 6 | 6 | 16 |
| Fail-closed or non-conversation outcomes | 44 | 44 | 34 |
| Success rate | 12% | 12% | 32% |
| Self-resolution responses | 6 | 6 | 9 |
| Provider-assisted final responses | 0 | 0 | 7 |
| Replay-visible provider responses | 0 | 35 | 37 |
| Conversation-stage provider responses | 0 | 8 | 8 |
| Worker invocations | 0 | 0 | 0 |
| Execution requests | 0 | 0 | 0 |

## Impact Assessment

The provider response acceptance refinement materially improved conversational
coverage:

```text
success_rate_delta_from_baseline = +20 percentage points
responses_created_delta_from_baseline = +10
```

## Prompts Newly Succeeding Compared To Third Epoch

| Prompt | Fourth source | Quality |
| --- | --- | --- |
| How does AiGOL work? | SELF_RESOLUTION | High |
| Explain authorization. | PROVIDER_ASSISTED | High |
| Explain fail closed behavior. | PROVIDER_ASSISTED | High |
| Summarize recent progress. | PROVIDER_ASSISTED | Evidence-limited |
| Can AiGOL summarize progress? | PROVIDER_ASSISTED | High |
| Explain. | PROVIDER_ASSISTED | Mixed |
| Summarize operation history. | PROVIDER_ASSISTED | Evidence-limited |
| How does AiGOL prevent provider authority? | SELF_RESOLUTION | High |
| How does AiGOL preserve worker isolation? | SELF_RESOLUTION | High |
| Explain AiGOL in Slovenian. | PROVIDER_ASSISTED | High |

## Still Failing Categories

| Category | Count | Dominant evidence |
| --- | ---: | --- |
| Classification normalization failure | 29 | `human_prompt is required` |
| Provider unavailable | 3 | `OpenAI provider unavailable` |
| Authority text validation | 1 | `provider conversation response contains authority-bearing text` |
| Non-conversation routing | 1 | `CONSTITUTIONAL_MEMORY_CONSULTATION` |
