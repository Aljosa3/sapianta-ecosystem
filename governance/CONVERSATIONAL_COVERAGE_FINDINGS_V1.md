# Conversational Coverage Findings V1

Status: measured findings from replay evidence.

## Finding 1: Coverage Was Low

The epoch created 6 responses from 50 prompts.

```text
success_rate = 12%
fail_closed_rate = 88%
```

Evidence: `SECOND_REAL_CONVERSATIONAL_USAGE_CERTIFICATION.json`.

## Finding 2: Successful Prompts Were Narrow

Successful prompts:

- `What is AiGOL?`
- `What is AiGOL? Explain simply.`
- `Explain replay.`
- `Explain governance.`
- `Can AiGOL explain governance?`
- `Can AiGOL explain replay?`

All six succeeded by deterministic self-resolution.

Evidence: `SECOND_REAL_CONVERSATIONAL_USAGE_LOG_V1.md` and replay artifacts under `/tmp/aigol_second_conversation_epoch/case_1`, `case_2`, `case_3`, `case_4`, `case_19`, and `case_21`.

## Finding 3: Most Failures Stopped At Intent Classification

30 prompts failed at intent classification.

Observed examples:

- `What can AiGOL do today?`
- `Kaj zna AiGOL?`
- `What happened in the last operation?`
- `Read the replay ledger.`
- `What is conversation runtime?`
- `Give me current status.`

Replay evidence shows provider-assisted classification was attempted inside the conversation runtime and failed closed because OpenAI was unavailable during the epoch.

## Finding 4: Ten Prompts Reached Provider Activation

10 prompts were classified as `CONVERSATION`, routed successfully, failed self-resolution, and then attempted provider response generation.

Observed examples:

- `Explain worker execution.`
- `Explain provider boundaries.`
- `Explain authorization.`
- `Summarize recent progress.`
- `Explain AiGOL in Slovenian.`

Each stopped at provider activation with `OpenAI provider unavailable`.

## Finding 5: Three Prompts Failed Response Validation

Three prompts were classified as conversation and self-resolved, but response validation rejected the generated text:

- `How does AiGOL work?`
- `How does AiGOL prevent provider authority?`
- `How does AiGOL preserve worker isolation?`

Evidence: replay response failure reason:

```text
conversation response validation failed closed: authority-bearing response
```

## Finding 6: Routing Was Not The Dominant Bottleneck

Prompt-level routing succeeded for all 20 prompts that classified successfully.

Routing failed for 30 prompts only because classification had already failed.

Evidence: replay routing artifacts show `ROUTED = 20`, `FAILED_CLOSED = 30`.

## Finding 7: Provider Connectivity Was Not Proven During The Epoch

The second conversational epoch recorded:

```text
provider_used = 0
provider_invoked = 0
provider_response_received = 0
```

This is epoch-local evidence. Later `REAL_OPENAI_CONNECTIVITY_PROOF_V1` proves real OpenAI connectivity exists now, but does not retroactively change the epoch outcomes.

