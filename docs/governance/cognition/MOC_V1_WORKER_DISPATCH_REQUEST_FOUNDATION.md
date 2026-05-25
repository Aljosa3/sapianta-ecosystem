# MOC V1 Worker Dispatch Request Foundation

## Status

`MOC_V1_WORKER_DISPATCH_REQUEST_FOUNDATION` defines a deterministic,
replay-visible, request-only artifact layer for MOC V1 worker dispatch
consideration.

The artifact records an explicit human/governance request that dispatch may be
considered by a future authorization layer for a previously prepared and
preview-eligible worker package.

## Boundary Statement

Dispatch request is not dispatch authorization.

Dispatch request is not execution.

Dispatch request is a request-only artifact.

Dispatch request creates no actual authorization.

Dispatch request performs no worker dispatch.

Dispatch request activates no providers.

Dispatch request creates no orchestration.

Dispatch request creates no autonomous cognition.

Dispatch request creates no automatic execution.

Future dispatch authorization requires a separate milestone.

## Request Eligibility

A dispatch request may reach `DISPATCH_REQUEST_CREATED` only when:

- the dispatch preview artifact is present
- the dispatch preview status is `DISPATCH_PREVIEW_ELIGIBLE`
- `dispatch_preview_hash` exists
- `worker_package_id` exists
- lineage references exist
- approval references exist
- replay references exist
- request evidence is explicit
- `requester_type` is explicit
- dispatch authority remains false
- execution authority remains false
- provider activation remains false
- worker dispatch remains false

Invalid or missing evidence fails closed. A valid dispatch preview artifact with
a non-eligible preview status is rejected and does not create authority.

## Request Statuses

- `DISPATCH_REQUEST_CREATED`
- `DISPATCH_REQUEST_REJECTED`
- `INVALID_PREVIEW_EVIDENCE`
- `FAIL_CLOSED`

## Authority Guarantees

Even when a request is created, the artifact always preserves:

```text
dispatch_authority = false
execution_authority = false
provider_activation = false
worker_dispatch = false
ready_for_actual_dispatch = false
```

The governance guarantee block also preserves:

```text
request_only = true
orchestration_authority = false
autonomous_continuation = false
governance_mutation = false
automatic_execution = false
```

## Non-Goals

This milestone does not:

- dispatch workers
- execute tasks
- activate providers
- create actual dispatch authorization
- create orchestration
- create autonomous cognition flows
- create hidden continuation
- infer hidden meaning
- mutate worker packages
- mutate dispatch previews
- mutate governance
- trigger automatic execution

## Future Dispatch Boundary

Actual dispatch authorization requires
`MOC_V1_WORKER_DISPATCH_AUTHORIZATION_FOUNDATION` or an equivalent future
milestone with explicit governance design, replay evidence, validation, and
human/governance authority boundaries.

This milestone creates request evidence only.
