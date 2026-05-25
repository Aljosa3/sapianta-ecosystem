# MOC V1 Worker Dispatch Authorization Preview Foundation

## Status

`MOC_V1_WORKER_DISPATCH_AUTHORIZATION_PREVIEW_FOUNDATION` defines a
deterministic, replay-visible, preview-only dispatch eligibility layer for MOC
V1 worker preparation packages.

This artifact previews whether a worker preparation package would satisfy
future dispatch eligibility semantics. It does not create dispatch authority.

## Boundary Statement

Dispatch preview is not dispatch.

Dispatch preview is not execution.

Dispatch preview is not actual authorization.

Dispatch preview does not activate providers, dispatch workers, orchestrate
work, mutate governance, or create autonomous continuation.

## Preview Eligibility

A preview may reach `DISPATCH_PREVIEW_ELIGIBLE` only when the worker preparation
package:

- has `preparation_status = PREPARED_FOR_WORKER`
- has `ready_for_dispatch = false`
- has `dispatch_authority = false`
- has `execution_authority = false`
- has `provider_activation = false`
- has `worker_dispatch = false`
- contains lineage references
- contains approval references
- contains replay references
- contains explicit non-empty allowed worker actions
- has no overlap between allowed and forbidden worker actions

Invalid or missing evidence fails closed or is rejected.

## Authority Guarantees

Even when a preview is eligible, the artifact always preserves:

```text
dispatch_authority = false
execution_authority = false
provider_activation = false
worker_dispatch = false
ready_for_actual_dispatch = false
```

The governance guarantee block also preserves:

```text
preview_only = true
orchestration_authority = false
autonomous_continuation = false
governance_mutation = false
automatic_execution = false
actual_dispatch_authorization = false
hidden_continuation = false
```

## Non-Goals

This milestone does not:

- dispatch workers
- execute tasks
- activate providers
- create actual dispatch authorization
- create orchestration
- create autonomous cognition
- create hidden continuation
- infer hidden meaning
- mutate worker packages
- mutate governance
- trigger automatic execution

## Future Dispatch Boundary

Any actual dispatch authorization requires a separate milestone with its own
governance design, replay evidence, validation, and explicit human/governance
authority boundary.

This milestone is preview-only.
