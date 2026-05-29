# Claude Provider Architecture Impact V1

Status: Claude architecture impact review.

## Architecture Impact Classification

`CLAUDE_ARCHITECTURE_IMPACT`: `NO_NEW_ARCHITECTURE_REQUIRED`

## Required Claude-Specific Work

Claude adapter implementation requires only provider-specific adapter logic:

- Claude SDK isolation
- Claude credential boundary
- Claude request envelope
- Claude response extraction
- Claude provider error mapping
- Claude timeout handling
- Claude raw response capture before normalization

These are adapter-local requirements.

## Not Required

Claude does not require:

- new runtime concepts
- new governance concepts
- new authority concepts
- new replay concepts
- new worker concepts
- new capability concepts
- provider routing
- provider discovery
- provider selection
- memory
- orchestration

## Architecture Reuse

Claude should reuse:

- `REAL_PROVIDER_ATTACHMENT_V1`
- `EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1`
- proposal normalization
- AiGOL governance validation
- authorization model
- read-only worker path
- replay reconstruction
- OpenAI pressure validation categories

## Boundary Difference From OpenAI

The only expected differences are:

- provider identity: `CLAUDE`
- normalized provider identity: `claude`
- SDK/client boundary
- response text extraction shape
- credential environment convention
- provider-specific error names

These differences do not alter AiGOL constitutional architecture.

## Constraint

Claude must not introduce tools, function calling, streaming, retries, memory, orchestration, provider routing, or provider authority.

