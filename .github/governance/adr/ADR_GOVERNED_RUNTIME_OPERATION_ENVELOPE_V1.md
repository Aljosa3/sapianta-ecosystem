# ADR_GOVERNED_RUNTIME_OPERATION_ENVELOPE_V1

## Decision

Introduce the first deterministic governed runtime operation envelope.

## Rationale

Activation authorization is not operation authorization. Once a runtime is activatable, the architecture still needs a replay-visible contract describing what bounded operation may enter it. Structured envelope semantics replace informal command interpretation with explicit payload, policy, boundary, and lineage evidence.

## Boundary

This milestone is pre-executional. It does not add command execution, shell access, subprocess invocation, agents, orchestration, retries, routing, hidden memory, or autonomous continuation.

## Consequence

Runtime operations become structured, bounded, policy-checked, replay-visible, and fail-closed before execution implementation exists.
