# Memory Based Response Fail-Closed Rules V1

Status: fail-closed model for future Memory-Based Response implementation.

## Required Fail-Closed Conditions

Missing citation bundle: `FAIL_CLOSED`

Invalid citation bundle: `FAIL_CLOSED`

Corrupt citation bundle: `FAIL_CLOSED`

Missing consultation record: `FAIL_CLOSED`

Conflicting references: `FAIL_CLOSED`

Ambiguous references: `FAIL_CLOSED`

Uncited response content: `FAIL_CLOSED`

Authority-bearing response content: `FAIL_CLOSED`

Corrupt response record: `FAIL_CLOSED`

Replay corruption: `FAIL_CLOSED`

Append-only replay violation: `FAIL_CLOSED`

## No Silent Recovery

Response construction must not:

- infer missing citations
- substitute artifacts
- invent constitutional conclusions
- smooth over conflicting sources
- invoke a provider to fill gaps
- invoke a worker to validate gaps
- continue into execution or authorization

## Failure Evidence

Failures must remain replay-visible and preserve failure reason, consultation reference when available, and reference-only status.
