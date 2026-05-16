# ADR_GOVERNED_RUNTIME_EXECUTION_SURFACE_V1

## Decision

Introduce the first deterministic executable runtime surface layer.

## Rationale

Capability authorization alone still leaves a semantic gap between an allowed executor primitive and the bounded runtime surface that may realize it. Static executor-to-surface mapping removes that remaining manual interpretation.

## Boundary

This layer does not execute commands, infer surfaces dynamically, auto-discover executors, or permit raw shell, unrestricted subprocess, unrestricted network execution, or autonomous runtime expansion.
