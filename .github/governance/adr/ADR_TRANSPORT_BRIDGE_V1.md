# ADR: Transport Bridge v1

## Context

AiGOL already has provider abstraction, execution envelopes, bounded adapter runtime, normalized results, and replay-safe runtime evidence.

The next milestone is deterministic transport delivery between governance-created envelopes and bounded execution providers.

## Decision

Introduce `TRANSPORT_BRIDGE_V1`.

The transport bridge creates a deterministic transport request from a validated execution envelope, binds the request to one explicit provider identity, invokes bounded adapter runtime delivery, returns a transport response, and emits replay-safe transport evidence.

Transport bridge is deterministic bounded execution transport, not orchestration.

## Why Transport Bridge Exists

Transport provides the request/response boundary between governance and execution providers. It makes delivery semantics explicit and replay-visible before any production bridge or real provider execution exists.

## Why Transport Must Remain Bounded

Transport cannot expand authority, mutate governance, mutate replay state, retry silently, fall back silently, or reroute dynamically. It only delivers bounded contracts.

## Why Transport Is Not Orchestration

Orchestration would select providers, schedule work, retry, chain tasks, coordinate multiple agents, or adapt based on runtime behavior. This milestone does none of that.

## Why Replay-Safe Transport Matters

Transport evidence preserves envelope identity, provider identity, replay identity, runtime binding validity, transport binding validity, authority preservation, and workspace preservation.

## Why Providers Cannot Mutate Transport State

Providers are execution workers. They cannot change transport request semantics, mutate runtime binding, alter replay identity, or inject provider-specific permissions.

## Relationship To Prior Milestones

- `PROVIDER_ABSTRACTION_FOUNDATION_V1` defines providers as bounded workers.
- `EXECUTION_ENVELOPE_MODEL_V1` defines bounded execution contracts.
- `EXECUTOR_ADAPTER_RUNTIME_V1` defines explicit adapter runtime delivery.
- `AGOL_LAYER_SEPARATION_MODEL_V1` separates governance, execution, validation, reflection, and interaction authority.

## Consequences

Positive:

- Validated envelopes can be transported to bounded runtime adapters.
- Transport evidence is deterministic and replay-safe.
- Provider identity is enforced.
- Authority and workspace scope are preserved across transport.

Tradeoffs:

- No provider routing exists.
- No fallback or retry exists.
- No production provider API integration exists.

## Explicit Non-Goals

- Autonomous orchestration.
- Autonomous planning.
- Provider routing intelligence.
- Dynamic optimization.
- Retry systems.
- Adaptive fallback.
- Hidden execution.
- Multi-agent coordination.
- Unrestricted provider execution.
- Autonomous scheduling.
- Full production bridge.
