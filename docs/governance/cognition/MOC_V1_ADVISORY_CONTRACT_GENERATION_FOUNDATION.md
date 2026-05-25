# MOC_V1_ADVISORY_CONTRACT_GENERATION_FOUNDATION

Status: advisory-only generation foundation.

## Purpose

`MOC_V1_ADVISORY_CONTRACT_GENERATION_FOUNDATION` creates deterministic MOC V1 semantic contract drafts from explicit operator input and immediately validates each generated contract with `MOC_V1_CONTRACT_VALIDATION_FOUNDATION`.

This is the first cautious cognition-behavior milestone. It generates advisory semantic contracts only.

## Generation Scope

The generator accepts explicit input fields:

- `intent_summary`
- `scope`
- `risk_level`
- `mutation_classification`
- `governance_anchors`
- `allowed_actions`
- `forbidden_actions`
- `required_approvals`
- `expected_outputs`
- `deterministic_constraints`

It derives a deterministic `intent_id` from the explicit input and emits a schema-bound semantic contract draft with:

- `advisory_only: true`
- `replay_safe: true`

## Default Safety Additions

Generated contracts include default forbidden actions:

- `execute_task`
- `dispatch_worker`
- `activate_provider`
- `mutate_governance`
- `hidden_continuation`
- `recursive_orchestration`
- `self_authorize`

Generated contracts also include default required approval:

- `human_review`

These defaults are boundary-preserving constraints, not authority grants.

## Validation Gate

Every generated contract is immediately validated by the existing MOC V1 validator.

Generation statuses:

- `GENERATED_VALID`
- `GENERATED_INVALID`
- `INVALID_INPUT`
- `FAIL_CLOSED`

Missing required generation input fails closed. Invalid generated contracts cannot be marked valid.

## Governance Boundaries

This milestone is:

- advisory-only
- schema-bound
- deterministic
- validation-gated
- replay-visible
- non-executing
- non-dispatching

It does not introduce:

- execution authority
- worker dispatch
- provider activation
- orchestration
- autonomous cognition
- autonomous planning
- hidden continuation
- semantic reasoning engine
- hidden inference
- governance mutation
- contract auto-repair
- runtime cognition loops
- task execution

## CLI

The CLI command:

```bash
aigol moc generate-contract --input <generation_input.json> --json --output <path>
```

reads explicit generation input JSON, generates an advisory semantic contract draft, validates it, prints a deterministic summary or JSON result, and optionally writes the generation result artifact.

The command does not create worker tasks, dispatch workers, activate providers, execute contracts, infer hidden meaning, or repair invalid contracts.

## Principle

Proposal does not equal execution.

Cognition does not equal authority.
