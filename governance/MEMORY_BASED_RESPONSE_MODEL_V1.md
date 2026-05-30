# Memory Based Response Model V1

Status: canonical model for a future `MEMORY_BASED_RESPONSE`.

## Definition

A Memory-Based Response is an operator-facing governed explanation derived from Constitutional Memory citations.

It may communicate:

- what citation evidence was retrieved
- which artifacts were referenced
- a bounded constitutional summary
- replay and reconstruction references
- limitations or missing/conflict status

It may not communicate:

- authorization decisions
- governance decisions
- execution requests
- provider instructions
- worker instructions
- autonomous correction instructions

## Required Boundary

The response must be constructed from an existing `CONSTITUTIONAL_MEMORY_CONSULTATION_RECORD` and its citation bundle.

The response cannot bypass:

- intent classification
- intent routing attachment
- consultation activation
- replay evidence
- citation requirements

## Response Artifact Concept

A future response artifact should include:

- response id
- consultation record reference
- citation bundle reference
- constitutional summary
- citation references
- replay reference
- response timestamp
- response version
- reconstruction metadata
- non-authority status

No authority fields are permitted.
