# G6-01 Existing External Provider Platform Reuse Audit V1

Status: reuse audit complete.

Final verdict: EXTERNAL_PROVIDER_PLATFORM_EXTENSION_REQUIRED

## 1. Purpose

G6-01 audits whether AiGOL already contains a canonical External Provider Platform broader than LLM cognition providers.

This is a reuse audit only. It does not introduce runtime changes, provider execution, Worker execution, repository mutation, deployment, approval creation, authorization creation, retry, fallback, or tests.

The guiding rule is:

```text
Reuse before redesign.
```

## 2. Executive Determination

AiGOL already contains a reusable External Provider Platform foundation.

The foundation is distributed across:

- provider abstraction and provider registry surfaces;
- External Resource Registry capability selection;
- unified resource selection;
- Provider Services identity and governance;
- credential vault and credential diagnostics;
- provider attachment and connector contracts;
- real provider transport boundaries;
- multi-provider cognition runtime;
- natural-language provider onboarding certification;
- PGSP provider cognition entrypoints.

However, these capabilities are not yet normalized into one production-certified External Provider Platform contract for arbitrary external systems.

The correct next step is extension and canonicalization, not a new Provider Registry or redesigned Provider Services layer.

## 3. Existing Platform Inventory

| Existing Surface | Capability | Reuse Assessment |
| --- | --- | --- |
| `sapianta_bridge/providers/` | Provider abstraction, provider identity, provider contracts, passive provider registry, normalized execution results, placeholder adapters. | Reuse as foundational provider abstraction and authority boundary. |
| `sapianta_bridge/provider_connectors/` | Connector identity, request/response/evidence, execution gate, bounded Codex execution connector, timeout/process evidence. | Reuse as connector/transport handoff layer. |
| `sapianta_bridge/real_provider_transport/` | Real-provider transport request, response, evidence, validation, boundary rules. | Reuse as generic provider transport substrate. |
| `aigol/runtime/external_resource_registry_runtime.py` | Passive resource registry and capability-based resource selection with replay. | Reuse as shared external resource lookup foundation. |
| `aigol/runtime/unified_resource_selection_runtime.py` | Provider, Worker, hybrid provider/worker, operator tool, governance runtime, and domain runtime resource selection. | Reuse as broad resource selection policy surface. |
| `aigol/provider/provider_registry.py` | Metadata-only provider registry with identity hashes and passive boundary. | Reuse as Provider Services registry component. |
| `aigol/runtime/provider_governance_runtime.py` | Provider lifecycle governance, credential diagnostics, participation and usage metrics. | Reuse as provider governance evidence layer. |
| `aigol/runtime/provider_credential_vault.py` | Credential add, verify, rotate, disable, delete, retrieval attempts, secret-free replay. | Reuse as credential lifecycle boundary. |
| `aigol/runtime/provider_attachment.py` | Proposal-only provider response attachment and external LLM attachment handoff. | Reuse as provider output attachment model. |
| `aigol/runtime/providers/` | Read-only filesystem, HTTP GET, metadata inspection, OpenAI provider, provider envelope/gate/config. | Reuse as early provider implementation catalog. |
| `aigol/runtime/multi_provider_cognition_runtime.py` | Multi-provider cognition request/result bundles, failure isolation, usage evidence. | Reuse for multi-provider cognition and future failover policy. |
| `aigol/runtime/g5_pgsp_bound_read_only_provider_cognition_runtime.py` | PGSP-bound read-only cognition provider execution. | Reuse unchanged for bounded cognition execution. |
| `aigol/runtime/g5_live_pgsp_provider_cognition_entrypoint.py` | Live PGSP routing into G5-02 with UHCL review. | Reuse as PGSP provider invocation entrypoint. |
| `aigol/runtime/provider_onboarding_domain_certification_v1.py` | Natural-language provider onboarding and management certification. | Reuse for governed provider onboarding UX. |

## 4. Capability Matrix

