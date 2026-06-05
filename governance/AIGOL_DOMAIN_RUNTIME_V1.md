# AIGOL_DOMAIN_RUNTIME_V1

## Status

Runtime implementation certification.

```text
AIGOL_DOMAIN_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Introduce the first governed domain lifecycle runtime for AiGOL.

The runtime can create, validate, activate, suspend, and retire a domain while preserving deterministic replay visibility and lifecycle lineage.

## Runtime Scope

Runtime file:

```text
aigol/runtime/domain_runtime.py
```

Test file:

```text
tests/test_domain_runtime_v1.py
```

Certification artifact:

```text
governance/AIGOL_DOMAIN_RUNTIME_V1_CERTIFICATION.json
```

## Domain Model

The runtime creates these component artifacts:

- `DOMAIN_IDENTITY_ARTIFACT_V1`;
- `DOMAIN_MANIFEST_ARTIFACT_V1`;
- `DOMAIN_CAPABILITY_DECLARATION_ARTIFACT_V1`;
- `DOMAIN_GOVERNANCE_BINDING_ARTIFACT_V1`;
- `DOMAIN_LIFECYCLE_ARTIFACT_V1`.

Each lifecycle artifact records component hashes and a lifecycle chain hash.

## Lifecycle States

The certified lifecycle states are:

- `CREATED`;
- `VALIDATED`;
- `ACTIVE`;
- `SUSPENDED`;
- `RETIRED`.

Allowed transitions:

| From | To |
| --- | --- |
| `CREATED` | `VALIDATED` |
| `VALIDATED` | `ACTIVE` |
| `ACTIVE` | `SUSPENDED` |
| `ACTIVE` | `RETIRED` |
| `SUSPENDED` | `ACTIVE` |
| `SUSPENDED` | `RETIRED` |

Unauthorized transitions fail closed.

## Replay Events

The runtime records:

- `DOMAIN_CREATED`;
- `DOMAIN_VALIDATED`;
- `DOMAIN_ACTIVATED`;
- `DOMAIN_SUSPENDED`;
- `DOMAIN_RETIRED`.

Replay reconstruction verifies:

- replay wrapper ordering;
- wrapper hash integrity;
- lifecycle artifact hash integrity;
- domain replay identity continuity;
- previous artifact hash continuity;
- previous lifecycle state continuity;
- authorized lifecycle transition continuity.

## Governance Binding

Every domain requires a governance binding with explicit policy references.

Missing governance policy references fail closed. A domain lifecycle artifact does not certify a domain unless its identity, manifest, capability declaration, and governance binding hashes remain continuous.

## Authority Boundaries

This runtime is lifecycle registration only.

It does not:

- invoke providers;
- invoke workers;
- dispatch work;
- perform execution;
- authorize execution;
- mutate governance semantics;
- perform autonomous lifecycle transitions;
- bypass human authority.

The runtime records `human_authority_required = true` and preserves non-authority flags in lifecycle artifacts and reconstructed replay summaries.

## Certification Evidence

Certified tests cover:

- valid full lifecycle handoff from `CREATED` to `RETIRED`;
- replay event persistence;
- unauthorized activation before validation;
- duplicate capability declaration rejection;
- missing governance binding rejection;
- replay hash break detection;
- lineage break detection;
- state sequence reconstruction;
- absence of provider, worker, dispatch, or execution authority.

Validation result:

```text
python -m pytest tests/test_domain_runtime_v1.py
9 passed
```

## Success Criteria

AiGOL can create, validate, activate, suspend, and retire domains under governance while preserving replay visibility and certification guarantees.

Final status:

```text
AIGOL_DOMAIN_RUNTIME_STATUS = CERTIFIED
```
