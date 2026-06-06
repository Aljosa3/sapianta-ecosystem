# AIGOL_CONVERSATIONAL_FAILURE_TRACE_REVIEW_V1

## Status

Review-only failure trace.

No runtime was changed. No provider behavior was changed. No OCS cognition behavior was changed. No new functionality is certified by this review.

## Executive Finding

The certified OCS LLM cognition end-to-end runtime is not the runtime being used by the failing `aigol conversation` path.

The observed terminal sequence:

```text
[1/8] Routing
[2/8] Cognition
[3/8] Provider Invocation
[4/8] Comparison
[5/8] Continuity
[6/8] Clarification
[7/8] Result Assembly
[8/8] Replay
FAILED_CLOSED: conversation provider clarification fallback failed closed: prompt is not clarification-eligible
```

is produced by the conversational progress binding plus the older prompt-to-conversation provider fallback path.

The progress lines are visibility checkpoints. They do not prove that `AIGOL_OCS_LLM_COGNITION_END_TO_END_V1` executed.

## Root Cause

`aigol conversation` still has a default branch that calls `submit_prompt_to_conversation(...)`.

When that older provider-assisted conversation path fails because provider-assisted intent classification or response generation cannot complete, the CLI invokes:

```text
run_conversation_provider_unavailable_clarification_fallback(...)
```

That fallback is only eligible for a narrow hard-coded ambiguity set, such as:

- workstation creation ambiguity;
- exact short capability prompts such as `improve trading`, `add analysis`, or `create reporting`.

Normal cognition prompts such as product strategy, commercialization continuation, and broad recommendation questions are not eligible. The fallback therefore fails closed with:

```text
conversation provider clarification fallback failed closed: prompt is not clarification-eligible
```

## Trace Summary

### Runtime Trace

| Step | Runtime | Input | Output | Decision |
| --- | --- | --- | --- | --- |
| 1 | `aigol conversation` interactive loop | Human prompt | turn id, prompt id, progress binding | Continue |
| 2 | source-of-truth router | Human prompt | source router artifacts | Source selected |
| 3 | conversational progress binding | Turn state | progress snapshots for Cognition through Clarification | Visibility only |
| 4 | branch selection in `aigol_cli.py` | Human prompt | default branch | No certified explicit workflow matched |
| 5 | `submit_prompt_to_conversation` | Human prompt | prompt artifact and provider-assisted conversation capture | Older conversation path selected |
| 6 | provider-assisted conversation runtime | Prompt capture | failed provider-assisted conversation artifacts | Provider unavailable or prompt not conversation-resolved |
| 7 | conversation chain continuity | Failed conversation capture | continuity artifacts | Failure lineage preserved |
| 8 | provider-unavailable clarification fallback | Failed conversation capture | fallback artifact | Fallback attempted |
| 9 | fallback ambiguity classifier | Original human prompt | no clarification artifact | Prompt not clarification-eligible |
| 10 | CLI result assembly | fallback capture | final `FAILED_CLOSED` terminal line | Fail closed |

### Decision Trace

The failing path is entered at `aigol/cli/aigol_cli.py`:

- lines 1960-1970 call `submit_prompt_to_conversation(...)` in the default branch;
- lines 1973-1983 call `run_conversation_provider_unavailable_clarification_fallback(...)` when that capture has `fail_closed = true`;
- lines 1988-1996 render the fallback failure.

The fallback runtime is `aigol/runtime/conversation_provider_unavailable_clarification_fallback.py`:

- lines 53-57 require provider-unavailable evidence;
- line 58 calls `_classify_ambiguity(prompt)`;
- lines 229-231 raise the final `prompt is not clarification-eligible` error;
- lines 331-367 replace the capture response with deterministic fallback metadata.

### Routing Trace

The conversational routing registry does not provide a broad route for general OCS LLM cognition.

Evidence:

- `aigol/runtime/conversational_cli_runtime.py` lines 197-222 only map a finite set of workflows;
- decision-support detection requires specific phrases, including `product domain`;
- `aigol/cli/aigol_cli.py` does not import or call `run_ocs_llm_cognition_end_to_end(...)`.

For example, `I want to create the first real AiGOL product.` does not match the decision-support route because the certified matcher expects `product domain` or `aigol product domain`.

## Artifact Trace

The reproduced failing turn created these replay-visible artifacts:

- source router artifacts;
- conversational progress binding artifact;
- eight runtime progress visibility snapshots;
- human prompt artifact;
- prompt lineage artifact;
- deterministic intent-classification attempt;
- provider semantic-assistance failure artifacts;
- provider-assisted conversation failure artifacts;
- conversation chain continuity artifacts;
- provider-unavailable clarification fallback artifact.

The reproduced failing turn did not create:

- `OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1`;
- `LLM_COGNITION_ARTIFACT_V1`;
- `MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1`;
- `COGNITION_COMPARISON_ARTIFACT_V1`;
- `COGNITION_CONTINUITY_ARTIFACT_V1`;
- `COGNITION_CLARIFICATION_ARTIFACT_V1`;
- `OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1`.

