# AIGOL_CONVERSATIONAL_OPENAI_OUTPUT_BUDGET_RUNTIME_V1

## Status

Implementation milestone.

Conversational OCS OpenAI provider calls now carry a deterministic output budget and record replay-visible budget evidence before provider invocation.

## Objective

Prevent real OpenAI conversational OCS cognition responses from exceeding the bounded provider response size by adding an explicit provider output budget.

## Implemented Runtime Boundary

The budget is applied only to conversational OCS OpenAI provider bindings:

```text
aigol/cli/aigol_cli.py::_conversation_openai_provider_adapter
```

The underlying provider adapter remains backward-compatible. Existing callers that do not pass `max_output_tokens` keep the previous payload shape.

## Output Budget

```text
max_output_tokens: 1200
estimated_char_budget: 6000
max_provider_response_chars: 8192
```

The estimate uses a deterministic 5-character-per-token guard:

```text
1200 * 5 = 6000
```

Since `6000 <= 8192`, provider invocation is allowed. If the estimated budget exceeds the provider response bound, the runtime fails closed before invocation.

## Replay Artifact

Each conversational OCS provider attachment directory records:

```text
000_openai_output_budget_recorded.json
```

Artifact type:

```text
OPENAI_OUTPUT_BUDGET_ARTIFACT_V1
```

Recorded fields include:

- `provider_id`
- `model`
- `max_output_tokens`
- `estimated_char_budget`
- `max_provider_response_chars`
- `budget_status`
- `budget_deterministic`
- `provider_invocation_allowed`
- `fail_closed`
- `replay_visible`
- `artifact_hash`

## Runtime Path

```text
Human prompt
-> conversational OCS routing
-> multi-provider cognition request
-> conversational OpenAI transport
-> OPENAI_OUTPUT_BUDGET_ARTIFACT_V1
-> run_provider_attachment(...)
-> OpenAIProviderAdapter(max_output_tokens=1200)
-> Responses API payload includes max_output_tokens
-> provider response bound remains enforced
```

## Boundary Preservation

Preserved:

- comparison runtime;
- continuity runtime;
- clarification runtime;
- provider non-authority;
- replay compatibility;
- fail-closed provider response bound.

No comparison, continuity, clarification, or cognition artifact schema changes were required.

## Tests

Validated with:

```text
python -m pytest tests/test_conversational_openai_output_budget_runtime_v1.py tests/test_real_openai_conversational_attachment_v1.py tests/test_conversational_ocs_cognition_binding_v1.py tests/test_first_real_provider_attachment_v1.py tests/test_provider_health_and_readiness_runtime_v1.py tests/test_openai_provider_failure_diagnostics_v1.py
```

Result:

```text
29 passed
```

## Final Outputs

```text
OUTPUT_BUDGET_ACTIVE = true
EXPECTED_RESPONSE_WITHIN_LIMIT = true
COMPARISON_COMPATIBLE = true
```

