# Provider Abstraction Foundation v1

## Purpose

This evidence artifact establishes the first canonical provider abstraction substrate for AGOL.

Execution providers are interchangeable bounded workers. AGOL remains the governance/control substrate.

## Canonical Dependencies

- `FINALIZE_REPO_WIDE_TEST_COLLECTION_STABILIZATION_V1`
- `AGOL_LAYER_SEPARATION_MODEL_V1`
- `GOVERNANCE_WORKTREE_HYGIENE_V1`

## Provider Contract

Every provider must expose deterministic contract fields:

```json
{
  "provider_id": "codex",
  "provider_type": "REMOTE_LLM",
  "bounded_execution": true,
  "governance_authority": false,
  "replay_safe": true
}
```

Providers must not self-authorize, mutate governance, mutate replay evidence, escalate authority, bypass validation, or generate hidden tasks.

## Normalized Result

All providers must return replay-compatible normalized results. Provider-specific output must not change governance interpretation semantics.

## Provider Identity

Provider identity is explicit, deterministic, replay-safe, and immutable during execution. Provider identity must not alter governance authority, validation semantics, or replay semantics.

## Registry Boundary

The provider registry is passive metadata. It validates contracts and exposes provider metadata. It does not schedule, route, optimize, dynamically select, or orchestrate.

## Adapters

The adapters are structural placeholders only:

- Codex
- Claude Code
- local executor
- deterministic mock

They do not call real provider APIs.

## Permanent Invariant

```text
PROVIDER != GOVERNANCE
```

## Explicit Non-Goals

This milestone does not implement runtime routing, provider optimization, orchestration, dynamic scheduling, autonomous provider selection, fallback logic, execution envelopes, multimodal orchestration, adaptive runtime behavior, or provider intelligence ranking.
