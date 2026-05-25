# MOC V1 Worker Preparation Foundation

## Status

`MOC_V1_WORKER_PREPARATION_FOUNDATION` defines a deterministic, replay-visible,
approval-gated worker preparation layer for Minimal Operational Cognition V1.

This milestone prepares a governed worker package from explicit approved
advisory proposal evidence.

## Boundary Statement

Worker preparation is not execution.

Worker preparation is not dispatch.

Worker preparation does not activate providers.

The worker preparation package is a non-executing governance artifact that
records readiness for later human-governed worker preparation review only. It
does not create runtime authority.

## Required Approval Gate

A worker preparation package may reach `PREPARED_FOR_WORKER` only when the
linked approval gate result has:

```text
approval_status = APPROVED_FOR_WORKER_PREPARATION
```

Any missing, malformed, rejected, or inconsistent approval evidence fails closed
or remains `NOT_APPROVED`.

## Package Scope

The package records:

- proposal identity and proposal hash
- linked semantic contract identity and hash
- linked approval gate hash
- allowed worker actions from explicit proposal `suggested_actions`
- forbidden worker actions from explicit proposal `forbidden_actions`
- expected outputs
- lineage references
- approval references
- replay references
- deterministic worker preparation hash

Worker actions are derived only from explicit proposal evidence. The package
does not infer missing actions, repair proposals, or create new worker tasks.

## Deterministic Eligibility Checks

The preparation layer verifies:

- approval gate status is `APPROVED_FOR_WORKER_PREPARATION`
- proposal remains `advisory_only = true`
- proposal remains `replay_safe = true`
- proposal hash matches approval evidence
- worker actions are explicit
- worker actions remain within explicit allowed actions
- worker actions do not appear in explicit forbidden actions
- lineage references are present
- approval references are present or linked to approval gate evidence
- forbidden authority fields are absent or false

Invalid or missing evidence fails closed.

## Governance Guarantees

The worker preparation package always declares:

```text
ready_for_dispatch = false
dispatch_authority = false
execution_authority = false
provider_activation = false
worker_dispatch = false
```

The governance guarantee block always preserves:

```text
execution_authority = false
worker_dispatch = false
provider_activation = false
orchestration_authority = false
autonomous_continuation = false
governance_mutation = false
automatic_execution = false
hidden_continuation = false
```

## Non-Goals

This milestone does not:

- execute worker packages
- dispatch workers
- activate providers
- orchestrate work
- create autonomous cognition
- create hidden continuation
- mutate governance
- repair proposals
- infer hidden semantic meaning
- trigger automatic execution

## Replay Visibility

Worker preparation produces a deterministic `MOC_V1_WORKER_PREPARATION_PACKAGE`
with replay-visible lineage, approval references, replay references, and a
canonical `worker_preparation_hash`.

The artifact is preparation evidence only.