| Required Capability | Existing Support | Gap |
| --- | --- | --- |
| Canonical external provider abstraction | Exists in bridge provider abstraction and AiGOL Provider Services. | Needs one canonical cross-package name and contract. |
| Provider attachment architecture | Exists through provider attachment, external LLM response attachment, real provider transport, connectors, runtime attachment. | Needs unified attachment lifecycle taxonomy. |
| Provider identity model | Exists across bridge provider identity, ProviderMetadata, G5 provider identity, ERR resources, unified resource selection. | Needs canonical identity facade and role mapping. |
| Provider lifecycle | Exists in provider governance and credential vault lifecycle operations. | Needs production certification lifecycle spanning attach, enable, disable, rotate, revoke, remove, recertify. |
| Provider capability model | Exists in ERR capabilities, unified resource selection role bindings, provider contracts, provider catalogs. | Needs canonical capability vocabulary for arbitrary external systems. |
| Provider registry | Exists in multiple passive registries. | Needs normalized registry-of-record or compatibility facade. |
| Provider discovery | Exists as metadata lookup and capability selection. | Needs production discovery policy and certification status binding. |
| Provider routing | Partially exists in ERR selection, unified selection, OCS cognition routing, PGSP entrypoints. | Needs canonical routing/selection policy; current registries intentionally do not orchestrate. |
| Governance checkpoints | Exists in provider governance, G5 provider runtime, live transport boundaries. | Needs production provider governance packet. |
| Replay integration | Exists across provider registry, attachment, transport, credential, G5, and multi-provider runtimes. | Needs one External Provider Platform replay index. |
| Natural-language integration | Exists for provider onboarding and conversational provider usage surfaces. | Needs PGSP-wide provider lifecycle command contract. |

## 5. Supported Provider Type Assessment

The existing architecture supports a broad provider concept, but production readiness differs by provider type.

| Provider Type | Current Support | Assessment |
| --- | --- | --- |
| LLM cognition providers | Strong support through G5 provider cognition, multi-provider cognition, OpenAI adapter, live transport boundary. | Reuse and extend for production certification. |
| Translation providers | Architecturally permitted as separate role identities. | Needs role-specific certification before production use. |
| Repair providers | Architecturally permitted and represented in provider proposal repair surfaces. | Needs canonical role policy and certification. |
| Worker providers / hybrid provider-workers | Represented in unified resource selection, Codex/Claude Code hybrid entries, provider connectors. | Needs strict role separation and Worker authorization binding. |
| External APIs | Represented by real provider transport and read-only HTTP provider concepts. | Needs generic API provider contract and credential/transport certification. |
| Search systems | Not production-certified as a distinct provider family. | Extend via external API/read-only provider contract. |
| Database services | Not production-certified. | Requires storage/data governance, query boundary, and credential policy. |
| ERP systems | Not production-certified. | Requires domain-specific connector and authorization model. |
| CRM systems | Not production-certified. | Requires domain-specific connector and data governance model. |
| Payment systems | Not production-certified. | Requires high-risk transaction authorization, audit, rollback, and compliance model. |
| Authentication providers | Not production-certified. | Requires identity/security-specific governance model. |
| File services | Partially represented by read-only filesystem and Worker/file services. | Needs external file-service provider certification. |
| Storage providers | Not production-certified. | Requires persistence, data handling, and credential lifecycle policy. |
| Monitoring systems | Partially implied by metadata inspection and external runtime inspection. | Needs monitoring-provider contract. |
| Future arbitrary systems | Architecturally intended through provider/resource/connector abstractions. | Needs canonical External Provider Platform extension model. |

Conclusion:

```text
The architecture is broad enough for arbitrary external systems, but production certification currently covers only narrower provider classes.
```

## 6. Provider Identity Assessment

Provider identity is already canonical in principle.

Existing identity rules include:

- provider id;
- provider type or resource type;
- provider role;
- capability declarations;
- lifecycle status;
- trust level;
- credential reference;
- replay-safe identity hash;
- authority flags;
- role-specific identity separation.

Certified invariants:

- same external system may appear under distinct Platform Core roles;
- provider identity does not create governance authority;
- provider identity does not create execution authorization;
- provider output remains evidence until OCS/Governance transforms it;
- credentials are isolated from replay;
- replay owns reconstruction evidence.

Gap:

The identity model exists in multiple schemas. A canonical External Provider Identity facade is required to normalize these schemas without replacing them.

## 7. Provider Attachment Assessment

Provider attachment already exists as several compatible concepts:

- proposal-only provider response attachment;
- external LLM response attachment;
- runtime attachment;
- terminal attachment;
- provider connector artifact handoff;
- real provider transport request/response/evidence;
- PGSP provider cognition routing.

