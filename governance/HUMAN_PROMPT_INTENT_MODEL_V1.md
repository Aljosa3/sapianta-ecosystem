# HUMAN_PROMPT_INTENT_MODEL_V1

## Purpose

This artifact defines how Human Prompt intent should be understood before implementation.

## Current Destinations

The current valid intent destinations are:

- `CONVERSATION`;
- `CONSTITUTIONAL_MEMORY_CONSULTATION`;
- `PROVIDER_PROPOSAL`;
- `EXECUTION_REQUEST`.

## Intent Determination

V1 intent determination should use deterministic bounded rules before any provider involvement.

Provider-based classification is not required for the first implementation.

## Destination Semantics

### Conversation

Use when the operator asks for a bounded human-facing response and no provider proposal, execution, or memory citation is required.

Current maturity: `PARTIAL`.

### Constitutional Memory Consultation

Use when the operator asks about AiGOL constitutional knowledge or governance artifacts.

Provider required: no.

### Provider Proposal

Use when the operator asks AiGOL to generate a candidate proposal.

Provider required: yes.

### Execution Request

Use when the operator asks for a governed operation that may reach authorization and worker boundaries.

Provider may be required if the operation is not already explicit.

## Ambiguity

Ambiguous prompts must not route automatically into execution.

They should fail closed or require clarification in a future implementation review.

## Replay Requirement

Intent classification must be replay-visible and linked to the original Human Prompt artifact.
