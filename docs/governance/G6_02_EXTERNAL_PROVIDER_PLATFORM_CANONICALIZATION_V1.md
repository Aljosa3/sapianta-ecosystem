# G6-02 External Provider Platform Canonicalization V1

Status: canonical architecture defined.

Final verdict: EXTERNAL_PROVIDER_PLATFORM_CANONICAL_READY

## 1. Purpose

G6-02 defines the canonical External Provider Platform architecture by consolidating existing provider abstractions into one Platform Core model.

This is a documentation and canonicalization milestone only. It does not introduce runtime changes, provider execution, Worker execution, repository mutation, deployment, approval creation, authorization creation, retry, fallback, or tests.

The objective is to prevent duplicate Provider Services architecture while preserving existing certified runtime behavior.

## 2. Canonical Determination

The canonical Platform Core abstraction is:

```text
EPP - External Provider Platform
```

EPP is the Platform Core capability for representing, attaching, governing, selecting, invoking, replaying, and certifying external systems.

EPP is broader than LLM cognition providers. It covers:

- LLM cognition providers;
- translation providers;
- repair providers;
- external API providers;
- file and storage providers;
- search providers;
- monitoring providers;
- database providers;
- ERP and CRM providers;
- payment providers;
- authentication providers;
- hybrid provider/Worker resources;
- future governed external systems.

EPP is not a new runtime layer. It is the canonical name and consolidation model for existing provider, connector, transport, resource selection, credential, replay, and governance surfaces.

## 3. Canonical Architecture

The canonical EPP architecture is:

```text
Human request
-> Interface Adapter
-> PGSP session
-> UBTR translation
-> CSA provider/service intent
-> OCS orchestration and provider selection request
-> Governance admissibility checkpoint
-> EPP registry and identity lookup
-> EPP credential boundary
-> EPP connector or transport boundary
-> external provider interaction or attachment
-> EPP response/error evidence
-> Replay reconstruction
-> UHCL review summary
-> OCS proposal or execution pipeline continuation
```

EPP does not replace PGSP, UBTR, CSA, OCS, Governance, UHCL, Replay, Provider Services, Worker Services, or adapters.

EPP consolidates the external-provider-facing surfaces those layers already use.

## 4. Canonical Components

| EPP Component | Canonical Role | Existing Surfaces |
| --- | --- | --- |
| External Provider Identity | Stable identity, role, capability, lifecycle, trust, credential reference, authority flags. | `sapianta_bridge/providers/provider_identity.py`, `aigol/provider/provider_registry.py`, G5 provider identity artifacts, ERR resources, unified resource selection resources. |
| External Provider Registry | Passive metadata registry and source for provider/resource lookup. | `sapianta_bridge/providers/provider_registry.py`, `aigol/provider/provider_registry.py`, `external_resource_registry_runtime.py`, `unified_resource_selection_runtime.py`. |
| External Provider Capability Model | Capability declarations, role bindings, domain scope, and authority profile. | ERR capabilities, unified resource role bindings, provider contracts, provider catalogs. |
| External Provider Connector | Artifact handoff contract between Platform Core and provider-facing interface. | `sapianta_bridge/provider_connectors/`, `aigol/runtime/provider_attachment.py`. |
| External Provider Transport | Bounded communication substrate and request/response/error evidence. | `sapianta_bridge/real_provider_transport/`, `aigol/runtime/live_provider_http_transport.py`, `aigol/runtime/providers/`. |
| Credential Boundary | Secret-free credential reference, lifecycle, retrieval attempt, diagnostics, rotation/disable/delete evidence. | `aigol/runtime/provider_credential_vault.py`, provider governance credential diagnostics. |
| Provider Selection Policy | Governed selection over capability, role, lifecycle, trust, health, credential state, and replay. | ERR selection, unified resource selection, provider necessity policy, OCS cognition routing. |
| Provider Attachment Lifecycle | Attach, validate, certify, enable, suspend, rotate credential, recertify, disable, remove, archive. | Provider attachment, natural-language onboarding certification, provider governance events, credential vault lifecycle. |
| Provider Replay Bundle | Unified replay references across identity, registry, selection, credential, connector, transport, response/error, and review. | Existing replay functions across G5 provider, ERR, transport, connector, attachment, governance, and vault runtimes. |
| Provider Communication | Human-facing review, explanation, confirmation, and recovery guidance. | UHCL provider cognition review and provider onboarding summaries. |

## 5. Ownership Matrix

