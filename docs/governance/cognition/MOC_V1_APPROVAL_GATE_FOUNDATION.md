# MOC_V1_APPROVAL_GATE_FOUNDATION

Status: operational approval boundary foundation.

## Purpose

`MOC_V1_APPROVAL_GATE_FOUNDATION` creates the first formal operational approval boundary for MOC V1 advisory proposals.

Approval does not equal execution.

Approval only grants eligibility for worker preparation.

## Approval Inputs

The gate requires explicit evidence:

- proposal artifact
- appended proposal ledger entry
- human approval evidence

Missing or malformed evidence fails closed.

## Approval Statuses

The approval gate may return:

- `APPROVED_FOR_WORKER_PREPARATION`
- `APPROVAL_REJECTED`
- `APPROVAL_PENDING`
- `INVALID_APPROVAL_EVIDENCE`
- `FAIL_CLOSED`

## Eligibility Rules

Approval eligibility requires:

- proposal is already `VALIDATED`
- proposal lineage exists
- proposal exists in proposal ledger
- `replay_safe: true`
- `advisory_only: true`
- human review approval exists
- correction loop is not unresolved
- forbidden authority fields are absent
- no hidden continuation evidence exists

## Boundary Guarantees

This milestone is:

- advisory-governed
- deterministic
- replay-visible
- governance-safe
- approval-only

It does not introduce:

- execution authority
- worker dispatch
- provider activation
- orchestration
- autonomous cognition
- hidden continuation
- runtime cognition loops
- semantic reasoning
- governance mutation
- automatic execution
- autonomous approval
- proposal repair

## Worker Preparation Boundary

`APPROVED_FOR_WORKER_PREPARATION` means only that a proposal is eligible for a future worker-preparation boundary.

It does not:

- execute
- dispatch
- activate workers
- activate providers
- bypass additional governance checks

## CLI

The CLI command:

```bash
aigol moc approval-gate --proposal <proposal.json> --ledger-entry <ledger_entry.json> --approval-evidence <approval.json> --json --output <path>
```

reads explicit evidence, evaluates approval eligibility, emits a replay-visible approval artifact, and optionally writes the result JSON.

The command does not execute proposals, dispatch workers, activate providers, mutate governance, mutate the ledger, mutate proposals, auto-approve, infer hidden meaning, or trigger worker preparation automatically.
