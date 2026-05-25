# MOC_V1_CONTRACT_VALIDATION_FOUNDATION

Status: validation-only foundation.

## Purpose

`MOC_V1_CONTRACT_VALIDATION_FOUNDATION` validates whether an explicit MOC V1 semantic contract conforms to the canonical schema and boundary guarantees.

This milestone validates semantic contracts. It does not generate semantic contracts, execute them, route them to workers, infer missing meaning, or repair invalid contracts.

## Validation Scope

The validator checks:

- schema conformance against `schemas/semantic_contract.schema.json`
- `advisory_only: true`
- `replay_safe: true`
- absence of forbidden authority fields
- explicit required approvals
- explicit forbidden actions
- presence of deterministic constraints
- valid `risk_level`
- valid `mutation_classification`
- deterministic replay-visible validation evidence

## Status Classes

Validation may return:

- `VALID`
- `INVALID_SCHEMA`
- `INVALID_BOUNDARY`
- `UNKNOWN_INSUFFICIENT_EVIDENCE`
- `FAIL_CLOSED`

Malformed JSON fails closed.

## Boundary Checks

The validator fails contracts that explicitly contain forbidden authority fields, including:

- `execution_authority`
- `dispatch_authority`
- `provider_activation`
- `autonomous_continuation`
- `orchestration_authority`
- `mutation_authority`
- `governance_mutation`
- `hidden_continuation`
- `recursive_worker_spawn`
- `self_authorization`
- `semantic_repair`
- `authority_issuance`

The validator only inspects explicit fields. It does not infer semantic intent.

## Governance Guarantees

This milestone is:

- validation-only
- schema-bound
- deterministic
- fail-closed
- replay-visible

It does not introduce:

- execution authority
- orchestration
- autonomous cognition
- planning
- proposal generation
- worker dispatch
- provider activation
- semantic reasoning
- hidden inference
- governance mutation
- semantic repair
- contract auto-correction
- runtime cognition loops

## CLI

The CLI command:

```bash
aigol moc validate-contract --input <semantic_contract.json> --json --output <path>
```

reads one semantic contract JSON file, validates it, prints a deterministic summary or JSON result, and optionally writes the validation result artifact.

The command does not mutate the contract.
