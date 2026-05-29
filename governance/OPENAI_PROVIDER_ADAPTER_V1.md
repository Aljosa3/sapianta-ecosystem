# OpenAI Provider Adapter V1

Status: first real OpenAI provider adapter milestone.

This milestone implements the first OpenAI provider adapter as a proposal-source-only boundary.

It preserves the frozen invariant:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Runtime Surface

Implemented runtime surface:

- `aigol/runtime/openai_provider_adapter.py`

Implemented tests:

- `tests/test_openai_provider_adapter_v1.py`

## Adapter Role

OpenAI is treated as:

```text
UNTRUSTED_PROPOSAL_SOURCE
```

OpenAI is never:

- execution authority
- authorization authority
- governance authority
- replay authority
- worker authority

## Flow

The adapter flow is:

```text
Human request
-> OpenAI provider adapter
-> provider request metadata capture
-> raw provider response capture
-> REAL_PROVIDER_ATTACHMENT_V1
-> EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1
-> proposal normalization
-> AiGOL governance
-> authorization
-> existing read-only worker
-> replay
```

## Operational Boundaries

The adapter uses:

- single request
- single response
- full response capture before normalization
- no streaming
- no automatic retries
- no tool use
- no function calling
- no memory

The OpenAI client is isolated behind an injected adapter boundary for deterministic testing and bounded provider invocation.

## Replay Evidence

Top-level adapter replay records:

- provider request metadata
- raw provider response
- provider attachment capture
- governed result

Nested replay under `real_provider_attachment` records:

- provider identity
- raw provider response
- provider attachment record
- governed result
- external LLM response attachment replay

## Success Result

OpenAI output can enter AiGOL as an untrusted proposal source while preserving:

- proposal-only provider behavior
- AiGOL governance authority
- worker execution only after authorization
- replay visibility
- fail-closed handling

This milestone does not introduce provider ecosystem routing, worker expansion, orchestration, agents, memory, shell execution, filesystem mutation, or capability expansion.

