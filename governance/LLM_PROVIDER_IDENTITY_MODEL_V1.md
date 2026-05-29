# LLM Provider Identity Model V1

Status: model-only provider identity definition.

## Purpose

Provider identity exists to make external proposal sources replay-visible, attributable, deterministic, and bounded.

It does not grant the provider authority.

## Required Identity Fields

A real LLM attachment should record:

- `provider_id`: deterministic identifier for the attached provider boundary
- `provider_type`: bounded source category, such as `external_llm`
- `provider_name`: provider label supplied by the adapter boundary
- `model_identity`: model label supplied by the adapter boundary
- `invocation_id`: replay-visible invocation reference
- `response_id`: replay-visible response reference
- `attachment_boundary_version`: attachment model version
- `created_at`: deterministic timestamp supplied by the operator/runtime boundary

## Identity Rules

Provider identity must be:

- explicit
- replay-visible
- immutable after capture
- linked to raw response evidence
- linked to normalized proposal evidence

## Non-Authority Rule

Provider identity does not authorize execution.

Provider identity does not imply trust, governance authority, worker authority, capability authority, or replay authority.

## Fail-Closed Identity Conditions

The attachment must fail closed when:

- provider identity is missing
- provider identity is ambiguous
- invocation id is missing
- response id is missing
- model identity is missing
- identity values mutate after capture
- identity lineage cannot be linked to raw response evidence

## Boundary

Provider identity belongs to the attachment boundary.

AiGOL core consumes only normalized proposal artifacts after provider evidence has been captured and linked.
