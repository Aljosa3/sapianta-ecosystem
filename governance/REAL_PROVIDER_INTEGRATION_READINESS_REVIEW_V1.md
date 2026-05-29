# Real Provider Integration Readiness Review V1

Status: provider integration readiness review.

This milestone determines whether AiGOL is ready to begin provider-specific adapter milestones:

- `OPENAI_PROVIDER_ADAPTER_V1`
- `CLAUDE_PROVIDER_ADAPTER_V1`
- `CODEX_PROVIDER_ADAPTER_V1`

It does not implement provider adapters, SDKs, network transport, credentials, orchestration, memory, capability expansion, worker expansion, or autonomous execution.

## Frozen Invariant

All provider integrations must preserve:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Provider remains proposal source only.

Provider is never execution authority, authorization authority, governance authority, or replay authority.

## Reviewed Surfaces

Reviewed:

- provider boundary
- external response attachment
- proposal normalization
- replay model
- authority separation
- pressure validation
- provider identity model

## Readiness Summary

`OPENAI_PROVIDER_ADAPTER_V1`: `READY_WITH_CONSTRAINTS`

`CLAUDE_PROVIDER_ADAPTER_V1`: `READY_WITH_CONSTRAINTS`

`CODEX_PROVIDER_ADAPTER_V1`: `NOT_READY`

## OpenAI Readiness

OpenAI is ready with constraints because AiGOL now has:

- provider boundary
- raw response capture expectations
- external response attachment
- proposal normalization
- pressure validation
- replay-visible failure handling

OpenAI is not fully ready without constraints because the adapter must still define SDK isolation, credential boundary, network failure handling, raw response extraction, provider-specific error mapping, and no-retry behavior.

## Claude Readiness

Claude is ready with constraints for the same provider-boundary reasons as OpenAI.

Claude remains constrained because no Claude-specific response extraction, SDK isolation, credential handling, or provider failure mapping has been defined yet.

## Codex Readiness

Codex is not ready as a provider adapter because Codex language and tooling can blur proposal source and execution role.

Before Codex provider adapter work begins, AiGOL needs a dedicated Codex proposal-only adapter model proving that Codex cannot execute, modify files, invoke tools, or act as a worker through this provider path.

## Readiness Result

The first real provider integration can begin safely only for OpenAI or Claude, and only as proposal-source-only adapters that forward bounded model text into `REAL_PROVIDER_ATTACHMENT_V1`.

Codex should wait.
