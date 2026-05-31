# FIRST_DAILY_AIGOL_USAGE_ADR_V1

## Decision

AiGOL is considered ready for first daily usage within its current bounded scope.

## Context

`AIGOL_OPERATOR_INTERFACE_EXTENSION_V1` made governed operation submission possible through the existing CLI surface.

This milestone tested actual operation rather than designing more architecture.

## Evidence

Observed operation:

```text
Human Request
↓
Provider Proposal
↓
Governed Authorization
↓
Authorized Worker Request
↓
Filesystem Worker
↓
Replay
```

One successful governed operation created `/tmp/first_daily_aigol_usage_v1.txt`.

One negative operation failed closed on unknown worker.

## Decision Rationale

The evidence supports daily usage because:

- the operator can submit a governed operation;
- replay evidence is produced;
- authorization remains visible;
- worker execution is bounded;
- unsupported worker input fails closed;
- no new architecture was needed.

## Rejected Alternatives

### Build More Architecture First

Rejected.

The observed gaps are usability gaps, not foundational architecture gaps.

### Add Orchestration

Rejected.

No evidence from daily usage requires orchestration.

### Add Provider Execution Expansion

Rejected.

The current operation used a deterministic local proposal path. Real provider reliability should be measured separately when a use case requires it.

## Consequences

AiGOL should now be exercised in real tasks before further architectural expansion.

Future changes should be justified by observed operator pain, replay gaps, worker gaps, or reliability evidence.
