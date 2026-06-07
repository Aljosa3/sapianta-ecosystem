# AIGOL_REAL_COGNITION_PIPELINE_TRACE_V1

## Status

Review-only trace.

No runtime fix was implemented.
No CLI behavior was intentionally changed by this trace.
No provider behavior was changed.
No workflow behavior was changed.

## Goal

Trace the real conversational OCS cognition path and identify where structured cognition collapses into a serialized JSON string visible to the operator.

## Runtime Path

The relevant path is:

```text
acli / conversational CLI
-> OCS_LLM_COGNITION
-> OpenAI Provider
-> provider proposal envelope response
-> conversational OCS transport
-> multi-provider cognition provider response artifact
-> LLM_COGNITION_ARTIFACT_V1
-> human_facing_cognition_result
-> render_operator_visible_ocs_llm_cognition(...)
-> CLI output
```

## Stage Trace

### 1. OpenAI Provider Response

Location:

```text
aigol/provider/providers/openai_provider.py:75-82
```

Observed type:

```text
OpenAI response object: dict
OpenAI output content text: str
```

OpenAI Responses API content is text. If the model returns JSON, it arrives as a string in:

```text
output[].content[].text
```

This is expected and not itself a failure.

### 2. Provider Response Artifact

Location:

```text
aigol/provider/providers/openai_provider.py:76-82
```

`response_text` is extracted as a string and stored in the provider proposal envelope response.

If OpenAI emits:

```json
{"findings":["{\"findings\":[...],\"assumptions\":[...]}"]}
```

then `response_text` is a string containing that outer JSON object.

### 3. Multi-Provider Cognition Provider Response Artifact

Location:

```text
aigol/runtime/multi_provider_cognition_runtime.py:421-447
```

The transport return is stored as `raw_response`.

`_extract_response_text(...)` at:

```text
aigol/runtime/multi_provider_cognition_runtime.py:849-859
```

extracts provider response text as a string.

### 4. LLM_COGNITION_ARTIFACT_V1 Creation

Location:

```text
aigol/runtime/cognition_artifact_runtime.py:266-306
```

Top-level JSON parsing occurs at:

```text
aigol/runtime/cognition_artifact_runtime.py:269
aigol/runtime/cognition_artifact_runtime.py:287-294
```

If the top-level provider text is valid JSON, it is parsed to a dict.

The loss occurs when the top-level dict has this shape:

```json
{
  "findings": [
    "{\"findings\":[...],\"assumptions\":[...],\"risks\":[...]}"
  ],
  "confidence": "MEDIUM"
}
```

The inner JSON remains a string item in `findings`.

The exact preservation point is:

```text
aigol/runtime/cognition_artifact_runtime.py:302-306
```

`_normalize_string_list(...)` treats each list item as a bounded string. It does not recursively parse JSON-looking strings inside `findings`, and it does not redistribute inner `assumptions`, `risks`, or `uncertainties`.

### 5. Human-Facing Cognition Normalization

Location:

```text
aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py:465-480
```

The human-facing result reads from normalized cognition artifacts. If `LLM_COGNITION_ARTIFACT_V1.findings[0]` is already a JSON string, that string is the source value available to human-facing projection.

Current workspace code includes a renderer-side extraction helper, but the root collapse has already occurred in the cognition artifact field assignment.

### 6. Operator Renderer

Location:

```text
aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py:300-320
```

The renderer receives `human_facing_cognition_result["findings"]`.

If that list contains a serialized JSON string, the renderer can only render, suppress, or locally unwrap it. It is not the first serialization stage.

## Determination

Structured cognition first appears as model-generated JSON text inside the OpenAI response content string.

The problematic nested structure is not:

```text
top-level JSON string
```

because top-level JSON is parsed.

The problematic structure is:

```text
JSON string nested inside findings[]
```

The first in-repository point where that nested JSON is preserved as a finding string is:

```text
aigol/runtime/cognition_artifact_runtime.py:302-306
```

## Root Cause

The provider output shape is one level too deeply serialized:

```json
{
  "findings": [
    "{\"findings\":[...],\"assumptions\":[...],\"risks\":[...]}"
  ]
}
```

`_normalize_provider_cognition(...)` parses only the top-level JSON object. `_normalize_string_list(...)` then treats the inner JSON document as a valid string finding.

As a result:

- `findings` receives the JSON blob string;
- `assumptions` remains empty;
- `risks` remains empty;
- `uncertainties` remains empty.

## No Fix Applied

This artifact is trace-only. It identifies the boundary and does not change runtime code.

