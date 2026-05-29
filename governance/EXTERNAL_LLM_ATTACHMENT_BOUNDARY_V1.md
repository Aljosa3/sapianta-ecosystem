# External LLM Attachment Boundary V1

Status: implemented boundary definition.

## Boundary Principle

An external LLM response may enter AiGOL only as untrusted proposal input.

The boundary ends at the normalized proposal artifact. AiGOL governance remains responsible for validation, authorization, rejection, replay recording, and governed return evidence.

## Accepted Input

The attachment accepts:

- `provider_identity`: deterministic provider/source identity
- `external_response`: raw externally supplied LLM response text

Both must be explicit.

## Boundary Rejections

The attachment fails closed on:

- missing provider identity
- ambiguous provider identity
- empty response
- malformed response
- unsupported target capability
- authority escalation language
- hidden continuation language
- replay corruption
- normalization failure
- invalid proposal structure

## Proposal Boundary

The normalized proposal remains untrusted.

It contains non-authority evidence:

- LLM cannot execute
- LLM cannot authorize
- LLM cannot govern
- LLM cannot bypass replay
- LLM cannot create capabilities

## Governance Handoff

Only after raw capture, normalization, and proposal validation does the attachment call the existing cognition-to-execution bridge.

The bridge remains responsible for AiGOL validation, authorization, execution boundary enforcement, and governed return construction.

## Boundary Result

The boundary proves external response ingestion without provider authority, execution authority, or governance authority.
