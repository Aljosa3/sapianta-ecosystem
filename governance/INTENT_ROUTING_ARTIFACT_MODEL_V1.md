# Intent Routing Artifact Model V1

Status: conceptual artifact model only.

This artifact defines the future `INTENT_ROUTING_ARTIFACT`.

It does not implement routing.

## Purpose

The `INTENT_ROUTING_ARTIFACT` records the selected destination for a Human Prompt.

It is evidence, not authority.

## Required Fields

A future routing artifact should contain:

- `routing_id`
- `human_prompt_reference`
- `human_prompt_hash`
- `candidate_destination`
- `destination_status`
- `routing_status`
- `ambiguity_status`
- `classification_basis`
- `created_at`
- `replay_parent`
- `lineage_references`
- `authority_guarantees`
- `failure_reason`
- `artifact_hash`

## Candidate Destinations

Allowed destination values:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

No other destination may be emitted without governance review.

## Routing Status Values

Suggested status values:

- `ROUTED`
- `REJECTED`
- `FAILED_CLOSED`

## Authority Limits

The artifact must explicitly certify:

- `authorization_authority`: false
- `governance_authority`: false
- `execution_authority`: false
- `provider_authority`: false
- `worker_authority`: false
- `memory_authority`: false

## Failure Semantics

The artifact must fail closed on:

- unknown intent
- ambiguous intent
- multiple valid destinations
- conflicting destinations
- missing destination
- invalid destination

## Replay Visibility

The artifact must be replay-visible and lineage-bound.

It should be recorded before the destination boundary runs.

