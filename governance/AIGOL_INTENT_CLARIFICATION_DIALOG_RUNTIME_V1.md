# AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_V1

## Status

Runtime certification.

## Final Classification

```text
AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_STATUS = CERTIFIED
```

## Purpose

`AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_V1` provides deterministic multi-step clarification for ambiguous human intent.

It prevents AiGOL from guessing when prompts can map to multiple domains, workers, capabilities, intent classes, or resources.

## Target Flow

```text
Human Intent
-> Ambiguity Detection
-> Clarification Request
-> Human Response
-> Clarification Resolution
-> Resolved Intent
-> Cognition
```

## Supported Ambiguity Categories

The runtime supports:

- `DOMAIN_AMBIGUITY`;
- `WORKER_AMBIGUITY`;
- `CAPABILITY_AMBIGUITY`;
- `INTENT_AMBIGUITY`;
- `RESOURCE_AMBIGUITY`.

## Output Artifacts

The runtime creates:

- `HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1`;
- `HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1`;
- `HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1`.

## Clarification Lifecycle

1. AiGOL receives ambiguous human intent.
2. AiGOL records bounded candidate interpretations.
3. AiGOL creates a clarification request with bounded questions.
4. Human selects one candidate, rejects all candidates, cancels, or requests additional clarification.
5. AiGOL records the human response.
6. AiGOL validates the response against the request, candidate set, chain id, and allowed resume stage.
7. AiGOL creates a resolved intent only when ambiguity is resolved.
8. AiGOL exposes the resolved intent as cognition-compatible input.

## Fail-Closed Conditions

The runtime fails closed when:

- ambiguity category is missing or unsupported;
- candidate interpretations are missing;
- selected interpretation is outside the allowed response scope;
- human answers contradict the selected candidate;
- clarification history exceeds the configured limit;
- chain continuity fails;
- replay artifact hashes mismatch;
- append-only replay artifacts already exist.

## Replay Model

Replay records:

- clarification request;
- clarification response;
- clarification resolution;
- returned dialog result.

Replay reconstruction validates:

- wrapper ordering;
- wrapper hashes;
- request hash;
- response hash;
- resolution hash;
- request-response references;
- response-resolution references;
- returned resolution reference.

## Authority Boundaries

The runtime does not:

- create proposals;
- invoke providers;
- invoke workers;
- authorize;
- dispatch;
- execute;
- mutate governance.

## Human Usability

The runtime turns ambiguous prompts such as:

```text
Create a workstation.
Improve trading.
Add analysis.
Create reporting.
```

into bounded choices instead of unstated assumptions.

## Recommended Next Milestone

```text
AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_V1
```