Attachment lifecycle already covers:

- identity capture;
- raw response capture;
- provider attachment record;
- governed result;
- connector request/response;
- replay reconstruction;
- fail-closed validation.

Missing production lifecycle states:

- canonical attach;
- validate;
- certify;
- enable;
- suspend;
- rotate credential;
- recertify;
- disable;
- remove;
- archive.

These are extensions to existing attachment surfaces, not a reason to redesign them.

## 8. Provider Routing And Selection Assessment

Existing routing and selection support:

- ERR selects active resources by capability;
- unified resource selection evaluates provider, Worker, hybrid provider/Worker, operator tool, governance runtime, and domain runtime resources;
- provider necessity policy distinguishes required, optional, and prohibited provider use;
- OCS cognition runtimes route provider cognition;
- PGSP live provider entrypoint routes PGSP context into provider cognition;
- multi-provider cognition supports multiple approved cognition providers and isolated provider failures.

Existing constraints:

- passive registries do not orchestrate;
- connectors are not routers;
- provider transport is not orchestration;
- fallback and retry are mostly prohibited unless separately certified;
- provider comparison is separate from provider selection.

Gap:

Production provider routing needs a canonical selection policy that binds capability, role, trust, credential state, health, cost, latency, governance admissibility, and replay evidence.

## 9. Provider Communication Integration

| Integration Layer | Existing State | Assessment |
| --- | --- | --- |
| UBTR | Architecture requires universal semantic translation before canonical intent. Provider-specific translators are prohibited. | Canonical invariant exists; provider lifecycle commands should route through UBTR, not provider-local translators. |
| CSA | Canonical semantic artifacts can represent intent before OCS/resource selection. | Reuse for provider lifecycle and usage intents. |
| OCS | OCS cognition and provider-to-OCS proposal transformation are certified. | Reuse for provider proposal and decision flow. |
| UHCL | G5 provider cognition review and provider summaries exist. | Extend to production provider lifecycle summaries and recovery guidance. |
| PGSP | G5 live provider entrypoint exists. | Extend PGSP provider lifecycle commands through canonical contract. |
| Replay | Provider, credential, transport, connector, and PGSP replays exist. | Need unified replay bundle index. |

Communication ownership remains:

```text
Adapters render.
UHCL communicates.
OCS orchestrates.
UBTR translates.
Replay reconstructs.
Provider Services execute or attach external evidence only within scope.
```

## 10. Natural-Language Integration Assessment

Platform Core already supports governed natural-language provider integration.

Existing evidence includes:

- provider onboarding domain certification;
- prompts such as adding Claude, Gemini, or Mistral as providers;
- provider disablement prompts;
- deterministic provider onboarding routing;
- execution summary requirement;
- human approval requirement;
- vault onboarding visibility;
- provider registration visibility;
- secret-safe replay reconstruction.

Assessment:

```text
NATURAL_LANGUAGE_PROVIDER_INTEGRATION_PARTIALLY_CERTIFIED
```

Gap:

Natural-language provider lifecycle operations must be normalized under PGSP and UHCL so future adapters can request provider attachment, replacement, configuration, certification, removal, or usage through one canonical contract.

## 11. Ownership Matrix

| Capability | Canonical Owner | Reuse Determination |
| --- | --- | --- |
| External Provider Platform | Platform Core / Provider Services | Exists as distributed foundation; needs canonical facade. |
| Provider Registry | Provider Services / External Resource Registry | Reuse existing passive registries; normalize contract. |
| Provider Selection | OCS / resource selection policy under Governance | Reuse ERR and unified selection; add production policy. |
| Provider Identity | Provider Services | Reuse existing identity hashes and role separation; add facade. |
| Provider Credentials | Credential vault / Provider Services | Reuse vault and diagnostics; bind to dispatch. |
| Provider Routing | OCS / PGSP orchestration | Reuse existing routing; keep registries passive. |
| Provider Governance | Governance | Reuse provider governance runtime and G5 checkpoints. |
| Provider Replay | Replay | Reuse replay functions; add unified replay bundle. |
| Provider Communication | UHCL | Reuse provider cognition review; extend lifecycle summaries. |
| Interface Rendering | Adapters | Unchanged; adapters do not own reusable provider communication. |
| Connector Handoff | Provider connectors / transport | Reuse artifact handoff boundaries; do not make connectors routers. |

