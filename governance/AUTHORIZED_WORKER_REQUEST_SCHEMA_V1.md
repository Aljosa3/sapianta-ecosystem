# AUTHORIZED_WORKER_REQUEST_SCHEMA_V1

## Status

Certified schema model.

## Required Fields

```json
{
  "request_id": "string",
  "authorization_id": "string",
  "worker_id": "string",
  "authorized_scope": "string",
  "request_timestamp": "string",
  "request_hash": "string"
}
```

## Required Lineage Fields

```json
{
  "proposal_reference": "string",
  "authorization_hash": "string",
  "capability_binding": "string",
  "replay_reference": "string"
}
```

## Required Boundary Fields

```json
{
  "request_type": "AUTHORIZED_WORKER_REQUEST",
  "worker_invoked": false,
  "dispatch_performed": false,
  "execution_performed": false,
  "provider_authority": false,
  "proposal_authority": false,
  "replay_visible": true
}
```

## Forbidden Fields

The request must not contain:

- raw_provider_output
- raw_proposal
- raw_authorization_artifact
- governance_decision_authority
- dispatch_instruction
- execution_result
- worker_self_authorization
- replay_mutation
- memory_mutation

## Hash Rule

`request_hash` must be computed over the canonical request object excluding
`request_hash`.

## Scope Rule

`authorized_scope` must be equal to or narrower than the originating
authorization scope.

It must never exceed the authorization scope.
