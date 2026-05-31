# PROVIDER_SUBSTITUTION_ADR_V1

## Status

Accepted.

## Context

`FIRST_REAL_PROVIDER_ATTACHMENT_V1` attached OpenAI as the first real provider.

The next constitutional question is whether OpenAI is structurally special, or
whether providers are substitutable through the existing provider runtime.

## Decision

Certify provider substitution at the adapter boundary.

OpenAI, Claude, Codex, Gemini, Local LLM, and future providers are
interchangeable if they implement the same provider adapter contract and return
the same `ProviderProposalEnvelope`.

## Rationale

The provider runtime depends on:

- provider metadata
- provider status
- adapter identity/version match
- `generate_proposal(...)`
- valid proposal envelope
- replay-visible provider evidence

It does not depend on provider-specific governance, provider-specific authority,
provider-specific execution semantics, provider routing, provider orchestration,
or provider dispatch.

## Consequences

Provider-specific integration work remains adapter-local.

Provider substitution does not require changes to:

- governance
- replay
- authority model
- execution model

## Non-Goals

This ADR does not implement:

- Claude adapter
- Codex adapter
- Gemini adapter
- local LLM adapter
- provider execution
- worker execution
- governance changes
- authority changes
- orchestration
- planning
- reflection
- dispatch

## Certification

PROVIDER_SUBSTITUTION_STATUS = CERTIFIED
