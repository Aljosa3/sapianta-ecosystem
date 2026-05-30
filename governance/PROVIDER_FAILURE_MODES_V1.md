# Provider Failure Modes V1

Status: provider attachment failure mode model.

## Failure Modes

Timeout: `FAIL_CLOSED`

Unavailable provider: `FAIL_CLOSED`

Malformed response: `FAIL_CLOSED`

Provider drift: `FAIL_CLOSED`

Provider replacement: `FAIL_CLOSED_UNTIL_REVALIDATED`

Incompatible provider version: `FAIL_CLOSED`

Missing provider identity: `FAIL_CLOSED`

Invalid provider identity: `FAIL_CLOSED`

Replay discontinuity: `FAIL_CLOSED`

Proposal hash mismatch: `FAIL_CLOSED`

## No Silent Recovery

Provider attachment must not:

- silently switch providers
- retry into a different provider
- fabricate provider output
- normalize malformed output into authority
- continue without replay evidence

## Failure Evidence

Every provider failure must preserve:

- provider identity when available
- failure class
- lifecycle state
- timestamp
- replay reference
- fail-closed status
