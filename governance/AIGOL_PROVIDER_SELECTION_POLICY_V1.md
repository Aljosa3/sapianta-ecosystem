# AIGOL_PROVIDER_SELECTION_POLICY_V1

## Status

Provider selection policy foundation.

## Purpose

Provider selection determines which approved provider may be used for a proposal workflow.

Selection is deterministic, policy-mediated, replay-visible, and fail-closed.

Selection does not invoke providers.

## Selection Inputs

Provider selection requires:

- workflow type;
- domain;
- task kind;
- provider necessity classification;
- required capability;
- risk class;
- cost constraints;
- trust requirement;
- provider registry hash;
- provider capability hash;
- human approval requirement when applicable.

## Selection Output

Selection should produce:

```text
PROVIDER_SELECTION_DECISION_V1
```

containing:

- selected provider id;
- selected provider version;
- selected adapter id when present;
- selected capability id;
- selection reason;
- fallback providers;
- rejected providers;
- policy version;
- policy hash;
- registry hash;
- capability hash;
- fail-closed status;
- replay references.

## Selection Order

Provider selection should evaluate:

1. provider necessity policy;
2. provider approval status;
3. provider availability;
4. domain allowlist;
5. workflow allowlist;
6. capability compatibility;
7. trust threshold;
8. cost constraints;
9. failure history;
10. deterministic tie-breaker.

## Deterministic Tie-Breaking

When multiple providers are eligible, tie-breaking must be deterministic.

Allowed tie-breakers:

- explicit operator-selected provider;
- governance-defined provider priority;
- lowest acceptable cost;
- highest trust level;
- most recent successful provider for same capability;
- lexical provider id as final fallback.

Random selection is prohibited.

## Provider Necessity Interaction

Selection must respect provider necessity:

- `PROVIDER_PROHIBITED`: selection fails closed with no provider selected;
- `PROVIDER_OPTIONAL`: selection may choose self-resolution or an eligible provider;
- `PROVIDER_REQUIRED`: selection must choose an eligible provider or fail closed.

## Failure Handling

Provider failure handling:

- unavailable provider fails closed or selects a deterministic approved fallback;
- malformed response routes to proposal validation failure;
- repairable proposal failures route to repair/retry policy;
- ambiguous intent routes to human clarification;
- high-risk domain routes to human approval;
- repeated provider failure may suspend or degrade provider status.

Fallback is allowed only when:

- fallback provider is approved;
- fallback capability matches;
- fallback domain and workflow are allowed;
- fallback choice is replay-visible;
- no authority boundary changes.

## Cost Policy

Selection must reject or escalate when:

- cost exceeds workflow budget;
- cost is unknown for a bounded-cost workflow;
- provider pricing metadata is stale beyond policy;
- operator approval is required for high-cost provider use.

Cost policy must not hide provider choice from replay.

## Trust Policy

Selection must reject or escalate when:

- provider trust is below required threshold;
- provider is suspended;
- provider has repeated unresolved validation failures;
- provider is not approved for the requested domain.

Trust does not grant authority.

## Replay Requirements

Every provider selection decision must preserve:

- selected provider id;
- selected provider version;
- rejected provider ids and reasons;
- policy version;
- policy hash;
- registry hash;
- capability hash;
- cost class;
- trust level;
- canonical chain id;
- fail-closed reason when no provider is selected.

## Authority Boundaries

Provider selection must not:

- invoke providers;
- create proposals;
- authorize implementation;
- dispatch;
- execute;
- mutate governance;
- mutate replay except append-only selection evidence when implemented.

## Provider Independence

AiGOL remains provider-independent when no single provider is privileged as a constitutional requirement.

Provider selection is a policy decision, not an architectural dependency.

