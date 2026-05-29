# Human Request Gaps V1

Status: genuine Human Request gap analysis.

## Current Gap Summary

Human Request is mostly defined as bounded replay-visible operator input, but several areas remain incomplete.

## Gap 1: Canonical Vocabulary

Classification: `SHOULD_CANONICALIZE_LATER`

Current terms include:

- `human_request`
- `human_prompt`
- request text
- provider request metadata
- proposal `human_prompt`

These terms are compatible but not fully canonicalized.

## Gap 2: Standalone Human Request Identity

Classification: `OPTIONAL`

AiGOL has replay-visible request artifacts, but no standalone `HumanRequestIdentity` model.

This is not a blocker because operator flow id, request text hash, created timestamp, and replay lineage already identify the request in current flows.

## Gap 3: Multi-Provider Request Compatibility Matrix

Classification: `OPTIONAL`

No artifact defines which provider accepts which request shape.

This is not required for a single bounded provider adapter and should not become a routing system by accident.

## Gap 4: Request Adaptation Policy

Classification: `NOT_CURRENTLY_REQUIRED`

No evidence proves a need for provider-specific request adaptation outside adapter-local formatting.

## Gap 5: Request Registry

Classification: `UNDEFINED_AND_NOT_REQUIRED`

No request registry exists.

No evidence shows that first useful AiGOL or first real provider support requires one.

## Non-Gaps

The following are not gaps for current operation:

- prompt optimization
- provider-specific prompt templates
- memory-based request expansion
- adaptive prompt selection
- request routing
- autonomous request interpretation

Adding these now would expand architecture without a proven need.

