# ADR: HUMAN_APPROVAL_QUEUE_V1

## Context

SAPIANTA introduced advisory reflection after deterministic protocol, transport, and observability layers were established. Before any bounded autonomy or policy engine can exist, advisory proposals require an explicit human governance checkpoint.

The approval boundary prevents reflection output from becoming implicit execution authority.

## Decision

Introduce immutable approval artifacts, approval queue lifecycle, governance decision evidence, and a human-governed approve/reject workflow.

Approval records:

- Source reflection lineage.
- Source task lineage.
- Proposal summary.
- Pending, approved, or rejected state.
- Human decision identity and reason.
- Immutable decision evidence.

Approval does not grant execution authority in v1.

## Consequences

Positive:

- Reflection remains advisory.
- Execution authority remains excluded.
- Human checkpoint becomes explicit.
- Approval decisions become replay-visible.
- Task/reflection lineage is preserved.

Tradeoffs:

- Slower transition toward autonomy.
- Added governance overhead.
- No automatic approval.
- No approval-triggered execution.

## Explicit Non-Goals

- Execution.
- Automatic approval.
- Policy engine.
- Bounded autonomy.
- Recursive orchestration.
- Runtime authority escalation.
