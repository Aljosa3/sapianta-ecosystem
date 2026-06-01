# PROMPT_EVIDENCE_CONTINUITY_RESTORATION_ADR_V1

## Status

Accepted.

## Context

`PROMPT_EVIDENCE_CONTINUITY_ANALYSIS_V1` proved that `human_prompt` was
replay-visible but not preserved as a structured field inside the OpenAI
provider proposal envelope request.

The missing field caused fourth-epoch classification normalization failures:

```text
human_prompt is required
```

## Decision

Preserve original structured request evidence across the OpenAI provider
adapter boundary.

Provider proposal envelopes now retain:

- `human_prompt`;
- `original_request`;
- adapter-specific OpenAI `payload`;
- `api_key_captured = false`.

Secret-like fields in `original_request` are redacted before persistence.

## Consequences

Structured human prompt evidence now survives the:

```text
Human -> AiGOL -> Provider -> AiGOL
```

cycle.

The decision does not grant providers authority to route, govern, authorize,
execute, invoke workers, or mutate replay.

## Certification

```text
PROMPT_EVIDENCE_CONTINUITY_RESTORATION_STATUS = READY
```
