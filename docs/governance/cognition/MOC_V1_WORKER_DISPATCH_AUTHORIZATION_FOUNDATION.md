# MOC V1 Worker Dispatch Authorization Foundation

## Status

`MOC_V1_WORKER_DISPATCH_AUTHORIZATION_FOUNDATION` defines the first explicit,
deterministic, replay-visible dispatch authorization boundary for MOC V1.

This milestone authorizes future runtime dispatch eligibility only.

## Boundary Statement

Dispatch authorization is not execution.

Dispatch authorization is not runtime execution.

Dispatch authorization is an authorization-only boundary.

Dispatch authorization performs no worker execution.

Dispatch authorization activates no providers.

Dispatch authorization creates no orchestration.

Dispatch authorization creates no autonomous cognition.

Dispatch authorization creates no automatic execution.

Future runtime dispatch requires a separate milestone.

## Authorization Eligibility

Authorization may reach `DISPATCH_AUTHORIZED` only when:

- the dispatch request artifact is present
- the dispatch request status is `DISPATCH_REQUEST_CREATED`
- dispatch request lineage references exist
- dispatch request approval references exist
- dispatch request replay references exist
- dispatch request evidence remains `replay_safe`
- dispatch request evidence remains `advisory_only` where applicable
- dispatch authority in the request remains false
- execution authority in the request remains false
- provider activation in the request remains false
- worker dispatch in the request remains false

Invalid or missing evidence fails closed. A valid dispatch request artifact with
a non-created request status is rejected and does not create authorization.

## Authorization Statuses

- `DISPATCH_AUTHORIZED`
- `DISPATCH_AUTHORIZATION_REJECTED`
- `INVALID_DISPATCH_REQUEST`
- `FAIL_CLOSED`

## Authority Guarantees

Even when dispatch is authorized, the artifact always preserves:

```text
execution_authority = false
provider_activation = false
runtime_execution = false
worker_dispatch_performed = false
```

The governance guarantee block also preserves:

```text
authorization_only = true
orchestration_authority = false
autonomous_continuation = false
governance_mutation = false
automatic_execution = false
```

## Non-Goals

This milestone does not:

- execute workers
- perform runtime execution
- activate providers
- dispatch workers at runtime
- create orchestration
- create autonomous cognition flows
- create hidden continuation
- infer hidden meaning
- mutate dispatch request artifacts
- mutate governance
- trigger automatic execution

## Future Runtime Dispatch Boundary

Future runtime dispatch requires a separate milestone with explicit runtime
dispatch design, deterministic replay evidence, provider boundary controls,
execution separation, and governance validation.

This milestone creates dispatch authorization only.
