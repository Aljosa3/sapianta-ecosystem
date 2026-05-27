# PROVIDER_AGNOSTIC_RAW_RESPONSE_CAPTURE_V1

## Scope

This milestone adds provider-agnostic raw response capture to the live governed
cognition runtime so that the raw textual response from any LLM provider is
preserved as replay-visible evidence **before** bounded proposal normalization.

It exists to diagnose why live provider outputs fail normalization without
binding AiGOL core to OpenAI. AiGOL core continues to consume **only**
normalized `BoundedCognitionProposal` artifacts; the raw response evidence lives
strictly at the provider-adapter boundary.

It exposes:

- `RawProviderResponseEvidence`
- `capture_raw_provider_response(...)`
- `reconstruct_raw_provider_response_lineage(...)`
- `raw_response_evidence_hash` on `LiveOpenAIRuntimeConnectorEvidence`
- a `raw_provider_response` key in the OpenAI connector return surface
- `raw_provider_response_*` fields on `LiveCognitionRejectionAnalysisEvidence`
- raw response presence/hash/reason in the rejection analysis CLI render

## Provider-Agnostic Boundary

`aigol.runtime.raw_provider_response_capture` carries no OpenAI, Anthropic,
Claude, GPT, or any other provider-specific identifier in its source. The
evidence model only knows about:

- `provider_name` (free-form, e.g. "openai", "claude", "local")
- `model_name` (free-form, e.g. "gpt-5.5", "claude-opus-4-7")
- `raw_response_text` (free-form provider text)
- `raw_response_hash` (deterministic `sha256` of the text)
- `normalization_status` (`NORMALIZED` / `REJECTED` / `ABSENT`)
- `normalization_reason` (free-form adapter reason)

Provider adapters (currently OpenAI; future Claude / local) populate this
evidence at their boundary. AiGOL core never reads `raw_response_text` to make
governance decisions — it only consumes normalized `BoundedCognitionProposal`
artifacts past this boundary.

## OpenAI Adapter Integration

The existing OpenAI adapter (`live_openai_runtime_connector`) now:

1. Calls OpenAI.
2. Extracts the raw `output_text` string (provider-specific, lives only in the adapter).
3. Captures it into `RawProviderResponseEvidence` **before** attempting normalization.
4. Attempts JSON parsing + bounded proposal validation + `BoundedCognitionProposal` construction.
5. If normalization succeeds, the connector status is `NORMALIZED` and a proposal is emitted.
6. If normalization fails, the connector status is `REJECTED`, no proposal is emitted, but the raw evidence is **still** preserved with its deterministic hash and the adapter's `normalization_reason`.
7. The connector evidence carries `raw_response_evidence_hash` linking the connector lineage to the raw evidence lineage.

This change does **not** alter what AiGOL core consumes: only normalized
`BoundedCognitionProposal` artifacts cross the boundary into governance.

## Rejection Analysis Visibility

`LiveCognitionRejectionAnalysisEvidence` now surfaces:

- `provider_connector_status` / `provider_connector_reason` (renamed from
  `openai_connector_*` to remove provider lock-in in AiGOL core)
- `raw_provider_response_provider_name`
- `raw_provider_response_model_name`
- `raw_provider_response_present`
- `raw_provider_response_hash`
- `raw_provider_response_evidence_hash`
- `raw_provider_response_normalization_status`
- `raw_provider_response_normalization_reason`

The CLI render exposes these fields verbatim so an operator can inspect raw
provider behavior even when the proposal failed normalization.

A new rejection stage `PROPOSAL_NORMALIZATION` replaces the prior
`OPENAI_INVOCATION` stage label in the analyzer. The new
`RAW_PROVIDER_RESPONSE` stage covers the case where the provider returned no
recoverable raw text.

## Guarantees

- Raw response text preserved even when normalization fails closed.
- `raw_response_hash == sha256(raw_response_text)` is deterministic and verified at construction.
- Evidence hash mismatches fail closed.
- AiGOL core (`raw_provider_response_capture`, `live_cognition_rejection_analysis`) contains no OpenAI / Anthropic / Claude / GPT identifier.
- Only normalized `BoundedCognitionProposal` artifacts cross the adapter boundary.
- Replay-visible append-only lineage preserved.
- No new execution authority, orchestration, retries, async runtime, runtime mutation, provider mutation, or new capability layer introduced.

## Non-Goals

- New execution authority.
- New capability layers.
- New orchestration surfaces.
- Retries.
- Async runtime.
- Runtime mutation.
- Provider mutation.
- OpenAI lock-in.
- Claude-specific implementation (deferred to a future provider adapter milestone).
- New telemetry platform.

## Certification

`PROVIDER_AGNOSTIC_RAW_RESPONSE_CAPTURE_V1` certifies a provider-agnostic raw
response evidence model, integration into the OpenAI provider adapter before
normalization, preservation of raw text and deterministic hash even on
normalization failure, exposure of raw response presence/hash/reason in the
existing rejection analysis CLI, and preservation of the `BoundedCognitionProposal`
boundary as the only artifact AiGOL core consumes — without introducing new
runtime architecture, new capability layers, orchestration, retries, async
runtime, runtime mutation, provider mutation, OpenAI lock-in, Claude-specific
implementation, or a new telemetry platform.
