# Provider Replay Model V1

Status: implemented provider replay definition.

## Purpose

Provider replay records provider attachment evidence before the provider response enters the external LLM response attachment path.

Replay remains the source of truth.

## Provider Replay Stages

Provider attachment replay contains:

1. `provider_identity`
2. `raw_provider_response`
3. `provider_attachment_record`
4. `governed_result`

All stages are append-only and hash-verified.

## Nested Replay

The provider attachment delegates response ingestion to `EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1`.

Nested replay is stored under the provider replay scope and includes:

- raw external response
- normalized proposal
- proposal validation
- governed result

## Replay Requirements

Provider replay must preserve:

- provider identity
- raw provider response
- provider response hash
- provider attachment record
- external attachment lineage
- governed result
- non-authority flags

## Replay Failure Handling

Replay corruption, hash mismatch, ordering mismatch, missing artifacts, and append-only violations fail closed.

No replay repair or silent recovery is allowed.
