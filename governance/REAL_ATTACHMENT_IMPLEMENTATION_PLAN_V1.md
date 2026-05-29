# Real Attachment Implementation Plan V1

Status: planning-only real attachment roadmap.

This milestone defines the smallest safe implementation path from attachment models to first real attachments:

- `REAL_LLM_ATTACHMENT_V1`
- `REAL_WORKER_ATTACHMENT_V1`

It does not implement attachments, add providers, add workers, add orchestration, add memory, expand capabilities, or mutate runtime behavior.

## Frozen Invariant

All implementation planning preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Planning Inputs

This plan follows:

- `REAL_ATTACHMENT_GAP_ANALYSIS_V1`
- `REAL_LLM_ATTACHMENT_MODEL_V1`
- `REAL_WORKER_ATTACHMENT_MODEL_V1`
- `FIRST_USEFUL_AIGOL_V1`

## Primary Recommendation

First real LLM attachment:

- Recommended candidate: local/supplied external LLM response attachment.
- Reason: it exercises real model output attachment semantics without adding network calls, API credentials, provider SDK behavior, streaming, retries, or vendor-specific runtime complexity.

First real worker attachment:

- Recommended candidate: runtime inspection worker.
- Reason: it is read-only, already aligned with the frozen `READ_ONLY_RUNTIME_INSPECTION` capability, does not require filesystem path scoping, and has the smallest boundary surface.

## Implementation Strategy

The shortest safe path is:

1. Implement `REAL_LLM_ATTACHMENT_V1` as a provider-agnostic supplied-response attachment that captures raw response evidence, provider identity, and normalized proposal artifacts.
2. Pressure-test `REAL_LLM_ATTACHMENT_V1` against malformed, ambiguous, authority-escalating, and replay-corrupt model outputs.
3. Implement `REAL_WORKER_ATTACHMENT_V1` as a read-only runtime inspection worker attachment that accepts only AiGOL-authorized execution requests and emits replay-visible worker evidence.

## Why This Order

LLM attachment comes first because it remains non-executing. It can prove the proposal-only boundary before any external worker execution boundary is introduced.

Worker attachment comes second because it touches execution semantics and therefore needs stronger authorization, replay mapping, identity, and isolation guarantees.

## Success Definition

Success is a clear roadmap from attachment models to first implementation without weakening the frozen invariant.

Success is not a real attachment implementation.