## Clarification Trace

Two clarification systems are involved but they are not equivalent:

1. The certified unknown-domain clarification runtime is entered only when `is_unknown_domain_clarification_eligible(human_prompt)` returns true.
2. The provider-unavailable clarification fallback is entered only after the older provider-assisted conversation path fails.

The observed failure comes from the second system.

The fallback eligibility logic is `_classify_ambiguity(prompt)`. It accepts only:

- prompts containing `workstation` plus a creation verb;
- exact prompts in the set `improve trading`, `add analysis`, `create reporting`, with or without a period.

Everything else fails closed.

## Replay Trace

Replay captures the actual failure chain, not the desired certified OCS cognition chain.

The trace evidence confirms replay visibility for:

- progress snapshots;
- source routing;
- provider-assisted conversation failure;
- provider semantic-assistance failure;
- chain continuity;
- provider-unavailable clarification fallback.

Replay does not capture OCS LLM cognition artifacts for the failing turn because that runtime was not invoked.

## Review Question Answers

1. The runtime that triggers `conversation provider clarification fallback` is `run_interactive_conversation(...)` in `aigol/cli/aigol_cli.py`, after `submit_prompt_to_conversation(...)` returns `fail_closed = true`.

2. Entry into clarification fallback occurs when the default conversation capture has `fail_closed = true`.

3. Normal cognition prompts reach fallback because they miss explicit conversational workflow branches and fall into the older provider-assisted conversation path, not the certified OCS LLM cognition path.

4. The component that determines `prompt is not clarification-eligible` is `_classify_ambiguity(...)` in `aigol/runtime/conversation_provider_unavailable_clarification_fallback.py`.

5. Eligibility is limited to workstation creation ambiguity and a few exact capability prompts. Broad product, strategy, commercialization, and continuation prompts are not eligible.

6. In the reproduced failure, real OCS cognition was not executed. The older provider-assisted intent-classification path attempted provider semantic assistance and failed with `OpenAI provider unavailable`.

7. No valid `LLM_COGNITION_ARTIFACT_V1` was produced in the failing `aigol conversation` path.

8. No cognition comparison was executed in the failing path.

9. OCS cognition continuity was not executed. Conversation-chain continuity for the older conversation capture was executed.

10. OCS cognition clarification was not executed. Provider-unavailable clarification fallback was attempted and failed closed.

11. The final fail-closed outcome is caused by `CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_ARTIFACT_V1` with `fallback_status = FAILED_CLOSED` and `failure_reason = conversation provider clarification fallback failed closed: prompt is not clarification-eligible`.

12. The original prompt appears lost or replaced because the fallback capture overwrites `response_text`, `response_source`, and `conversation_replay_reference` with fallback-specific values. The original prompt remains hash-bound but is not rendered as the human-facing result.

13. The `AiGOL > AiGOL >` display can occur when the interactive loop receives an empty prompt and immediately continues. The loop strips input and continues without output for blank prompts. This can also be amplified by terminal buffering after a turn with sparse output.

14. The reviewed code shows an output-routing issue, not evidence of prompt-buffer mutation: blank prompts are ignored without rendering, and the final output assembly separates progress lines from failure lines. No prompt text mutation was found.

15. Replay captures the executed failure chain. It does not capture the full OCS LLM cognition chain because that chain is not executed by the failing branch.

## Additional Observed Failure Class

`Create a marketing domain.` is a different failure class in the current repository state.

It routes to native development and PPP handoff, proceeds into worker-related governed stages, and fails because the target artifact already exists:

```text
generic domain factory failed closed: target already exists: governance/MARKETING_DOMAIN_FOUNDATION_V1.md
```

That is not the same provider-clarification fallback failure.

## Minimal Fix Scope

The minimal fix is not inside the provider-unavailable clarification fallback.

Required binding work:

1. Add an explicit conversational route for broad OCS LLM cognition prompts.
2. Connect that route to `run_ocs_llm_cognition_end_to_end(...)`.
3. Render `human_facing_cognition_result` from `OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1`.
4. Preserve the existing provider-unavailable clarification fallback only for the narrow legacy fallback cases it was designed to handle.
5. Distinguish progress visibility from actual stage execution in terminal output or result metadata.

## Final Classification

`AIGOL_CONVERSATIONAL_FAILURE_TRACE_REVIEW_V1`

## Conclusion

The certified OCS cognition pipeline is not failing after completing its stages. The failing conversational path does not invoke that pipeline.

The observed failure is caused by a missing CLI routing/binding from general conversational cognition prompts to the certified OCS LLM cognition end-to-end runtime. The CLI instead falls through to an older provider-assisted conversation runtime and then into a narrow provider-unavailable clarification fallback that correctly fails closed for non-eligible prompts.
