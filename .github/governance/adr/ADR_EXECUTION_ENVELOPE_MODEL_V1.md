# ADR: Execution Envelope Model v1

## Context

AiGOL now has deterministic collection stabilization, layer separation, governance worktree hygiene, and provider abstraction.

The next structural step is a canonical bounded execution transport contract between governance and execution providers.

## Decision

Introduce `EXECUTION_ENVELOPE_MODEL_V1`.

Execution envelopes bind provider identity, workspace scope, authority scope, allowed and forbidden actions, timeout semantics, replay identity, validation requirements, and deterministic constraints.

Execution envelopes are bounded authority transport contracts, not execution orchestration systems.

## Why Bounded Execution Matters

Providers must never receive unconstrained authority or undefined execution scope. Explicit envelopes prevent implicit permissions and make execution authority replay-visible.

## Why Providers Need Constrained Authority

Providers are bounded workers, not governance authorities. The envelope defines what they may do and what they must not do.

## Why Replay-Safe Transport Contracts Are Necessary

Replay binding ensures the same envelope yields the same authority semantics across providers and validation runs.

## Why Execution Scope Must Be Explicit

Workspace roots, forbidden paths, generated artifact areas, allowed actions, forbidden actions, constraints, and validation requirements must all be visible before execution can occur.

## Why Provider-Independent Envelopes Matter

Codex, Claude, local executors, and deterministic executors must interpret the same envelope semantics. Provider-specific authority behavior is forbidden.

## Relationship To Prior Milestones

- `STABILIZATION_CERTIFICATION_EPOCH_V1` provides the replay-safe substrate baseline.
- `AGOL_LAYER_SEPARATION_MODEL_V1` separates governance, execution, validation, interaction, and reflection authority.
- `GOVERNANCE_WORKTREE_HYGIENE_V1` prevents transient runtime pollution in governance lineage.
- `PROVIDER_ABSTRACTION_FOUNDATION_V1` defines providers as replaceable bounded workers.

## Consequences

Positive:

- Execution authority becomes explicit and replay-bound.
- Providers receive bounded, provider-independent contracts.
- Undefined permissions fail closed.
- Future transport can validate authority before execution.

Tradeoffs:

- No runtime orchestration exists yet.
- No provider routing or fallback exists yet.
- Real provider API integration remains out of scope.

## Explicit Non-Goals

- Runtime orchestration.
- Autonomous execution.
- Provider routing.
- Provider optimization.
- Dynamic scheduling.
- Adaptive retry logic.
- Hidden fallback execution.
- Real provider API integration.
- Autonomous planning.
- Autonomous task chaining.