## 12. Duplication Risk Assessment

Implementing a new Provider Registry or Provider Services layer would duplicate:

- passive provider registry metadata;
- ERR resource registry;
- unified resource selection;
- provider identity hashes;
- credential vault lifecycle;
- provider governance event artifacts;
- provider attachment replay;
- provider transport request/response/evidence;
- provider connector boundaries;
- G5 PGSP provider cognition entrypoint.

High-risk duplication outcomes:

- conflicting provider identity schemas;
- unclear credential source of truth;
- adapter-owned provider semantics;
- registry-owned routing contrary to existing passive-registry invariant;
- provider output accidentally treated as authority;
- replay fragmentation.

Allowed work:

- canonical facade over existing provider/resource registries;
- schema normalization;
- capability taxonomy extension;
- production provider selection policy;
- unified replay bundle;
- natural-language lifecycle command contract;
- provider family certification packs.

## 13. Platform Core Integration Assessment

The External Provider Platform is already integrated with Platform Core concepts:

- PGSP for session invocation;
- UBTR/CSA for semantic intent before routing;
- OCS for orchestration and proposal formation;
- Governance for admissibility and checkpoints;
- UHCL for human-facing summaries and recovery;
- Replay for evidence reconstruction;
- credential vault for secret-free credential lifecycle;
- Worker Services for separate execution identities;
- provider connectors for external handoff boundaries.

The missing piece is not architectural presence. The missing piece is canonical consolidation.

## 14. Production Readiness Assessment

| Area | Current Readiness | Production Requirement |
| --- | --- | --- |
| LLM cognition provider execution | Bounded ready | Production certification package required. |
| Generic external API provider | Partial | Generic API contract, credential binding, transport policy. |
| Hybrid provider/Worker resources | Partial | Stronger role separation and authorization binding. |
| Provider lifecycle management | Partial | Canonical lifecycle state machine. |
| Provider registry | Partial | Facade over existing registries and source-of-truth declaration. |
| Provider selection | Partial | Production selection policy. |
| Multi-provider operation | Partial | Failover/retry/selection governance. |
| Arbitrary enterprise systems | Architectural placeholder | Domain-specific connector and governance packs. |
| Natural-language provider management | Partial | PGSP/UHCL normalized command contract. |

Production readiness determination:

```text
EXTERNAL_PROVIDER_PLATFORM_FOUNDATION_READY
PRODUCTION_EXTERNAL_PROVIDER_PLATFORM_REQUIRES_EXTENSION
```

## 15. Implementation Recommendation

Do not implement a new Provider Registry from scratch.

Recommended next implementation batch:

1. `G6_02_EXTERNAL_PROVIDER_PLATFORM_CANONICAL_FACADE_AND_REGISTRY_NORMALIZATION_V1`
2. `G6_03_EXTERNAL_PROVIDER_CAPABILITY_AND_ROLE_TAXONOMY_V1`
3. `G6_04_EXTERNAL_PROVIDER_LIFECYCLE_AND_ATTACHMENT_CONTRACT_V1`
4. `G6_05_EXTERNAL_PROVIDER_SELECTION_POLICY_AND_ROUTING_GOVERNANCE_V1`
5. `G6_06_EXTERNAL_PROVIDER_REPLAY_BUNDLE_AND_CERTIFICATION_PACKET_V1`
6. `G6_07_NATURAL_LANGUAGE_PROVIDER_LIFECYCLE_PGSP_CONTRACT_V1`

Implementation rules:

- reuse existing registries;
- preserve passive registry boundaries;
- keep OCS/PGSP responsible for orchestration;
- keep UHCL responsible for communication;
- keep credential vault secret-free;
- keep replay append-only;
- do not merge provider, Worker, and connector identities;
- do not enable fallback, retry, or production dispatch without separate certification.

## 16. Final Determination

A canonical External Provider Platform foundation already exists, but it is distributed and not yet production-normalized for arbitrary external systems.

New provider architecture would duplicate existing Platform Core capabilities.

The correct path is reuse plus targeted extension.

Final verdict: EXTERNAL_PROVIDER_PLATFORM_EXTENSION_REQUIRED
