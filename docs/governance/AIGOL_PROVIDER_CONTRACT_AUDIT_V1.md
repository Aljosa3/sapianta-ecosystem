# AIGOL Provider Contract Audit V1

Status: completed architecture audit.

Purpose: determine whether a canonical provider contract already exists.

This audit is read-only. It does not introduce provider execution, adapters, routing, ranking, dispatch, authorization, lifecycle management, ELL, or governance mutation.

## Verdict

```text
PROVIDER_CONTRACT_GAPS_FOUND
```

Reason:

AiGOL already has strong provider-neutral contract and artifact components, especially for OCS cognition. However, the repository does not yet have one canonical provider contract that governs all provider-facing runtime paths.

The current state is a contract family, not a single canonical contract.

## Provider-Facing Runtime Paths

The audit identified these provider-facing paths:

| Path | File | Provider Role |
| --- | --- | --- |
| OCS multi-provider cognition | `aigol/runtime/multi_provider_cognition_runtime.py` | Invokes approved cognition-provider transports and normalizes responses into cognition artifacts. |
| OCS single-provider cognition | `aigol/runtime/llm_cognition_provider_runtime.py` | Invokes one approved OpenAI cognition provider after explicit human approval. |
| OCS end-to-end cognition | `aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py` | Orchestrates context, optional ERR provider selection, provider cognition, availability gating, mode selection, comparison, continuity, and replay. |
| Cognition artifact normalization | `aigol/runtime/cognition_artifact_runtime.py` | Converts provider response artifacts into canonical `LLM_COGNITION_ARTIFACT_V1`. |
| Provider-assisted intent classification | `aigol/runtime/provider_assisted_intent_classification.py` | Uses provider assistance only after deterministic classification fails. |
| Provider-assisted conversation | `aigol/runtime/provider_assisted_conversation_runtime.py` | Provider-assisted conversation response path. |
| Raw provider response capture | `aigol/runtime/raw_provider_response_capture.py` | Provider-agnostic raw response evidence before bounded normalization. |
| Live cognition rejection analysis | `aigol/runtime/live_cognition_rejection_analysis.py` | Read-only inspection of rejected live provider cognition evidence. |
| Native provider execution | `aigol/runtime/native_provider_execution_runtime.py` | Direct provider invocation after explicit human approval and execution summary confirmation. |
| OpenAI provider adapter | `aigol/runtime/openai_provider_adapter.py` | OpenAI-specific provider attachment path. |
| Bridge provider abstraction | `sapianta_bridge/providers/` | Execution-provider abstraction with normalized execution result semantics. |
| Real provider transport bridge | `sapianta_bridge/real_provider_transport/` | Provider transport request/response/evidence layer. |
| Provider connectors | `sapianta_bridge/provider_connectors/` | Bounded external connector infrastructure, mostly execution-worker oriented. |
| ERR provider registry | `aigol/runtime/external_resource_registry_runtime.py` | Passive provider metadata registration and capability lookup. |

## Cognition Artifact Structures

The main cognition artifact structure is:

```text
LLM_COGNITION_ARTIFACT_V1
```

Defined by `aigol/runtime/cognition_artifact_runtime.py`.

Canonical normalized fields:

- `findings`
- `assumptions`
- `alternatives`
- `risks`
- `uncertainties`
- `clarification_questions`
- `recommended_next_milestone`
- `confidence`

Boundary fields:

- `canonical_provider_assisted_cognition_output`
- `untrusted_provider_output_normalized`
- `non_authoritative`
- `human_review_required`
- `authority_flags`
- `provider_invoked`
- `worker_invoked`
- `approval_created`
- `execution_requested`
- `dispatch_requested`
- `governance_modified`
- `replay_modified`

Lineage fields:

- `context_hash`
- `request_hash`
- `response_hash`
- `provider_identity`
- `provider_metadata`
- `lineage_refs`
- `artifact_hash`

This is the strongest existing canonical cognition output structure.

## Replay-Visible Provider Outputs

The audit found multiple replay-visible provider output forms:

### OCS Cognition Provider Response

```text
LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1
```

Used by both single-provider and multi-provider cognition paths.

Common fields include:

- `provider_id`
- `provider_role`
- `provider_schema_id`
- `provider_identity`
- `provider_metadata`
- `raw_response`
- `raw_response_hash`
- `response_text`
- `response_text_hash`
- `response_status`
- `untrusted_provider_output`
- `non_authoritative`
- `authority_flags`
- `lineage_refs`
- `replay_visible`

