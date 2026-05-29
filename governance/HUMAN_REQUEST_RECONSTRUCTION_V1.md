# Human Request Reconstruction V1

Status: reconstruction of existing Human Request semantics.

## What A Human Request Is

A Human Request is operator-supplied bounded input asking AiGOL to perform a governed read-only operation or to obtain a provider proposal that may later be governed.

It is not:

- execution authority
- authorization authority
- governance authority
- replay authority
- worker authority
- provider routing authority

## Existing Request Shapes

AiGOL currently represents human requests through several compatible shapes:

- `human_request` in the minimal operator entrypoint
- `human_prompt` in the end-to-end governed read-only flow
- `human_prompt` inside cognition proposal artifacts
- request text and request hash in OpenAI provider request metadata

These are semantically aligned but not fully canonicalized into one vocabulary.

## Human Request Identity

Classification: `PARTIAL`

Evidence:

- Direct operator flow creates a replay-visible `human_prompt` artifact.
- Operator flow artifacts include `operator_flow_id`, `human_prompt`, `target_capability`, and `created_at`.
- OpenAI provider adapter records request text and request hash in provider request metadata.
- Request identity is replay-visible, but no standalone canonical `HumanRequestIdentity` object exists.

## Replay Visibility

Human Request is replay-visible in current flows.

Evidence:

- `human_prompt_to_governed_readonly_result` persists `000_human_prompt.json`.
- OpenAI provider adapter persists `000_provider_request_metadata.json` containing request text and request hash.
- Proposal artifacts link back to the human prompt artifact hash.

## Lifecycle Reconstruction

The current lifecycle is:

```text
Human Request
-> request/prompt capture
-> proposal creation or provider proposal path
-> proposal normalization
-> AiGOL validation
-> AiGOL authorization or rejection
-> worker execution only if authorized
-> governed result
-> replay reconstruction
```

Lifecycle classification: `COMPLETE` for the first useful governed read-only flow, `PARTIAL` for generalized multi-provider request handling.

## Reconstruction Result

Human Request is already a bounded, replay-visible operator input.

It is mostly positioned, but the exact canonical terminology remains split across prompt, request, proposal, and provider metadata surfaces.

