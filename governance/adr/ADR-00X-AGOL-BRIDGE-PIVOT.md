# ADR-00X - AGOL Bridge Pivot:
Governed Execution Bridge over Full Autonomous Runtime

# Status

Accepted

# Context

The current AGOL operational workflow depends on three distinct roles:

- ChatGPT performs semantic reasoning.
- Human operators manually transport intent and context through copy and paste.
- Codex performs bounded execution.

This workflow preserves human oversight, but it creates operational friction. Manual transport slows iteration, breaks continuity between reasoning and execution, fragments governance context, and makes replay evidence harder to preserve across the full lifecycle.

The project currently over-invests in autonomous semantic infrastructure while under-investing in governed transport, operational continuity, and replay-safe execution workflows.

The architectural need is not a larger autonomous semantic runtime. The immediate need is a governed bridge that preserves context, replay identity, confirmation boundaries, and execution evidence between existing reasoning and execution layers.

# Decision

AGOL v1 will evolve as a governed execution bridge.

AGOL v1 will not evolve as a full autonomous semantic operating system.

The selected architecture preserves the following role boundaries:

- ChatGPT remains the cognition layer and semantic reasoning layer.
- Codex remains the execution layer.
- AGOL becomes the governance layer, replay layer, lifecycle layer, and transport substrate.

This decision prioritizes governed movement of intent, context, approval state, execution requests, and replay evidence across the operator workflow. It does not grant AGOL independent semantic authority or autonomous planning authority.

# Architectural Principle

Reasoning remains model-native.
Governance becomes system-native.

# Positive Consequences

- Reduced architectural complexity.
- Faster implementation of operationally useful workflows.
- Lower manual transport friction.
- Immediate improvement in operator continuity.
- Preserved governance guarantees.
- Clearer separation between reasoning, governance, and execution.
- Model-agnostic future potential because the bridge governs lifecycle and transport rather than embedding one reasoning engine as constitutional authority.

# Negative Consequences

- Semantic normalization is deferred.
- Domain inference is deferred.
- Reasoning remains non-deterministic.
- Semantic replay remains incomplete in v1.
- Some governance evidence will describe transport and approval continuity before it can describe deterministic semantic interpretation.

# Non-Goals

AGOL v1 intentionally excludes:

- autonomous semantic planning;
- hidden orchestration;
- unrestricted autonomy;
- self-modifying governance;
- multi-agent routing;
- semantic inference engine.

# Governance Alignment

The governed execution bridge aligns with the existing governance model by preserving fail-closed execution, replayability, deterministic governance checks, bounded execution, and explicit approval boundaries.

The bridge does not replace human authority. It preserves operator confirmation points and makes lifecycle state more visible. It does not convert model reasoning into execution authority. It records and transports governed intent so downstream execution can remain bounded, reviewable, and replay-safe.

# Consequences for Future Architecture

Semantic governance may be added later as a bounded governance layer after transport continuity is stable.

Transport governance is prioritized first because it directly reduces operational discontinuity without expanding autonomous authority.

The bridge architecture becomes the substrate for future workers, provided those workers remain governed by explicit boundaries, replay evidence, deterministic validation, and approval controls.

# References

- AGOL Bridge Transport Spec v1.
- Existing replay-safe governance principles.
- Existing fail-closed execution and bounded approval principles.
