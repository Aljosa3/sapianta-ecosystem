# ADR: CODEX_BRIDGE_TRANSPORT_MVP_V1

## Context

Bounded execution transport was introduced only after `BRIDGE_PROTOCOL_V0_1_FINAL` and `BRIDGE_SCHEMA_VALIDATOR_INTEGRATION_V1` established deterministic schemas, validation contracts, lifecycle constraints, replay-safe hashing, lineage checks, enforcement gates, and quarantine handling.

This sequencing ensures the transport cannot define its own governance semantics or bypass protocol enforcement.

## Decision

Introduce single-task Codex transport with protocol validation, lock acquisition, bounded subprocess execution, canonical result generation, result validation, and append-only replay logging.

Codex remains non-authoritative. The governance substrate remains authoritative.

## Consequences

Positive:

- Removes manual copy/paste bottleneck.
- Creates governed execution transport.
- Preserves Codex as non-authoritative.
- Produces replay-safe runtime evidence.
- Establishes foundation for future observability and reflection.

Tradeoffs:

- No recursion.
- No auto-follow-up execution.
- No systemd daemon yet.
- No autonomous orchestration.
- Additional governance overhead.

## Explicit Non-Goals

- Recursion.
- Reflection orchestration.
- Auto-repair.
- Auto-merge.
- Auto-push.
- Autonomous chaining.
- Runtime authority escalation.
- Systemd daemonization.

