# Provider Replay Visibility V1

Status: provider replay visibility model.

## Mandatory Replay Fields

Provider attachment replay must record:

- `provider_id`
- `provider_type`
- `provider_version`
- request reference
- response reference
- request timestamp
- response timestamp
- proposal hash
- provider lifecycle state
- failure status when applicable

## Reconstruction Requirement

Replay must answer:

```text
What did the provider return?
```

without granting authority to the provider output.

## Replay Boundary

Replay may preserve provider evidence.

Replay must not:

- authorize provider output
- execute provider output
- mutate provider output
- convert provider response into governance decision
- hide provider identity

## Certification

Provider replay visibility is mandatory for implementation readiness.
