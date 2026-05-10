# ADR: Finalize Constitutional Governance Foundation

Status: accepted.

## Context

SAPIANTA governance evolved through audit, constitutional reconstruction, canonical specification, conformance verification, and replay-safe evidence generation. The architecture contained multiple layer taxonomies, distributed enforcement surfaces, domain-specific constitutional components, and known partial enforcement gaps.

Without canonical finalization, future contributors or Codex instances could misread dormant governance memory as runtime activation, conflate layer models, or treat documentation-only governance as enforcement.

## Decision

Finalize the constitutional governance subsystem as an evidence-backed, replay-safe governance foundation.

The finalization locks:

- canonical constitutional semantics;
- canonical layer meanings;
- invariant semantics;
- enforcement hierarchy semantics;
- governance lineage semantics;
- scope and mutation boundaries.

It preserves known limitations rather than hiding them.

## Rationale

Constitutional formalization was required because SAPIANTA is not merely a system with policy documents. It is a constrained autonomous system whose development and governance flows depend on protected mutation boundaries, replay evidence, certification gates, and fail-closed behavior.

Canonicalization occurred to resolve the L0-L4 mutation model and the separate safety authority model without erasing either one.

Conformance verification exists to bridge documented constitution and actual enforcement.

Replay-safe governance matters because governance evidence must remain inspectable, reproducible, and resistant to silent drift.

Governance is treated as runtime infrastructure because mutation boundaries, certification gates, replay verification, and development guards directly constrain what the system may generate, certify, or activate.

## Consequences

Future governance evolution must preserve this finalization baseline or explicitly supersede it with governed evidence.

Known hook drift remains visible as a limitation and does not get silently converted into conformance.

The finalization does not add runtime execution, autonomous mutation, broker/API integration, or AI reasoning.

