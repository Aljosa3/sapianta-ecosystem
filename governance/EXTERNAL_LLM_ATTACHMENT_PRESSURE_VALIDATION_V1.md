# External LLM Attachment Pressure Validation V1

Status: post-attachment pressure validation milestone.

This milestone validates `EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1` under bounded pressure before any real provider integration.

It preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Validation Scope

Validated pressure cases:

- empty responses
- whitespace-only responses
- malformed responses
- oversized responses
- invalid provider identity
- missing provider identity
- proposal normalization failures
- replay corruption attempts
- authority escalation attempts
- append-only violations
- repeated successful attachments
- repeated failed attachments

## Runtime Validation

Pressure validation is implemented by:

- `tests/test_external_llm_attachment_pressure_validation_v1.py`

The existing attachment tests remain active:

- `tests/test_external_llm_response_attachment_v1.py`

## Bounded Hardening

The pressure validation introduced an explicit bounded response size limit for externally supplied responses.

Oversized responses fail closed before proposal normalization.

## Result

The external LLM attachment remained stable under bounded pressure. Failure paths produced replay-visible rejection artifacts, and successful paths preserved proposal-only semantics.

## Non-Expansion

This milestone does not introduce:

- real provider integration
- OpenAI API calls
- Claude API calls
- Codex API calls
- network access
- provider SDKs
- orchestration
- memory
- capability expansion
- execution expansion
- worker changes
