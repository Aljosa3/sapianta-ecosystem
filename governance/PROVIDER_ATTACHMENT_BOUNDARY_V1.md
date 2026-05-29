# Provider Attachment Boundary V1

Status: implemented provider boundary definition.

## Boundary Principle

Provider output enters AiGOL only as proposal-source evidence.

The provider attachment may identify the provider, capture the provider response, and forward the response into the existing external LLM response attachment path.

The provider attachment may not authorize, execute, govern, mutate replay, or bypass downstream AiGOL governance.

## Accepted Input

The provider boundary accepts:

- `provider_identity`
- `provider_response`

Provider identity must be deterministic.

Provider response must be explicit, bounded, and replay-visible.

## Boundary Flow

```text
provider_identity
-> raw_provider_response
-> provider_attachment_record
-> external_llm_response_attachment
-> governed_result
```

## Fail-Closed Boundary Conditions

The boundary fails closed on:

- missing provider identity
- invalid provider identity
- empty provider response
- malformed provider response
- replay corruption
- append-only violation
- proposal normalization failure

## Boundary Result

Successful provider attachment means only that provider output was admitted as untrusted proposal input and processed through existing AiGOL governance.

It does not mean the provider gained authority.
