# REPLAY_VERIFY_OPERATOR_RUNTIME_COMPATIBILITY_ADR_V1

## Decision

Extend the existing `aigol replay verify` command to recognize the existing operator runtime replay layout.

## Context

`aigol replay operation` could reconstruct operator runtime replay, but `aigol replay verify` still assumed governed-return ledger evidence.

This created a false negative:

```text
operator replay exists
replay operation succeeds
replay verify fails
```

## Decision Rationale

This is a compatibility issue, not a replay architecture issue.

The smallest correct change is:

1. If `<runtime_root>/<replay_identity>` exists as an operator operation directory, verify it with existing operator replay reconstruction helpers.
2. If it does not exist, use the existing governed-return verification path unchanged.

## Rejected Alternatives

### Replay Redesign

Rejected.

The existing operator replay is reconstructable.

### Replay Migration

Rejected.

No evidence requires moving existing replay artifacts.

### New Replay Model

Rejected.

The issue was recognition by `replay verify`, not replay structure.

## Consequences

After this fix:

```text
aigol replay operation --operation-id <id>
```

and:

```text
aigol replay verify --replay-identity <id>
```

can both succeed for the same operator runtime replay.

Legacy governed-return verification remains available through the same command when no operator operation directory is present.
