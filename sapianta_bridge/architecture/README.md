# AGOL Layer Separation Model v1

This package defines the first canonical layered authority model for AGOL.

AGOL acts as a governance/control plane, not as execution intelligence. The model separates interaction intelligence, governance authority, execution authority, validation authority, and reflection authority so no layer silently inherits another layer's power.

## Layers

- `INTERACTION_LAYER`: receives user intent, creates proposals, explains outcomes, and summarizes replay evidence. It has no execution authority.
- `GOVERNANCE_LAYER`: classifies intent, evaluates admissibility and risk, constrains execution, and establishes approval requirements.
- `EXECUTION_LAYER`: executes only inside a provided bounded envelope and returns normalized artifacts.
- `VALIDATION_LAYER`: certifies, rejects, and verifies replay-safe determinism.
- `REFLECTION_LAYER`: interprets evidence and proposes future directions as advisory-only output.

## Authority Boundary Model

Undefined authority is blocked. Layers cannot self-promote, bypass governance, mutate another layer's state, override approval, or silently retry execution.

The permanent invariant is:

```text
INTERACTION_LAYER != EXECUTION_LAYER
```

## Communication Flow

Allowed flow:

```text
User -> Interaction -> Governance -> Execution -> Validation -> Reflection -> Interaction
```

Forbidden examples:

- `Execution -> User`
- `Reflection -> Execution`
- `Execution -> Governance mutation`
- `Validation -> silent Execution retry`
- `Interaction -> Execution`

## Provider Abstraction Philosophy

Execution providers are replaceable bounded workers. Codex, Claude Code, Gemini, local executors, and deterministic tools may provide execution, but provider identity must not affect governance semantics.

Replay evidence format remains stable across providers.

## Stabilization Epoch

This model depends on `STABILIZATION_CERTIFICATION_EPOCH_V1` as the canonical replay-safe substrate baseline. It does not redefine, mutate, or weaken that stabilization epoch.

## Non-Goals

This package does not implement orchestration, adaptive routing, provider switching, execution envelopes, scheduling, token optimization, runtime optimization, recursive autonomy, or hidden planning.
