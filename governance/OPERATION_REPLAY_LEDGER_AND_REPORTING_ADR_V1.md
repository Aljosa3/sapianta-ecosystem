# OPERATION_REPLAY_LEDGER_AND_REPORTING_ADR_V1

## Decision

Add replay-backed operator operation reporting to the existing replay CLI surface.

## Context

`FIRST_WEEKLY_AIGOL_USAGE_V1` and `FIRST_REAL_WORKFLOW_DISCOVERY_V1` showed that operators had to manually aggregate:

- operation counts;
- success rates;
- fail-closed rates;
- worker usage;
- replay verification failures.

The replay evidence already existed. The missing capability was aggregate visibility.

## Decision Rationale

The smallest useful implementation is:

```text
aigol replay report --runtime-root <runtime-root>
```

This reads existing operator runtime replay directories and verifies each operation through the existing replay verification compatibility path.

## Rejected Alternatives

### New Replay Architecture

Rejected.

Existing operator replay is sufficient.

### New Worker

Rejected.

Reporting is replay inspection, not execution.

### New Provider

Rejected.

No provider behavior is needed for aggregate replay visibility.

### Operation Planning Or Orchestration

Rejected.

The report observes completed operations only.

## Consequences

Operators can now answer:

```text
What happened this week?
How many operations succeeded?
How many failed closed?
Which workers were used?
Which replay chains failed verification?
```

without manual shell aggregation.
