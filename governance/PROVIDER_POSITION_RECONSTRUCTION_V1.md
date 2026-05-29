# Provider Position Reconstruction V1

Status: reconstruction of current provider position.

## What A Provider Is

A provider is an external proposal source boundary.

A provider may supply bounded response evidence that can be normalized into a proposal artifact. The provider is not a governor, executor, authorizer, replay authority, worker, orchestrator, or agent.

## Current Provider Identity

Provider identity is already modeled through:

- `provider_identity` in `REAL_PROVIDER_ATTACHMENT_V1`
- `provider_id`, `provider_type`, `provider_name`, `model_identity`, `invocation_id`, and `response_id` in `LLM_PROVIDER_IDENTITY_MODEL_V1`
- `provider_name` and `model_name` in `PROVIDER_AGNOSTIC_RAW_RESPONSE_CAPTURE_V1`
- provider envelope identity in governed provider activation

Classification: `COMPLETE`

Evidence:

- Identity is replay-visible.
- Identity is immutable after capture.
- Identity is linked to raw response evidence.
- Identity does not grant authority.
- Runtime identity validation fails closed on missing or malformed identity.

## Current Provider Flow

The reconstructed provider flow is:

```text
Provider identity
-> raw provider response
-> provider attachment record
-> external response attachment
-> normalized proposal
-> AiGOL governance
-> authorization or rejection
-> governed result
-> replay reconstruction
```

## Current Provider Authority

Provider authority is explicitly absent.

Provider cannot:

- execute
- authorize
- govern
- mutate replay
- mutate governance
- spawn workers
- select capabilities
- bypass proposal normalization

Classification: `ABSENT`

## Current Provider Relationship To AiGOL

Provider output is untrusted input.

AiGOL remains responsible for:

- validation
- normalization acceptance or rejection
- authorization
- replay recording
- governed return
- fail-closed handling

## Current Provider Relationship To Worker

Provider does not address Worker directly.

The invariant remains:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Worker execution occurs only after AiGOL governance and authorization.

## Current Provider Replaceability

Provider replacement is constitutionally supported because provider identity is generic and provider authority is absent.

Classification: `PARTIAL`

Evidence:

- OpenAI, Claude, local models, and future providers can be represented as provider identities.
- Replay can preserve different provider identities.
- Adapter-specific code may still be required for transport and response extraction.
- Provider selection and lifecycle are not complete.

## Current Provider Registry And Activation

Existing evidence contains:

- a passive provider registry that registers and exposes metadata
- a provider activation gate requiring explicit registration and authorized governance state
- OpenAI provider activation evidence

This proves registration and activation are partially present, but not a full provider ecosystem.

## Reconstruction Result

The current provider position is mostly complete as a constitutional proposal-source boundary.

It is not complete as a multi-provider ecosystem.

