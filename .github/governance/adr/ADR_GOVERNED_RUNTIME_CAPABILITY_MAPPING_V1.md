# ADR_GOVERNED_RUNTIME_CAPABILITY_MAPPING_V1

## Decision

Introduce deterministic governed runtime capability mapping.

## Rationale

Allowed operation types still need a bounded executable realization. Static operation-to-executor mapping removes manual interpretation while preserving governance limits and replay-safe evidence.

## Boundary

This layer does not execute commands, invent executors, add agents, orchestrate runtime work, route providers, or permit raw shell, unrestricted subprocess, or unrestricted network execution.
