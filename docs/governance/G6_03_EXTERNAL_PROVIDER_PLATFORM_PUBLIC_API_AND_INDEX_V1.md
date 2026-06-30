# G6-03 External Provider Platform Public API And Index V1

Status: public architecture index defined.

Final verdict: EXTERNAL_PROVIDER_PLATFORM_PUBLIC_API_READY

## 1. Purpose

G6-03 defines the canonical public Platform Core architecture and discoverability index for the External Provider Platform.

This is a documentation and public-index milestone only. It does not introduce a new runtime layer, facade runtime, provider execution, Worker execution, repository mutation, deployment, approval creation, authorization creation, retry, fallback, or tests.

Existing runtime names, modules, and responsibilities remain unchanged.

## 2. Executive Determination

The External Provider Platform public API is ready as an architectural index over existing runtimes.

No new runtime facade is required before the next implementation batch.

The correct public API model is:

```text
Canonical EPP public API = documented Platform Core entrypoint map + compatibility aliases + ownership boundaries.
```

Runtime facade code may be added later only if repeated adapter/runtime integration requires it. It is not required for G6-03.

## 3. Architectural Index

| EPP Area | Canonical Public Surface | Existing Module |
| --- | --- | --- |
| Provider abstraction | Provider identity, provider contract, normalized result. | `sapianta_bridge/providers/` |
| Provider registry | Passive provider metadata registration and lookup. | `sapianta_bridge/providers/provider_registry.py`, `aigol/provider/provider_registry.py` |
| External resource registry | Passive resource registration, lookup, capability matching, selection evidence. | `aigol/runtime/external_resource_registry_runtime.py` |
| Unified resource selection | Governed provider/Worker/hybrid/tool/runtime/domain selection without invocation. | `aigol/runtime/unified_resource_selection_runtime.py` |
| Connector model | Provider-facing artifact handoff, connector identity, connector binding. | `sapianta_bridge/provider_connectors/` |
| Transport model | Request/response/error transport evidence and validation. | `sapianta_bridge/real_provider_transport/`, `aigol/runtime/live_provider_http_transport.py` |
| Credential boundary | Credential lifecycle, retrieval, diagnostics, secret-free replay. | `aigol/runtime/provider_credential_vault.py` |
| Provider governance | Lifecycle operations, credential diagnostics, usage metrics, participation records. | `aigol/runtime/provider_governance_runtime.py` |
| Provider attachment | Proposal-only provider response attachment and governed result. | `aigol/runtime/provider_attachment.py` |
| Multi-provider cognition | Multi-provider request/result bundles, failure isolation, replay. | `aigol/runtime/multi_provider_cognition_runtime.py` |
| PGSP provider cognition | Bounded read-only provider cognition and live PGSP entrypoint. | `aigol/runtime/g5_pgsp_bound_read_only_provider_cognition_runtime.py`, `aigol/runtime/g5_live_pgsp_provider_cognition_entrypoint.py` |
| Natural-language onboarding | Provider onboarding and disablement through governed natural language. | `aigol/runtime/provider_onboarding_domain_certification_v1.py` |

## 4. Canonical Public Platform API

The public EPP API is an architectural API, not a single code module.

Canonical operations:

