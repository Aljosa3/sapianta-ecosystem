# FIRST_REAL_PROVIDER_ATTACHMENT_V1

## Status

FIRST_REAL_PROVIDER_ATTACHMENT_STATUS = READY

## Purpose

This milestone attaches OpenAI as the first real provider adapter through the
existing minimal provider attachment runtime.

The provider remains proposal-only.

## Constitutional Invariant

LLM proposes.

AiGOL governs.

Worker executes.

Replay records.

## Implemented Provider

Provider:

- OpenAI

Runtime adapter:

- `aigol/provider/providers/openai_provider.py`

Validation:

- `tests/test_first_real_provider_attachment_v1.py`

## Target Flow

Human Prompt

Provider Runtime

OpenAI Provider Adapter

Provider Proposal Envelope

Replay Evidence

## Provider Contract

The OpenAI provider adapter implements the existing provider adapter contract.

It may:

- receive a request
- perform one provider call when configured with credentials
- return a provider response
- create a `ProviderProposalEnvelope`

It may not:

- execute
- authorize
- govern
- dispatch
- invoke workers
- mutate replay
- mutate memory
- rank providers
- select providers
- orchestrate providers

## Runtime Boundary

The adapter is invoked only through `run_provider_attachment`.

The adapter does not bypass:

- provider registry lookup
- provider state verification
- provider proposal envelope validation
- replay recording
- append-only replay enforcement
- replay reconstruction verification

## Replay Evidence

Replay captures:

- provider_id
- provider_version
- request
- response
- timestamp
- proposal_hash

Replay reconstructs:

What exactly did the provider return?

without granting authority.

## Fail-Closed Behavior

The attachment fails closed on:

- missing API key
- provider unavailable
- malformed response
- empty response
- authority-bearing provider response
- invalid proposal envelope
- unknown provider
- replay corruption

There is no silent fallback.

There is no provider-to-worker path.

There is no provider-to-governance authority path.

## Scope Lock

This milestone does not implement:

- provider execution
- worker execution
- authorization
- governance decisions
- planning
- reflection
- orchestration
- autonomous dispatch
- multi-provider routing
- provider ranking
- provider selection intelligence
- memory mutation
- replay mutation

## Final Classification

FIRST_REAL_PROVIDER_ATTACHMENT_STATUS = READY

Provider authority remains absent.

Provider remains proposal-only.
