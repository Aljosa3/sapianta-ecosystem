# Raw External Response Replay V1

Status: implemented replay evidence definition.

## Purpose

Raw external response replay preserves externally supplied LLM output before normalization.

This makes the proposal source visible without allowing raw text to become authority.

## Replay Stages

The attachment records:

1. `raw_external_response`
2. `normalized_proposal`
3. `proposal_validation`
4. `governed_result`

All stages are append-only and hash-verified.

## Raw Response Artifact

The raw response artifact records:

- attachment id
- provider identity
- created timestamp
- raw response text
- raw response hash
- untrusted input flag
- non-authority flags

## Normalized Proposal Artifact

The normalized proposal artifact records:

- provider identity
- raw response artifact hash
- bridge-compatible proposal artifact
- proposal artifact hash
- untrusted proposal flag
- non-authority flags

## Failure Replay

Failures produce replay-visible rejection artifacts for all required replay stages.

Failure replay preserves:

- failure reason
- provider identity if available
- attachment id if available
- non-authority guarantees
- no worker execution

## Replay Integrity

Reconstruction validates:

- replay ordering
- replay wrapper hashes
- artifact hashes
- append-only presence
- final status

Replay corruption fails closed.
