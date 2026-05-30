# Provider Lifecycle Model V1

Status: canonical provider lifecycle model for attachment architecture.

## Allowed States

Provider lifecycle states are:

```text
DETACHED
ATTACHED
AVAILABLE
UNAVAILABLE
DETACHED
```

## State Meanings

`DETACHED`: provider is not connected to AiGOL.

`ATTACHED`: provider adapter identity and boundary have been registered for use.

`AVAILABLE`: provider can receive bounded proposal requests.

`UNAVAILABLE`: provider cannot currently return a proposal.

`DETACHED`: provider attachment has ended or been removed.

## Lifecycle Boundaries

Lifecycle state must not imply:

- execution
- authorization
- governance
- dispatch
- provider authority
- worker authority

## Fail-Closed Rule

Any unknown, ambiguous, corrupted, or unsupported lifecycle state fails closed.
