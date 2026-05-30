# Intent Classification Artifact Structure V1

Status: required structure for future implementation.

## Field Classification

`artifact_id`: `REQUIRED`

`human_request_reference`: `REQUIRED`

`human_prompt_hash`: `REQUIRED`

`normalized_request_reference`: `OPTIONAL`

`classification_destination`: `REQUIRED`

`classification_reason`: `REQUIRED`

`classification_timestamp`: `REQUIRED`

`classification_version`: `REQUIRED`

`replay_reference`: `REQUIRED`

`replay_parent`: `REQUIRED`

`lineage_references`: `REQUIRED`

`ambiguity_status`: `REQUIRED`

`classification_status`: `REQUIRED`

`failure_reason`: `OPTIONAL`

`confidence_semantics`: `OPTIONAL`

`constitutional_memory_references`: `OPTIONAL`

`artifact_hash`: `REQUIRED`

## Forbidden Fields

The artifact must not contain:

- authorization decision
- governance decision
- execution request
- provider command
- worker command
- memory retrieval result
- proposal artifact
- correction instruction

## Destination Field

The artifact may contain exactly one destination value:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

or a failed status with no active destination.

## Structure Rule

The artifact must be deterministic, JSON-serializable, replay-hashable, and reconstructable.

