# G19-01 Platform Knowledge Runtime Audit

Status: AUDIT COMPLETE

Date: 2026-07-11

Scope: Architectural audit of whether Platform Knowledge already exists in distributed Platform Core capabilities and whether a future Platform Knowledge Runtime can be implemented as a deterministic composition layer. This audit does not implement a new runtime, registry, replay structure, governance mechanism, provider path, worker path, Human Interface behavior, or Root Cause Trace behavior.

## Executive Summary

Platform Knowledge already exists in distributed form across Platform Core.

The strongest existing foundations are:

- the Platform Capability Certification Registry;
- Platform Core Project Services;
- Project Knowledge Reuse and contextual task mapping;
- Human Intent to Capability Resolution;
- PCCL reference binding and decision records;
- governance certification reports;
- replay and workspace metadata where architecture evidence needs replay-visible continuity.

The platform already answers most required architectural questions in separate, deterministic places:

| Question | Existing answer source |
| --- | --- |
| Does this capability already exist? | `discover_candidate_capabilities(...)`, `project_knowledge_context_from_workspace(...)`, certification registry lookup |
| Where is it implemented? | `implementation_owner` in certification registry records |
| Which implementation is canonical? | certification registry status, milestone, evidence, component owner |
| Who owns it? | `capability_owner`, `architectural_owner`, Project Services authority fields, PCCL owner maps |
| Is it certified? | `is_platform_capability_certified(...)`, certification status and scope |
| Can it be reused? | Knowledge Reuse classification and `reuse_recommended` |
| Which service should be reused? | certification registry owner/component metadata, Project Services goal mapping, PCCL reference types |

The missing piece is not a new knowledge system. The missing piece is a small, deterministic Platform Knowledge Runtime that composes existing read-only evidence into one canonical query result.

Platform Knowledge must remain separate from Deterministic Root Cause Trace:

- Platform Knowledge answers: "What does the platform already know?"
- Root Cause Trace answers: "Why did this runtime result occur?"

Final recommendation: implement a first-class Platform Core Platform Knowledge Runtime as a thin, read-only composition layer.

Final verdict: `PLATFORM_KNOWLEDGE_RUNTIME_REUSE_WITH_MINIMAL_COMPOSITION_BINDING`.

## Current Platform Knowledge Architecture

Current Platform Knowledge is distributed rather than centralized.

Existing Platform Core components already hold architectural knowledge:

- `aigol/runtime/platform_capability_certification_registry.py` holds certification, owner, implementation, milestone, and evidence metadata for certified Platform Core capabilities.
- `aigol/runtime/platform_core_project_services.py` holds project workspace, guidance, goal mapping, capability discovery, knowledge reuse, and contextual task mapping.
- `aigol/runtime/platform_core_cognition_layer.py` holds PCCL reference and evidence-binding structures that can point to existing services without duplicating their authority.
- `docs/governance/*.md` reports remain authoritative certification and architectural evidence.
- replay-visible workspace state records preserve implementation history, known goal targets, certified artifacts by target, and recent governed decisions.

This is already a deterministic architectural knowledge substrate. It is not yet a single query runtime.

## Inventory Of Reusable Platform Core Capabilities

