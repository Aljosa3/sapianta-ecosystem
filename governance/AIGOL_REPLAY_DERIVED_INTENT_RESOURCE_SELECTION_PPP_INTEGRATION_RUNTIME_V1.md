# AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_RUNTIME_V1

## Status

Runtime implemented.

## Purpose

`AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_RUNTIME_V1` converts replay-derived, Resource Selection-routed intent into PPP-compatible input.

It preserves replay lineage while presenting PPP with a source-agnostic contract equivalent to human-origin intent.

## Target Flow

```text
Replay
-> Gap Detection
-> Improvement Intent
-> Cognition
-> Resource Selection
-> PPP Integration
-> PPP
```

## Inputs

The runtime accepts:

- `RESOURCE_SELECTION_ROUTED_INTENT_V1`;
- `RESOURCE_SELECTION_ROUTING_EVIDENCE_V1`;
- `RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1`;
- replay references and replay hashes contained in upstream artifacts.

## Outputs

The runtime produces:

- `PPP_ROUTED_INTENT_ARTIFACT_V1`;
- `PPP_ROUTING_EVIDENCE_V1`;
- `PPP_ROUTING_CLASSIFICATION_V1`.

## PPP Input Contract

The PPP input contract contains only PPP-consumable fields:

- intent reference;
- workflow type;
- required capability;
- requested role type;
- domain id;
- provider necessity classification;
- confidence;
- PPP stage;
- source visibility marker set to false.

Replay-derived source lineage remains outside the PPP contract in replay evidence.

## Replay Preservation

The runtime persists:

- source Resource Selection routed intent reference and hash;
- source Resource Selection routing evidence reference and hash;
- source Resource Selection routing classification reference and hash;
- source replay references;
- source replay hashes;
- canonical chain id;
- PPP routed intent hash.

## Fail-Closed Conditions

The runtime fails closed when:

- Resource Selection routed intent is missing;
- upstream evidence or classification is missing;
- artifact hashes mismatch;
- lineage references mismatch;
- chain continuity fails;
- source visibility leaks into PPP input;
- the Resource Selection contract is missing or incomplete;
- append-only replay artifacts already exist.

## Authority Boundaries

The runtime does not:

- invoke PPP proposal production;
- invoke providers;
- invoke workers;
- create proposals;
- authorize;
- dispatch;
- execute;
- mutate governance;
- mutate replay outside append-only routing evidence.

## Source-Agnostic Invariant

Human intent and replay-derived intent become equivalent PPP inputs after routing.

PPP receives a normalized contract and remains unaware of the original intent source.

## Final Classification

```text
AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_RUNTIME_STATUS = CERTIFIED
```
