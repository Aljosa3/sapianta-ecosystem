# ADR: FIRST_OPERATIONAL_GOVERNED_AI_EXECUTION_EPOCH_V1

## Status

Accepted.

## Context

SAPIANTA now has replay-visible evidence for the first bounded live provider execution path: ingress, natural-language-to-envelope interpretation, governed session binding, provider transport, explicit execution gating, bounded Codex runtime, live validation, runtime stabilization, and deterministic result capture.

The substrate has crossed from experimental governed execution components into an operational governed execution foundation. That transition needs a formal freeze so later work cannot blur the boundary between operational execution and autonomy.

## Decision

Finalize `FIRST_OPERATIONAL_GOVERNED_AI_EXECUTION_EPOCH_V1` with operational status `FOUNDATIONAL_OPERATIONAL`.

This epoch certifies:

- first real governed provider execution
- first deterministic bounded result capture
- first governed result return continuity
- first operational replay-safe worker execution

The epoch preserves fail-closed behavior, deterministic replay, bounded runtime execution, `shell=False`, explicit human authorization, workspace containment, timeout containment, lineage preservation, and explicit evidence generation.

## Boundaries

The epoch is not `FULLY_AUTONOMOUS`.

It does not introduce orchestration, autonomous continuation, retries, routing, multimodal execution, async/background execution, distributed workers, or persistent memory.

## Consequences

The repository now has a frozen operational governed execution foundation for future bounded evolution. Future work must build on this evidence without reclassifying bounded governed execution as autonomous execution or weakening the replay-safe constitutional boundary.
