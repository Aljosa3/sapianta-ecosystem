# AIGOL Provider Contract Migration Audit V1

Status: completed migration readiness audit.

Purpose: validate whether existing provider-facing implementations can migrate to `AIGOL_CANONICAL_PROVIDER_CONTRACT_V1`.

This audit is read-only. It does not change runtime behavior, invoke providers, implement transport, add authentication, expand ERR, or create provider execution.

## Migration Readiness Verdict

```text
CANONICAL_PROVIDER_CONTRACT_ADOPTION_FEASIBLE = YES
ARCHITECTURAL_REDESIGN_REQUIRED = NO
MIGRATION_READINESS = READY_WITH_ADAPTATION
```

Reason:

The main OCS cognition provider dialects already contain the core canonical fields: provider identity, provider role, provider schema id, authority flags, replay visibility, request lineage, response lineage, non-authoritative provider output, and normalized cognition artifacts.

Canonical adoption is feasible through schema adapters and field normalization. It does not require redesigning OCS, ERR, replay, HIRR, or worker assignment.

However, adoption is not a direct drop-in for every provider-facing path. Execution-provider, native execution, raw-response, and ERR metadata surfaces require explicit boundaries or adapters.

## Migration Classification Legend

```text
DIRECT_MIGRATION
```

Existing structure already matches the canonical schema or is intentionally retained as canonical.

```text
MINOR_ADAPTATION
```

Existing structure has most required fields and needs naming, hash, field relocation, or supplemental metadata adaptation.

```text
MAJOR_ADAPTATION
```

Existing structure is adjacent but semantically different, execution-capable, or outside cognition-provider scope. Migration requires boundary decisions and explicit adapters.

## Migration Matrix

| Dialect | Classification | Readiness Summary |
| --- | --- | --- |
| `MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1` | `MINOR_ADAPTATION` | Strong field alignment; needs canonical artifact type, `capabilities`, `prohibited_outputs`, `contract_hash`, and mode fields moved out of contract identity. |
| `LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1` | `MINOR_ADAPTATION` | Strong field alignment; OpenAI endpoint and `single_provider_only` must become optional provider metadata or invocation scope. |
| `LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1` | `MINOR_ADAPTATION` | Almost canonical input; needs naming migration from request id/request hash to provider input id/input hash. |
| `LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1` | `MINOR_ADAPTATION` | Almost canonical output; needs naming migration from request id/response hash to input id/output hash and consistent contract hash presence. |
| `LLM_COGNITION_ARTIFACT_V1` | `DIRECT_MIGRATION` | Retained as canonical cognition artifact schema. |
| `RawProviderResponseEvidence` | `MINOR_ADAPTATION` | Maps into raw-response evidence inside canonical output metadata; not itself canonical cognition output. |
| `ProviderContract` in `sapianta_bridge/providers` | `MAJOR_ADAPTATION` | Execution-provider contract with different semantics; should remain separate or be bridged only through explicit scope mapping. |
| `NormalizedExecutionResult` | `MAJOR_ADAPTATION` | Execution result schema, not cognition-provider output. Should remain out of canonical cognition-provider scope. |
| Native provider execution request/response | `MAJOR_ADAPTATION` | Execution-capable path with credentials and invocation semantics; cannot migrate without preserving execution boundary. |
| ERR resource metadata | `MINOR_ADAPTATION` | Passive metadata can reference canonical contract in future, but must not become authoritative. |
| Real provider transport bridge | `MAJOR_ADAPTATION` | Transport-level request/response evidence is adjacent but not the cognition-provider contract. |
| Provider connectors | `MAJOR_ADAPTATION` | Bounded execution connector infrastructure; not cognition-provider contract. |

## Dialect Details

### MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1

Classification:

```text
MINOR_ADAPTATION
```

Direct field mappings:

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

Missing fields:

- `capabilities`;
- `prohibited_outputs`;
- `contract_hash`;
- canonical `artifact_type`;
- canonical `contract_reference`;
- expanded authority flags: `dispatch_authority`, `authorization_authority`.

Incompatible fields:

- `single_provider_only`;
- `multi_provider_cognition_scope`.

Migration risks:

- mode flags could be mistaken for provider identity if not moved into invocation scope;
- existing tests may depend on current artifact type;
- historical replay artifacts must remain reconstructable.

Readiness:

```text
ready for pure conversion helper
```

### LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1

Classification:

```text
MINOR_ADAPTATION
```

