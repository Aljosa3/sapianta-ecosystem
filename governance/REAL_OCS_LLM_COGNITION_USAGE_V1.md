# REAL_OCS_LLM_COGNITION_USAGE_V1

## Status

Real-world operational validation.

This validation checks whether a real LLM cognition provider is currently participating inside the certified OCS LLM cognition workflow.

No runtime was created. No implementation was performed. No provider credentials were persisted.

## Test Scenario

Human request:

`I want to create the first real AiGOL product.`

Target flow:

Human Question
-> OCS Context
-> Cognition Provider
-> Cognition Artifact
-> Comparison
-> Continuity
-> Clarification
-> Human-facing Result

## Validation Result

```text
REAL_LLM_PROVIDER_ATTACHED = false
REAL_LLM_PROVIDER_USED_BY_OCS = false
```

## Evidence Summary

At least one real cognition provider can be registered and approved:

- provider id: `openai`
- provider type: `external_llm`
- provider role: `COGNITION_PROVIDER`
- contract source: `create_default_openai_cognition_provider_contract`
- provider schema: `openai.responses.v1`
- endpoint: `https://api.openai.com/v1/responses`

The local environment has a provider credential available. The credential value was not printed into governance artifacts and was not persisted.

With network access enabled, a direct OpenAI Responses API probe succeeded.

However, the real provider did not produce a valid `LLM_COGNITION_ARTIFACT_V1` in the certified OCS end-to-end cognition flow.

## OCS End-To-End Probe

The certified `AIGOL_OCS_LLM_COGNITION_END_TO_END_V1` runtime was invoked with:

- real OpenAI cognition provider;
- deterministic local control provider;
- replay-visible OCS source context;
- human request: `I want to create the first real AiGOL product.`

Result:

```text
final_status = FAILED_CLOSED
failure_reason = cognition comparison failed closed: at least two cognition artifacts are required for comparison
```

The deterministic control provider produced a valid `LLM_COGNITION_ARTIFACT_V1`.

The OpenAI provider failed during `PROVIDER_COGNITION_PROCESSING`.

Provider failure reason:

```text
provider response did not include response text
```

## Exact Missing Component

The current multi-provider cognition runtime does not normalize the current OpenAI Responses API output shape.

Observed safe response shape:

- top-level `output_text` absent;
- content available under `output[].content[].text`;
- content item type: `output_text`.

Current failing extractor:

- `aigol/runtime/multi_provider_cognition_runtime.py`
- `_extract_response_text`
- accepts only top-level `output_text`, `text`, or `response_text`.

Therefore OpenAI can be reached, but the certified multi-provider OCS path cannot currently convert the real OpenAI response into a provider response artifact and then into `LLM_COGNITION_ARTIFACT_V1`.

## Single-Provider Probe

The certified single-provider cognition runtime was also tested with OpenAI.

Result:

```text
final_status = FAILED_CLOSED
failure_reason = cognition provider response exceeds authority boundary
```

This means the single-provider path can reach OpenAI and inspect the response shape, but the real output did not pass the authority-boundary filter for this product-domain prompt.

## Validation Question Answers

1. Is at least one real cognition provider registered?

Yes. OpenAI can be represented by the certified cognition-provider contract.

2. Is at least one real cognition provider approved?

Yes. The OpenAI cognition-provider contract marks `provider_approved = true`.

3. Can OCS invoke that provider?

Partially. The operational probe reached OpenAI when network access was enabled, but OCS did not complete provider response capture for OpenAI in the multi-provider runtime.

4. Does the provider produce a valid `LLM_COGNITION_ARTIFACT_V1`?

No. The OpenAI output did not become a valid cognition artifact.

5. Does the artifact participate in comparison, continuity, and clarification?

No. No OpenAI cognition artifact was produced, so OpenAI could not participate in comparison, continuity, or clarification.

6. Can replay reconstruct the entire chain?

No for the real-provider OCS E2E chain. Replay exists for the failed OCS attempt and deterministic provider branch, but the full chain fails closed before comparison and continuity.

## Final Classification

```text
REAL_OCS_LLM_COGNITION_USAGE_V1 = FAILED_REAL_PROVIDER_OCS_PARTICIPATION
```

## Next Required Fix

Recommended next milestone:

`AIGOL_REAL_OPENAI_COGNITION_RESPONSE_NORMALIZATION_V1`

Required scope:

- normalize OpenAI Responses API `output[].content[].text` in the multi-provider cognition runtime;
- preserve authority-boundary filtering;
- preserve fail-closed behavior;
- prove that real OpenAI output can become `LLM_COGNITION_ARTIFACT_V1`;
- rerun full OCS E2E comparison, continuity, clarification, and replay reconstruction.
