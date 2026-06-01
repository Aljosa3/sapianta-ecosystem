# PROVIDER_ASSISTED_CONVERSATION_RUNTIME_V1

## Status

`PROVIDER_ASSISTED_CONVERSATION_RUNTIME_STATUS = READY`

## Purpose

This milestone implements the first provider-assisted conversation response
runtime.

It allows a `CONVERSATION` intent to produce a replay-visible response while
preserving AiGOL authority over validation and final response emission.

## Constitutional Invariant

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Provider response remains proposal evidence only.

AiGOL validates and emits the final response artifact.

## Runtime Surface

Implemented:

```text
aigol/runtime/provider_assisted_conversation_runtime.py
```

Primary runtime function:

```text
run_provider_assisted_conversation(...)
```

Focused validation:

```text
tests/test_provider_assisted_conversation_runtime_v1.py
```

## Operational Flow

```text
Human Prompt
↓
Provider-Assisted Intent Classification
↓
CONVERSATION
↓
Self-Resolution Attempt
↓
If resolved: AiGOL response
↓
If unresolved: provider response suggestion
↓
AiGOL response validation
↓
Conversation Response Artifact
↓
Replay
```

## Self-Resolution First

The runtime records a self-resolution attempt over:

- replay-backed explanations;
- Constitutional Memory;
- governance artifacts;
- deterministic runtime knowledge.

If deterministic self-resolution succeeds, provider conversational response is
not requested.

## Provider-Assisted Response

When self-resolution is insufficient, the provider may return:

- `suggested_response_text`;
- `response_reasoning`;
- `confidence`.

The provider may not return:

- authorization;
- governance decision;
- execution request;
- dispatch request;
- worker instruction;
- replay mutation;
- memory mutation.

## Replay Evidence

Replay records:

- provider-assisted conversation start;
- provider-assisted intent classification;
- self-resolution attempt;
- provider response request when required;
- provider response evidence when required;
- AiGOL validation artifact;
- final conversation response artifact;
- returned response evidence.

## Fail-Closed Cases

The runtime fails closed on:

- provider unavailable;
- invalid provider response;
- authority-bearing response;
- ambiguous response;
- non-conversation intent;
- replay corruption;
- append-only replay violation.

## Demonstrated Cases

Deterministic prompt:

```text
what is aigol
```

Result:

```text
provider_assistance_required = False
conversation_status = PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED
```

Provider-assisted prompt:

```text
Kaj je namen AiGOL?
```

Result:

```text
provider_assistance_required = True
conversation_status = PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED
```

## Final Classification

```text
PROVIDER_ASSISTED_CONVERSATION_RUNTIME_STATUS = READY
```