| Capability | Canonical Owner | Boundary |
| --- | --- | --- |
| EPP architecture | Platform Core / Provider Services | Consolidates external-provider-facing surfaces. |
| Provider identity | Provider Services | Does not grant authority. |
| Provider registry | Provider Services / External Resource Registry | Passive metadata; no orchestration. |
| Provider selection | OCS under Governance | Uses registry/resource metadata; does not live inside registry. |
| Provider credentials | Credential vault / Provider Services | Secret-free replay; governed lifecycle. |
| Connector model | EPP connectors | Artifact handoff only; not routing or orchestration. |
| Transport model | EPP transport | Communication evidence only; not execution authority. |
| Governance | Governance | Admissibility, authority, lifecycle, fail-closed checks. |
| Replay | Replay | Reconstruction and evidence continuity. |
| Human communication | UHCL | Reusable summaries, explanations, recovery guidance. |
| Session invocation | PGSP | Calls EPP through certified Platform Core flow. |
| Translation | UBTR | Translates human provider intent; no provider-specific translator. |
| Canonical semantic intent | CSA | Represents provider/service intent before orchestration. |
| Interface rendering | ACLI, Web, REST, Voice, Mobile, future adapters | Render only; do not own EPP semantics. |
| Worker execution | Worker Services | Separate identity and authorization boundary. |

## 6. Capability Matrix

| Capability | Canonical Status | Migration Requirement |
| --- | --- | --- |
| Provider abstraction | Canonicalized as EPP Provider Identity and EPP Provider Contract. | Alias existing provider abstraction docs to EPP. |
| Connector model | Canonicalized as EPP Connector. | Preserve `CONNECTOR != ORCHESTRATION`. |
| Transport model | Canonicalized as EPP Transport. | Preserve `TRANSPORT_ARTIFACT != EXECUTION_AUTHORITY`. |
| Credential vault integration | Canonicalized as EPP Credential Boundary. | Bind vault lifecycle state into future dispatch certification. |
| Provider identity | Canonicalized as EPP External Provider Identity. | Add facade over existing identity schemas. |
| Provider attachment lifecycle | Canonicalized as EPP Attachment Lifecycle. | Define lifecycle state names without changing existing artifacts. |
| Unified resource selection | Canonicalized as EPP Selection input plus OCS/Governance selection policy. | Keep registries passive; selection remains governed. |
| Governance integration | Canonicalized as EPP Governance Checkpoint. | Reuse provider governance and G5 checkpoints. |
| Replay integration | Canonicalized as EPP Replay Bundle. | Add bundle index over existing replay references. |
| PGSP integration | Canonicalized as PGSP-to-EPP invocation contract. | Reuse G5 live provider entrypoint. |
| UBTR integration | Canonicalized as provider lifecycle/usage intent translated through UBTR. | No provider-specific translators. |
| Natural-language onboarding | Canonicalized as PGSP provider lifecycle intent. | Extend existing onboarding certification into PGSP contract. |
| Certification lifecycle | Canonicalized as EPP Certification Packet. | Consolidate existing certification slices. |

## 7. Terminology Alignment

Canonical names:

| Canonical Term | Meaning | Compatibility Aliases |
| --- | --- | --- |
| External Provider Platform or EPP | Canonical Platform Core umbrella for external systems. | Provider Services, provider abstraction substrate, external resource platform. |
| External Provider | Any governed external system represented in EPP. | Provider, resource, external resource, connector target. |
| EPP Provider Identity | Canonical identity for one external system role. | provider metadata, provider identity artifact, ERR resource, unified resource. |
| EPP Registry | Passive metadata registry of external providers/resources. | provider registry, ERR registry, resource registry. |
| EPP Selection Policy | Governed OCS/Governance policy for choosing a provider/resource. | resource selection, provider routing, capability matching. |
| EPP Connector | Artifact handoff boundary to a provider-facing interface. | provider connector, attachment connector, bounded connector. |
| EPP Transport | Bounded request/response/error communication substrate. | real provider transport, live provider HTTP transport. |
| EPP Credential Boundary | Secret-free credential lifecycle and retrieval boundary. | provider credential vault, credential policy, credential diagnostic. |
| EPP Attachment | Provider output or interaction attached as governed evidence. | provider attachment, external LLM attachment, runtime attachment. |
| EPP Replay Bundle | Reconstruction package linking provider identity, selection, credential, transport, response, and review evidence. | provider replay, transport audit, connector evidence, G5 provider replay. |
| EPP Certification Packet | Production readiness and renewal artifact for a provider family or concrete provider. | provider certification report, readiness audit, certification package. |