| Operation | Public Entry Point | Output |
| --- | --- | --- |
| Register passive provider metadata | `ProviderRegistry.register_provider(...)` | Provider metadata with identity hash. |
| Lookup passive provider metadata | `ProviderRegistry.lookup_provider(...)` | Replay-safe provider metadata. |
| Register external resource | `register_resource(...)` | Passive ERR resource metadata. |
| Select resource by capability | `select_resource_for_capability(...)` | ERR selection evidence and replay reference. |
| Select unified resource | `select_unified_resource(...)` | Governed resource selection artifact. |
| Add provider credential | `add_provider_credential(...)` | Secret-free vault event artifact. |
| Verify provider credential | `verify_provider_credential(...)` | Credential verification event. |
| Rotate provider credential | `rotate_provider_credential(...)` | Human-approved rotation event. |
| Disable provider credential | `disable_provider_credential(...)` | Human-approved disable event. |
| Delete provider credential | `delete_provider_credential(...)` | Human-approved delete event. |
| Retrieve provider credential | `retrieve_provider_credential(...)` | Runtime-only credential secret plus replay-safe retrieval artifact. |
| Record provider lifecycle governance | `execute_provider_lifecycle_operation(...)` | Provider governance event. |
| Record provider usage | `record_provider_usage_metric(...)` | Usage metric evidence. |
| Record cognition participation | `record_cognition_participation(...)` | Cognition participation evidence. |
| Attach provider response | `attach_real_provider_response(...)` | Provider attachment replay and governed result. |
| Run multi-provider cognition | `run_multi_provider_cognition_runtime(...)` | Multi-provider result bundle and replay. |
| Run bounded PGSP provider cognition | `run_g5_pgsp_bound_read_only_provider_cognition_runtime(...)` | Provider cognition runtime summary and replay. |
| Run live PGSP provider cognition | `run_g5_live_pgsp_provider_cognition_entrypoint(...)` | Live PGSP provider review evidence. |
| Run live HTTP transport boundary | `run_live_provider_http_transport(...)` | Transport request/response/error/audit replay. |
| Route provider onboarding prompt | `route_provider_onboarding_domain_prompt(...)` | Provider onboarding intake artifact. |
| Certify provider onboarding domain | `run_provider_onboarding_domain_certification(...)` | Provider onboarding certification report. |

Canonical replay operations:

| Replay Operation | Entry Point |
| --- | --- |
| ERR selection replay | `reconstruct_err_v0_selection_replay(...)` |
| Unified resource selection replay | `reconstruct_unified_resource_selection_replay(...)` |
| Provider governance replay | `reconstruct_provider_governance_replay(...)` |
| Provider attachment replay | `reconstruct_provider_attachment_replay(...)` |
| Multi-provider cognition replay | `reconstruct_multi_provider_cognition_replay(...)` |
| G5-02 provider cognition replay | `reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay(...)` |
| G5-03 live PGSP provider replay | `reconstruct_g5_live_pgsp_provider_cognition_entrypoint_replay(...)` |
| Live HTTP transport replay | `reconstruct_live_provider_http_transport_replay(...)` |
| Provider onboarding domain replay | `reconstruct_provider_onboarding_domain_replay(...)` |

## 5. Ownership Matrix

| Public API Area | Owner | Boundary |
| --- | --- | --- |
| EPP public architecture index | Platform Core / Provider Services | Documentation and discovery only. |
| Provider identity and metadata | Provider Services | Passive identity; no authority. |
| Provider registry | Provider Services / External Resource Registry | Passive metadata; no routing or orchestration. |
| Resource selection | OCS / Governance selection policy | Selection evidence only; no invocation. |
| Credential lifecycle | Credential vault / Provider Services | Secret-free replay; governed mutation. |
| Connector handoff | EPP connector layer | Artifact handoff only. |
| Transport | EPP transport layer | Communication evidence only. |
| Provider governance | Governance | Admissibility, lifecycle, metrics, authority constraints. |
| PGSP invocation | PGSP | Session-level invocation into certified runtimes. |
| Semantic translation | UBTR | Human provider intent translation. |
| Canonical semantic representation | CSA | Provider/service intent representation. |
| Human communication | UHCL | Explanation, confirmation, review, recovery. |
| Replay | Replay | Reconstruction and continuity evidence. |
| Adapter rendering | Interface adapters | Render and capture responses only. |

## 6. Compatibility Mapping

