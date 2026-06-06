# AIGOL_REAL_OPENAI_COMPARISON_ARTIFACT_TRACE_REVIEW_V1

## Status

Review-only investigation.

No code was changed. No runtime was changed. No provider behavior was changed. No governance model was changed.

## Executive Finding

The conversational CLI reached:

```text
workflow: OCS_LLM_COGNITION
```

and the conversational OCS binding created two provider request slots:

```text
openai
openai-comparison
```

However, neither provider produced a successful `LLM_COGNITION_ARTIFACT_V1` in the observed replay.

Both provider slots failed during:

```text
PROVIDER_COGNITION_PROCESSING
```

The underlying provider attachment replay for both slots recorded:

```text
event_type: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
provider_invoked: false
response: null
```

Therefore comparison failed correctly because the comparison runtime received zero successful cognition artifacts:

```text
SUCCESSFUL_COGNITION_ARTIFACT_COUNT = 0
COMPARISON_MINIMUM_REQUIRED = 2
```

## Final Answer

```text
OPENAI_ARTIFACT_CREATED = false
OPENAI_COMPARISON_ARTIFACT_CREATED = false
SUCCESSFUL_COGNITION_ARTIFACT_COUNT = 0
COMPARISON_MINIMUM_REQUIRED = 2
ROOT_CAUSE = Both OpenAI-backed provider attachment attempts failed closed with OpenAI provider unavailable before provider response artifact creation and cognition artifact normalization; the multi-provider runtime isolated both provider failures and comparison then failed because zero successful cognition artifacts were available.
```

## Direct Answers

1. `openai` did not produce a valid successful `LLM_COGNITION_ARTIFACT_V1` in the observed replay.

2. `openai-comparison` did not produce a valid successful `LLM_COGNITION_ARTIFACT_V1` in the observed replay.

3. Both providers failed before artifact normalization. No provider-specific `providers/<provider_id>/cognition_artifact` replay directory exists for the observed failed turn.

4. `openai-comparison` uses the same provider adapter and credential path as `openai`. In `aigol/cli/aigol_cli.py`, both transport keys call `run_provider_attachment(...)` with `provider_id=OPENAI_PROVIDER_ID`, `_conversation_openai_provider_registry()`, and `_conversation_openai_provider_adapter()`.

5. Both provider contracts are approved as `COGNITION_PROVIDER`. The request bundle contains request artifacts for both providers with `provider_role: COGNITION_PROVIDER` and `provider_schema_id: openai.responses.v1`.

6. The transport registry contains both keys:

```text
openai
openai-comparison
```

7. In the observed failed replay, the OpenAI transport did not return valid response text for either provider. Provider attachment replay recorded `response: null`.

8. Neither provider was rejected during response extraction, cognition artifact normalization, authority-language validation, or response schema validation. The failure happened earlier at the provider attachment / OpenAI availability boundary.

9. The multi-provider runtime does not silently discard failed provider outputs. It records isolated `PROVIDER_COGNITION_FAILURE_ARTIFACT_V1` entries in the result bundle.

10. The final provider failure artifacts are recorded inside:

```text
.aigol_conversation_runtime/AIGOL-INTERACTIVE-CONVERSATION-000001/TURN-000153/ocs_llm_cognition_end_to_end/stages/multi_provider_cognition/001_multi_provider_cognition_result_bundle.json
```

The comparison failure artifact is recorded at:

```text
.aigol_conversation_runtime/AIGOL-INTERACTIVE-CONVERSATION-000001/TURN-000153/ocs_llm_cognition_end_to_end/stages/cognition_comparison/000_cognition_comparison_artifact.json
```

## Execution Trace

### Human Prompt To Binding

```text
Human Prompt
-> conversational routing
-> OCS_LLM_COGNITION
-> _run_conversational_ocs_llm_cognition(...)
```

Binding implementation:

```text
aigol/cli/aigol_cli.py::_conversation_ocs_cognition_provider_contracts
aigol/cli/aigol_cli.py::_conversation_ocs_cognition_transports
```

### Provider Contracts

The binding constructs two OpenAI-backed contracts:

```text
openai
openai-comparison
```

Both carry:

```text
provider_role: COGNITION_PROVIDER
provider_schema_id: openai.responses.v1
provider_kind: external_llm
```

### Transport Registry

The binding returns:

```text
{
  "openai": _transport,
  "openai-comparison": _transport
}
```

### OpenAI Adapter Call

For both provider IDs, `_transport(...)` calls:

```text
run_provider_attachment(
  provider_id="openai",
  adapter=_conversation_openai_provider_adapter(),
  registry=_conversation_openai_provider_registry(),
)
```

The OpenAI adapter attempts:

```text
OpenAIProviderAdapter.generate_proposal(...)
-> _resolve_api_key(...)
-> _call_openai(...)
-> OpenAIHTTPClient
```

### Observed Provider Attachment Replay

For `openai`:

```text
event_type: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
provider_invoked: false
response: null
```

For `openai-comparison`:

```text
event_type: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
provider_invoked: false
response: null
```

### Multi-Provider Result Bundle

Observed result:

```text
provider_count: 2
successful_provider_count: 0
failed_provider_count: 2
cognition_artifact_hashes: []
provider_results: []
provider_failures:
  - provider_id: openai
    failed_stage: PROVIDER_COGNITION_PROCESSING
  - provider_id: openai-comparison
    failed_stage: PROVIDER_COGNITION_PROCESSING
```

### Comparison Runtime

The comparison runtime extracts cognition artifacts from successful provider results only. It requires at least two artifacts:

```text
if len(artifacts) < 2:
    raise FailClosedRuntimeError("at least two cognition artifacts are required for comparison")
```

Because `len(artifacts) == 0`, comparison failed closed.

## Root Cause

The immediate root cause is provider unavailability at the OpenAI provider attachment boundary for both provider slots.

The architectural contributing factor is that `run_provider_attachment(...)` returns a failed provider proposal envelope instead of raising. The conversational OCS transport then expects `provider_proposal_envelope["response"]` to be a response object; because the failed envelope contains `response: null`, provider processing fails and the multi-provider runtime records generic isolated provider failures.

The comparison runtime behavior is correct: it should fail closed when fewer than two successful cognition artifacts exist.

## Classification

```text
AIGOL_REAL_OPENAI_COMPARISON_ARTIFACT_TRACE_REVIEW_V1
REVIEW_ONLY
ROOT_CAUSE_CONFIRMED
```
