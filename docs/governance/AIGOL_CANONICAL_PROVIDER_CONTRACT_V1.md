# AIGOL Canonical Provider Contract V1

Status: canonical schema specification.

Purpose: define one canonical provider contract family for AiGOL cognition-provider integration after `AIGOL_PROVIDER_CONTRACT_AUDIT_V1` found multiple provider-contract dialects.

This artifact is schema unification only.

It does not implement provider execution, provider invocation, transport, authentication, routing, ranking, optimization, lifecycle management, ELL, governance mutation, replay mutation, dispatch, or worker invocation.

## Scope

`AIGOL_CANONICAL_PROVIDER_CONTRACT_V1` applies to cognition providers only.

It does not merge cognition providers with execution workers.

It does not replace ERR. ERR remains passive provider metadata and capability lookup.

It does not authorize provider execution. Provider invocation remains governed by the relevant runtime, approval, credential, and replay controls.

## Dialect Inventory

The following provider-contract dialects are recognized:

| Dialect | Existing Location | Current Role | Canonical Treatment |
| --- | --- | --- | --- |
| `MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1` | `aigol/runtime/multi_provider_cognition_runtime.py` | Multi-provider OCS cognition contract. | Migrate into canonical cognition-provider contract. |
| `LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1` | `aigol/runtime/llm_cognition_provider_runtime.py` | Single-provider OpenAI cognition contract. | Migrate into canonical cognition-provider contract with provider-specific endpoint moved to optional provider metadata. |
| `LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1` | OCS cognition runtimes | Replay-visible provider request artifact. | Becomes canonical provider input schema. |
| `LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1` | OCS cognition runtimes | Replay-visible provider response artifact. | Becomes canonical provider output schema. |
| `LLM_COGNITION_ARTIFACT_V1` | `aigol/runtime/cognition_artifact_runtime.py` | Normalized cognition artifact. | Remains canonical cognition artifact schema. |
| `RawProviderResponseEvidence` | `aigol/runtime/raw_provider_response_capture.py` | Provider-agnostic raw response evidence. | Mapped as raw-response evidence, not canonical cognition output. |
| `ProviderContract` | `sapianta_bridge/providers/provider_contracts.py` | Execution-provider abstraction contract. | Explicitly out of cognition-provider scope; retain as execution-provider contract. |
| `NormalizedExecutionResult` | `sapianta_bridge/providers/normalized_result.py` | Execution result normalization. | Explicitly out of cognition-provider output scope. |
| Native provider execution request/response | `aigol/runtime/native_provider_execution_runtime.py` | Execution-capable provider invocation path. | Not canonical cognition contract; may reference canonical schema only if converted into cognition-provider mode. |
| ERR resource metadata | `aigol/runtime/external_resource_registry_runtime.py` | Passive provider discovery. | May reference canonical contract in a future governed extension, but ERR remains non-authoritative. |

## Common Fields

The following fields are common enough to become canonical:

- `artifact_type`
- `contract_reference`
- `provider_id`
- `provider_role`
- `provider_schema_id`
- `provider_identity`
- `provider_approved`
- `allowed_outputs`
- `authority_flags` or `authority_model`
- `replay_visible`
- `created_at`
- `artifact_hash`
- `provider_contract_hash`
- `lineage_refs`
- `request_hash`
- `response_hash`
- `raw_response_hash`
- `response_text_hash`
- `non_authoritative`
- `untrusted_provider_output`
- `provider_invoked`
- `worker_invoked`
- `approval_created`
- `execution_requested`
- `dispatch_requested`
- `governance_modified`
- `replay_modified`

## Incompatible Fields

The following fields are incompatible or dialect-specific:

