# FIRST_REAL_PROVIDER_OPERATION_V1

## Status

`FIRST_REAL_PROVIDER_OPERATION_STATUS = READY_WITH_GAPS`

## Purpose

This milestone verifies whether AiGOL can use a real provider in the
Human Prompt to provider fallback path.

The preferred real provider was OpenAI.

This milestone introduces no new provider, worker, governance layer,
orchestration, planning, or authority.

## Operational Test

Prompt:

```text
Explain provider boundaries.
```

Command:

```text
python -m aigol.cli.aigol_cli prompt submit \
  --prompt "Explain provider boundaries." \
  --runtime-root /tmp/aigol_first_real_provider_operation/explain_provider_boundaries
```

The command was run with real provider network access.

## Observed Flow

```text
Human Prompt
↓
Intent Classification
↓
CONVERSATION
↓
Routing
↓
Conversation Runtime
↓
Provider Fallback
↓
OpenAI Provider Request
↓
OpenAI Provider Response
↓
AiGOL Validation
↓
FAILED_CLOSED
↓
Replay
```

## Result

OpenAI was reached.

OpenAI returned a response.

AiGOL recorded replay-visible provider evidence.

AiGOL failed closed during response validation because the real OpenAI adapter
returned a generic provider envelope containing:

```text
response_text
```

while `PROVIDER_ASSISTED_CONVERSATION_RUNTIME_V1` requires structured semantic
fields:

```text
suggested_response_text
response_reasoning
confidence
```

## Evidence

Provider replay reconstructed:

```text
provider_id = openai
provider_version = openai-responses-v1
provider_invoked = True
response_text_present = True
proposal_hash_present = True
```

Prompt CLI result:

```text
response_status = FAILED_CLOSED
response_source = UNAVAILABLE
failure_reason = suggested_response_text is required
worker_invoked = False
execution_requested = False
```

## Answers

Can AiGOL reach the provider?

Yes.

Can AiGOL receive responses?

Yes.

Can AiGOL validate responses?

Partially. The validation boundary works, but the current real provider response
shape does not match the provider-assisted conversation schema.

Can AiGOL produce replay-backed responses?

Not yet for real provider-assisted conversation. It can produce replay-backed
provider evidence, but final conversation response validation fails closed.

Does provider substitution still work?

Yes at the provider envelope boundary. Semantic conversation substitution needs
a shared structured response contract.

## Boundary Certification

The failed real provider operation preserved:

- no provider authority;
- no worker invocation;
- no execution request;
- no authorization;
- replay visibility;
- fail-closed validation.

## Final Classification

```text
FIRST_REAL_PROVIDER_OPERATION_STATUS = READY_WITH_GAPS
```

AiGOL can operate with a real provider at the provider request/response/replay
boundary. The next gap is structured semantic response compatibility between
real provider adapters and provider-assisted conversation validation.
