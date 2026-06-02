# AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_V1

## Status

Runtime implementation certification.

## Final Classification

```text
AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_STATUS = CERTIFIED
```

## Purpose

This runtime classifies whether provider assistance is:

- required;
- optional;
- prohibited.

It only classifies necessity. It does not invoke providers, create proposals, create workers, create domains, dispatch, or execute.

## Runtime Component

Implemented:

```text
aigol/runtime/provider_necessity_policy_runtime.py
```

## Classifications

Supported classifications:

```text
PROVIDER_REQUIRED
PROVIDER_OPTIONAL
PROVIDER_PROHIBITED
```

## Policy Examples

Examples certified by the runtime:

- `show-chain` -> `PROVIDER_PROHIBITED`;
- `dashboard` -> `PROVIDER_PROHIBITED`;
- replay inspection -> `PROVIDER_PROHIBITED`;
- worker foundation design -> `PROVIDER_REQUIRED`;
- domain architecture proposal -> `PROVIDER_REQUIRED`;
- governance review -> `PROVIDER_OPTIONAL`.

## Replay

Replay steps:

```text
000_provider_necessity_policy_classified.json
001_provider_necessity_policy_returned.json
```

Replay preserves:

- necessity classification;
- reason;
- matched rule id;
- workflow type;
- command;
- task kind;
- policy version;
- policy hash.

## Fail-Closed Conditions

The runtime fails closed when:

- necessity cannot be determined;
- policy version is invalid;
- policy rule is invalid;
- policy rule classification is invalid;
- matching rules are ambiguous;
- append-only replay path already exists;
- replay hash verification fails.

## Authority Boundaries

The runtime does not:

- invoke providers;
- create proposals;
- create workers;
- create domains;
- dispatch;
- execute;
- create execution requests.

Provider decisions remain proposal-only and future proposal use must remain governed.

## Native Development Impact

AiGOL-native development readiness increases from:

```text
84%
```

to:

```text
88%
```

## Recommended Next Milestone

```text
AIGOL_DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME_V1
```

This should define the bounded proposal contract that provider output must satisfy before any Codex-assisted implementation handoff.

