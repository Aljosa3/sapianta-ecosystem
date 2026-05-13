# ADR: AGOL Layer Separation Model v1

## Context

AGOL needs a canonical authority model before provider abstraction, execution envelopes, executor routing, or future bounded autonomy can be implemented safely.

The repository now has `STABILIZATION_CERTIFICATION_EPOCH_V1` as the replay-safe certification substrate baseline. That epoch restored deterministic collection and honest separation between collection stability and execution correctness.

Layer separation builds on that baseline. It must not redefine or mutate stabilization semantics.

## Decision

Introduce `AGOL_LAYER_SEPARATION_MODEL_V1` with five canonical layers:

- `INTERACTION_LAYER`
- `GOVERNANCE_LAYER`
- `EXECUTION_LAYER`
- `VALIDATION_LAYER`
- `REFLECTION_LAYER`

AGOL acts as a governance/control plane, not execution intelligence.

Interaction intelligence may create proposals, explain outcomes, and summarize evidence. It does not execute.

Governance remains independent and controls admissibility before execution.

Execution providers remain bounded workers inside a supplied envelope.

Validation remains isolated and determines artifact validity without hidden repair or silent mutation.

Reflection remains advisory-only and cannot enqueue tasks or trigger execution.

## Why Interaction Is Not Execution

Conversational systems can reason, explain, propose, and interpret, but those abilities must not imply execution authority. The permanent invariant is:

```text
INTERACTION_LAYER != EXECUTION_LAYER
```

This protects provider replaceability and prevents accidental authority inheritance.

## Why Governance Must Remain Independent

Governance classifies intent, determines admissibility, assigns risk, requires approval, and constrains execution. If execution or reflection can bypass governance, replay-safe authority separation collapses.

## Why Validation Must Remain Isolated

Validation certifies, rejects, and verifies determinism. It cannot plan execution, repair silently, or retry execution without explicit governance flow.

## Why Reflection Is Advisory-Only

Reflection interprets evidence and proposes future directions. It cannot execute, enqueue tasks, escalate autonomously, mutate governance, or trigger providers.

## Provider Abstraction Rationale

Provider abstraction requires authority separation because Codex, Claude Code, Gemini, local executors, and deterministic tools must be replaceable without changing governance semantics.

Provider identity must not affect governance decisions. Replay evidence format must remain stable across providers.

## Consequences

Positive:

- Authority boundaries become explicit.
- Provider replacement becomes safer.
- Replay evidence can remain provider-independent.
- Interaction intelligence remains distinct from execution authority.
- Future execution envelopes have a stable control-plane model.

Tradeoffs:

- More explicit contracts are required.
- Cross-layer communication is narrower.
- Future executor routing cannot bypass governance.

## Explicit Non-Goals

- Autonomous orchestration.
- Adaptive routing.
- Runtime executor optimization.
- Multi-agent coordination.
- Hidden planning.
- Recursive autonomy.
- Provider selection intelligence.
- Token optimization logic.
- Execution scheduling.
- Runtime mutation authority.
