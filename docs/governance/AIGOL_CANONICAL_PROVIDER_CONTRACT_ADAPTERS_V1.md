# AIGOL Canonical Provider Contract Adapters V1

Status: adapter adoption design.

Purpose: define adapter-based adoption of `AIGOL_CANONICAL_PROVIDER_CONTRACT_V1` without changing provider execution, transport, authentication, OCS architecture, ERR authority, replay semantics, or worker boundaries.

This artifact is governance design only.

It does not implement runtime adapters.

## Context

`AIGOL_PROVIDER_CONTRACT_MIGRATION_AUDIT_V1` concluded:

```text
CANONICAL_PROVIDER_CONTRACT_ADOPTION_FEASIBLE = YES
ARCHITECTURAL_REDESIGN_REQUIRED = NO
MIGRATION_READINESS = READY_WITH_ADAPTATION
```

This artifact defines how adoption should happen through pure schema adapters.

## Adapter Architecture

Canonical provider contract adoption should use adapter layers at schema boundaries:

```text
existing dialect artifact
-> pure schema adapter
-> canonical contract/input/output view
-> existing runtime behavior preserved
-> existing replay compatibility preserved
```

Adapters are not providers.

Adapters do not invoke providers.

Adapters do not call transport.

Adapters do not authorize execution.

Adapters do not mutate existing replay history.

Adapters create replay-visible canonical views or compatibility evidence from already-existing artifacts.

## Adapter Classes

The adapter architecture contains five adapter categories:

| Adapter Category | Purpose |
| --- | --- |
| Contract adapters | Convert existing provider contract dialects into `CANONICAL_COGNITION_PROVIDER_CONTRACT_V1`. |
| Input adapters | Convert provider request artifacts into `CANONICAL_COGNITION_PROVIDER_INPUT_V1`. |
| Output adapters | Convert provider response artifacts into `CANONICAL_COGNITION_PROVIDER_OUTPUT_V1`. |
| Raw evidence adapters | Attach `RawProviderResponseEvidence` as nested raw-response evidence, not as cognition output. |
| Scope boundary adapters | Mark execution-provider, connector, native execution, or ERR surfaces as out of scope or reference-only. |

## Dialect Adapter Strategy

### MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1

Adapter:

```text
MultiProviderContractToCanonicalAdapter
```

Classification:

```text
MINOR_ADAPTATION
```

Responsibilities:

- map `provider_id`, `provider_role`, `provider_schema_id`, `provider_identity`;
- map `provider_approved`;
- map `allowed_outputs`;
- map `authority_model` to `authority_flags`;
- add canonical `artifact_type`;
- add canonical `contract_reference`;
- add `capabilities` from explicit adapter input or governed fixture;
- add canonical `prohibited_outputs`;
- add missing authority flags as false;
- compute `contract_hash`;
- compute canonical `artifact_hash`;
- preserve original artifact hash as `source_contract_hash`.

Must not:

- preserve `single_provider_only` as core contract identity;
- preserve `multi_provider_cognition_scope` as core contract identity;
- invoke provider transport.

### LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1

Adapter:

```text
SingleProviderContractToCanonicalAdapter
```

Classification:

```text
MINOR_ADAPTATION
```

Responsibilities:

- map provider identity and schema fields;
- preserve OpenAI-specific endpoint only as optional non-secret provider metadata;
- move `single_provider_only` to invocation-scope metadata;
- add `capabilities`;
- add canonical authority flags;
- compute `contract_hash` and canonical `artifact_hash`;
- preserve original artifact hash as `source_contract_hash`.

Must not:

- make OpenAI endpoint required for all providers;
- include credentials, API keys, or credential env names;
- authorize single-provider invocation.

### LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1

Adapter:

```text
ProviderRequestToCanonicalInputAdapter
```

Classification:

```text
MINOR_ADAPTATION
```

Responsibilities:

