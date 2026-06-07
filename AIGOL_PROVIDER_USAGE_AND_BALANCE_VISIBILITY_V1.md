# AIGOL_PROVIDER_USAGE_AND_BALANCE_VISIBILITY_V1

## Status

Provider usage visibility runtime and governance certification.

Conversational OCS cognition now exposes replay-safe provider usage metrics to the operator. No provider authority, approval authority, execution authority, worker authority, governance authority, or replay authority was added.

## Executive Finding

OpenAI Responses API output may include a `usage` object. AiGOL now captures that usage into:

```text
PROVIDER_USAGE_ARTIFACT_V1
```

and renders it in conversational OCS operator output as:

```text
PROVIDER USAGE
Provider: openai
Model: gpt-5.1
Prompt Tokens: 1450
Completion Tokens: 980
Total Tokens: 2430
Elapsed: 0.01s
Estimated Cost: $0.011612
Balance: PARTIAL
```

Balance visibility is classified as:

```text
BALANCE_VISIBILITY_SUPPORTED = PARTIAL
```

Reason: OpenAI documents Usage and Costs APIs for organization usage and spend visibility, but the individual provider response does not include remaining account balance. AiGOL therefore defines balance source semantics but does not claim direct remaining-balance display.

## Current Provider Response Availability

### Available From Provider Response

Status: `SUPPORTED_WHEN_RETURNED_BY_PROVIDER`

Fields:

- `usage.prompt_tokens` or `usage.input_tokens`;
- `usage.completion_tokens` or `usage.output_tokens`;
- `usage.total_tokens`;
- `model`;
- response text.

### Added By AiGOL Runtime

Status: `SUPPORTED`

Fields:

- `elapsed_seconds`;
- `estimated_cost`;
- `currency`;
- usage hash;
- provider non-authority flags.

`elapsed_seconds` is measured around the bounded provider transport call. `estimated_cost` is calculated from replay-visible token counts and an explicit local pricing table for known OpenAI models.

## Canonical Artifact

```text
PROVIDER_USAGE_ARTIFACT_V1
```

Required fields:

- `artifact_type`
- `provider_id`
- `model`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `elapsed_seconds`
- `estimated_cost`
- `currency`
- `timestamp`
- `usage_hash`
- `artifact_hash`
- `balance_visibility_supported`
- `balance_source`
- `remaining_balance`

Authority fields:

- `provider_authority`
- `approval_authority`
- `execution_authority`
- `worker_authority`
- `governance_authority`
- `replay_authority`

Required authority values:

```text
provider_authority = false
approval_authority = false
execution_authority = false
worker_authority = false
governance_authority = false
replay_authority = false
```

## Conversational CLI Visibility

The OCS operator-visible renderer now appends usage after normalized cognition content and before the existing technical summary.

Ordering:

```text
AIGOL OCS COGNITION
Findings
Assumptions
Risks
Uncertainties
Clarification Questions
Recommended Next Milestone
PROVIDER USAGE
AIGOL OCS LLM COGNITION END-TO-END
```

The usage section does not render raw provider payloads, replay implementation details, artifact schemas, or authority metadata.

## Balance Visibility

### Direct Remaining Balance

Status: `NOT_SUPPORTED_FROM_PROVIDER_RESPONSE`

The OpenAI provider response does not include a remaining balance field.

### Organization Usage And Cost Visibility

Status: `PARTIAL`

OpenAI documents organization Usage and Costs endpoints for usage and spend reporting. These can support a future spend-visibility artifact, but they are not the same as a direct remaining balance and may require organization-level permissions and separate refresh policy.

## Balance Artifact Definition

Direct balance is not implemented in this milestone. The canonical future artifact is reserved as:

```text
PROVIDER_BALANCE_ARTIFACT_V1
```

Required future fields:

- `artifact_type`
- `provider_id`
- `balance_visibility_status`
- `balance_source`
- `remaining_balance`
- `currency`
- `last_refresh_timestamp`
- `permission_scope`
- `artifact_hash`

Current classification:

```text
PROVIDER_BALANCE_ARTIFACT_V1 = DEFINED_NOT_IMPLEMENTED
BALANCE_SOURCE_DEFINED = OPENAI_ORGANIZATION_USAGE_AND_COSTS_APIS
```

## Replay Compatibility

Usage is captured inside the provider response artifact and result bundle lineage:

```text
LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1
-> PROVIDER_USAGE_ARTIFACT_V1
-> MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1
-> OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1
-> operator-visible rendering
```

Replay remains append-only. Usage visibility is reconstructable from replay artifacts.

## Governance Compatibility

Provider usage visibility is operational evidence only.

It does not:

- authorize provider output;
- approve execution;
- select workers;
- dispatch workers;
- invoke workers;
- mutate governance;
- mutate replay;
- expose credentials;
- expose raw provider payloads in the operator usage section.

## Implementation Notes

Changed runtime surfaces:

- `aigol/runtime/multi_provider_cognition_runtime.py`
- `aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py`
- `aigol/cli/aigol_cli.py`

Added regression coverage:

- provider usage artifact creation;
- token extraction from OpenAI Responses-style `usage`;
- model capture;
- latency capture;
- estimated cost rendering;
- balance visibility classification;
- operator-visible usage section without raw provider payload or authority metadata.

## Final Outputs

```text
TOKEN_USAGE_VISIBLE = TRUE
ESTIMATED_COST_VISIBLE = TRUE
LATENCY_VISIBLE = TRUE
BALANCE_VISIBILITY_SUPPORTED = PARTIAL
BALANCE_SOURCE_DEFINED = TRUE
REPLAY_COMPATIBLE = TRUE
GOVERNANCE_COMPATIBLE = TRUE
```
