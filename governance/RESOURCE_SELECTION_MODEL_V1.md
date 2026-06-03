# RESOURCE_SELECTION_MODEL_V1

## Status

Resource selection model.

## Purpose

Resource selection determines which Resource and role may satisfy a requested workflow.

Selection is deterministic, replay-visible, and fail-closed.

Selection does not invoke providers, invoke workers, dispatch, execute, authorize, or mutate governance.

## Selection Inputs

Selection requires:

- workflow type;
- requested domain;
- requested capability;
- provider necessity classification when proposal may be needed;
- worker authorization requirement when execution may be needed;
- risk class;
- trust requirement;
- cost requirement;
- dependency requirement;
- registry hash;
- capability hash;
- authority boundary hash;
- canonical chain id.

## Selection Output

Selection should produce:

```text
RESOURCE_SELECTION_DECISION_V1
```

containing:

- selected resource id;
- selected resource category;
- selected role type;
- selected capability id;
- selected version;
- selection reason;
- rejected resources and reasons;
- reuse-or-create recommendation when applicable;
- policy version;
- policy hash;
- registry hash;
- capability hash;
- authority boundary hash;
- canonical chain id;
- fail-closed status;
- replay references.

## Selection Order

Selection should evaluate:

1. workflow role requirement;
2. provider necessity or worker authorization requirement;
3. resource category compatibility;
4. role binding compatibility;
5. capability compatibility;
6. authority boundary compatibility;
7. lifecycle status;
8. trust threshold;
9. cost threshold;
10. dependency availability;
11. replay contract compatibility;
12. deterministic tie-breaker.

## Provider Selection

Select Provider role when workflow requires proposal evidence.

Provider role selection must respect provider necessity policy.

`PROVIDER_PROHIBITED` fails closed for Provider role.

## Worker Selection

Select Worker role when workflow requires authorized bounded work.

Worker role selection must require governance authorization before invocation.

Selection may identify an eligible Worker but may not invoke it.

## Hybrid Selection

Hybrid selection must choose one active role:

```text
PROVIDER_ROLE
```

or

```text
WORKER_ROLE
```

The selected role determines authority boundaries, capability contracts, replay contracts, and downstream runtime eligibility.

Implicit role switching is prohibited.

## Reuse Or Create

Resource selection may recommend:

```text
REUSE_EXISTING_RESOURCE
CREATE_NEW_RESOURCE_PROPOSAL_REQUIRED
UPGRADE_EXISTING_RESOURCE_PROPOSAL_REQUIRED
REPAIR_EXISTING_RESOURCE_PROPOSAL_REQUIRED
RETIRE_RESOURCE_REVIEW_REQUIRED
```

Selection must not create, upgrade, repair, or retire a Resource.

PPP governs those proposals.

## Deterministic Tie-Breaking

Allowed tie-breakers:

- explicit operator selection;
- governance priority;
- highest compatible trust;
- lowest acceptable cost;
- most recent certified version;
- strongest replay compatibility;
- lexical resource id as final fallback.

Random selection is prohibited.

## Fail-Closed Conditions

Selection fails closed when:

- role requirement is ambiguous;
- no eligible Resource exists;
- multiple Resources tie without deterministic resolution;
- authority boundary is missing;
- trust requirement is unmet;
- cost requirement is unmet;
- dependency is missing;
- replay contract is incompatible;
- provider necessity conflicts with selected role;
- worker authorization requirement conflicts with selected role.