| Existing Name | Canonical EPP Name | Compatibility Status |
| --- | --- | --- |
| Provider Services | EPP Provider Services | Valid alias. |
| Provider abstraction substrate | EPP Provider Abstraction | Valid alias. |
| External Resource Registry or ERR | EPP Registry / EPP Resource Registry | Valid alias for passive resource lookup. |
| Unified Resource Selection | EPP Selection input under OCS/Governance | Valid alias for current selection runtime. |
| Provider connector | EPP Connector | Valid alias. |
| Real provider transport | EPP Transport | Valid alias. |
| Provider credential vault | EPP Credential Boundary | Valid alias. |
| Provider attachment | EPP Attachment | Valid alias. |
| Multi-provider cognition | EPP multi-provider cognition specialization | Valid alias. |
| G5 provider cognition runtime | EPP bounded cognition specialization | Valid alias. |
| Provider onboarding domain | EPP natural-language lifecycle specialization | Valid alias. |

Compatibility constraints:

- do not rename existing runtime modules for G6-03;
- do not move registry ownership into OCS;
- do not move selection ownership into passive registries;
- do not turn connectors into routers;
- do not turn transports into execution authorities;
- do not let adapters own EPP semantics.

## 7. Facade Necessity Assessment

A new runtime facade is not required now.

Reasons:

- existing public entrypoints already exist for registry, selection, credential, governance, attachment, transport, cognition, replay, and onboarding;
- G6-02 established EPP as a canonical architecture name without requiring runtime movement;
- facade code would risk becoming an unnecessary indirection before the compatibility index and production policy are certified;
- adapters can use the documented public API map while PGSP/OCS/Governance remain the architectural callers.

Future facade criteria:

A lightweight facade may become useful only when:

1. multiple adapters need one import surface;
2. production provider certification requires one stable package namespace;
3. replay bundle creation needs a single index builder;
4. compatibility aliases become hard to maintain in documentation alone.

If introduced later, the facade must be thin and must delegate to existing runtimes.

## 8. Documentation Strategy

Documentation should be the public API for G6-03.

Required documentation set:

- G6-02 EPP canonical architecture;
- G6-03 public API and architectural index;
- future EPP compatibility index;
- future EPP provider identity and capability taxonomy;
- future EPP replay bundle definition;
- future EPP natural-language lifecycle PGSP contract.

Documentation should preserve exact existing runtime names and should not hide the fact that EPP is currently a consolidated architecture over multiple existing modules.

## 9. Migration Strategy

Migration is compatibility-first:

1. Keep existing runtime entrypoints unchanged.
2. Treat this document as the canonical public EPP index.
3. Add future docs that map module-specific schemas into EPP identity, capability, replay, and certification concepts.
4. Add a thin compatibility index only if production integration needs it.
5. Certify provider family packs after selection, credential binding, replay bundle, and lifecycle contracts are defined.

No runtime migration is required for G6-03.

## 10. Implementation Recommendation

Recommended next implementation batch:

1. `G6_04_EPP_COMPATIBILITY_INDEX_ARTIFACT_V1`
2. `G6_05_EPP_PROVIDER_IDENTITY_AND_CAPABILITY_TAXONOMY_V1`
3. `G6_06_EPP_SELECTION_POLICY_AND_GOVERNANCE_CHECKPOINTS_V1`
4. `G6_07_EPP_REPLAY_BUNDLE_AND_CERTIFICATION_PACKET_V1`
5. `G6_08_EPP_NATURAL_LANGUAGE_PROVIDER_LIFECYCLE_PGSP_CONTRACT_V1`

No new runtime facade should be implemented before the compatibility index proves one is needed.

## 11. Certification Impact

G6-03 certifies EPP discoverability.

Certification impact:

- one canonical public architecture index now exists;
- existing runtime names remain valid;
- Provider Registry duplication risk is reduced;
- connector, transport, registry, selection, credential, replay, and PGSP responsibilities remain separated;
- future production EPP implementation can proceed through policy and compatibility work instead of redesign.

## 12. Final Determination

The External Provider Platform public API is ready as a documented Platform Core architecture index.

Runtime behavior remains unchanged.

Final verdict: EXTERNAL_PROVIDER_PLATFORM_PUBLIC_API_READY
