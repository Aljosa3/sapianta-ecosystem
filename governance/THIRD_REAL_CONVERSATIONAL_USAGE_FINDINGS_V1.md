# THIRD_REAL_CONVERSATIONAL_USAGE_FINDINGS_V1

## Status

Findings for `THIRD_REAL_CONVERSATIONAL_USAGE_EPOCH_V1`.

## Finding 1: Conversational Success Did Not Increase

The third epoch produced:

```text
prompts_submitted = 50
responses_created = 6
fail_closed_responses = 44
success_rate = 12%
```

This matches the second epoch result exactly.

Evidence:

```text
governance/SECOND_REAL_CONVERSATIONAL_USAGE_CERTIFICATION.json
/tmp/aigol_third_conversation_epoch/
```

## Finding 2: Provider Understanding Improved

The third epoch produced 35 replay-visible provider responses, compared to 0
in the second epoch.

For the prompt:

```text
Explain provider boundaries.
```

the provider received the minimal AiGOL context capsule and returned an
AiGOL-specific provider-boundary explanation instead of a generic professional
boundary answer.

Evidence:

```text
/tmp/aigol_third_conversation_epoch/case_12/AIGOL-HUMAN-PROMPT-8987B3838E74/conversation_response/provider_conversation_response/000_provider_proposal_created.json
```

## Finding 3: Improved Provider Understanding Was Not Converted Into Final Responses

Eight prompts received conversation-stage provider responses, but all eight
failed closed before final response delivery.

Observed failure reason:

```text
provider conversation response contains authority-bearing text
```

Evidence:

```text
/tmp/aigol_third_conversation_epoch/case_12/AIGOL-HUMAN-PROMPT-8987B3838E74/conversation_response/004_provider_assisted_conversation_response_returned.json
```

## Finding 4: Provider-Assisted Classification Still Fails On Contract Shape

Twenty-seven prompts failed as classification failures. The dominant failure
reason was:

```text
suggested_destination is required
```

This indicates that the provider returned useful explanatory text in many
cases, but the provider-assisted classification path required structured
classification output.

Evidence examples:

```text
/tmp/aigol_third_conversation_epoch/case_6/AIGOL-HUMAN-PROMPT-EFFB68CCCFC8/conversation_response/intent_classification/001_provider_assisted_intent_classification_artifact.json
/tmp/aigol_third_conversation_epoch/case_47/
```

## Finding 5: The Context Capsule Preserved Constitutional Boundaries

Across the 50-prompt epoch:

```text
worker_invoked = False
execution_requested = False
provider_response_authority = False
```

Provider outputs remained proposal-only and replay-visible.

## Finding 6: The Primary Bottleneck Moved

Before the capsule, the practical bottleneck was missing provider context and
provider unavailability.

After the capsule, replay evidence shows provider-side AiGOL understanding in
multiple cases. The primary observed bottlenecks are now:

- provider-assisted classification contract mismatch;
- provider conversation response validation over-blocking safe explanations;
- absence of replay-backed data for some historical/current-status questions;
- intermittent provider unavailability on five prompts.
