# G6-04 Natural Language External Provider Onboarding Reuse Audit V1

Status: existing onboarding capability audited.

Final verdict: NATURAL_LANGUAGE_PROVIDER_ONBOARDING_EXTENSION_REQUIRED

## 1. Purpose

G6-04 audits whether AiGOL already supports governed natural-language onboarding and management of external providers through PGSP, UBTR, CSA, OCS, Governance, UHCL, and Replay.

This is a reuse audit only. It does not introduce a new onboarding runtime, provider runtime, registry, selection policy, credential mechanism, Worker path, repository mutation path, deployment path, approval activation path, or authorization activation path.

## 2. Executive Determination

Natural-language provider onboarding already exists as a certified Platform Core capability, but it is not yet production-complete for the full External Provider Platform lifecycle.

The existing reusable capability is implemented by:

- `aigol/runtime/provider_onboarding_domain_certification_v1.py`
- `aigol/runtime/provider_credential_vault.py`
- `aigol/runtime/provider_governance_runtime.py`
- the EPP public API index established in G6-03

The existing runtime supports deterministic natural-language routing for provider onboarding and disablement, execution summaries, explicit human approval evidence, vault credential operations, credential verification, certification workflow generation, replay reconstruction, and secret-free evidence.

The missing work is extension and production alignment, not restructuring.

## 3. Existing Runtime Inventory

| Runtime Area | Existing Surface | Reuse Status |
| --- | --- | --- |
| Natural-language onboarding domain | `route_provider_onboarding_domain_prompt(...)` | Reuse unchanged. |
| Onboarding certification execution | `run_provider_onboarding_domain_certification(...)` | Reuse unchanged as certification runtime. |
| Onboarding replay | `reconstruct_provider_onboarding_domain_replay(...)` | Reuse unchanged. |
| Credential vault lifecycle | `add_provider_credential(...)`, `verify_provider_credential(...)`, `rotate_provider_credential(...)`, `disable_provider_credential(...)`, `delete_provider_credential(...)` | Reuse unchanged; expand natural-language coverage later. |
| Credential diagnostics | `provider_credential_diagnostic(...)` | Reuse unchanged. |
| Provider governance lifecycle | `execute_provider_lifecycle_operation(...)` | Reuse unchanged for governance events. |
| Provider governance replay | `reconstruct_provider_governance_replay(...)` | Reuse unchanged. |
| EPP public API | G6-03 architectural index | Reuse as canonical discovery surface. |

## 4. Capability Matrix

| Required Capability | Current Support | Evidence | Assessment |
| --- | --- | --- | --- |
| Natural-language provider attachment | Implemented for Claude, Gemini, Mistral onboarding prompts. | `Dodaj Claude kot cognition provider.`, `Dodaj Gemini.`, `Zelim uporabljati Mistral.` route to `ONBOARD_PROVIDER`. | Reuse confirmed for the certified onboarding domain. |
| Provider configuration through conversation | Partial. | Existing prompts route provider identity and lifecycle operation. | Configuration values, capability options, model policy, cost policy, timeout policy, and routing policy are not yet conversation-certified. |
| Credential onboarding flow | Implemented for onboarding certification. | Runtime adds credential through the vault, verifies it, records diagnostic evidence, and prevents credential value replay. | Reuse confirmed; production credential collection policy still needs PGSP contract alignment. |
| Provider validation | Implemented at credential verification and certification workflow generation level. | `verify_provider_credential(...)`, `provider_credential_diagnostic(...)`, certification workflow artifacts. | Reuse confirmed; live provider validation remains a later certification step. |
| Provider certification | Partially implemented. | Domain certification produces coverage, evidence, replay, and certification report artifacts. | Domain certification exists; production EPP provider family certification remains future work. |
| Provider replacement | Partial. | Credential vault supports rotation with human approval. | Natural-language replacement scenarios are not yet certified. |
| Provider retirement | Partial. | `Onemogoci Claude.` routes to `DISABLE_PROVIDER`; vault supports disable and delete. | Disablement is certified; retirement, deletion, archive, and restoration need lifecycle certification. |
| Replay evidence | Implemented. | Intake, execution summary, approval, workflow execution, certification workflow, evidence package, replay package, reconstruction. | Reuse confirmed. |
| Governance checkpoints | Implemented for approval boundary and no provider or Worker invocation. | Approval artifact records no provider, execution, Worker, or governance authority transfer. | Reuse confirmed; broader EPP governance policy checkpoints still need production contract. |
| Human approval flow | Implemented for certification scenarios. | `_human_approval(...)` and fail-closed execution if approval is absent. | Reuse confirmed; live adapter approval UX remains future work. |
| Existing onboarding commands | Implemented for certified prompts. | Claude/Gemini/Mistral add prompts and Claude disable prompt. | Reuse confirmed for current command set. |
| Existing onboarding runtimes | Implemented. | Provider onboarding domain runtime, credential vault, provider governance runtime. | Reuse confirmed; no new runtime family is justified. |

