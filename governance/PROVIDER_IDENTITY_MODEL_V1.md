# Provider Identity Model V1

Status: canonical provider identity model for attachment architecture.

## Provider Definition

Provider is defined as:

```text
external proposal producer
```

Provider is not:

- worker
- governance component
- authority component
- replay component
- memory component

## Required Identity Fields

Provider attachment must identify:

- `provider_id`
- `provider_type`
- `provider_version`
- `provider_adapter_version`
- `provider_identity_hash`

## Identity Requirements

Provider identity must be:

- explicit
- replay-visible
- stable for the duration of one provider request
- reconstructable from replay
- non-authoritative

## Authority Boundary

Provider identity identifies proposal source only.

It must not imply:

- permission to execute
- permission to authorize
- permission to govern
- permission to dispatch
- permission to mutate replay or memory