- map `cognition_provider_request_id` to `provider_input_id`;
- map `request_hash` to `input_hash`;
- preserve request object;
- preserve OCS context reference;
- preserve provider contract hash;
- preserve lineage refs;
- map authority flags;
- add canonical `artifact_type`;
- add canonical `contract_reference`;
- preserve original request artifact hash as `source_input_artifact_hash`;
- fail closed if provider input already claims provider invocation.

Must not:

- store secrets;
- create provider transport payloads;
- change the prompt;
- mutate existing request replay artifacts.

### LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1

Adapter:

```text
ProviderResponseToCanonicalOutputAdapter
```

Classification:

```text
MINOR_ADAPTATION
```

Responsibilities:

- map `cognition_provider_request_id` to `provider_input_id`;
- map `provider_request_hash` to `provider_input_hash`;
- map `response_hash` to `output_hash`;
- preserve raw response and response text hashes;
- preserve provider identity and provider metadata;
- preserve non-authoritative and untrusted-output markers;
- preserve lineage refs;
- add explicit canonical `provider_output_id`;
- add canonical `artifact_type`;
- add canonical `contract_reference`;
- preserve original response artifact hash as `source_output_artifact_hash`;
- fail closed if authority flags escalate.

Must not:

- infer provider invocation from ERR selection;
- alter provider raw output;
- normalize cognition fields itself;
- bypass `LLM_COGNITION_ARTIFACT_V1`.

### LLM_COGNITION_ARTIFACT_V1

Adapter:

```text
NoOpCanonicalCognitionArtifactAdapter
```

Classification:

```text
DIRECT_MIGRATION
```

Responsibilities:

- validate existing artifact hash;
- validate canonical cognition fields;
- validate confidence and uncertainty fields;
- validate authority flags;
- expose the artifact as canonical without shape mutation.

Must not:

- rename the artifact type;
- change replay lineage;
- recalculate historical replay artifacts in place.

### RawProviderResponseEvidence

Adapter:

```text
RawProviderResponseEvidenceToCanonicalOutputMetadataAdapter
```

Classification:

```text
MINOR_ADAPTATION
```

Responsibilities:

- map provider name and model name into provider metadata;
- map raw response text and hash into raw-response evidence;
- map normalization status and reason into provider metadata;
- preserve `evidence_hash` in canonical lineage refs;
- mark raw evidence as pre-normalization only.

Must not:

- promote raw output directly into cognition output;
- treat `normalization_status` as cognition confidence;
- bypass authority-bearing text checks.

### ERR Resource Metadata

Adapter:

```text
ErrResourceToCanonicalProviderReferenceAdapter
```

Classification:

```text
MINOR_ADAPTATION
```

Responsibilities:

- map `resource_id` to `provider_id`;
- map `resource_type = COGNITION_PROVIDER` to `provider_role = COGNITION_PROVIDER`;
- map ERR capabilities to canonical capabilities;
- optionally associate a canonical contract hash in a future governed extension.

Must not:

- make ERR authoritative;
- make ERR approve provider invocation;
- add routing, ranking, optimization, lifecycle, or transport behavior;
- require ERR schema expansion in the first adapter phase.

### ProviderContract In sapianta_bridge/providers

Adapter:

```text
ExecutionProviderContractBoundaryAdapter
```

Classification:

```text
MAJOR_ADAPTATION
```

Responsibilities:

- mark execution-provider contracts as out of canonical cognition-provider scope;
- optionally expose shared authority-boundary facts for governance comparison;
- prevent accidental merging of execution providers and cognition providers.

Must not:

- convert bounded execution semantics into cognition-provider authority;
- treat execution-provider outputs as cognition artifacts.

### NormalizedExecutionResult

Adapter:

```text
NormalizedExecutionResultBoundaryAdapter
```

Classification:

```text
MAJOR_ADAPTATION
```

Responsibilities:

- mark normalized execution results as out of canonical cognition-provider output scope;
- preserve worker/execution result semantics separately.

Must not:

- map `execution_status` to provider cognition status;
- interpret stdout or stderr as cognition output.

