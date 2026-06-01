# Conversational Coverage Analysis V1

Status: evidence-based analysis of `SECOND_REAL_CONVERSATIONAL_USAGE_EPOCH_V1`.

Final classification:

```text
CONVERSATIONAL_COVERAGE_STATUS = READY_WITH_GAPS
```

## Scope

This analysis measures why the 50-prompt conversational epoch had low coverage.

It does not redesign architecture, governance, replay, providers, routing, or validation.

## Evidence Sources

- `governance/SECOND_REAL_CONVERSATIONAL_USAGE_EPOCH_V1.md`
- `governance/SECOND_REAL_CONVERSATIONAL_USAGE_LOG_V1.md`
- `governance/SECOND_REAL_CONVERSATIONAL_USAGE_CERTIFICATION.json`
- Replay root: `/tmp/aigol_second_conversation_epoch`
- Runtime source: `aigol/runtime/prompt_to_conversation_integration.py`
- Runtime source: `aigol/runtime/provider_assisted_conversation_runtime.py`
- Provider connectivity proof: `governance/REAL_OPENAI_CONNECTIVITY_PROOF_V1.md`

## Aggregate Outcome

| Metric | Count | Percent |
| --- | ---: | ---: |
| Prompts submitted | 50 | 100% |
| Responses created | 6 | 12% |
| Fail-closed responses | 44 | 88% |
| Prompt-level classifications succeeded | 20 | 40% |
| Prompt-level classifications failed | 30 | 60% |
| Prompt-level routing succeeded | 20 | 40% |
| Prompt-level routing failed | 30 | 60% |
| Provider proposal artifacts created | 10 | 20% |
| Provider actually invoked | 0 | 0% |
| Provider response received | 0 | 0% |
| Failed before provider response | 44 | 88% |

## Stop Points

| Stop point | Count | Percent of all prompts | Percent of failed prompts |
| --- | ---: | ---: | ---: |
| Success by self-resolution | 6 | 12.0% | n/a |
| Intent classification | 30 | 60.0% | 68.2% |
| Provider activation | 10 | 20.0% | 22.7% |
| Provider response validation | 3 | 6.0% | 6.8% |
| Non-conversation intent | 1 | 2.0% | 2.3% |

## Primary Explanation

The 12% success rate was caused by narrow deterministic self-resolution plus failed provider assistance during the epoch.

The largest measured failure group was 30 prompts that stopped at intent classification. In each case, replay evidence shows provider-assisted classification failed with:

```text
provider-assisted conversation failed closed: OpenAI provider unavailable
```

The second-largest measured failure group was 10 prompts that reached conversation routing but stopped at provider activation. In each case, replay evidence shows provider proposal creation failed with:

```text
OpenAI provider unavailable
```

Three prompts were classified and self-resolved but failed response validation because safe explanatory text was treated as authority-bearing.

## Post-Connectivity Gap

`REAL_OPENAI_CONNECTIVITY_PROOF_V1` falsifies the global hypothesis that OpenAI is not attached.

However, the 50-prompt epoch itself recorded `provider_invoked = 0` and `provider_response_received = 0`. Therefore this analysis can prove where the second epoch failed, but it cannot prove the post-connectivity coverage rate without rerunning the same 50 prompts with live OpenAI available.

## Highest-Impact Next Improvement

The next highest-impact measured action is to rerun the same 50-prompt conversational epoch with the now-proven OpenAI provider available and compare stop points.

If provider availability remains fixed, the expected measured bottleneck to examine next is response validation plus conversational evidence availability for project status, replay history, component-specific explanations, and multilingual prompts.

