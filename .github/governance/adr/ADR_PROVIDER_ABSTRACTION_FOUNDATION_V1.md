# ADR: Provider Abstraction Foundation v1

## Context

AGOL already has a canonical stabilization baseline, a layer separation model, and governance worktree hygiene.

This milestone builds the first provider-independent execution substrate on top of those guarantees without adding runtime routing, orchestration, execution envelopes, optimization, or adaptive provider selection.

## Decision

Introduce deterministic provider abstraction contracts:

- explicit provider identity;
- bounded provider contract;
- normalized execution result;
- passive provider registry;
- structural provider adapters.

Providers are bounded execution implementations, not governance authorities.

## Why Provider Abstraction Matters

Provider abstraction lets Codex, Claude Code, local executors, deterministic mocks, and future executors remain replaceable without changing governance semantics.

This protects AGOL from coupling governance meaning to any single execution provider.

## Why Governance Must Remain Provider-Independent

Governance controls admissibility, risk, replay identity, and constraints. Provider identity must not alter governance authority, validation semantics, certification semantics, or replay semantics.

## Why Normalized Results Are Necessary

Providers produce different native outputs. Normalized results keep governance interpretation stable by requiring the same replay-compatible fields and forbidding provider-side governance mutation.

## Why Replay-Safe Provider Identity Matters

Provider identity must be explicit, deterministic, and immutable during execution so replay evidence can compare executions without hidden provider authority drift.

## Relationship To Prior Milestones

- `STABILIZATION_CERTIFICATION_EPOCH_V1` provides the canonical collection and replay baseline.
- `AGOL_LAYER_SEPARATION_MODEL_V1` establishes that execution providers are separate from governance authority.
- `GOVERNANCE_WORKTREE_HYGIENE_V1` protects provider abstraction artifacts from transient runtime pollution.

## Consequences

Positive:

- Execution providers become replaceable bounded workers.
- Governance semantics remain provider-independent.
- Provider metadata becomes deterministic and replay-safe.
- Future execution envelopes can target a stable provider interface.

Tradeoffs:

- Real provider execution remains out of scope.
- No routing or dynamic selection is available yet.
- Adapters are structural placeholders only.

## Explicit Non-Goals

- Runtime routing.
- Provider optimization.
- Orchestration.
- Dynamic scheduling.
- Autonomous provider selection.
- Hidden fallback logic.
- Execution envelope implementation.
- Multimodal orchestration.
- Adaptive runtime behavior.
- Provider intelligence ranking.
