# RESOURCE_AUTHORITY_BOUNDARY_MODEL_V1

## Status

Resource authority boundary model.

## Purpose

Authority boundaries define what a selected Resource role may and may not do.

Authority is role-specific, not Resource-wide.

## Authority Profile

Each Resource role must reference an authority profile.

Authority profile fields:

```text
can_propose
can_execute_authorized_task
can_dispatch
can_authorize
can_govern
can_mutate_replay
can_mutate_governance
can_create_resources
can_select_resources
can_continue_autonomously
can_invoke_provider
can_invoke_worker
```

## Provider Role Profile

Provider role:

```text
can_propose = true
can_execute_authorized_task = false
can_dispatch = false
can_authorize = false
can_govern = false
can_mutate_replay = false
can_mutate_governance = false
can_create_resources = false
can_select_resources = false
can_continue_autonomously = false
can_invoke_provider = false
can_invoke_worker = false
```

## Worker Role Profile

Worker role:

```text
can_propose = false
can_execute_authorized_task = true
can_dispatch = false
can_authorize = false
can_govern = false
can_mutate_replay = false
can_mutate_governance = false
can_create_resources = false
can_select_resources = false
can_continue_autonomously = false
can_invoke_provider = false
can_invoke_worker = false
```

Worker execution requires separate governed authorization and dispatch/invocation runtime.

## Hybrid Resource Boundary

Hybrid Resource identity may contain provider and worker role profiles.

Only one role profile may be active for a selection decision.

No authority may flow from provider role to worker role.

No authority may flow from worker role to provider role.

## Governance Runtime Profile

Governance runtimes may validate, classify, or reconstruct within a defined AiGOL-owned scope.

They may not:

- become providers;
- become workers by default;
- dispatch;
- execute domain work;
- mutate governance outside defined append-only or file-editing scope;
- mutate replay outside append-only runtime evidence when implemented.

## Boundary Verification

Selection must verify:

- role-specific authority profile exists;
- selected workflow is compatible with profile;
- no forbidden authority is present;
- high-risk domains preserve human approval;
- replay records the active role and profile hash.

## Fail-Closed Conditions

Boundary verification fails closed when:

- authority profile is missing;
- authority profile grants forbidden power;
- selected role conflicts with workflow;
- Resource category conflicts with role;
- hybrid Resource role is ambiguous;
- provider output attempts execution;
- worker output attempts governance or authorization;
- replay or governance mutation is requested outside authorized scope.

## Constitutional Invariant

The unified Resource model preserves:

```text
Provider proposes.
AiGOL governs.
Human authorizes.
Worker executes only authorized work.
Replay records.
```