| Capability | Current owner | Current responsibility | Public interfaces | Evidence produced | Certification status | Reuse readiness |
| --- | --- | --- | --- | --- | --- | --- |
| Platform Capability Certification Registry | Platform Core Certification metadata | Read-only index over certification evidence | `platform_capability_certification_registry(...)`, `list_platform_capability_certifications(...)`, `lookup_platform_capability_certification(...)`, `is_platform_capability_certified(...)`, owner/evidence/scope helpers | Hash-stable metadata records with capability owner, implementation owner, certification evidence, scope, milestone, authority flags | G15-GOVERNANCE-01 implemented and regression-tested | High |
| Project Knowledge Reuse | Platform Core Project Services | Determine whether a request relates to existing workspace knowledge or certified artifacts | `project_knowledge_context_from_workspace(...)`, `project_knowledge_index_model(...)`, `certified_artifacts_for_goal_target(...)` | `classification`, `reuse_recommended`, certified artifacts, implementation history matches, duplicate-work evidence | G14-08 and G14-08A certified | High |
| Human Intent to Capability Resolution | Platform Core Project Services / Human Intent Resolution | Infer candidate capabilities from ordinary human language using deterministic keyword, workspace, and certified-artifact evidence | `discover_candidate_capabilities(...)`, `resolve_development_intent(...)` | candidate capability discovery artifact, selected goal target, capability resolution decision, hash | G14-47 certified | High for development-oriented architectural queries |
| Platform Core Project Context | Platform Core Project Services | Produce reusable Human Interface project context while preserving interface thinness | `prepare_unified_human_interface_project_context(...)`, `record_unified_human_interface_workspace_state(...)`, `latest_platform_core_workspace_state(...)` | UHI project context artifact, persistent workspace state, authority fields, replay references | G14-08A, G14-27, G14-38 lineage | High |
| PCCL Reference Binding | Platform Core Cognition Layer | Bind PCCL session/context/policy artifacts to existing Platform Core service references without invoking them | `create_pccl_reference_binding(...)`, `validate_pccl_reference_binding(...)` | `PCCL_REFERENCE_BINDING_ARTIFACT_V1`, source owner map, authority flags, reference-only evidence | G16-08 certified | High as a reference carrier |
| PCCL Orchestration Decision Record | Platform Core Cognition Layer | Record admissible lifecycle decision references without execution | `create_pccl_orchestration_decision_record(...)`, `validate_pccl_orchestration_decision_record(...)` | supporting evidence references, selected next lifecycle transition, non-execution flags | G16-11 certified | Medium for Platform Knowledge; useful as governance/reference evidence, not as the knowledge owner |
| Read-only capability lookup | Platform Core capability lookup | Map a small set of read-only worker capabilities to worker descriptors | `lookup_readonly_worker_capability(...)` | worker id/type/description for replay inspection, validation summary, canonical mapping lookup | Older G8 surface; referenced by G15 registry report | Medium; narrow and not sufficient as general Platform Knowledge |
| Replay Observation / Replay Certification | Platform Core Replay | Normalize and certify replay evidence | replay observation and certification runtimes | replay observations, certification records, replay hashes | G15 certified | Medium; useful for evidence continuity, not primary architectural knowledge |
| Deterministic Root Cause Trace | Platform Core Replay diagnostics | Explain runtime results from replay evidence | `aigol.runtime.platform_core_root_cause_trace` after G18-09 | root-cause trace artifacts | G18-09 implemented | Boundary evidence only; must remain separate from Platform Knowledge |

## Ownership Map

| Knowledge domain | Owner | Evidence |
| --- | --- | --- |
| Certification metadata | Platform Core Certification metadata | `CapabilityCertificationRecord`, registry helpers, G15-GOVERNANCE-01 |
| Capability discovery | Platform Core Project Services / Human Intent Resolution | `discover_candidate_capabilities(...)`, G14-47 |
| Project knowledge reuse | Platform Core Project Services | `project_knowledge_context_from_workspace(...)`, G14-08/G14-08A |
| Workspace continuity | Platform Core Project Services | `record_unified_human_interface_workspace_state(...)`, `latest_platform_core_workspace_state(...)` |
| Governance certification reports | Governance / Platform Core governance architecture | `docs/governance/*.md` evidence referenced by registry records |
| PCCL reference and decision artifacts | Platform Core Cognition Layer | G16-08 and G16-11 artifacts |
| Replay evidence and certification | Platform Core Replay | Replay Observation Layer and Replay Certification |
| Provider ownership | Provider Platform | Provider Platform records and certified provider attachment evidence |
| Worker ownership | Worker Platform | worker lifecycle and resolution evidence |
| Human Interface rendering | Human Interface | render-only; no knowledge ownership |

## Reuse Map

Platform Knowledge queries can be answered by composing existing evidence:

| Platform Knowledge query | Reused capability |
| --- | --- |
| "Does this capability already exist?" | `discover_candidate_capabilities(...)`, `project_knowledge_context_from_workspace(...)`, `lookup_platform_capability_certification(...)` |
| "Where is it implemented?" | `platform_capability_component_owner(...)` or `implementation_owner` in registry records |
| "Which implementation is canonical?" | certification registry `certification_status`, `certification_milestone`, `certification_evidence`, and `certification_record_hash` |
| "Who owns it?" | `platform_capability_owner(...)`, registry `architectural_owner`, PCCL owner maps |
| "Is it certified?" | `is_platform_capability_certified(...)`, `platform_capability_certification_scope(...)` |
| "Can it be reused?" | Knowledge Reuse `classification`, `reuse_recommended`, `duplicate_work_avoided`, `new_work_required` |
| "Which Platform Core service should be reused?" | registry `implementation_owner`, Project Services selected goal target, PCCL supported reference types |
| "What evidence supports this?" | certification evidence references, relevant certified artifacts, workspace history matches, PCCL references |

