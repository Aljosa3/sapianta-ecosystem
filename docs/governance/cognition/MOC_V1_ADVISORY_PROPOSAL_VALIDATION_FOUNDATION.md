# MOC_V1_ADVISORY_PROPOSAL_VALIDATION_FOUNDATION

Status: advisory proposal validation foundation.

## Purpose

`MOC_V1_ADVISORY_PROPOSAL_VALIDATION_FOUNDATION` validates explicit advisory proposals that reference already-validated MOC V1 semantic contracts.

This milestone validates advisory proposals only.

Proposal does not equal execution.

## Proposal Role

A semantic contract defines governance-bounded cognition structure.

An advisory proposal defines a bounded suggested operational action. It remains advisory-only, replay-visible, and non-executing.

## Validation Scope

The validator checks:

- proposal structure
- linked validated semantic contract reference
- linked contract hash match
- `advisory_only: true`
- `replay_safe: true`
- suggested actions remain within contract `allowed_actions`
- suggested actions do not appear in contract `forbidden_actions`
- `approvals_required` includes `human_review`
- forbidden proposal authority fields are absent
- replay-visible validation evidence is produced

## Status Classes

Validation may return:

- `VALID`
- `INVALID_SCHEMA`
- `INVALID_BOUNDARY`
- `INVALID_CONTRACT_REFERENCE`
- `UNKNOWN_INSUFFICIENT_EVIDENCE`
- `FAIL_CLOSED`

Malformed proposal JSON fails closed.

## Forbidden Proposal Fields

The validator rejects explicit authority fields including:

- `execution_authority`
- `dispatch_authority`
- `provider_activation`
- `orchestration_authority`
- `autonomous_continuation`
- `governance_mutation`
- `recursive_worker_spawn`
- `self_authorization`

## Governance Boundaries

This milestone is:

- advisory-only
- deterministic
- replay-visible
- validation-only
- governance-safe
- non-executing

It does not introduce:

- execution authority
- worker dispatch
- orchestration
- autonomous cognition
- provider activation
- hidden continuation
- proposal execution
- semantic reasoning engine
- hidden inference
- governance mutation
- proposal auto-repair
- runtime cognition loops

## CLI

The CLI command:

```bash
aigol moc validate-proposal --proposal <proposal.json> --contract <validated_contract.json> --json --output <path>
```

reads an explicit proposal JSON file, reads explicit validated contract evidence, validates proposal boundaries and contract linkage, prints a deterministic summary or JSON result, and optionally writes the validation artifact.

The command does not execute, dispatch, activate providers, mutate proposals, mutate contracts, repair proposals, infer hidden meaning, or generate new proposals.
