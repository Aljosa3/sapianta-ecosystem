# AIGOL_PROVIDER_REQUEST_PROMPT_PROJECTION_REPAIR_V1

## Objective

Repair the execution path blocker identified in:

```text
AIGOL_ACLI_PROVIDER_PROPOSAL_PRODUCTION_AUDIT_V1
```

The blocker was:

```text
OPENAI_PROVIDER_ADAPTER_PROMPT_EXTRACTION
```

because `PROVIDER_REQUEST_PACKET_V1` lacked an adapter-compatible:

```text
prompt
human_prompt
request
```

string field.

## Repair

Implemented deterministic replay-visible provider prompt projection inside:

```text
aigol/runtime/provider_proposal_production_runtime.py
```

The runtime still creates and persists:

```text
PROVIDER_REQUEST_PACKET_V1
```

Then it creates:

```text
PROVIDER_REQUEST_PROMPT_PROJECTION_V1
```

The projection is:

- deterministic;
- replay-visible;
- hash-bound to `PROVIDER_REQUEST_PACKET_V1`;
- shaped for `OpenAIProviderAdapter`;
- proposal-only;
- authority-neutral;
- non-executing.

The OpenAI adapter now receives a request containing:

```text
prompt
human_prompt
request
```

while preserving the original provider request packet hash and replay lineage.

## Preserved Boundaries

The projection preserves:

```text
proposal_only = true
provider_authority = false
execution_requested = false
dispatch_requested = false
worker_created = false
domain_created = false
governance_modified = false
replay_modified = false
```

No ACLI redesign, PPP redesign, governance redesign, replay redesign, worker lifecycle redesign, provider selection change, or automatic execution path was introduced.

## Response Normalization

Provider proposal production now accepts structured OpenAI proposal output when returned as JSON text in:

```text
response_text
```

Malformed provider text still fails closed as provider response invalid.

## Validation

Focused provider production validation:

```bash
python -m pytest tests/test_provider_proposal_production_runtime_v1.py
```

Result:

```text
9 passed
```

Relevant path validation:

```bash
python -m pytest \
  tests/test_provider_proposal_production_runtime_v1.py \
  tests/test_conversation_ppp_routing_integration_v1.py \
  tests/test_context_assembled_to_ppp_routing_continuation_v1.py \
  tests/test_conversation_native_development_context_integration_v1.py
```

Result:

```text
27 passed
```

The ACLI native-context continuation regression now uses `OpenAIProviderAdapter` with a deterministic fake OpenAI client and verifies:

```text
continue ppp
-> provider prompt projection
-> provider proposal production
-> execution summary reference
-> human confirmation reference
-> execution authorization
-> worker invocation request
```

## Final Fields

```text
PROMPT_PROJECTION_IMPLEMENTED = YES
PROVIDER_REQUEST_PROMPT_AVAILABLE = YES
PPP_REACHED = YES
PROVIDER_PROPOSAL_GENERATED = YES
EXECUTION_SUMMARY_REACHED = YES
AUTHORIZATION_BOUNDARY_PRESERVED = YES
FAIL_CLOSED_PRESERVED = YES
EXECUTION_PATH_BLOCKER_RESOLVED = YES
```
