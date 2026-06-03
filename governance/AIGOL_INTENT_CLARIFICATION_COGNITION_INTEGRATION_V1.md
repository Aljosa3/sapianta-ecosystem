# AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_V1

## Status

Runtime certification.

## Final Classification

```text
AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_STATUS = CERTIFIED
```

## Purpose

`AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_V1` converts resolved human clarification into cognition-compatible input.

It ensures AiGOL can ask a bounded clarification question, receive a human answer, and pass only normalized structured intent forward.

## Target Flow

```text
Human Intent
-> Clarification Dialog
-> Clarification Resolution
-> Cognition Integration
-> Cognition
```

## Inputs

The runtime accepts:

- `HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1`;
- `HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1`;
- `HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1`.

## Outputs

The runtime creates:

- `CLARIFIED_COGNITION_INPUT_ARTIFACT_V1`;
- `CLARIFICATION_COGNITION_EVIDENCE_V1`;
- `CLARIFICATION_COGNITION_CLASSIFICATION_V1`.

## Cognition Input Contract

The cognition input contract contains:

- intent reference;
- normalized intent;
- normalized intent class;
- domain id;
- worker family id;
- milestone type;
- capability id;
- resource category;
- confidence;
- source visibility marker set to false.

Clarification source lineage remains replay-visible outside the cognition contract.

## Source-Equivalence Invariant

Resolved clarification intent and direct intent become equivalent cognition inputs after normalization.

Cognition receives structured intent and does not need to know whether the intent came directly from a human prompt or from a clarification dialog.

## Replay Requirements

Replay preserves:

- clarification request reference and hash;
- clarification response reference and hash;
- clarification resolution reference and hash;
- clarification history;
- clarification history hash;
- canonical chain id;
- confidence;
- domain references;
- classification hash;
- clarified cognition input hash.

## Fail-Closed Conditions

The runtime fails closed when:

- clarification is unresolved;
- clarification is contradictory;
- request, response, or resolution hashes mismatch;
- request, response, or resolution references mismatch;
- chain continuity fails;
- source replay is corrupted;
- authority boundary flags are present.

## Authority Boundaries

The runtime does not:

- invoke cognition;
- invoke PPP;
- invoke providers;
- invoke workers;
- authorize;
- dispatch;
- execute;
- mutate governance.

## Recommended Next Milestone

```text
AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_V1
```