| Field | Existing Dialect | Incompatibility |
| --- | --- | --- |
| `single_provider_only` | Single-provider and multi-provider contracts | Mode flag, not provider identity. Must be represented as invocation scope, not core contract identity. |
| `multi_provider_cognition_scope` | Multi-provider contract | Runtime scope flag, not provider contract identity. |
| `endpoint` | OpenAI single-provider contract | Provider-specific transport metadata. Must not be required for all providers. |
| `provider_type` | Bridge execution provider contract | Execution-provider vocabulary, not cognition-provider role. |
| `bounded_execution` | Bridge execution provider contract | Execution-provider field. Cognition providers do not own execution. |
| `execution_status` | Normalized execution result | Worker/execution result field, not cognition-provider output. |
| `provider_name` / `model_name` | Raw response evidence | Raw evidence vocabulary. Must map into `provider_identity` and `provider_metadata`. |
| `normalization_status` | Raw response evidence | Raw-response normalization state, not cognition confidence. |
| `credential_env` / `_credential_secret` | Provider execution runtimes | Invocation/credential policy fields. Must not enter canonical provider contract. |
| `api_key` | Transport metadata | Secret transport field. Forbidden from canonical contract and replay artifacts. |

## Canonical Provider Contract Schema

Canonical artifact type:

```text
CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
```

Canonical contract reference:

```text
AIGOL_CANONICAL_PROVIDER_CONTRACT_V1
```

Required fields:

```text
artifact_type
contract_reference
provider_id
provider_role
provider_schema_id
provider_identity
capabilities
provider_approved
allowed_outputs
prohibited_outputs
authority_flags
replay_visible
created_at
contract_hash
artifact_hash
```

Field semantics:

| Field | Requirement |
| --- | --- |
| `artifact_type` | Must be `CANONICAL_COGNITION_PROVIDER_CONTRACT_V1`. |
| `contract_reference` | Must be `AIGOL_CANONICAL_PROVIDER_CONTRACT_V1`. |
| `provider_id` | Stable lower-case provider identifier. |
| `provider_role` | Must be `COGNITION_PROVIDER`. |
| `provider_schema_id` | Provider response schema id, for example `openai.responses.v1` or `anthropic.messages.v1`. |
| `provider_identity` | Provider identity object. Must include `provider_id` and `provider_kind`; may include `provider_label`, `model_family`, or non-secret provider metadata. |
| `capabilities` | Non-empty list of capability strings, aligned with ERR capability vocabulary where possible. |
| `provider_approved` | Boolean approval for contract admissibility. Does not authorize invocation. |
| `allowed_outputs` | Bounded cognition output categories. |
| `prohibited_outputs` | Authority-bearing or execution-bearing output categories. |
| `authority_flags` | All authority flags must be false. |
| `replay_visible` | Must be true. |
| `created_at` | Replay-visible timestamp string. |
| `contract_hash` | Deterministic hash over contract semantics excluding `artifact_hash`. |
| `artifact_hash` | Deterministic replay hash over the full artifact excluding itself. |

Canonical authority flags:

```text
provider_authority = false
approval_authority = false
execution_authority = false
worker_authority = false
governance_authority = false
replay_authority = false
dispatch_authority = false
authorization_authority = false
```

Canonical allowed outputs:

```text
findings
assumptions
alternatives
risks
uncertainties
confidence
clarification_questions
recommended_next_milestone
```

Canonical prohibited outputs:

```text
approvals
authorizations
governance mutations
replay mutations
worker invocation
execution authorization
dispatch instruction
domain creation authorization
implementation authorization
credential disclosure
secret handling
```

## Canonical Provider Input Schema

Canonical artifact type:

```text
CANONICAL_COGNITION_PROVIDER_INPUT_V1
```

Required fields:

```text
artifact_type
contract_reference
provider_input_id
provider_id
provider_role
provider_schema_id
provider_identity
request
ocs_context_reference
provider_contract_hash
lineage_refs
authority_flags
replay_visible
provider_invoked
worker_invoked
approval_created
execution_requested
dispatch_requested
governance_modified
replay_modified
created_at
input_hash
artifact_hash
```

Request object:

```text
human_request
human_request_hash
input
input_hash
streaming = false
tool_use = false
function_calling = false
automatic_retries = false
```

Input constraints:

- `provider_invoked` must be false at input creation.
- No credentials, API keys, secrets, transport handles, endpoint tokens, session ids, or lifecycle state may be stored.
- `provider_contract_hash` must match the canonical provider contract used to create the input.
- `ocs_context_reference` must include context id, context hash, context artifact hash, and context status.
- All authority flags must be false.

