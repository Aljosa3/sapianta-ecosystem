# Attachment Implementation Blockers V1

Status: planning-only blocker classification.

## MUST FIX

Before `REAL_LLM_ATTACHMENT_V1`:

- define supplied-response attachment function boundary
- define provider identity envelope schema
- define raw response evidence schema
- define deterministic hash validation
- define normalization into existing proposal shape
- define fail-closed malformed and authority-escalating output tests

Before `REAL_WORKER_ATTACHMENT_V1`:

- define worker identity envelope schema
- define worker execution request schema
- require AiGOL authorization evidence
- define worker replay stages
- define worker termination evidence
- reject worker self-authorization

## SHOULD FIX

For `REAL_LLM_ATTACHMENT_V1`:

- add operator-facing rejection summaries for provider normalization failure
- add replay summary support for raw response evidence
- document supplied-response examples for ChatGPT, Codex, Claude, and local model outputs without provider-specific code

For `REAL_WORKER_ATTACHMENT_V1`:

- add replay summary support for worker identity and termination state
- add pressure tests for repeated worker invocations
- add explicit no-hidden-state evidence checks

## OPTIONAL

For later milestones:

- live OpenAI provider invocation
- live Claude provider invocation
- ChatGPT browser/session attachment
- local live model inference
- filesystem read-only worker
- API query worker
- CLI read-only worker

## Overengineering To Avoid

Avoid introducing:

- provider registry expansion
- multi-provider routing
- worker pools
- orchestration
- agents
- retries
- async lifecycle
- memory
- streaming
- capability expansion

These are not required for first real attachment implementation.