Direct field mappings:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_id` | `provider_id` |
| `provider_role` | `provider_role` |
| `provider_schema_id` | `provider_schema_id` |
| `provider_identity.provider_id` | `provider_identity.provider_id` |
| `provider_identity.provider_kind` | `provider_identity.provider_kind` |
| `provider_approved` | `provider_approved` |
| `allowed_outputs` | `allowed_outputs` |
| `prohibited_outputs` | `prohibited_outputs` |
| `authority_model` | `authority_flags` |
| `replay_visible` | `replay_visible` |
| `created_at` | `created_at` |

Missing fields:

- `capabilities`;
- `contract_hash`;
- canonical `artifact_type`;
- canonical `contract_reference`;
- expanded authority flags: `dispatch_authority`, `authorization_authority`.

Incompatible fields:

- `single_provider_only`;
- `provider_identity.endpoint` if treated as required contract identity.

Migration risks:

- OpenAI-specific endpoint assumptions may leak into canonical provider identity;
- provider-specific schema validation must not become universal;
- migration must preserve explicit human approval requirements for actual invocation.

Readiness:

```text
ready for pure conversion helper with OpenAI-specific metadata isolation
```

### LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1

Classification:

```text
MINOR_ADAPTATION
```

Direct field mappings:

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
| `replay_visible` | `replay_visible` |
| `request_hash` | `input_hash` |
| `artifact_hash` | `artifact_hash` |

Missing fields:

- canonical `artifact_type`;
- canonical `contract_reference`;
- expanded authority flags if missing;
- exact `input_hash` name.

Incompatible fields:

- single-provider requests may contain timeout metadata;
- some request artifacts include approval or credential policy references that are invocation-scope evidence, not canonical input identity.

Migration risks:

- renaming `request_hash` to `input_hash` may break existing lineage checks if compatibility aliases are not preserved;
- credential-policy lineage must not put secrets into canonical artifacts.

Readiness:

```text
ready for compatibility-preserving field aliasing
```

### LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1

Classification:

```text
MINOR_ADAPTATION
```

Direct field mappings:

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
| `replay_visible` | `replay_visible` |
| `response_hash` | `output_hash` |
| `artifact_hash` | `artifact_hash` |

Missing fields:

- canonical `artifact_type`;
- canonical `contract_reference`;
- explicit `provider_output_id`;
- explicit `provider_contract_hash` outside lineage in some response forms;
- expanded authority flags if missing.

Incompatible fields:

- provider usage artifacts are output-adjacent evidence, not core canonical output fields;
- single-provider provider metadata may include endpoint/model assumptions that should remain provider metadata.

Migration risks:

- downstream cognition artifact lineage expects existing response hash names;
- raw provider output must remain untrusted and non-authoritative;
- provider invocation flag must remain truthful and not be inferred from metadata-only selection.

Readiness:

```text
ready for compatibility-preserving response wrapper or adapter
```

### LLM_COGNITION_ARTIFACT_V1

Classification:

```text
DIRECT_MIGRATION
```

Direct field mappings:

The canonical provider contract explicitly retains `LLM_COGNITION_ARTIFACT_V1` as the canonical cognition artifact.

Missing fields:

- none for current canonical scope.

Incompatible fields:

- none for current canonical scope.

Migration risks:

- avoid changing a stable normalized cognition artifact unnecessarily;
- any future change requires replay and OCS recertification.

Readiness:

```text
already canonical
```

### RawProviderResponseEvidence

Classification:

```text
MINOR_ADAPTATION
```

Direct field mappings:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_name` | `provider_identity.provider_id` or `provider_metadata.provider_name` |
| `model_name` | `provider_metadata.model` |
| `raw_response_text` | `raw_response` |
| `raw_response_hash` | `raw_response_hash` |
| `normalization_status` | `provider_metadata.raw_response_normalization_status` |
| `normalization_reason` | `provider_metadata.raw_response_normalization_reason` |
| `evidence_hash` | `lineage_refs.raw_provider_response_evidence_hash` |

Missing fields:

- `provider_role`;
- `provider_schema_id`;
- `provider_contract_hash`;
- `provider_input_hash`;
- `response_text_hash`;
- canonical authority flags.

Incompatible fields:

- `normalization_status` is not cognition confidence;
- raw evidence does not equal canonical provider output.

Migration risks:

- raw-response evidence must not be promoted into downstream cognition directly;
- mapping requires a surrounding provider output or adapter context.

Readiness:

```text
ready as nested evidence, not standalone canonical output
```

### ProviderContract In sapianta_bridge/providers

Classification:

```text
MAJOR_ADAPTATION
```