## Canonical Provider Output Schema

Canonical artifact type:

```text
CANONICAL_COGNITION_PROVIDER_OUTPUT_V1
```

Required fields:

```text
artifact_type
contract_reference
provider_output_id
provider_input_id
provider_id
provider_role
provider_schema_id
provider_identity
provider_metadata
provider_contract_hash
provider_input_hash
request_hash
ocs_context_hash
raw_response
raw_response_hash
response_text
response_text_hash
response_status
untrusted_provider_output
non_authoritative
authority_flags
lineage_refs
replay_visible
provider_invoked
worker_invoked
approval_created
execution_requested
dispatch_requested
governance_modified
replay_modified
output_hash
artifact_hash
```

Output constraints:

- `provider_invoked` may be true only in a governed invocation runtime.
- `worker_invoked` must be false.
- `approval_created` must be false.
- `execution_requested` must be false.
- `dispatch_requested` must be false.
- `governance_modified` must be false.
- `replay_modified` must be false.
- `untrusted_provider_output` must be true.
- `non_authoritative` must be true.
- Authority-bearing provider text must fail closed before canonical cognition artifact creation.

## Canonical Cognition Artifact Schema

Canonical artifact type:

```text
LLM_COGNITION_ARTIFACT_V1
```

This schema remains canonical.

Required cognition fields:

```text
findings
assumptions
alternatives
risks
uncertainties
clarification_questions
recommended_next_milestone
confidence
```

Required boundary fields:

```text
provider_assisted_cognition
canonical_provider_assisted_cognition_output
untrusted_provider_output_normalized
non_authoritative
human_review_required
authority_flags
provider_invoked
worker_invoked
approval_created
execution_requested
dispatch_requested
governance_modified
replay_modified
replay_visible
```

Required lineage fields:

```text
context_hash
request_hash
response_hash
provider_identity
provider_metadata
lineage_refs
cognition_hash
artifact_hash
```

The cognition artifact is the only normalized cognition output that downstream governance should interpret.

Provider raw output remains untrusted evidence.

## Canonical Confidence Representation

Canonical field:

```text
confidence
```

Allowed values:

```text
LOW
MEDIUM
HIGH
DETERMINISTIC
UNKNOWN
```

Rules:

- Provider output may contain confidence text, but canonical confidence must normalize into one allowed value.
- Missing confidence normalizes to `UNKNOWN`.
- Invalid confidence fails closed during cognition artifact normalization.
- `DETERMINISTIC` is reserved for deterministic AiGOL-produced cognition, not ordinary external provider claims unless governance explicitly marks the source deterministic.
- Raw-response normalization status is not cognition confidence.

## Canonical Uncertainty Representation

Canonical field:

```text
uncertainties
```

Required type:

```text
list[str]
```

Rules:

- Missing uncertainties normalize to an empty list.
- Each uncertainty must be a bounded string.
- Authority-bearing text inside uncertainties fails closed.
- Clarification needs should be represented separately in `clarification_questions`.
- Unknown confidence does not imply an uncertainty item by itself; it remains represented as `confidence = UNKNOWN`.

## Replay Requirements

Every canonical provider contract, input, output, and cognition artifact must be replay-visible and hash-verifiable.

Minimum replay requirements:

- deterministic JSON serialization;
- stable artifact hash;
- stable semantic hash where defined;
- append-only replay files;
- explicit replay step ordering;
- reconstruction validates ordering;
- reconstruction validates artifact hashes;
- request lineage binds to provider contract hash;
- output lineage binds to input hash and request hash;
- cognition artifact lineage binds to context, input, output, provider identity, and provider contract;
- no replay artifact may contain secrets or API keys;
- no replay artifact may silently mutate governance state;
- replay reconstruction must fail closed on corruption, missing hashes, mismatched lineage, or authority flag escalation.

Canonical replay chain:

```text
CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
-> CANONICAL_COGNITION_PROVIDER_INPUT_V1
-> CANONICAL_COGNITION_PROVIDER_OUTPUT_V1
-> LLM_COGNITION_ARTIFACT_V1
-> downstream OCS evidence
```