## 5. Reuse Assessment

The existing onboarding domain should remain the canonical seed implementation for natural-language EPP lifecycle management.

Reusable without redesign:

- deterministic provider intent detection for the certified onboarding domain;
- provider lifecycle operation classification for onboarding and disablement;
- execution summary before action;
- explicit human approval before vault mutation;
- credential vault add, verify, rotate, disable, delete, retrieve, and diagnostic boundaries;
- secret-free replay artifacts;
- replay reconstruction;
- provider governance lifecycle and credential diagnostics;
- EPP public API documentation from G6-03.

Required extensions:

- canonical PGSP lifecycle contract for all provider lifecycle operations;
- conversation-certified provider replacement;
- conversation-certified credential rotation;
- conversation-certified retirement, deletion, archival, and restoration;
- arbitrary EPP provider onboarding beyond the currently certified cognition providers;
- live adapter onboarding entrypoint certification;
- production provider validation and family certification packets.

## 6. Ownership Verification

| Concern | Canonical Owner | Verification |
| --- | --- | --- |
| Natural-language capture | Interface Adapter | Adapter captures text only; it must not own provider semantics. |
| Semantic translation | UBTR | Future production onboarding should route provider lifecycle intent through UBTR. |
| Canonical intent | CSA | Provider lifecycle operation, provider identity, and lifecycle target belong in CSA artifacts. |
| Orchestration | OCS | OCS owns proposal and lifecycle orchestration; providers do not. |
| Governance | Governance | Governance owns admissibility, approval requirements, fail-closed boundaries, and authority separation. |
| Human communication | UHCL | UHCL owns explanation, confirmation, provider summary, recovery guidance, and review language. |
| Credential lifecycle | EPP Credential Boundary | Vault owns credential storage, retrieval, rotation, disablement, deletion, diagnostics, and secret-free replay. |
| Provider identity | EPP Provider Services | Provider identities remain passive, role-scoped, and non-authoritative. |
| Replay | Replay | Replay owns reconstruction evidence and secret-free continuity. |
| Provider execution | Provider runtime | Out of scope for onboarding; onboarding certification records no provider invocation. |

The existing implementation preserves these boundaries in certification form. Production alignment should formalize the same ownership through the PGSP adapter contract instead of introducing a separate onboarding owner.

## 7. Replay Assessment

Replay support is strong for the current domain certification.

Existing replay-visible artifacts include:

- provider onboarding intake artifact;
- execution summary artifact;
- human approval artifact;
- workflow execution artifact;
- certification workflow artifact;
- evidence package;
- replay package;
- replay reconstruction.

Replay explicitly records:

- provider id;
- operation;
- workflow target;
- approval boundary;
- vault action completion;
- credential presence and enabled state;
- provider registration visibility;
- verification visibility;
- absence of live provider invocation;
- absence of Worker invocation.

Replay intentionally does not record:

- credential value;
- credential hash;
- bearer token material;
- API key material;
- provider secret source paths outside replay-safe references.

Production extension should preserve this exact replay safety model.

## 8. Governance Assessment

The current onboarding runtime is governance-preserving.

Certified governance properties:

- unclear provider requests fail closed;
- unclear operations fail closed;
- workflow execution requires explicit approval;
- provider onboarding and management remain non-authoritative;
- providers receive no governance authority;
- providers receive no execution authority;
- Workers are not invoked;
- live providers are not invoked;
- replay is secret-free;
- certification output identifies next certification work instead of claiming production completeness.