Direct field mappings:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_id` | `provider_id` |
| `governance_authority = false` | `authority_flags.governance_authority = false` |
| `replay_safe = true` | `replay_visible = true` equivalent intent |
| `authority_escalation_allowed = false` | authority boundary evidence |
| `validation_bypass_allowed = false` | validation boundary evidence |

Missing fields:

- `provider_role = COGNITION_PROVIDER`;
- `provider_schema_id`;
- `provider_identity`;
- `capabilities`;
- `allowed_outputs`;
- `prohibited_outputs`;
- canonical input/output lineage fields.

Incompatible fields:

- `provider_type`;
- `bounded_execution`;
- execution-provider semantics.

Migration risks:

- merging execution-provider and cognition-provider contracts would blur provider/worker/execution boundaries;
- bridge provider abstraction may include bounded execution semantics that do not belong in cognition contract.

Readiness:

```text
not a migration target unless explicitly scoped as cognition provider
```

### NormalizedExecutionResult

Classification:

```text
MAJOR_ADAPTATION
```

Direct field mappings:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_id` | `provider_id` |
| `governance_modified = false` | `governance_modified = false` |
| `replay_safe = true` | replay-safe boundary evidence |

Missing fields:

- cognition provider identity;
- cognition provider schema;
- cognition input/output hashes;
- raw response evidence;
- normalized cognition fields.

Incompatible fields:

- `execution_status`;
- `artifacts_created`;
- `tests_executed`;
- `execution_time_ms`;
- stdout/stderr fields.

Migration risks:

- treating execution results as cognition outputs would violate worker/provider separation.

Readiness:

```text
out of scope for canonical cognition provider contract
```

### Native Provider Execution Request/Response

Classification:

```text
MAJOR_ADAPTATION
```

Direct field mappings:

| Existing Field | Canonical Field |
| --- | --- |
| `provider_id` | `provider_id` |
| `provider_request` | canonical input only if running in cognition-provider mode |
| `provider_response` | canonical output only if running in cognition-provider mode |
| `raw_response_hash` | `raw_response_hash` |
| `response_text_hash` | `response_text_hash` |

Missing fields:

- canonical cognition-provider contract hash;
- OCS context reference in all cases;
- canonical cognition artifact lineage in all cases;
- consistent authority flags matching OCS cognition.

Incompatible fields:

- credential policy;
- credential environment;
- explicit execution summary;
- human execution confirmation;
- execution-capable provider invocation.

Migration risks:

- native provider execution can cross into execution-capable territory;
- credentials and transport metadata must remain outside canonical replay artifacts;
- migration must not authorize provider execution through schema conformance.

Readiness:

```text
requires separate governed boundary review before any adoption
```

### ERR Resource Metadata

Classification:

```text
MINOR_ADAPTATION
```

Direct field mappings:

| Existing Field | Canonical Field |
| --- | --- |
| `resource_id` | `provider_id` |
| `resource_type = COGNITION_PROVIDER` | `provider_role = COGNITION_PROVIDER` |
| `capabilities` | `capabilities` |
| `status = ACTIVE` | provider availability metadata only |

Missing fields:

- `provider_schema_id`;
- `provider_identity`;
- `provider_approved`;
- `allowed_outputs`;
- `prohibited_outputs`;
- `authority_flags`;
- `contract_hash`;

Incompatible fields:

- ERR status is registry metadata, not contract approval;
- ERR selection evidence is not provider authorization.

Migration risks:

- adding contract references to ERR could accidentally make ERR appear authoritative;
- passive ERR boundary must remain locked.

Readiness:

```text
ready for optional contract-hash reference only after governance approval
```

### Real Provider Transport Bridge

Classification:

```text
MAJOR_ADAPTATION
```

Direct field mappings:

Transport request/response fields may map to provider input/output evidence only after a cognition-provider context is established.

Missing fields:

- canonical cognition-provider contract;
- OCS context reference;
- normalized cognition artifact lineage;
- canonical confidence and uncertainty semantics.

Incompatible fields:

- transport-level request/response semantics;
- connector or bridge state;
- possible provider-specific transport metadata.

Migration risks:

- confusing transport evidence with provider contract evidence;
- leaking transport or credential details into canonical replay artifacts.

Readiness:

```text
requires adapter layer; not direct migration
```

### Provider Connectors

Classification:

```text
MAJOR_ADAPTATION
```

Direct field mappings:

Limited provider identity and boundary fields may map to governance evidence, but not to canonical cognition-provider contract without re-scoping.

Missing fields:

- cognition provider role;
- cognition provider schema id;
- OCS context reference;
- canonical cognition output fields.

Incompatible fields:

- bounded execution connector semantics;
- process state;
- execution gate semantics;
- timeout and completion state.

Migration risks:

- connector execution semantics could blur cognition-provider and execution-worker boundaries;
- migration would require separate execution/governance review.

Readiness:

```text
not a direct target for cognition-provider contract migration
```

## Gap Analysis

### Gap 1: Contract Hash Is Not Uniform

Existing dialects use `artifact_hash`; the canonical contract requires both `contract_hash` and `artifact_hash`.

Migration action:

```text
add deterministic contract_hash in pure conversion helpers
```

### Gap 2: Capabilities Are Missing From Existing Cognition Contracts

