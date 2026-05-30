# MINIMAL_PROVIDER_ATTACHMENT_RUNTIME_V1

## Status

PROVIDER_ATTACHMENT_RUNTIME_STATUS = READY

## Purpose

This milestone implements the first operational provider attachment runtime for
AiGOL.

The runtime proves that an external provider can attach as an external proposal
producer while remaining non-authoritative.

## Constitutional Invariant

LLM proposes.

AiGOL governs.

Worker executes.

Replay records.

## Implemented Components

- `aigol/provider/provider_registry.py`
- `aigol/provider/provider_adapter.py`
- `aigol/provider/provider_proposal_envelope.py`
- `aigol/provider/provider_runtime.py`

## Runtime Flow

Human Prompt

Provider Runtime

Provider Adapter

Provider Proposal Envelope

Replay Evidence

## Provider Position

Provider is:

- external proposal producer
- metadata-identified
- replay-visible
- substitutable under a common adapter contract

Provider is not:

- execution authority
- authorization authority
- governance authority
- dispatch authority
- replay authority
- memory authority

## Deterministic Provider Registry

The registry records provider metadata only:

- provider_id
- provider_type
- provider_version
- provider_status

Allowed statuses:

- DETACHED
- ATTACHED
- AVAILABLE
- UNAVAILABLE

The registry cannot execute, dispatch, authorize, govern, mutate replay, or
mutate memory.

## Provider Adapter Contract

The adapter may receive a request and return a provider proposal envelope.

The adapter may not execute, authorize, govern, dispatch, mutate replay, or
mutate memory.

## Provider Proposal Envelope

The envelope contains:

- proposal_id
- provider_id
- provider_version
- request
- response
- timestamp
- proposal_hash

The envelope contains no authority metadata, execution metadata, governance
decision, authorization decision, dispatch request, worker instruction, replay
mutation, or memory mutation.

## Replay Visibility

The runtime records replay-visible evidence for:

- provider identity
- provider version
- request
- response
- timestamp
- proposal hash

Replay reconstruction answers:

What exactly did the provider return?

without granting authority.

## Fail-Closed Behavior

The runtime fails closed on:

- unknown provider
- unavailable provider
- missing metadata
- malformed provider response
- invalid proposal envelope
- authority-bearing request
- replay corruption
- append-only replay violation

No fallback execution exists.

No silent degradation exists.

No provider ranking, routing intelligence, orchestration, planning, reflection,
or autonomous behavior is introduced.

## Provider Substitutability

OpenAI, Claude, Codex, Gemini, local LLM, and future providers fit the same
adapter contract without modifying governance, replay, authorization, or worker
execution models.

## Scope Lock

This milestone implements only:

Provider Request

Provider Adapter

Provider Proposal Envelope

Replay Evidence

It does not implement provider execution, worker execution, authorization,
governance decisions, planning, reflection, orchestration, task dispatch,
memory mutation, replay mutation, agent autonomy, multi-provider coordination,
provider ranking, or provider selection intelligence.
