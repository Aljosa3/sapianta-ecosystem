# FIRST_REAL_PROVIDER_OPERATION_FINDINGS_V1

## Findings Summary

The first real provider operation reached OpenAI and received a real response.

The operation did not produce a final conversation response because AiGOL
correctly failed closed on schema mismatch.

## Finding 1: Provider Was Reachable

The real OpenAI provider was invoked successfully.

Replay evidence:

```text
event_type = PROVIDER_PROPOSAL_CREATED
provider_id = openai
provider_status = AVAILABLE
provider_invoked = true
proposal_hash = sha256:...
```

## Finding 2: Provider Response Was Received

The provider envelope included:

```text
response_text
raw_response
raw_response_hash
model = gpt-5.1
```

Provider replay reconstruction confirmed:

```text
response_text_present = True
proposal_hash_present = True
```

## Finding 3: AiGOL Validation Failed Closed Correctly

Conversation validation required:

```text
suggested_response_text
response_reasoning
confidence
```

The real OpenAI adapter returned:

```text
response_text
```

Validation result:

```text
validation_status = FAILED_CLOSED
failure_reason = suggested_response_text is required
```

This is a schema compatibility gap, not a provider reachability gap.

## Finding 4: Provider Output Was Semantically Misaligned

The provider interpreted `Explain provider boundaries.` as a generic human
services question, not an AiGOL constitutional provider-boundary question.

This shows that the real provider adapter currently lacks a governed semantic
instruction layer for AiGOL-specific provider-assisted conversation.

## Finding 5: Replay Worked

Replay recorded:

- provider request;
- provider response;
- provider proposal hash;
- raw response hash;
- failed validation artifact;
- final failed response artifact.

## Finding 6: Authority Boundaries Held

The provider did not:

- authorize;
- govern;
- execute;
- invoke a worker;
- dispatch;
- mutate memory;
- mutate replay outside append-only provider evidence.

## Final Finding

The provider layer is operational.

The provider-assisted conversation layer is not yet compatible with the real
provider response shape.
