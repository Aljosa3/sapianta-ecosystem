# Intent Classification Artifact Model V1

Status: conceptual artifact model only.

The `INTENT_CLASSIFICATION_ARTIFACT` records classifier output.

It is evidence, not authority.

## Required Fields

A future artifact should contain:

- `classification_id`
- `human_prompt_reference`
- `human_prompt_hash`
- `normalized_request_reference`
- `classifier_version`
- `candidate_destination`
- `classification_status`
- `ambiguity_status`
- `confidence_semantics`
- `classification_basis`
- `created_at`
- `replay_parent`
- `lineage_references`
- `authority_guarantees`
- `failure_reason`
- `artifact_hash`

## Destination Field

Allowed destination values:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

No other destination may be emitted without governance review.

## Confidence Semantics

Confidence is advisory.

It is not:

- authorization
- governance decision
- execution permission
- provider trust
- worker trust

If confidence semantics are ambiguous, classification must fail closed.

## Status Values

Suggested values:

- `CLASSIFIED`
- `REJECTED`
- `FAILED_CLOSED`

## Failure Semantics

Failure must be explicit and replay-visible.

Failure conditions include:

- unknown intent
- ambiguous intent
- multiple valid intents
- missing destination
- invalid destination
- classifier failure

