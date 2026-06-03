# AIGOL_HUMAN_CLARIFICATION_MODEL_V1

## Status

Human clarification model.

## Clarification Artifact

Required artifact:

```text
HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1
```

Future response artifact:

```text
HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1
```

## Clarification Request Fields

`HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1` must include:

- `artifact_type`;
- `clarification_request_id`;
- `canonical_chain_id`;
- `ambiguity_category`;
- `clarification_reason`;
- `source_artifact_reference`;
- `source_artifact_hash`;
- `context_reference`;
- `context_hash`;
- `provider_response_reference`;
- `provider_response_hash`;
- `candidate_interpretations`;
- `allowed_response_scope`;
- `resume_candidate_stages`;
- `created_at`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

## Clarification Response Fields

`HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1` must include:

- `artifact_type`;
- `clarification_response_id`;
- `clarification_request_reference`;
- `clarification_request_hash`;
- `canonical_chain_id`;
- `selected_interpretation`;
- `selected_domain_id`;
- `selected_worker_family_id`;
- `selected_milestone_type`;
- `selected_output_scope`;
- `human_response_text_hash`;
- `resume_stage`;
- `created_at`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

## Allowed Clarification Responses

Allowed response classes:

- select one candidate interpretation;
- reject all candidates;
- provide missing domain id;
- provide missing worker family id;
- provide missing milestone type;
- provide missing output scope;
- request cancellation;
- request additional clarification.

## Disallowed Clarification Responses

Clarification response must not:

- authorize execution;
- dispatch workers;
- create domains;
- create workers;
- mutate governance;
- mutate replay;
- place trading orders;
- invoke brokers;
- invoke exchanges;
- deploy strategies.

## Validation Rules

AiGOL must validate:

- response references existing clarification request;
- request hash matches;
- chain continuity holds;
- selected interpretation is within allowed response scope;
- resume stage is allowed;
- high-risk approval is still required when applicable.

## Clarification Outcome Classes

Allowed outcomes:

- `CLARIFICATION_RESOLVED`;
- `CLARIFICATION_REJECTED`;
- `CLARIFICATION_CANCELLED`;
- `ADDITIONAL_CLARIFICATION_REQUIRED`;
- `FAILED_CLOSED`.