ERR selection evidence may precede the contract chain:

```text
ERR_RESOURCE_SELECTION_EVIDENCE_V0
-> CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
```

ERR selection does not authorize provider invocation.

## Migration Mapping

### Multi-Provider Contract

From:

```text
MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1
```

To:

```text
CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
```

Mapping:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_id` | `provider_id` |
| `provider_role` | `provider_role` |
| `provider_schema_id` | `provider_schema_id` |
| `provider_identity` | `provider_identity` |
| `provider_approved` | `provider_approved` |
| `allowed_outputs` | `allowed_outputs` |
| `authority_model` | `authority_flags` |
| `replay_visible` | `replay_visible` |
| `created_at` | `created_at` |
| `artifact_hash` | prior contract hash evidence |

`single_provider_only` and `multi_provider_cognition_scope` become runtime invocation-scope fields, not canonical contract fields.

### Single-Provider OpenAI Contract

From:

```text
LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1
```

To:

```text
CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
```

Mapping:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_id` | `provider_id` |
| `provider_role` | `provider_role` |
| `provider_schema_id` | `provider_schema_id` |
| `provider_identity.provider_id` | `provider_identity.provider_id` |
| `provider_identity.provider_kind` | `provider_identity.provider_kind` |
| `provider_identity.endpoint` | optional `provider_identity.endpoint` only if non-secret and governance-approved |
| `provider_approved` | `provider_approved` |
| `allowed_outputs` | `allowed_outputs` |
| `prohibited_outputs` | `prohibited_outputs` |
| `authority_model` | `authority_flags` |
| `replay_visible` | `replay_visible` |
| `created_at` | `created_at` |

`single_provider_only` becomes an invocation-scope field.

### Provider Request Artifact

From:

```text
LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1
```

To:

```text
CANONICAL_COGNITION_PROVIDER_INPUT_V1
```

Mapping:

| Existing Field | Canonical Field |
| --- | --- |
| `cognition_provider_request_id` | `provider_input_id` |
| `provider_id` | `provider_id` |
| `provider_role` | `provider_role` |
| `provider_schema_id` | `provider_schema_id` |
| `provider_identity` | `provider_identity` |
| `request` | `request` |
| `ocs_context_reference` | `ocs_context_reference` |
| `provider_contract_hash` | `provider_contract_hash` |
| `lineage_refs` | `lineage_refs` |
| `authority_flags` | `authority_flags` |
| `request_hash` | `input_hash` and lineage evidence |
| `artifact_hash` | `artifact_hash` |

### Provider Response Artifact

From:

```text
LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1
```

To:

```text
CANONICAL_COGNITION_PROVIDER_OUTPUT_V1
```

Mapping:

| Existing Field | Canonical Field |
| --- | --- |
| `cognition_provider_request_id` | `provider_input_id` |
| `provider_id` | `provider_id` |
| `provider_role` | `provider_role` |
| `provider_schema_id` | `provider_schema_id` |
| `provider_identity` | `provider_identity` |
| `provider_metadata` | `provider_metadata` |
| `provider_request_hash` | `provider_input_hash` |
| `request_hash` | `request_hash` |
| `ocs_context_hash` | `ocs_context_hash` |
| `raw_response` | `raw_response` |
| `raw_response_hash` | `raw_response_hash` |
| `response_text` | `response_text` |
| `response_text_hash` | `response_text_hash` |
| `response_status` | `response_status` |
| `untrusted_provider_output` | `untrusted_provider_output` |
| `non_authoritative` | `non_authoritative` |
| `authority_flags` | `authority_flags` |
| `lineage_refs` | `lineage_refs` |
| `response_hash` | `output_hash` and lineage evidence |
| `artifact_hash` | `artifact_hash` |

### Raw Provider Response Evidence

From:

```text
RawProviderResponseEvidence
```

To:

```text
CANONICAL_COGNITION_PROVIDER_OUTPUT_V1 raw_response evidence fields
```