This composition is deterministic because each existing source already normalizes identifiers, records authority, hashes artifacts, or fails closed on unknown records.

## Gap Analysis

Genuine missing capabilities:

1. No single Platform Knowledge Runtime query contract exists.

   Existing services answer pieces of the question, but there is no canonical function such as `query_platform_knowledge(...)` that returns one deterministic answer envelope.

2. No unified result schema exists for architectural knowledge answers.

   A future runtime needs a stable result shape containing query text, canonical capability identifier, owner, implementation owner, certification status, certification evidence, reuse recommendation, recommended service to reuse, source references, limitations, and result hash.

3. No canonical alias bridge exists between all natural-language architecture questions and certification-registry identifiers.

   G14-47 covers development-oriented capability inference through `CAPABILITY_CATALOG`. The certification registry uses uppercase canonical capability identifiers. A Platform Knowledge Runtime needs deterministic matching between these surfaces without creating a duplicate registry.

4. No explicit precedence rule exists across distributed sources.

   The future runtime should prefer certification registry records for certified capability identity and ownership, Project Knowledge Reuse for workspace/project reuse, governance reports for architectural authority, and replay only for evidence continuity.

5. No certification packet exists for Platform Knowledge itself.

   Existing foundations are certified, but the composition runtime has not yet been implemented or certified.

Not missing:

- a new certification registry;
- a new capability registry;
- a new knowledge store;
- a new replay structure;
- a new governance authority;
- a new provider or worker selection path;
- a Root Cause Trace replacement.

## Minimal Implementation Proposal

Implement a thin read-only Platform Core service in a future milestone, for example:

```text
aigol/runtime/platform_knowledge_runtime.py
```

Candidate public interface:

```text
query_platform_knowledge(
    *,
    query: str,
    capability_identifier: str | None = None,
    goal_target: str | None = None,
    workspace_state: dict | None = None,
) -> dict
```

The runtime should compose only existing evidence:

- certification registry list and lookup helpers;
- Project Services `discover_candidate_capabilities(...)`;
- Project Services `project_knowledge_context_from_workspace(...)`;
- `certified_artifacts_for_goal_target(...)`;
- optional `latest_platform_core_workspace_state(...)`;
- PCCL reference type and owner maps when a reference-bound architectural answer is needed.

The runtime should not:

- create a new registry;
- mutate replay;
- certify replay;
- invoke providers;
- invoke workers;
- authorize governance;
- call Deterministic Root Cause Trace for architectural knowledge;
- move ownership out of existing services.

Expected output fields:

- `platform_knowledge_runtime_version`;
- `query`;
- `query_classification`;
- `canonical_capability_identifier`;
- `goal_target`;
- `capability_exists`;
- `capability_owner`;
- `architectural_owner`;
- `implementation_owner`;
- `certification_status`;
- `certification_scope`;
- `certification_evidence`;
- `reuse_recommended`;
- `reuse_reason`;
- `recommended_platform_service`;
- `source_evidence`;
- `source_precedence`;
- `unknown_or_missing_evidence`;
- boundary flags proving read-only behavior;
- deterministic `artifact_hash`.

## Recommended Platform Knowledge Runtime Architecture

Platform Knowledge should become a first-class Platform Core runtime, but only as a composition layer.

Recommended architectural properties:

- read-only;
- deterministic;
- fail-closed for malformed explicit capability identifiers;
- non-authoritative over governance, replay, provider, worker, and Human Interface behavior;
- source-cited;
- hash-stable;
- reusable by Human Interfaces, PCCL, Improvement Analysis, Governance, and future bounded autonomous services;
- separate from Root Cause Trace.

Recommended source precedence:

1. Certification registry for certified capability identity, owner, implementation owner, scope, milestone, and certification evidence.
2. Platform Core Project Services for natural-language capability discovery, workspace knowledge, reuse classification, and goal mapping.
3. Governance reports for architectural authority and certification rationale.
4. PCCL references for reference-bound service linkage and owner maps.
5. Replay/workspace metadata for continuity evidence only.

## Certification Readiness Assessment

Certification readiness is high because most required evidence sources are already implemented and certified.

Required future validation should prove:

- exact certification-registry lookup returns owner, implementation owner, status, scope, evidence, and hash;
- natural-language architecture queries are mapped through existing Project Services capability discovery, not a duplicate resolver;
- Knowledge Reuse contributes reuse recommendation and duplicate-work avoidance;
- unknown explicit capability identifiers fail closed;
- unknown free-form queries return deterministic unknown/new-work evidence rather than fabricating capability existence;
- Root Cause Trace remains separate and is not used to answer architecture inventory questions;
- Human Interfaces render Platform Knowledge answers but do not own them;
- no provider, worker, governance, replay mutation, or runtime execution authority is introduced.

## Architectural Conclusions

1. Platform Knowledge already exists substantially inside Platform Core.

   The certification registry answers certified identity, ownership, implementation location, certification state, and evidence. Project Services answer capability inference and reuse. PCCL can bind references to existing services without absorbing their authority.

2. Capability Registry and Knowledge Reuse provide most of the required functionality.

   The registry is strong for certified capability metadata. Knowledge Reuse is strong for workspace/project reuse. Human Intent to Capability Resolution bridges ordinary language to candidate capability targets.

3. Missing functionality is integration, not a new knowledge architecture.

   The platform lacks one canonical query envelope and deterministic precedence rules across existing sources.

4. Platform Knowledge should become first-class.

   A first-class runtime would let future implementation work begin with deterministic architectural queries instead of external manual audits, while preserving the existing governance-native ownership model.

5. Platform Knowledge must not become Root Cause Trace.

   Platform Knowledge may cite runtime/replay capabilities as known certified capabilities. It should not explain runtime failures or trace result causality. That remains Root Cause Trace.

## Final Recommendation

Proceed to a future implementation milestone for a minimal Platform Knowledge Runtime binding.

The implementation should be a read-only Platform Core composition layer over existing certified capabilities:

- Platform Capability Certification Registry;
- Platform Core Project Services;
- Project Knowledge Reuse;
- Human Intent to Capability Resolution;
- governance evidence references;
- PCCL reference metadata where useful.

No new registry, replay structure, provider path, worker path, governance authority, or Root Cause Trace replacement is required.

## Final Verdict

`PLATFORM_KNOWLEDGE_RUNTIME_REUSE_WITH_MINIMAL_COMPOSITION_BINDING`

The conclusion is supported by deterministic source-code evidence, regression evidence, and governance evidence:

- `aigol/runtime/platform_capability_certification_registry.py` already exposes owner, implementation, certification, scope, milestone, evidence, metadata-only authority flags, and fail-closed lookup.
- `tests/test_g15_governance_01_platform_capability_certification_registry.py` proves deterministic ordering, lookup, evidence references, metadata-only behavior, and fail-closed unknown capability handling.
- `aigol/runtime/platform_core_project_services.py` already exposes `CAPABILITY_CATALOG`, `discover_candidate_capabilities(...)`, `resolve_development_intent(...)`, `project_knowledge_context_from_workspace(...)`, `goal_mapping_from_workspace(...)`, workspace state, and certified-artifact mapping.
- `tests/test_g14_08_project_knowledge_reuse_v1.py` proves reuse classifications and deterministic workspace knowledge.
- `tests/test_g14_47_human_intent_to_capability_resolution_v1.py` proves natural-language capability inference, Knowledge Reuse integration, and Human Interface thinness.
- `aigol/runtime/platform_core_cognition_layer.py` and `docs/governance/G16_08_PCCL_REFERENCE_BINDING.md` prove reference-only service binding without duplicating capability discovery, governance, runtime, replay, provider, or worker authority.
- `docs/governance/G18_08_DETERMINISTIC_ROOT_CAUSE_TRACE_REUSE_AUDIT.md` establishes the separate Root Cause Trace boundary and confirms that replay-backed runtime causality is a different service than architectural Platform Knowledge.
