# UNIFIED_REPLAY_RECONSTRUCTION_ADR_V1

## Status

Accepted foundation decision.

## Decision

AiGOL will define a unified replay reconstruction model that can inspect complete or partial chains across conversation, source routing, execution lifecycle, governed learning lifecycle, learning-to-execution bridge, worker evidence, and replay evidence.

Future runtime should produce:

```text
UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1
```

The report is read-only and inspection-only.

## Context

AiGOL has certified:

- Execution Lifecycle;
- Governed Learning Lifecycle;
- Learning-to-Execution Bridge;
- Replay Inspector Worker;
- Interactive Conversation CLI.

`AIGOL_CLI_PRIMARY_INTERFACE_READINESS_V1` identified the primary missing capability:

```text
Unified replay reconstruction and chain inspection.
```

## Rationale

The CLI cannot become the primary operator interface until a human can inspect:

- latest chain;
- chain by id;
- learning lifecycle;
- execution lifecycle;
- bridge lineage;
- full chain lineage;
- missing evidence;
- corruption;
- authority boundaries.

Unified reconstruction provides the canonical model for those future CLI commands.

## Decision Rules

1. `canonical_chain_id` is the preferred identity.
2. Compatibility reconstruction may use references and hashes where older artifacts lack `canonical_chain_id`.
3. Compatibility lineage must not be written back as canonical identity.
4. Replay reconstruction is read-only.
5. Reconstruction may report `INCOMPLETE`, `CORRUPT`, `AMBIGUOUS`, or `FAILED_CLOSED`.
6. Reconstruction may not infer missing authorization.
7. Reconstruction may not repair corrupt evidence.
8. Reconstruction may not merge unrelated chains by timestamp alone.
9. Reconstruction must preserve lifecycle boundaries.
10. Future CLI commands must present safe next actions without creating hidden execution authority.

## Consequences

AiGOL gains a canonical foundation for future commands:

```text
show latest chain
inspect chain <CHAIN_ID>
show learning lifecycle
show execution lifecycle
explain chain lineage
reconstruct full chain
```

This foundation directly addresses a major blocker in CLI primary-interface readiness.

## Non-Goals

This ADR does not implement:

- unified reconstruction runtime;
- CLI commands;
- replay mutation;
- governance mutation;
- chain id propagation changes;
- approval management;
- execution request creation;
- dispatch;
- invocation;
- execution;
- self-improvement.

## Final Decision

Unified Replay Reconstruction is accepted as a foundation model.

```text
UNIFIED_REPLAY_RECONSTRUCTION_FOUNDATION_STATUS = READY_WITH_GAPS
```
