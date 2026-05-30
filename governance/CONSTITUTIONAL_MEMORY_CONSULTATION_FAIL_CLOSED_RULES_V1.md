# Constitutional Memory Consultation Fail-Closed Rules V1

Status: fail-closed rules for consultation activation.

## Required Fail-Closed Conditions

Missing artifact: `FAIL_CLOSED`

Missing source: `FAIL_CLOSED`

Ambiguous retrieval: `FAIL_CLOSED`

Multiple conflicting sources: `FAIL_CLOSED`

Invalid source: `FAIL_CLOSED`

Corrupt citation bundle: `FAIL_CLOSED`

Invalid routing evidence: `FAIL_CLOSED`

Unsupported retrieval scope: `FAIL_CLOSED`

Provider-triggered retrieval: `FAIL_CLOSED`

Worker-triggered retrieval: `FAIL_CLOSED`

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

- trigger reference
- retrieval scope attempt
- failure reason
- reference-only status

