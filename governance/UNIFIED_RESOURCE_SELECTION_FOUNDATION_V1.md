# UNIFIED_RESOURCE_SELECTION_FOUNDATION_V1

## Status

Unified resource selection foundation.

## Final Classification

```text
UNIFIED_RESOURCE_SELECTION_FOUNDATION_STATUS = CERTIFIED
```

## Purpose

This milestone defines the constitutional foundation for selecting AiGOL resources across Providers, Workers, and Hybrid Provider-Workers.

Provider selection alone is insufficient because some resources can participate as proposal sources and as bounded work performers under different authority paths.

Worker selection alone is insufficient because not all useful resources execute work.

## Scope

Foundation only.

This milestone does not implement:

- runtime selection;
- provider integration;
- worker implementation;
- provider invocation;
- worker invocation;
- dispatch;
- execution;
- governance mutation;
- replay mutation.

## What Is A Resource?

A Resource is a registered selectable capability boundary.

A Resource may have one or more roles:

- Provider role;
- Worker role;
- Hybrid role;
- Operator tool role;
- Governance runtime role.

The Resource identity is stable.

Authority is role-specific.

No Resource receives authority from identity alone.

## Resource Categories

Resource categories:

```text
PROVIDER
WORKER
HYBRID_PROVIDER_WORKER
OPERATOR_TOOL
GOVERNANCE_RUNTIME
DOMAIN_RUNTIME
```

Category determines eligible role bindings.

Category does not grant authority.

## Hybrid Resource Representation

A Hybrid Resource is represented as:

```text
resource_id
resource_category = HYBRID_PROVIDER_WORKER
provider_role_binding
worker_role_binding
role_specific_capabilities
role_specific_authority_profiles
role_specific_replay_contracts
```

Hybrid Resources must never switch roles implicitly.

Every selection decision must identify the active role.

## Initial Resource Classification

Initial classifications:

| Resource | Category | Provider Role | Worker Role |
| --- | --- | --- | --- |
| `OPENAI` | `PROVIDER` | Yes | No |
| `ANTHROPIC` | `PROVIDER` | Yes | No |
| `CODEX` | `HYBRID_PROVIDER_WORKER` | Yes | Future governed Worker-capable |
| `CLAUDE_CODE` | `HYBRID_PROVIDER_WORKER` | Yes | Future governed Worker-capable |

## PPP Interaction

PPP interacts with Resources by role:

- Provider role: request proposal evidence;
- Worker role: propose Worker lifecycle changes or prepare future authorized work;
- Hybrid role: select the correct role-specific boundary before any downstream action.

PPP may:

- request provider proposals;
- validate proposals;
- create implementation handoffs;
- recommend Worker creation, upgrade, repair, or deprecation.

PPP may not:

- invoke Workers;
- dispatch;
- execute;
- authorize;
- mutate governance;
- mutate replay.

## Provider Versus Worker Decision

AiGOL determines active role from workflow intent:

- proposal generation requires Provider role;
- authorized task execution requires Worker role;
- implementation assistance may require Hybrid Resource classification, but must still select exactly one role for the current step;
- governance validation uses Governance Runtime role;
- operator display uses Operator Tool role.

Ambiguous role selection fails closed.

## Resource Lifecycle

Unified lifecycle states:

```text
REGISTERED
REVIEWED
APPROVED
ATTACHED
AVAILABLE
DEGRADED
SUSPENDED
DEPRECATED
RETIRED
```

Role-specific lifecycle may differ inside one Resource.

For example, `CODEX` may be approved as a Provider role while Worker role remains `REVIEWED` or `FOUNDATION_DEFINED`.

## Certification Judgment

Unified resource selection is certified as the correct foundation before provider or worker selection runtime.

The first runtime should implement deterministic, replay-visible Resource selection without invocation.

