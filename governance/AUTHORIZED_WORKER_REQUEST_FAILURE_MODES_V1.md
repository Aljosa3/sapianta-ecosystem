# AUTHORIZED_WORKER_REQUEST_FAILURE_MODES_V1

## Status

Certified failure modes.

## Fail-Closed Principle

The authorized worker request boundary fails closed on any unresolved mismatch,
missing evidence, invalid lineage, or authority pressure.

## Failure Modes

| Failure Mode | Required Outcome |
| --- | --- |
| missing authorization | FAIL_CLOSED |
| scope mismatch | FAIL_CLOSED |
| worker mismatch | FAIL_CLOSED |
| invalid request lineage | FAIL_CLOSED |
| invalid request metadata | FAIL_CLOSED |
| authorization not found | FAIL_CLOSED |
| malformed request hash | FAIL_CLOSED |
| raw proposal included | FAIL_CLOSED |
| raw provider output included | FAIL_CLOSED |
| raw authorization artifact included | FAIL_CLOSED |
| execution instruction included | FAIL_CLOSED |
| dispatch instruction included | FAIL_CLOSED |

## Failure Artifact Expectations

Failure evidence should record:

- failure reason
- failed boundary
- proposal reference if available
- authorization reference if available
- worker target if available
- explicit non-execution statement

## Certification

No worker may receive a malformed or unresolved authorized worker request.
