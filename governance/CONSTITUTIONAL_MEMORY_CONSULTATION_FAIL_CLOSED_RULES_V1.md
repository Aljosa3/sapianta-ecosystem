# Constitutional Memory Consultation Fail-Closed Rules V1

Status: implemented fail-closed rules for `CONSTITUTIONAL_MEMORY_CONSULTATION_ACTIVATION_V1`.

## Required Fail-Closed Conditions

Missing routing record: `FAIL_CLOSED`

Invalid routing record: `FAIL_CLOSED`

Corrupt routing record: `FAIL_CLOSED`

Non-memory destination: `FAIL_CLOSED`

Authority-bearing routing record: `FAIL_CLOSED`

Replay corruption: `FAIL_CLOSED`

Append-only replay violation: `FAIL_CLOSED`

Unsupported retrieval scope: `FAIL_CLOSED`

Missing source: `FAIL_CLOSED`

Invalid source: `FAIL_CLOSED`

Ambiguous source: `FAIL_CLOSED`

Corrupt citation bundle: `FAIL_CLOSED`

Authority-bearing retrieval request: `FAIL_CLOSED`

## No Silent Recovery

Activation must not:

- guess source
- substitute artifacts
- infer missing rules
- silently resolve conflicts
- retry automatically
- continue into answer, execution, provider, or worker paths

## Failure Evidence

Failure must be replay-visible and preserve:

- routing reference when available
- retrieval scope attempt
- failure reason
- reference-only status

Failures must not fabricate citation evidence.
