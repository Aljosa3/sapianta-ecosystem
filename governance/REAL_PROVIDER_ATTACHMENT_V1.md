# Real Provider Attachment V1

Status: first real provider boundary milestone.

This milestone implements the smallest provider attachment boundary above `EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1`.

It preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Runtime Surface

Implemented runtime surface:

- `aigol/runtime/provider_attachment.py`

Implemented tests:

- `tests/test_real_provider_attachment_v1.py`

## Provider Boundary Scope

The provider adapter accepts:

- `provider_identity`
- `provider_response`

It validates provider identity, captures raw provider response evidence, records provider attachment lineage, and forwards the response into the existing external LLM response attachment path.

## Provider Role

Provider remains:

- proposal source only
- replay-visible evidence source
- non-authoritative
- non-executing

Provider is never:

- execution authority
- authorization authority
- governance authority
- replay authority

## Replay Artifacts

The provider attachment records:

- `000_provider_identity.json`
- `001_raw_provider_response.json`
- `002_provider_attachment_record.json`
- `003_governed_result.json`

The nested external response attachment records:

- raw external response
- normalized proposal
- proposal validation
- governed result

## Non-Goals Preserved

This milestone does not implement:

- OpenAI SDK
- Anthropic SDK
- Codex SDK
- network transport
- API credentials
- orchestration
- memory
- capability expansion
- worker expansion
- autonomous execution

## Result

The provider boundary proves:

```text
Provider
-> Provider Attachment
-> External Response Attachment
-> AiGOL Governance
```

without granting provider authority.