ERR resources contain capabilities, while existing cognition provider contracts do not consistently include them.

Migration action:

```text
derive capabilities from ERR metadata or explicit governed contract fixtures
```

### Gap 3: Prohibited Outputs Are Not Uniform

Single-provider OpenAI contract includes `prohibited_outputs`; multi-provider contract relies more on authority flags and runtime text rejection.

Migration action:

```text
standardize prohibited_outputs in canonical contract fixtures
```

### Gap 4: Authority Flag Vocabulary Needs Expansion

Existing authority models cover most flags but not always `dispatch_authority` and `authorization_authority`.

Migration action:

```text
canonical conversion must add missing authority flags as false
```

### Gap 5: Mode Flags Are Mixed Into Contracts

`single_provider_only` and `multi_provider_cognition_scope` describe invocation mode, not provider identity.

Migration action:

```text
move mode flags to runtime invocation scope or compatibility metadata
```

### Gap 6: Raw Response Evidence Is Adjacent But Not Complete

Raw provider response capture lacks contract, context, and request lineage.

Migration action:

```text
embed raw evidence inside canonical output lineage rather than treating it as a standalone output
```

### Gap 7: Execution-Capable Paths Are Semantically Different

Native provider execution, bridge execution providers, and connectors carry execution semantics.

Migration action:

```text
keep these outside cognition-provider migration unless a separate governed boundary review approves a bridge
```

## Risk Analysis

### Low Risks

- OCS multi-provider contract conversion.
- OCS provider request artifact conversion.
- OCS provider response artifact conversion.
- Retaining `LLM_COGNITION_ARTIFACT_V1` as canonical cognition output.

Reason:

```text
existing OCS cognition surfaces already enforce replay visibility, non-authority, lineage, and fail-closed validation
```

### Medium Risks

- Single-provider OpenAI contract conversion.
- Raw provider response evidence mapping.
- ERR optional contract hash reference.

Reason:

```text
these surfaces have provider-specific or adjacent metadata that must not become authority, transport, credential, or lifecycle state
```

### High Risks

- Native provider execution migration.
- Bridge provider abstraction migration.
- Provider connector migration.
- Normalized execution result migration.

Reason:

```text
these surfaces are execution-capable or execution-oriented and must not be collapsed into cognition-provider contract semantics
```

## Architectural Redesign Assessment

Canonical provider contract adoption does not require architectural redesign for OCS cognition.

Supporting evidence:

- OCS already validates provider contracts before provider request creation.
- OCS already creates replay-visible provider request and response artifacts.
- OCS already normalizes provider responses into `LLM_COGNITION_ARTIFACT_V1`.
- OCS already preserves authority flags and fail-closed behavior.
- ERR already supports passive provider metadata lookup.
- HIRR, OCS, ERR, replay, and worker boundaries do not need to move.

Required work is adapter-level and schema-level:

```text
existing dialect -> canonical contract/input/output wrappers
```

Not required:

```text
new OCS architecture
new ERR role
new provider runtime
new transport layer
new ELL
new worker/provider coupling
```

## Migration Readiness Verdict

```text
MIGRATION_READINESS_VERDICT = READY_WITH_ADAPTATION
CANONICAL_PROVIDER_CONTRACT_ADOPTION_FEASIBLE = YES
ARCHITECTURAL_REDESIGN_REQUIRED = NO
PROVIDER_EXECUTION_REQUIRED = NO
TRANSPORT_IMPLEMENTATION_REQUIRED = NO
```

Blocking risks:

```text
NONE for schema-level adoption
```

Non-blocking risks:

- execution-provider and connector paths require explicit out-of-scope treatment;
- ERR contract references require governance approval before implementation;
- historical replay compatibility must be preserved;
- conversion helpers must fail closed on authority flag drift or lineage mismatch.

## Recommendation

Proceed with canonical provider contract migration in a staged, non-executing manner:

1. Add schema fixtures for canonical contract, input, and output.
2. Add pure conversion helpers for OCS multi-provider and single-provider cognition contracts.
3. Add pure conversion helpers for provider request and response artifacts.
4. Preserve `LLM_COGNITION_ARTIFACT_V1` unchanged.
5. Treat raw provider response evidence as nested evidence only.
6. Keep execution-provider, native execution, and connector surfaces outside the first migration.
7. Defer ERR contract hash reference until a separate passive-boundary review.
8. Run HIRR, ERR, OCS cognition, and provider contract conformance tests before any readiness claim.

Final recommendation:

```text
IMPLEMENT_SCHEMA_ADAPTERS_NEXT = YES
IMPLEMENT_PROVIDER_EXECUTION_NEXT = NO
KEEP_ERR_PASSIVE = YES
KEEP_EXECUTION_PROVIDER_CONTRACTS_SEPARATE = YES
```
