# AIGOL_HUMAN_COGNITION_EXTRACTION_FIX_V1

## Status

Implemented extraction boundary fix.

## Goal

Ensure operator-visible OCS cognition renders structured findings, assumptions, risks, uncertainties, clarification questions, and next milestone instead of a serialized JSON blob.

## Trace

The active path is:

```text
OpenAI provider response
-> provider proposal envelope response
-> conversational OCS transport
-> multi-provider cognition provider response artifact
-> LLM_COGNITION_ARTIFACT_V1
-> human_facing_cognition_result
-> render_operator_visible_ocs_llm_cognition(...)
-> CLI output
```

## Root Cause

The conversational OCS transport returned:

```text
response.get("raw_response") or {"output_text": response["response_text"]}
```

In this provider attachment path, `response["raw_response"]` is not the original OpenAI Responses API object. It is a replay-captured normalized text string.

When that normalized string contained JSON, downstream extraction could treat it as plain provider text. That allowed the cognition artifact to carry a serialized JSON object as one finding, while assumptions, risks, and uncertainties remained empty from the operator perspective.

## Determination

- JSON was stored as a string at the transport handoff.
- The JSON was not intentionally double-serialized by the cognition artifact runtime.
- The cognition normalizer can parse JSON when it receives JSON text in the expected `output_text` path.
- The renderer received normalized cognition content after the wrong handoff shape had already collapsed structure.

## Fix

The conversational OCS transport now always returns:

```text
{"output_text": response["response_text"]}
```

This preserves the provider attachment replay while giving the cognition runtime the expected provider-response shape.

## Preservation

Preserved:

- replay records;
- governance boundaries;
- provider non-authority;
- cognition artifact creation;
- routing;
- dispatch;
- existing technical summary.

No provider authority was granted.
No approval was created.
No execution was requested.
No worker invocation semantics changed.

## Regression

Regression coverage proves the conversational OpenAI path renders:

- findings;
- assumptions;
- risks;
- uncertainties;
- no serialized `{"findings": ...}` blob.

