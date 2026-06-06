# AIGOL_OPENAI_RESPONSE_SIZE_ROOT_CAUSE_REPORT_V1

## Status

Review-only response-size root-cause investigation.

No runtime code was changed. No provider behavior was changed. No governance semantics were changed.

## Executive Finding

The conversational OCS OpenAI response exceeds the provider adapter bound because the cognition provider request permits an unconstrained non-streaming model response for a multi-section strategic analysis prompt.

The same replayed OpenAI OCS request produced:

```text
REQUEST_CHARACTER_COUNT = 3059
REQUEST_TOKEN_ESTIMATE = 842 input tokens from OpenAI usage
EXPECTED_RESPONSE_CHARACTER_COUNT = 23052
OUTPUT_TOKENS = 4875
MAX_OPENAI_RESPONSE_CHARS = 8192
```

The response is approximately:

```text
23052 / 8192 = 2.81x
```

the current adapter response bound.

## Root Cause

The size failure is caused by the cognition provider request and OpenAI payload layer:

```text
multi_provider_cognition_runtime._provider_prompt(...)
-> OpenAIProviderAdapter._create_openai_payload(...)
-> {"model": "gpt-5.1", "input": prompt, "stream": False}
-> no max_output_tokens
-> long multi-section response
-> _bounded_response_text(...)
-> OpenAI provider response exceeds bounded size
```

The response-size failure happens before:

- cognition artifact normalization;
- comparison;
- continuity;
- clarification.

Therefore the excessive output is not caused by comparison, continuity, clarification, or replay writing. It is caused by unconstrained cognition-provider output generation for the conversational OCS prompt.

## Prompt And Context Trace

Provider prompt construction:

```text
aigol/runtime/multi_provider_cognition_runtime.py::_create_provider_request_artifact
-> _provider_prompt(...)
```

The prompt contains:

- isolated cognition-provider instruction;
- provider id;
- full human request;
- OCS context reference;
- allowed outputs.

Context assembly:

```text
aigol/runtime/ocs_context_assembly_runtime.py::assemble_ocs_context
```

The validated replayed context had:

```text
accepted_input_count: 3
deduplicated_input_count: 0
rejected_input_count: 0
context_artifact_chars: 6094
```

The actual provider input was much smaller than the full context artifact because `_provider_prompt(...)` includes context references and sections, not the full context artifact:

```text
openai input_chars: 3059
openai-comparison input_chars: 3070
```

## Component Attribution

| Component | Causes excessive output? | Finding |
| --- | --- | --- |
| Cognition provider request | `YES` | Full human request asks for ten sections and reasoning. |
| OpenAI payload assembly | `YES` | Payload has no output-token or response-size budget. |
| Prompt assembly | `YES` | Prompt passes the broad human request through unchanged. |
| Replay context | `NO` | Request is only about 3.1k chars / 842 input tokens. |
| Comparison | `NO` | Not reached before provider response-size failure. |
| Continuity | `NO` | Not reached. |
| Clarification | `NO` | Not reached. |

## Sanitized Live Measurement

Using the same replayed OCS provider request, direct `OpenAIHTTPClient` measurement with a 60 second timeout returned a raw response successfully. The generated text was not printed or persisted by the probe.

Measured metadata:

```text
elapsed_seconds: 41.636
response_text_chars: 23052
input_tokens: 842
output_tokens: 4875
total_tokens: 5717
exceeds_8192: true
```

## Why The Existing Bound Fails

The adapter accepts only:

```text
MAX_OPENAI_RESPONSE_CHARS = 8192
```

implemented at:

```text
aigol/provider/providers/openai_provider.py::_bounded_response_text
```

The observed response was:

```text
23052 characters
```

so `_bounded_response_text(...)` correctly fails closed.

## Smallest Safe Fix

The smallest safe fix is not to remove the response bound.

Recommended minimal safe change:

1. Add an explicit bounded output budget to the conversational OCS OpenAI payload.
2. Make that budget deterministic and replay-visible.
3. Keep `MAX_OPENAI_RESPONSE_CHARS` as a post-response safety guard.
4. Adjust the cognition provider instruction to require concise bounded JSON-like sections that fit the response bound.

Example target semantics:

```text
Provider request output budget <= current response character bound
OpenAI payload max_output_tokens configured accordingly
Adapter response bound remains fail-closed
```

If the product needs longer cognition, the safer alternative is to deliberately certify a larger governed response bound together with replay-size limits and tests.

## Expected Post-Fix Behavior

After adding an explicit output budget below the adapter bound:

- OpenAI should return a bounded provider response;
- `_bounded_response_text(...)` should pass;
- provider proposal envelope creation should complete;
- cognition artifact normalization should become the next validated stage;
- comparison should receive two cognition artifacts if both providers complete.

If only the response-size cap is increased without output budgeting, large responses may enter replay and create new replay-size and operator-visibility risk.

## Final Outputs

```text
RESPONSE_SIZE_ROOT_CAUSE =
Unconstrained conversational OCS cognition-provider generation produces a
23052-character response for a request whose adapter bound is 8192 characters.

MINIMAL_SAFE_FIX =
Add a deterministic OpenAI output budget for conversational OCS provider
requests and keep the existing fail-closed response bound as a safety guard.

EXPECTED_POST_FIX_BEHAVIOR =
Provider responses fit the bound, provider envelopes are created, and
multi-provider cognition can proceed to artifact normalization and comparison.
```

