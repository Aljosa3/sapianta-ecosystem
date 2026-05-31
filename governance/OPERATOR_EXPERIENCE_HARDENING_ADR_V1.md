# OPERATOR_EXPERIENCE_HARDENING_ADR_V1

## Decision

Improve the existing operator interface by adding:

- deterministic default operation ids;
- inline replay summary;
- operation-id replay lookup;
- explicit operator status visibility.

## Context

`FIRST_DAILY_AIGOL_USAGE_V1` proved that AiGOL can be operated today, but with friction.

The observed gaps were usability gaps:

- operation ids were manual;
- replay navigation required direct path inspection;
- operation status was visible but not separated from operator readiness;
- replay summary was not shown inline.

## Decision Rationale

These improvements reduce friction without changing the governed path:

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

No new authority is introduced.

## Rejected Alternatives

### New Operator CLI Framework

Rejected.

`AIGOL_OPERATOR_INTERFACE_STATE_REVIEW_V1` and `AIGOL_OPERATOR_INTERFACE_EXTENSION_V1` already established that the existing CLI surface should be extended.

### New Replay Architecture

Rejected.

The existing provider, authorization, and worker replay reconstruction helpers are sufficient for operation-level summary.

### New Worker Or Provider

Rejected.

Daily-use evidence did not justify expanding workers or providers for this milestone.

## Consequences

Operators can now run a governed operation with fewer required fields and inspect replay by operation id.

Future operator hardening should continue to require observed usage evidence before implementation.
