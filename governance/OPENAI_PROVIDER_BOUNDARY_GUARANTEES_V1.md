# OpenAI Provider Boundary Guarantees V1

Status: OpenAI adapter boundary guarantees.

## Proposal-Only Guarantee

OpenAI output is proposal input only.

It is never:

- execution
- authorization
- governance
- replay authority
- worker instruction authority

## Authority Separation

The adapter records explicit authority denial:

- `openai_execution_authority = false`
- `openai_authorization_authority = false`
- `openai_governance_authority = false`
- `openai_replay_authority = false`
- `openai_worker_authority = false`

AiGOL remains responsible for validation, authorization, rejection, replay recording, and governed return.

## Tool And Action Boundary

The adapter does not enable:

- tool use
- function calling
- assistant actions
- code execution
- browser execution
- shell execution
- filesystem mutation
- worker spawning

## Runtime Boundary

The adapter is bounded to:

- one OpenAI request
- one OpenAI response
- full response capture
- deterministic replay evidence
- fail-closed rejection

The adapter does not implement:

- streaming
- automatic retries
- conversation memory
- persistent memory
- orchestration
- provider routing
- autonomous continuation

## Existing Attachment Path Guarantee

OpenAI output must route through:

```text
REAL_PROVIDER_ATTACHMENT_V1
-> EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1
```

No OpenAI output may bypass the existing provider attachment and proposal normalization path.

