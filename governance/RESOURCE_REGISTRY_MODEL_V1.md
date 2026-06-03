# RESOURCE_REGISTRY_MODEL_V1

## Status

Resource registry model.

## Purpose

The Resource registry is the canonical metadata layer for selectable ecosystem resources.

It unifies provider, worker, and hybrid identities while preserving role-specific authority boundaries.

The registry is deterministic and replay-visible.

It does not invoke, dispatch, execute, or authorize resources.

## Registry Entry

Each Resource entry should contain:

```text
resource_id
resource_category
display_name
vendor_or_origin
resource_version
role_bindings
capability_refs
trust_profile_id
cost_profile_id
dependency_refs
lifecycle_status
authority_boundary_refs
selection_policy_refs
replay_contract_refs
retirement_policy_id
resource_hash
```

## Role Binding

A role binding should contain:

```text
role_id
role_type
role_status
capability_refs
authority_profile_id
input_contract
output_contract
replay_contract_id
approval_requirement
trust_requirement
cost_requirement
```

Role types:

```text
PROVIDER_ROLE
WORKER_ROLE
OPERATOR_TOOL_ROLE
GOVERNANCE_RUNTIME_ROLE
DOMAIN_RUNTIME_ROLE
```

## Registration

Resource registration records identity and eligible roles.

Registration does not:

- approve the Resource;
- attach the Resource;
- invoke the Resource;
- dispatch the Resource;
- authorize the Resource;
- execute the Resource.

## Discovery

Resource discovery is deterministic registry filtering.

Discovery may filter by:

- category;
- role type;
- capability;
- domain;
- trust level;
- lifecycle status;
- dependency availability;
- cost class;
- replay contract.

Discovery must not invoke or test resources.

## Versioning

Resource versioning must distinguish:

- resource identity version;
- role binding version;
- capability schema version;
- authority profile version;
- replay contract version;
- adapter or worker implementation version when present.

Version changes must be replay-visible.

## Retirement

Retirement may occur at:

- Resource level;
- role level;
- capability level;
- version level.

Retirement must not rewrite historical replay.

Historical replay remains reconstructable under the Resource, role, and version recorded at the time of use.

## Fail-Closed Conditions

Registry use fails closed when:

- Resource id is unknown;
- Resource category is invalid;
- duplicate Resource id exists;
- role binding is missing for requested role;
- role status is unavailable, suspended, deprecated, or retired;
- authority boundary reference is missing;
- capability reference is unknown;
- trust profile is missing;
- replay contract is missing;
- resource hash mismatches;
- role ambiguity exists.