Production governance gaps:

- policy-specific onboarding admissibility is not yet generalized across arbitrary external systems;
- replacement, rotation, retirement, deletion, archival, and restoration are not yet natural-language lifecycle-certified;
- approval evidence is certification-local, not yet a full production approval lifecycle integrated across PGSP, OCS, and UHCL;
- credential collection UX and operator confirmation text require canonical UHCL contract coverage.

## 9. Production Readiness

| Area | Readiness | Reason |
| --- | --- | --- |
| Certified onboarding seed domain | Ready for reuse. | Existing runtime and tests certify deterministic onboarding and disablement evidence. |
| Production natural-language provider lifecycle | Extension required. | Lifecycle coverage is narrower than full EPP provider management. |
| Arbitrary external provider onboarding | Extension required. | Current detection is limited to Claude, Gemini, and Mistral cognition providers. |
| Live adapter onboarding | Extension required. | Certification recommends live ACLI session certification as a next step. |
| Credential safety | Ready for reuse. | Vault evidence is secret-free and approval-gated for destructive operations. |
| Provider validation | Partial. | Credential verification exists; live provider certification remains separate. |
| Provider replacement and retirement | Partial. | Vault primitives exist; natural-language lifecycle certification is incomplete. |

## 10. Duplication Risk Assessment

Creating a new natural-language provider onboarding runtime now would duplicate existing Platform Core capabilities.

Duplication risks:

- duplicate provider lifecycle intent routing;
- duplicate credential vault operations;
- duplicate approval boundary evidence;
- duplicate provider governance event recording;
- duplicate replay packages;
- duplicate certification workflow generation;
- duplicate provider identity handling.

The correct path is to extend the existing onboarding domain through PGSP/EPP lifecycle contracts.

## 11. Compatibility Layers

Current compatible aliases:

| Existing Name | Canonical EPP Meaning |
| --- | --- |
| Provider onboarding domain | EPP natural-language provider lifecycle domain. |
| Provider onboarding workflow | EPP provider attachment or credential onboarding lifecycle. |
| Provider management workflow | EPP provider disablement and future retirement lifecycle. |
| Provider credential vault | EPP credential lifecycle boundary. |
| Provider governance runtime | EPP governance evidence and lifecycle event boundary. |

These aliases should remain documentation-level until a repeated adapter integration problem proves a facade is needed.

## 12. Implementation Recommendation

Do not implement a new onboarding runtime.

Recommended next implementation batch:

1. `G6_05_EPP_NATURAL_LANGUAGE_PROVIDER_LIFECYCLE_CONTRACT_V1`
2. `G6_06_EPP_PROVIDER_REPLACEMENT_AND_ROTATION_NL_CERTIFICATION_V1`
3. `G6_07_EPP_PROVIDER_RETIREMENT_AND_RESTORATION_NL_CERTIFICATION_V1`
4. `G6_08_EPP_ARBITRARY_EXTERNAL_PROVIDER_ONBOARDING_SCHEMA_V1`
5. `G6_09_EPP_LIVE_PGSP_PROVIDER_ONBOARDING_ENTRYPOINT_V1`

Each step should reuse the existing onboarding domain runtime, credential vault, provider governance runtime, EPP public index, PGSP, UBTR, CSA, OCS, UHCL, and Replay boundaries.

## 13. Certification Impact

G6-04 certifies that natural-language external provider onboarding is already partially implemented and reusable.

Certification impact:

- no new onboarding runtime is architecturally justified;
- existing onboarding evidence should be treated as the canonical seed capability;
- production work should extend lifecycle coverage;
- replay and credential secrecy boundaries remain certified reuse targets;
- future adapter work must call Platform Core onboarding semantics, not implement adapter-owned onboarding logic.

## 14. Final Determination

Natural-language provider onboarding reuse is confirmed, but production extension is required before EPP can claim complete natural-language external provider lifecycle management.

Final verdict: NATURAL_LANGUAGE_PROVIDER_ONBOARDING_EXTENSION_REQUIRED
