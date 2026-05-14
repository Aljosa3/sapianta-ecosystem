# Provider Abstraction Foundation v1

This package defines the first canonical provider abstraction substrate for AGOL.

Execution providers are interchangeable bounded workers. AGOL remains the governance/control substrate.

## Provider Abstraction Philosophy

Providers implement bounded execution. They do not own governance, validation, replay semantics, approval, scheduling, orchestration, or provider selection.

Permanent invariant:

```text
PROVIDER != GOVERNANCE
```

## Provider Contracts

Every provider contract must declare:

- explicit provider identity;
- provider type;
- bounded execution;
- no governance authority;
- replay safety;
- no self-authorization;
- no governance mutation;
- no replay mutation;
- no authority escalation;
- no validation bypass.

## Normalized Execution Semantics

All providers return `NormalizedExecutionResult` with stable fields:

- `provider_id`
- `execution_status`
- `artifacts_created`
- `tests_executed`
- `governance_modified`
- `execution_time_ms`
- `replay_safe`

Provider-specific output must not change governance interpretation semantics.

## Provider Identity

Provider identity is explicit, normalized, replay-safe, and immutable during execution. Provider identity must not alter governance authority, validation semantics, or replay semantics.

## Registry Boundary

The provider registry is passive metadata. It registers providers, validates contracts, and exposes metadata. It does not route, schedule, optimize, select, or orchestrate.

## Adapters

Adapters are structural placeholders:

- `CodexAdapter`
- `ClaudeAdapter`
- `LocalAdapter`
- `DeterministicMockAdapter`

They do not connect real APIs, implement routing, or perform orchestration.

## Authority Separation

Governance authority belongs to governance. Validation authority belongs to validation. Interaction intelligence is separate from execution. Providers are bounded execution implementations only.