### Provider Request

```text
LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1
```

Common fields include:

- `provider_id`
- `provider_role`
- `provider_schema_id`
- `provider_identity`
- `request`
- `ocs_context_reference`
- `provider_contract_hash`
- `lineage_refs`
- `authority_flags`
- `replay_visible`

### Multi-Provider Bundles

```text
MULTI_PROVIDER_COGNITION_REQUEST_BUNDLE_V1
MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1
PROVIDER_COGNITION_FAILURE_ARTIFACT_V1
PROVIDER_USAGE_ARTIFACT_V1
```

These preserve request ordering, provider result/failure isolation, usage evidence, and replay hashes.

### Single-Provider Replay Binding

```text
LLM_COGNITION_PROVIDER_REPLAY_BINDING_ARTIFACT_V1
```

This binds request, response, provider identity, provider metadata, authority flags, and replay lineage.

### Raw Provider Response Evidence

```text
RawProviderResponseEvidence
```

Fields include:

- `raw_response_id`
- `provider_name`
- `model_name`
- `raw_response_present`
- `raw_response_text`
- `raw_response_hash`
- `normalization_status`
- `normalization_reason`
- `created_at`
- `evidence_hash`

This is provider-agnostic raw evidence, but it is separate from the OCS cognition-provider response artifact.

### Native Provider Execution Evidence

`aigol/runtime/native_provider_execution_runtime.py` records:

- credential policy;
- provider request;
- provider response;
- normalized provider response;
- replay binding.

This path is execution-capable and does not share the full OCS cognition contract.

## Confidence And Uncertainty Representations

The audit found several confidence and uncertainty forms:

### Canonical OCS Cognition Artifact

`LLM_COGNITION_ARTIFACT_V1` uses:

```text
confidence = LOW | MEDIUM | HIGH | DETERMINISTIC | UNKNOWN
uncertainties = list[str]
```

This is the clearest normalized representation.

### Provider Prompts / Allowed Outputs

Provider contracts and prompts allow:

- `confidence statements`
- `uncertainties`
- `clarification candidates`

These are semantic categories, not always normalized before artifact creation.

### Provider-Assisted Intent Classification

Provider-assisted intent classification carries:

- `confidence`
- `classification_reasoning`
- `provider_suggestion_authority = false`

This confidence representation is related but not identical to OCS cognition confidence.

### Raw Provider Response Capture

Raw response evidence records normalization status:

```text
NORMALIZED | REJECTED | ABSENT
```

This is not cognition confidence. It is normalization-state confidence/evidence.

### Live Rejection Analysis

Live rejection analysis records rejection stages and normalized proposal presence. It does not use the same confidence taxonomy as `LLM_COGNITION_ARTIFACT_V1`.

## Provider-Neutral Abstractions

The audit identified these provider-neutral abstractions:

1. `AIGOL_LLM_COGNITION_PROVIDER_CONTRACT_V1`

   Referenced by:

   - `MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1`;
   - `LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1`;
   - provider request artifacts.

2. `LLM_COGNITION_ARTIFACT_V1`

   Canonical provider-assisted cognition output.

3. `RawProviderResponseEvidence`

   Provider-agnostic raw response evidence before bounded normalization.

4. Bridge provider abstraction

   `sapianta_bridge/providers/provider_contracts.py` defines `ProviderContract` for bounded execution providers.

5. `NormalizedExecutionResult`

   Bridge-level normalized execution result semantics.

6. ERR provider metadata

   `COGNITION_PROVIDER` resources are discoverable by capability without execution.

These abstractions are valuable, but they are not unified into one canonical provider contract across cognition, execution-provider, transport, raw-response, and native-execution surfaces.

## Existing Contract Evidence

Evidence that a provider contract partially exists:

- `create_default_cognition_provider_contract()` creates `MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1`.
- `create_default_openai_cognition_provider_contract()` creates `LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1`.
- Both reference `AIGOL_LLM_COGNITION_PROVIDER_CONTRACT_V1`.
- Both encode provider role, provider identity, provider schema id, approval status, allowed outputs, replay visibility, and authority flags.
- OCS cognition validates provider contracts before request creation.
- Provider responses are normalized into `LLM_COGNITION_ARTIFACT_V1`.
- Replay bindings preserve request/response/contract lineage.

Evidence that the contract is not fully canonical:

