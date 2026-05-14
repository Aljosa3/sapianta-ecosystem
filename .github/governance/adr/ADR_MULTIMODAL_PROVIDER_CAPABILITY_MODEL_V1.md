# ADR: Multimodal Provider Capability Model v1

## Context

SAPIANTA / AiGOL now has a frozen first no-copy/paste loop and an end-to-end validation harness. Future provider evolution may include multimodal, browser, CAD, robotic, or industrial capability declarations.

Before any future execution expansion, capability metadata needs a deterministic governance model.

## Decision

Introduce `MULTIMODAL_PROVIDER_CAPABILITY_MODEL_V1` as a passive provider capability governance model.

The model defines capability classes, modality classes, replay-safe declarations, passive registry metadata, fail-closed validation, and capability evidence.

Capability declarations do not grant execution authority, invoke providers, bypass envelopes, enable routing, enable orchestration, or enable autonomous provider selection.

## Consequences

Positive:

- provider capabilities become explicit and replay-safe
- unknown capabilities and modalities fail closed
- future multimodal work has a governance boundary
- no-copy/paste continuity remains preserved

Tradeoffs:

- capability metadata is descriptive only
- no routing or provider selection is enabled
- no multimodal execution is introduced

## Invariants

- `CAPABILITY != AUTHORITY`
- `MODALITY != EXECUTION_PERMISSION`
- `PROVIDER_CAPABILITY != PROVIDER_INVOCATION`
- `CAPABILITY_MODEL != ROUTING`
- `CAPABILITY_MODEL != ORCHESTRATION`
