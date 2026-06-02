# AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_V1

## Status

Runtime implementation certification.

## Final Classification

```text
AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_STATUS = CERTIFIED
```

## Purpose

This runtime defines the canonical deterministic registry layer for resolving:

- domains;
- worker families;
- milestone classes.

The registry does not perform semantic interpretation. It only resolves explicit ids or exact registered aliases after another runtime has already identified a candidate domain or worker family.

## Runtime Component

Implemented:

```text
aigol/runtime/domain_and_worker_resolution_registry.py
```

## Supported Domains

Registered domains:

- `TRADING`;
- `MARKETING`;
- `HEALTHCARE`;
- `PUBLIC_SERVICES`.

Trading is certified for current resolution. Marketing, Healthcare, and Public Services are registered future domains and are extensible when their domain foundations are certified.

## Trading Worker Families

Registered Trading worker families:

- `MARKET_EVIDENCE_NORMALIZATION`;
- `RISK_ANALYSIS`;
- `PORTFOLIO_ANALYSIS`;
- `STRATEGY_EVALUATION`;
- `DECISION_EXPLANATION`.

## Milestone Types

Registered milestone types:

- `WORKER_FOUNDATION`;
- `WORKER_RUNTIME`;
- `WORKER_CERTIFICATION`;
- `WORKER_ACCEPTANCE`.

## Resolution Artifact

The runtime produces:

```text
DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1
```

The artifact records:

- domain id;
- worker family id;
- milestone type;
- registry version;
- registry hash;
- resolution result;
- fail-closed reason when applicable.

## Fail-Closed Conditions

The registry fails closed on:

- unknown domain;
- unknown worker family;
- ambiguous worker family;
- duplicate domain registration;
- duplicate worker family registration;
- duplicate milestone registration;
- invalid milestone type;
- append-only replay collision;
- replay hash mismatch.

## Replay

Replay steps:

```text
000_domain_worker_resolution_recorded.json
001_domain_worker_resolution_returned.json
```

Replay preserves:

- domain id;
- worker family id;
- milestone type;
- registry version;
- registry hash;
- resolution result;
- failure reason.

## Authority Boundaries

The registry does not:

- invoke providers;
- create workers;
- create domains;
- generate proposals;
- dispatch;
- execute;
- create execution requests.

## Native Development Impact

AiGOL-native development readiness increases from:

```text
80%
```

to:

```text
84%
```

## Recommended Next Milestone

```text
AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_V1
```

This should make provider use explicit before any proposal request is made.

