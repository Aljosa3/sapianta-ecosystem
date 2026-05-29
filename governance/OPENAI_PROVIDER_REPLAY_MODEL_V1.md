# OpenAI Provider Replay Model V1

Status: OpenAI adapter replay model.

## Replay Purpose

OpenAI provider replay preserves provider evidence before proposal normalization and before downstream governance decisions.

Replay remains the source of truth.

## Adapter Replay Stages

OpenAI adapter replay contains:

1. `provider_request_metadata`
2. `raw_provider_response`
3. `provider_attachment_capture`
4. `governed_result`

All stages are append-only and hash-verified.

## Request Metadata

Request metadata records:

- adapter id
- provider identity
- model
- timestamp
- request text hash
- credential source label
- no credential material
- timeout
- single request flag
- no streaming flag
- no retry flag
- no tool/function/memory flags

## Raw Response Capture

Raw response capture records:

- provider identity
- model
- timestamp
- raw provider response
- raw provider response hash
- response shape
- untrusted proposal flag
- authority-denial flags

Raw response evidence is recorded before `REAL_PROVIDER_ATTACHMENT_V1` receives the response.

## Nested Replay

The adapter delegates to `REAL_PROVIDER_ATTACHMENT_V1`, which records nested provider attachment replay and external LLM attachment replay.

The complete replay chain is:

```text
OpenAI adapter replay
-> provider attachment replay
-> external LLM attachment replay
-> proposal replay
-> governed replay
```

## Replay Failure Handling

Replay corruption, hash mismatch, ordering mismatch, missing artifacts, append-only violations, malformed response evidence, and replay reconstruction ambiguity fail closed.

No silent replay repair is allowed.

