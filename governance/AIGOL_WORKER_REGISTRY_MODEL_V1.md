# AIGOL_WORKER_REGISTRY_MODEL_V1

## Status

Worker registry model.

## Purpose

The Worker registry is the canonical metadata layer for Worker identity, family, capability, lifecycle, trust, dependency, and authority boundaries.

The registry is deterministic and replay-visible.

It does not discover, invoke, dispatch, upgrade, repair, or execute Workers.

## Registry Entry

Each Worker registry entry should contain:

```text
worker_id
worker_family_id
worker_class
worker_version
domain_scope
capability_ids
status
trust_level
authority_profile_id
dependency_refs
input_contract
output_contract
replay_contract
failure_policy_id
upgrade_policy_id
retirement_policy_id
registry_entry_hash
```

## Worker Status

Worker lifecycle status values:

```text
PROPOSED
FOUNDATION_DEFINED
IMPLEMENTED
CERTIFIED
AVAILABLE
DEGRADED
SUSPENDED
DEPRECATED
RETIRED
```

Only Workers with `AVAILABLE` status may be selected for execution-sensitive workflows, and only after governed authorization.

Foundation-only Workers are not executable.

## Worker Family Registration

Worker family entries should contain:

```text
worker_family_id
display_name
domain_scope
capability_family
generic_or_domain_specific
authority_profile_id
replay_contract_id
known_aliases
family_hash
```

Aliases may assist deterministic resolution.

Aliases must not create ambiguity.

## Authority Profile

Every Worker must have an authority profile.

Authority profile fields:

```text
can_execute_authorized_task
can_dispatch
can_authorize
can_govern
can_mutate_replay
can_mutate_governance
can_create_workers
can_create_domains
can_use_provider
can_continue_autonomously
```

Default Worker profile:

```text
can_execute_authorized_task = true
can_dispatch = false
can_authorize = false
can_govern = false
can_mutate_replay = false
can_mutate_governance = false
can_create_workers = false
can_create_domains = false
can_use_provider = false
can_continue_autonomously = false
```

## Dependency Representation

Worker dependencies should include:

- runtime environment;
- provider dependency when applicable;
- domain artifact dependency;
- governance policy dependency;
- replay model dependency;
- data source dependency;
- credential dependency if future approved;
- human approval dependency for high-risk domains.

Dependencies are eligibility constraints.

Dependencies do not grant authority.

## Discovery

Worker discovery is registry enumeration plus deterministic filtering.

Discovery may expose:

- available Worker families;
- available Worker versions;
- domain compatibility;
- capability compatibility;
- trust status;
- dependency gaps.

Discovery must not invoke Workers.

## Versioning

Worker versioning must preserve:

- Worker id;
- Worker family id;
- Worker version;
- capability schema version;
- replay contract version;
- authority profile version;
- dependency versions.

Worker version changes must be replay-visible.

## Fail-Closed Conditions

Worker registry use fails closed when:

- Worker id is unknown;
- Worker family is unknown;
- duplicate Worker id exists;
- duplicate family alias creates ambiguity;
- Worker status is invalid;
- Worker capability reference is unknown;
- authority profile is missing;
- authority profile grants forbidden power;
- dependency reference is missing;
- registry hash mismatches;
- requested domain or capability is incompatible.