- Multi-provider and single-provider contract artifact types differ.
- Single-provider OpenAI contract includes endpoint and strict OpenAI schema assumptions.
- Multi-provider contract defaults to `mock.cognition.v1`.
- Bridge provider contracts use different fields: `provider_type`, `bounded_execution`, `governance_authority`, `replay_safe`, and normalized execution result semantics.
- Raw provider response capture uses `provider_name` / `model_name`, not `provider_id` / `provider_schema_id`.
- Native provider execution has its own provider request/response/normalization flow.
- ERR provider metadata uses only resource metadata and does not bind to the cognition-provider contract.
- Confidence semantics are normalized inside cognition artifacts but not uniformly required across all provider paths.

## Gap Analysis

### Gap 1: Contract Identity Is Referenced But Not Materialized As One Canonical Artifact

`AIGOL_LLM_COGNITION_PROVIDER_CONTRACT_V1` is referenced, but the repo contains multiple concrete contract artifacts rather than one canonical contract schema consumed everywhere.

Impact:

```text
provider contract semantics are strong but distributed
```

### Gap 2: Cognition Provider And Execution Provider Contracts Are Separate

OCS cognition contracts and `sapianta_bridge.providers.ProviderContract` preserve similar authority boundaries, but they use different schemas and vocabulary.

Impact:

```text
provider-neutral abstraction exists in more than one dialect
```

### Gap 3: Real Provider Metadata Is Not Bound To Provider Contracts

ERR can register `openai`, `claude`, `gemini`, and `mistral` as passive metadata, but ERR resources do not include or reference a provider contract hash.

Impact:

```text
discovery and contract validation remain adjacent but not formally bound
```

This is acceptable for ERR passive scope, but it is a gap for canonical provider contract readiness.

### Gap 4: Provider Response Evidence Has Multiple Shapes

OCS cognition provider responses, raw provider response evidence, native provider execution responses, bridge transport responses, and provider attachment responses are not one replay-visible response schema.

Impact:

```text
replay-visible provider outputs are consistent in spirit but not canonical in shape
```

### Gap 5: Confidence Semantics Are Not Global

`LLM_COGNITION_ARTIFACT_V1` has a clear confidence taxonomy, but provider-assisted classification, raw-response normalization, rejection analysis, and native execution use related but different confidence/status vocabularies.

Impact:

```text
confidence is canonical for OCS cognition artifacts, not for all provider-facing outputs
```

### Gap 6: Single-Provider Runtime Is OpenAI-Specific

The single-provider cognition runtime validates OpenAI schema and endpoint assumptions.

Impact:

```text
single-provider cognition is not yet a provider-neutral canonical contract consumer
```

### Gap 7: Provider Execution-Capable Paths Are Not Contract-Aligned With ERR

Native provider execution and bridge/provider connector paths have their own authorization and execution semantics. They should not be merged casually into ERR, but their separation means no universal provider contract exists yet.

Impact:

```text
ERR discovery, cognition contracts, and execution-capable provider paths remain separate governance surfaces
```

## Recommendation

Do not declare provider-contract readiness yet.

Recommended next milestone:

```text
AIGOL_CANONICAL_PROVIDER_CONTRACT_V1
```

Minimum scope for that milestone:

1. Define one canonical cognition-provider contract schema.
2. Keep it separate from worker and execution-provider contracts.
3. Bind fields already proven in OCS:
   - `provider_id`;
   - `provider_role`;
   - `provider_schema_id`;
   - `provider_identity`;
   - `capabilities`;
   - `allowed_outputs`;
   - `prohibited_outputs`;
   - `authority_flags`;
   - `replay_visible`;
   - `contract_hash`.
4. Define one normalized provider response evidence shape for cognition providers.
5. Preserve `LLM_COGNITION_ARTIFACT_V1` as the canonical normalized cognition output.
6. Define how ERR metadata may reference a contract without making ERR authoritative.
7. Add tests proving multi-provider, single-provider, ERR-selected provider, raw-response, and fail-closed paths either conform or are explicitly outside scope.

Non-goals for the next milestone:

- provider API calls;
- new provider adapters;
- ranking;
- routing engines;
- marketplace logic;
- ELL;
- provider execution;
- worker invocation;
- governance mutation.

## Final Decision

```text
PROVIDER_CONTRACT_READY = NO
PROVIDER_CONTRACT_GAPS_FOUND = YES
```

AiGOL has enough provider-contract substrate to proceed carefully, but not enough to claim a single canonical provider contract across all provider-facing runtime paths.