Terminology constraints:

- `Provider Registry` must not imply routing authority.
- `Provider Connector` must not imply orchestration authority.
- `Provider Transport` must not imply execution authority.
- `Provider Response` must not imply governance decision.
- `Provider Identity` must not imply authorization.
- `Provider Selection` must remain governed by OCS/Governance.

## 8. Compatibility Strategy

Existing runtime names remain valid.

Compatibility aliases should be documented rather than forced through immediate code renames:

- `Provider Services` remains valid for provider-owned runtime capabilities.
- `External Resource Registry` remains valid for passive capability/resource lookup.
- `Unified Resource Selection` remains valid for current selection runtime.
- `provider_connectors` remains valid for connector implementation modules.
- `real_provider_transport` remains valid for transport implementation modules.
- G5 provider cognition runtimes remain valid as EPP cognition specializations.

Near-term code changes should be facade additions only, if needed.

No existing certified runtime should be renamed or moved solely for terminology.

## 9. Migration Strategy

Migration is documentation-first and compatibility-first.

Recommended migration phases:

1. Declare EPP canonical terminology in governance artifacts.
2. Add an EPP compatibility index that maps existing provider/resource/connector/transport modules to canonical EPP concepts.
3. Define EPP Provider Identity facade over existing provider metadata, ERR resources, unified resources, and G5 provider identity artifacts.
4. Define EPP Replay Bundle as an index over existing replay references.
5. Define EPP Selection Policy without moving selection into registries.
6. Extend provider onboarding natural-language flow into a PGSP EPP lifecycle contract.
7. Certify provider family packs for LLM cognition, external API, file service, search, database, ERP, CRM, payment, authentication, storage, and monitoring providers as needed.

Migration non-goals:

- no new Provider Registry from scratch;
- no registry-owned orchestration;
- no connector-owned routing;
- no transport-owned execution authority;
- no provider-specific UBTR translators;
- no autonomous fallback or retry without certification.

## 10. Production Readiness

EPP canonical architecture is ready.

Production EPP certification still requires:

- canonical EPP facade or index;
- external provider identity schema mapping;
- lifecycle state machine;
- selection policy;
- credential dispatch binding;
- replay bundle;
- certification packet;
- natural-language PGSP lifecycle contract;
- provider family-specific governance packs.

Readiness determination:

```text
EPP_CANONICAL_ARCHITECTURE_READY
EPP_PRODUCTION_CERTIFICATION_REQUIRES_IMPLEMENTATION
```

## 11. Implementation Recommendation

Recommended next implementation batch:

1. `G6_03_EPP_CANONICAL_COMPATIBILITY_INDEX_V1`
2. `G6_04_EPP_PROVIDER_IDENTITY_AND_CAPABILITY_TAXONOMY_V1`
3. `G6_05_EPP_ATTACHMENT_LIFECYCLE_AND_CREDENTIAL_BOUNDARY_V1`
4. `G6_06_EPP_SELECTION_POLICY_AND_GOVERNANCE_CHECKPOINTS_V1`
5. `G6_07_EPP_REPLAY_BUNDLE_AND_CERTIFICATION_PACKET_V1`
6. `G6_08_EPP_NATURAL_LANGUAGE_PROVIDER_LIFECYCLE_PGSP_CONTRACT_V1`

Implementation should reuse:

- existing passive provider registries;
- ERR;
- unified resource selection;
- provider credential vault;
- provider governance runtime;
- provider connectors;
- real provider transport;
- provider attachment;
- G5 provider cognition runtimes;
- natural-language provider onboarding certification.

## 12. Certification Impact

G6-02 establishes EPP as the canonical architecture name and consolidation model.

Certification impact:

- prevents duplicate Provider Registry design;
- preserves passive registry boundaries;
- preserves connector and transport non-authority boundaries;
- preserves PGSP, UBTR, CSA, OCS, Governance, UHCL, Replay ownership;
- preserves Worker identity separation;
- enables production provider certification to proceed through compatibility and extension.

## 13. Final Determination

EPP is now canonically defined as the External Provider Platform architecture.

Runtime behavior remains unchanged.

The architecture is ready for compatibility-index and production-certification implementation batches.

Final verdict: EXTERNAL_PROVIDER_PLATFORM_CANONICAL_READY
