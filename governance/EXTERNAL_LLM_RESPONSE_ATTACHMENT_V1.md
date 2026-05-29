# External LLM Response Attachment V1

Status: first real attachment milestone.

This milestone implements the smallest real LLM attachment boundary: an externally supplied LLM response is captured as untrusted input, normalized into a proposal artifact, and passed into the existing AiGOL governance path.

It preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Runtime Surface

Implemented runtime surface:

- `aigol/runtime/external_llm_response_attachment.py`

Implemented tests:

- `tests/test_external_llm_response_attachment_v1.py`

## Attachment Scope

The attachment accepts:

- `provider_identity`
- `external_response`

It records the external response before normalization and treats the response as untrusted input.

## Attachment Flow

```text
External LLM Response
-> raw_external_response
-> normalized_proposal
-> proposal_validation
-> existing AiGOL governance bridge
-> governed_result
```

## Replay Artifacts

The attachment records append-only replay artifacts:

- `000_raw_external_response.json`
- `001_normalized_proposal.json`
- `002_proposal_validation.json`
- `003_governed_result.json`

## Authority Boundary

The external response is never:

- execution authority
- authorization authority
- governance authority
- replay bypass authority
- worker instruction authority

It is proposal input only.

## Non-Goals Preserved

This milestone does not implement:

- OpenAI API integration
- Claude API integration
- Codex API integration
- network access
- provider SDKs
- orchestration
- memory
- capability expansion
- execution expansion
- worker changes

## Result

The external LLM response attachment proves that externally supplied model output can enter AiGOL as replay-visible proposal input without gaining authority.