### Native Provider Execution Request/Response

Adapter:

```text
NativeProviderExecutionBoundaryAdapter
```

Classification:

```text
MAJOR_ADAPTATION
```

Responsibilities:

- classify native provider execution as execution-capable and outside first canonical cognition migration;
- require separate governed review before any canonical cognition-provider mapping;
- block credentials and execution confirmation fields from canonical contract artifacts.

Must not:

- authorize provider execution by schema conformance;
- include credential policy or `_credential_secret` in canonical artifacts;
- collapse native execution into OCS cognition without governance.

### Real Provider Transport Bridge

Adapter:

```text
ProviderTransportBoundaryAdapter
```

Classification:

```text
MAJOR_ADAPTATION
```

Responsibilities:

- classify transport-level evidence as adjacent to, but not identical with, canonical provider input/output;
- require an existing canonical cognition-provider context before mapping transport response evidence.

Must not:

- implement transport;
- leak transport state into canonical contract;
- store credentials or sessions.

### Provider Connectors

Adapter:

```text
ProviderConnectorBoundaryAdapter
```

Classification:

```text
MAJOR_ADAPTATION
```

Responsibilities:

- mark provider connector surfaces as execution/connector infrastructure;
- keep them outside initial canonical cognition-provider contract migration;
- preserve worker/provider separation.

Must not:

- convert connector execution evidence into cognition-provider output;
- couple providers to workers.

## Mapping Dialect Outputs To Canonical Cognition Artifacts

Canonical downstream cognition remains:

```text
LLM_COGNITION_ARTIFACT_V1
```

Mapping rule:

```text
canonical provider output
-> cognition artifact normalization
-> LLM_COGNITION_ARTIFACT_V1
```

The canonical output adapter does not replace cognition normalization.

Dialect output mapping:

| Source Output | Adapter Path | Canonical Cognition Result |
| --- | --- | --- |
| `LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1` | `ProviderResponseToCanonicalOutputAdapter` then existing cognition artifact runtime | `LLM_COGNITION_ARTIFACT_V1` |
| `RawProviderResponseEvidence` | Nested into canonical output metadata only | No cognition artifact unless bounded provider output exists. |
| Native provider execution response | Out of first migration scope | No canonical cognition artifact without separate governance review. |
| Bridge execution result | Out of cognition-provider scope | No canonical cognition artifact. |
| Transport response | Boundary-only unless already attached to cognition-provider output | No direct cognition artifact. |

## Replay Compatibility Strategy

Adapters must preserve replay compatibility through additive canonical views.

Required replay behavior:

- existing replay artifacts remain readable;
- canonical views reference source artifact hashes;
- source artifact hashes are not replaced;
- canonical hashes are computed separately;
- replay reconstruction can validate both source and canonical views;
- adapters fail closed on source hash mismatch;
- adapters fail closed on authority flag escalation;
- adapters fail closed on missing required lineage;
- no historical replay file is rewritten.

Compatibility pattern:

```text
source_artifact
source_artifact_hash
-> canonical_adapter_view
canonical_artifact_hash
source_artifact_hash retained in lineage
```

## Runtime Behavior Preservation

Adapters must preserve existing runtime behavior:

- OCS still orchestrates.
- ERR still performs passive lookup.
- Provider transports are unchanged.
- Provider invocation gates are unchanged.
- Provider availability gates are unchanged.
- Cognition artifact normalization remains unchanged.
- Comparison, continuity, clarification, and replay reconstruction remain unchanged.
- Worker assignment remains separate.

No existing runtime should be required to change behavior before canonical schema views are validated.

## Migration Sequencing

### Phase 1: Schema Fixtures

Create JSON schema fixtures for:

- `CANONICAL_COGNITION_PROVIDER_CONTRACT_V1`;
- `CANONICAL_COGNITION_PROVIDER_INPUT_V1`;
- `CANONICAL_COGNITION_PROVIDER_OUTPUT_V1`.

