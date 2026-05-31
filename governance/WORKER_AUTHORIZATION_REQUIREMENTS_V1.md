# WORKER_AUTHORIZATION_REQUIREMENTS_V1

## Status

Certified authorization requirements for provider-to-worker compatibility.

## Requirement

A worker may execute only after governance approval and explicit authorization.

Provider proposals do not authorize workers.

Cognition outputs do not authorize workers.

Replay artifacts do not authorize workers.

Memory responses do not authorize workers.

## Required Authorization Evidence

Before worker execution, AiGOL must provide:

- explicit authorization state
- authorized request id
- execution id
- request id
- target capability
- authorization hash
- replay lineage
- worker identity
- capability binding

## Required Boundary Validation

Worker authorization must validate:

- capability scope
- worker domain compatibility
- worker capability compatibility
- absence of mutation pressure where denied
- absence of hidden continuation
- replay continuity
- explicit non-delegation of governance authority

## Fail-Closed Requirements

Worker execution must fail closed on:

- missing authorization
- invalid authorization
- unknown worker
- worker unavailable
- worker domain mismatch
- worker capability mismatch
- replay discontinuity
- authority escalation attempt

## Certification

Worker authority exists only inside the governed execution path.

No provider authority becomes worker authority.