Mapping:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_name` | `provider_identity.provider_id` or `provider_metadata.provider_name` |
| `model_name` | `provider_metadata.model` |
| `raw_response_text` | `raw_response` or provider-specific raw text field |
| `raw_response_hash` | `raw_response_hash` |
| `normalization_status` | `provider_metadata.raw_response_normalization_status` |
| `normalization_reason` | `provider_metadata.raw_response_normalization_reason` |
| `evidence_hash` | raw response evidence hash in lineage refs |

Raw response evidence is not itself a cognition artifact.

### ERR Provider Metadata

From:

```text
ERR resource metadata
```

To:

```text
optional contract reference in future governed ERR extension
```

Current ERR fields remain:

```text
resource_id
resource_type
capabilities
status
```

Future governed extension may add:

```text
canonical_provider_contract_hash
```

Only if tests prove ERR remains passive and non-authoritative.

## Governance Constraints

The canonical provider contract must preserve:

- `LLM proposes`;
- `AiGOL governs`;
- `Worker executes`;
- `Replay records`;
- Human authority over approval and authorization;
- OCS orchestration authority;
- ERR passive lookup boundary;
- provider output non-authority;
- worker/provider separation;
- fail-closed validation;
- replay-visible lineage.

The canonical provider contract must not:

- invoke providers;
- invoke workers;
- dispatch;
- authorize;
- govern;
- rank providers;
- optimize provider selection;
- create marketplace behavior;
- create lifecycle engines;
- create ELL;
- manage credentials;
- store secrets;
- mutate governance;
- mutate replay history.

## Acceptance Criteria

`AIGOL_CANONICAL_PROVIDER_CONTRACT_V1` is accepted when:

1. The canonical contract schema is documented.
2. The canonical input schema is documented.
3. The canonical output schema is documented.
4. `LLM_COGNITION_ARTIFACT_V1` remains the canonical cognition artifact schema.
5. Confidence values are explicitly bounded.
6. Uncertainty values are explicitly structured.
7. Replay requirements are explicit and fail-closed.
8. Migration mappings exist for all identified provider contract dialects.
9. ERR remains passive and non-authoritative.
10. No provider execution, invocation, transport, authentication, lifecycle, ELL, routing, ranking, dispatch, worker invocation, or governance mutation is introduced.

## Implementation Plan

Phase 1: Governance Specification

- Adopt this artifact as the canonical provider contract specification.
- Do not change runtime behavior in this phase.
- Keep all current tests unchanged unless they protect schema conformance documentation.

Phase 2: Schema Fixtures

- Add JSON schema fixtures for:
  - `CANONICAL_COGNITION_PROVIDER_CONTRACT_V1`;
  - `CANONICAL_COGNITION_PROVIDER_INPUT_V1`;
  - `CANONICAL_COGNITION_PROVIDER_OUTPUT_V1`.
- Add tests validating fixtures against documented required fields.

Phase 3: Runtime Adapters To Canonical Schema

- Add pure conversion helpers from existing dialects to canonical schema.
- Conversion helpers must not invoke providers.
- Conversion helpers must fail closed on missing authority flags, missing hashes, or schema mismatch.

Phase 4: OCS Contract Adoption

- Update multi-provider cognition and single-provider cognition to accept canonical contracts.
- Preserve existing replay compatibility during migration.
- Keep `LLM_COGNITION_ARTIFACT_V1` unchanged unless a separate governed migration is approved.

Phase 5: ERR Contract Reference Review

- Evaluate whether ERR should reference `canonical_provider_contract_hash`.
- Do not add the field unless governance confirms passive metadata remains preserved.

Phase 6: Recertification

- Rerun HIRR post-certification regression suite.
- Rerun ERR provider registration tests.
- Add provider-contract conformance tests.
- Produce a follow-up certification only after tests pass.

## Final Recommendation

Adopt `AIGOL_CANONICAL_PROVIDER_CONTRACT_V1` as the governance schema target for cognition-provider contracts.

Do not implement provider execution as part of this milestone.

The next concrete implementation should be schema fixtures and pure conformance tests, not transport or provider invocation.
