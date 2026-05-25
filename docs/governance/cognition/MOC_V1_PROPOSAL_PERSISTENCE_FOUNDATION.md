# MOC_V1_PROPOSAL_PERSISTENCE_FOUNDATION

Status: advisory proposal lifecycle persistence foundation.

## Purpose

`MOC_V1_PROPOSAL_PERSISTENCE_FOUNDATION` creates deterministic replay-visible persistence records for MOC V1 advisory proposal lifecycle transitions.

This milestone persists advisory proposal lifecycle state only.

Proposal does not equal execution.

## Lifecycle States

Supported states:

- `PROPOSED`
- `REJECTED`
- `CORRECTION_REQUIRED`
- `CORRECTED`
- `VALIDATED`
- `APPROVAL_PENDING`
- `APPROVED`
- `PREPARED_FOR_WORKER`
- `FAIL_CLOSED`

There is no execution state.

## Valid Transitions

The valid transition set is:

- `PROPOSED -> VALIDATED`
- `PROPOSED -> REJECTED`
- `REJECTED -> CORRECTION_REQUIRED`
- `CORRECTION_REQUIRED -> CORRECTED`
- `CORRECTED -> VALIDATED`
- `VALIDATED -> APPROVAL_PENDING`
- `APPROVAL_PENDING -> APPROVED`
- `APPROVED -> PREPARED_FOR_WORKER`

Everything else becomes `FAIL_CLOSED` unless explicitly defined by a future governance milestone.

## Persistence Record

The persistence record preserves:

- proposal identity
- proposal hash
- linked contract identity and hash
- requested and effective lifecycle state
- previous state
- correction attempt
- lineage references
- validation references
- correction references
- approval references
- transition validity
- replay-safe and advisory-only guarantees
- deterministic persistence hash

## Governance Boundaries

This milestone is:

- advisory-only
- deterministic
- replay-visible
- governance-safe
- persistence-only

It does not introduce:

- execution authority
- worker dispatch
- orchestration
- provider activation
- autonomous cognition
- proposal execution
- hidden continuation
- runtime cognition loops
- semantic reasoning
- governance mutation
- proposal auto-repair

## CLI

The CLI command:

```bash
aigol moc persist-proposal --proposal <proposal.json> --state <state> --previous-state <state> --json --output <path>
```

reads one explicit proposal artifact, validates the explicit state transition, emits a replay-visible persistence record, and optionally writes it as JSON.

The command does not execute, dispatch workers, activate providers, mutate governance, auto-correct proposals, infer hidden state, generate proposals, or trigger approval automatically.
