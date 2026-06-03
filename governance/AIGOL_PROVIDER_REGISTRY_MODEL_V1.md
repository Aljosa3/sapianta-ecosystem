# AIGOL_PROVIDER_REGISTRY_MODEL_V1

## Status

Provider registry model.

## Purpose

The provider registry is the canonical metadata layer for provider identity, lifecycle, capability, cost, trust, and selection eligibility.

The registry is deterministic and replay-visible.

It does not invoke providers.

## Registry Entry

Each provider registry entry should contain:

```text
provider_id
provider_family
provider_product
provider_version
adapter_id
adapter_version
provider_status
approval_status
capability_ids
domain_allowlist
workflow_allowlist
trust_level
cost_model_id
selection_policy_ids
failure_policy_id
retirement_policy_id
authority_denials
registry_entry_hash
```

## Provider Ids

Initial canonical provider ids:

```text
OPENAI
ANTHROPIC
CODEX
CLAUDE_CODE
```

Provider ids must be stable, deterministic, and replay-visible.

Provider display names may change without changing provider id.

## Lifecycle Status

Provider status values:

```text
REGISTERED
APPROVED
ATTACHED
AVAILABLE
DEGRADED
UNAVAILABLE
SUSPENDED
RETIRED
```

Selection must fail closed when a provider is:

- unknown;
- unapproved;
- unavailable;
- suspended;
- retired;
- incompatible with requested workflow;
- incompatible with requested domain;
- incompatible with capability requirements.

## Approval Status

Approval status values:

```text
NOT_REVIEWED
APPROVED_FOR_PROPOSAL
APPROVED_WITH_RESTRICTIONS
SUSPENDED
REJECTED
RETIRED
```

Only proposal-approved providers may be selected.

Approval does not grant execution authority.

## Authority Denials

Every provider entry must record:

```text
execution_authority = false
dispatch_authority = false
governance_authority = false
replay_authority = false
worker_authority = false
approval_authority = false
```

Missing authority denial metadata is a fail-closed condition.

## Cost Representation

Provider costs should be represented as policy metadata, not billing logic.

Cost fields:

- pricing unit;
- estimated input cost;
- estimated output cost;
- currency;
- budget class;
- max request cost;
- max workflow cost;
- cost freshness timestamp;
- cost source reference.

Unknown cost does not automatically prohibit a provider.

Unknown cost does prohibit workflows that require bounded cost certainty.

## Trust Representation

Trust levels:

```text
UNASSESSED
LOW
STANDARD
HIGH
RESTRICTED
SUSPENDED
```

Trust is not authority.

Trust only affects eligibility and required validation intensity.

## Registry Hash

The registry must expose:

- registry version;
- ordered provider entries;
- registry hash;
- policy references;
- replay timestamp or deterministic build reference.

Registry hash changes must be recorded for new replay.

Historical replay must remain reconstructable under the hash recorded at the time of use.

## Fail-Closed Conditions

Registry use fails closed when:

- provider id is unknown;
- duplicate provider id exists;
- provider version is missing;
- provider status is invalid;
- provider authority denial is missing;
- provider hash mismatches;
- capability reference is unknown;
- selection policy reference is unknown;
- provider is unavailable, suspended, or retired;
- requested domain or workflow is not allowed.

