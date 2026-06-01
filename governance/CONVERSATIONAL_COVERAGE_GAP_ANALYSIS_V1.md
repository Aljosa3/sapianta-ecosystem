# Conversational Coverage Gap Analysis V1

Status: gap analysis from replay-visible conversational outcomes.

## Proven Gaps

1. Provider assistance was unavailable during the measured epoch.

   Evidence: 40 failed prompts contain either direct provider activation failure or provider-assisted classification failure with `OpenAI provider unavailable`.

2. Deterministic self-resolution is narrow.

   Evidence: only six prompts were answered without provider assistance, and all were simple AiGOL, governance, or replay explanation prompts.

3. Response validation over-blocks some safe explanatory prompts.

   Evidence: cases 5, 41, and 42 failed with `conversation response validation failed closed: authority-bearing response`.

4. Replay/history/status questions are not connected to conversational evidence retrieval.

   Evidence: `Read the replay ledger`, `Show last replay report`, `What evidence supports the last result`, `What changed recently`, and `Give me current status` failed before a provider response.

5. Multilingual coverage is not available without provider assistance.

   Evidence: Slovenian prompts in cases 8 and 47-49 failed at intent classification; case 50 reached provider activation and failed because provider was unavailable.

## Cannot Prove From Current Evidence

The current evidence cannot prove the success rate after `REAL_OPENAI_CONNECTIVITY_PROOF_V1`.

Reason: the 50-prompt replay epoch was recorded when provider calls failed closed. The later connectivity proof is real but is a separate one-request proof, not a rerun of the conversational coverage suite.

## Improvement Solvability Matrix

| Failure group | Count | Can be solved by intent coverage? | routing coverage? | provider activation? | response validation? | conversational evidence availability? |
| --- | ---: | --- | --- | --- | --- | --- |
| Intent classification provider-unavailable | 30 | `UNKNOWN_WITHOUT_RERUN` | `NO_EVIDENCE` | `LIKELY_REQUIRES_RERUN` | `NO_EVIDENCE` | `PARTIAL_FOR_HISTORY_STATUS_PROMPTS` |
| Provider activation unavailable | 10 | `NO` | `NO` | `YES_FOR_THIS_EPOCH_FAILURE` | `UNKNOWN_AFTER_PROVIDER_AVAILABLE` | `PARTIAL_FOR_PROGRESS_HISTORY_PROMPTS` |
| Response validation over-block | 3 | `NO` | `NO` | `NO` | `YES` | `NO_EVIDENCE` |
| Non-conversation intent | 1 | `NO` | `NO` | `NO` | `NO` | `YES_IF_CONVERSATION_SHOULD_ANSWER_MEMORY_TOPICS` |

## Highest-Impact Gap

The highest-impact measured gap is not generic architecture.

It is the absence of a post-connectivity rerun of the same 50 prompts.

Without that rerun, the system cannot distinguish:

- failures that disappear once provider activation works;
- failures that remain because prompt classification is too narrow;
- failures that remain because response validation over-blocks;
- failures that remain because replay/history/status evidence is not available to conversation.

