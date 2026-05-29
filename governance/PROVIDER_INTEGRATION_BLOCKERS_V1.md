# Provider Integration Blockers V1

Status: readiness blocker classification.

## MUST FIX

Before any provider adapter:

- define provider-specific adapter input/output schema
- record provider id, model identity, invocation id, response id, and created timestamp
- capture raw provider output before normalization
- map provider errors to deterministic fail-closed artifacts
- prohibit provider authorization, execution, governance, replay mutation, retries, streaming, and hidden continuation
- ensure provider output enters only through `REAL_PROVIDER_ATTACHMENT_V1`

Before OpenAI adapter:

- define SDK isolation boundary
- define credential handling boundary
- define response text extraction
- define API failure and timeout evidence
- define no automatic retry rule

Before Claude adapter:

- define SDK isolation boundary
- define credential handling boundary
- define response text extraction
- define API failure and timeout evidence
- define no automatic retry rule

Before Codex adapter:

- define Codex proposal-only boundary
- prove Codex cannot execute through provider path
- prove Codex cannot mutate files through provider path
- prove Codex cannot become worker authority
- separate Codex proposal source semantics from Codex execution/tool semantics

## SHOULD FIX

- add provider adapter pressure tests before live invocation
- add replay summary support for provider-specific invocation evidence
- add operator-facing provider failure summaries
- add explicit redaction policy for credential-adjacent error messages
- add provider-specific response-size validation

## OPTIONAL

- add provider registry later
- add multiple provider support later
- add model selection later
- add provider health checks later
- add adapter-specific diagnostics later

These optional items must not block the first bounded provider adapter.