Add tests validating required fields and prohibited fields.

### Phase 2: Pure Contract Adapters

Implement pure conversion helpers for:

- `MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1`;
- `LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1`.

No provider execution.

No transport.

No authentication.

### Phase 3: Pure Input And Output Adapters

Implement pure conversion helpers for:

- `LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1`;
- `LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1`.

Adapters must be replay-visible and hash-verifiable.

### Phase 4: Cognition Artifact No-Op Validation

Add conformance tests proving:

- `LLM_COGNITION_ARTIFACT_V1` remains canonical;
- confidence values are bounded;
- uncertainties are lists;
- authority flags remain false;
- replay reconstruction remains valid.

### Phase 5: Raw Evidence Nesting

Add optional adapter for `RawProviderResponseEvidence` as nested evidence only.

Do not promote raw output into cognition.

### Phase 6: Boundary Adapter Tests

Add tests proving:

- execution-provider contracts are out of scope;
- normalized execution results are out of scope;
- native provider execution is out of scope;
- transport bridges are out of scope unless surrounded by canonical cognition context;
- provider connectors remain out of scope.

### Phase 7: OCS Compatibility Certification

Run:

- OCS cognition tests;
- ERR provider registration tests;
- HIRR post-certification regression suite;
- provider contract adapter conformance tests.

Only after this phase may canonical adoption be called runtime-compatible.

## Governance Constraints

Adapters must preserve:

- Human authority;
- OCS orchestration authority;
- ERR passive lookup boundary;
- provider non-authority;
- worker/provider separation;
- replay append-only semantics;
- fail-closed validation;
- no hidden execution;
- no credential capture;
- no replay mutation;
- no governance mutation.

Adapters must not:

- invoke providers;
- invoke workers;
- dispatch;
- authorize;
- govern;
- rank providers;
- optimize providers;
- compare providers;
- route providers;
- manage lifecycle;
- implement ELL;
- implement transport;
- authenticate;
- store secrets;
- change existing provider runtime behavior.

## Acceptance Criteria

Adapter adoption is accepted only when:

1. All dialects are assigned an adapter strategy.
2. OCS cognition contracts convert to canonical contract views.
3. Provider request artifacts convert to canonical input views.
4. Provider response artifacts convert to canonical output views.
5. `LLM_COGNITION_ARTIFACT_V1` remains unchanged and canonical.
6. Existing replay artifacts remain reconstructable.
7. Canonical adapter views preserve source artifact hashes.
8. Adapters fail closed on hash mismatch, missing lineage, authority escalation, or missing required fields.
9. ERR remains passive.
10. Execution-provider, native execution, transport, and connector paths remain out of initial migration scope.
11. No provider execution, invocation, transport, authentication, ranking, routing, lifecycle, ELL, dispatch, worker invocation, governance mutation, or replay mutation is introduced.

## Implementation Plan

Recommended next implementation milestone:

```text
AIGOL_CANONICAL_PROVIDER_CONTRACT_SCHEMA_FIXTURES_V1
```

Then:

1. Add schema fixtures.
2. Add conformance tests.
3. Add pure contract adapters.
4. Add pure input/output adapters.
5. Add boundary adapters for out-of-scope surfaces.
6. Preserve old artifacts and replay compatibility.
7. Certify compatibility with OCS, ERR, HIRR, and replay tests.

Do not implement provider execution or transport in this adapter milestone.

## Final Recommendation

Proceed with adapter-based canonical provider contract adoption.

Use the OCS cognition dialects as the first migration target.

Keep execution-capable and connector surfaces outside the first adoption wave.

Final recommendation:

```text
ADAPTER_BASED_ADOPTION_APPROVED = YES
ARCHITECTURAL_REDESIGN_REQUIRED = NO
PROVIDER_EXECUTION_CHANGE_ALLOWED = NO
TRANSPORT_CHANGE_ALLOWED = NO
ERR_PASSIVE_BOUNDARY_PRESERVED = YES
```
