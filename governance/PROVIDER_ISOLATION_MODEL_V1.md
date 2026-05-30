# Provider Isolation Model V1

Status: provider isolation model for non-authoritative attachment.

## Provider May

Provider may:

- receive bounded input
- return proposal output
- expose provider identity
- expose provider version
- fail closed

## Provider May Not

Provider may not:

- execute
- authorize
- govern
- dispatch
- mutate replay
- mutate memory
- invoke workers
- invoke other providers
- bypass AiGOL validation

## Isolation Boundary

Provider output remains untrusted proposal evidence until AiGOL records, validates, and governs it.

Provider output is not:

- execution request
- authorization decision
- governance decision
- worker instruction
- replay authority

## Required Implementation Constraint

Any future provider adapter must preserve a strict boundary between provider response capture and AiGOL governance processing.
