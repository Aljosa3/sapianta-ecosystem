# G16-06 - PCCL Capability Resolution Audit

Status: CERTIFIED

Date: 2026-07-08

Milestone: G16-06

Scope: Audit-only architectural decision for PCCL capability discovery, capability resolution, knowledge reuse, functional reuse, development intent resolution, and platform service resolution. This milestone does not implement Capability Resolution, Provider Integration, Cognitive Loop, Proposal Pipeline, Prompt Generation, Provider Runtime, new Platform Services, provider invocation, worker execution, governance execution, replay mutation, or AiCLI behavior.

## Executive Decision

Platform Core already contains reusable deterministic capabilities for the responsibilities requested by G16-06:

- capability discovery and reuse policy;
- human intent to candidate capability discovery;
- development intent resolution;
- project knowledge reuse and contextual task mapping;
- capability certification metadata lookup;
- capability audit, normalization, and delta evidence;
- role-scoped resource selection for provider and worker resources;
- domain and worker resolution for explicit domain and worker family identifiers.

PCCL must reuse these existing Platform Core capabilities. It must not introduce a new independent Capability Resolution service.

The only future gap is a thin PCCL integration binding: a deterministic reference artifact that can attach existing capability discovery, knowledge reuse, certification registry, and resource-selection references to a PCCL session, context envelope, and policy envelope. That future artifact must be reference-only and must not perform semantic interpretation, capability discovery, provider selection, governance, replay, provider invocation, worker execution, or certification.

## Knowledge Reuse Audit

G16-06 reviewed existing implementation and governance surfaces before any capability-resolution implementation was considered.

Reviewed implementation surfaces:

- `aigol/runtime/platform_core_project_services.py`
- `aigol/runtime/platform_core_capability_lookup.py`
- `aigol/runtime/platform_capability_certification_registry.py`
- `aigol/runtime/capability_audit_runtime.py`
- `aigol/runtime/capability_normalization_runtime.py`
- `aigol/runtime/capability_delta_runtime.py`
- `aigol/runtime/unified_resource_selection_runtime.py`
- `aigol/runtime/domain_and_worker_resolution_registry.py`
- `aigol/runtime/external_resource_registry_runtime.py`
- `aigol/runtime/conversation_native_development_intent_routing.py`
- `aigol/runtime/intent_routing_attachment.py`
- `aigol/runtime/governance_resolution_strategy.py`
- `aigol/runtime/replay_resolution_strategy.py`
- `aigol/runtime/constitutional_memory_resolution_strategy.py`
- `aigol/runtime/resolution_strategy_runtime.py`
- `aigol/runtime/ocs_semantic_resolution_runtime.py`
- `aigol/runtime/improvement_intent_cognition_routing_runtime.py`
- `aigol/runtime/replay_derived_intent_resource_selection_routing_runtime.py`
- `aigol/runtime/clarified_intent_resource_selection_routing_runtime.py`
- `aigol/runtime/read_only_capability_attachment.py`
- `aigol/runtime/capabilities/`
- `aigol/provider/provider_registry.py`

Reviewed governance evidence:

- `docs/governance/G6_05_PLATFORM_CAPABILITY_DISCOVERY_AND_REUSE_POLICY_V1.md`
- `docs/governance/G14_08_PROJECT_KNOWLEDGE_REUSE_AND_CONTEXTUAL_TASK_MAPPING_V1.md`
- `docs/governance/G14_08A_PLATFORM_CORE_PROJECT_SERVICES_EXTRACTION_V1.md`
- `docs/governance/G14_19_CANONICAL_DEVELOPMENT_INTENT_RESOLUTION_UNIFICATION_V1.md`
- `docs/governance/G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1.md`
- `docs/governance/G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY.md`
- `docs/governance/G15_ARCH_02_CANONICAL_GOVERNED_DEVELOPMENT_WORKFLOW.md`
- `docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md`
- `docs/governance/G16_04_CANONICAL_POLICY_ENVELOPE.md`
- `docs/governance/G16_05_PCCL_PROVIDER_INTEGRATION_AUDIT.md`

## Architecture Review

Ownership remains unchanged:

- Platform Core Project Services owns human intent resolution, deterministic candidate capability discovery, clarification planning, project context, project guidance, and knowledge reuse evidence.
- Platform Core Certification Registry owns certification metadata lookup only.
- Platform Core Replay owns replay evidence and certification.
- Platform Core Governance owns policy and authorization decisions.
- Platform Core Runtime owns runtime entry, runtime continuation, and workflow completion.
- Provider Platform owns provider registry, provider attachment, provider invocation, and provider replay evidence.
- Worker Platform owns worker execution.
- PCCL owns cognition orchestration state, PCCL session lifecycle, context envelope references, policy envelope references, and future proposal lifecycle references.

PCCL does not own:

- semantic interpretation;
- Human Intent Resolution;
- capability discovery;
- clarification;
- knowledge reuse classification;
- governance;
- provider selection;
- provider invocation;
- worker execution;
- replay;
- certification.

Generation 14 boundaries are preserved because this audit does not move existing Platform Core authority into PCCL. PCCL is a consumer of existing deterministic artifacts, not a replacement owner.

## Existing Capability Inventory

### Capability Discovery And Reuse Policy

File:

- `docs/governance/G6_05_PLATFORM_CAPABILITY_DISCOVERY_AND_REUSE_POLICY_V1.md`

Component:

- Mandatory Platform Capability Discovery and Reuse Policy.

Ownership:

- Platform Core governance architecture.

Current usage:

- Required pre-implementation audit discipline for proposed new subsystems, runtimes, facades, provider layers, worker layers, governance mechanisms, replay mechanisms, and execution paths.

Certification status:

- Canonical discovery and reuse policy defined; final verdict `PLATFORM_CAPABILITY_DISCOVERY_POLICY_READY`.

Limitations:

- Documentation-only. It does not execute capability lookup, route runtime behavior, or produce session artifacts.

PCCL reuse decision:

- Reuse as the architectural control requiring PCCL to audit existing capabilities before introducing new services.

### Human Intent To Capability Resolution

Files:

- `aigol/runtime/platform_core_project_services.py`
- `docs/governance/G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1.md`

Components:

- `discover_candidate_capabilities(...)`
- `resolve_development_intent(...)`
- candidate capability discovery artifact.

Ownership:

- Platform Core Project Services / Human Intent Resolution.

Current usage:

- Infers candidate Platform Core capabilities from deterministic keyword, workspace, active objective, and certified-artifact evidence.
- Produces `candidate_capability_discovery`, `candidate_capabilities`, `selected_goal_target`, and `capability_resolution_decision`.
- Feeds Knowledge Reuse before clarification.

Certification status:

- G14-47 certified Human Intent to Capability Resolution.

Limitations:

- Development-request oriented.
- It does not select providers, invoke workers, evaluate policy, or certify replay.
- It is not a general PCCL orchestration service.

PCCL reuse decision:

- Reuse unchanged for human-goal-to-candidate-capability evidence.
- PCCL must not duplicate this inference.

### Development Intent Resolution

Files:

- `aigol/runtime/platform_core_project_services.py`
- `docs/governance/G14_19_CANONICAL_DEVELOPMENT_INTENT_RESOLUTION_UNIFICATION_V1.md`
- `docs/governance/G15_ARCH_02_CANONICAL_GOVERNED_DEVELOPMENT_WORKFLOW.md`

Component:

- `resolve_development_intent(...)`

Ownership:

- Platform Core Project Services / Human Intent Resolution.

Current usage:

- Produces deterministic development intent resolution, admissibility flags, goal mapping, governed request, clarification decision, runtime-binding admissibility, and replay-visible artifact hash.

Certification status:

- G14-19 and G15 canonical governed development workflow evidence.

Limitations:

- Owns semantic and development-intent resolution for governed development requests.
- It is not PCCL-specific and should not be moved into PCCL.

PCCL reuse decision:

- PCCL may consume development intent resolution references through context and future integration artifacts.
- PCCL must not perform development intent resolution.

### Project Knowledge Reuse And Contextual Task Mapping

Files:

- `aigol/runtime/platform_core_project_services.py`
- `docs/governance/G14_08_PROJECT_KNOWLEDGE_REUSE_AND_CONTEXTUAL_TASK_MAPPING_V1.md`
- `docs/governance/G14_08A_PLATFORM_CORE_PROJECT_SERVICES_EXTRACTION_V1.md`

Components:

- `project_knowledge_context_from_workspace(...)`
- project knowledge index.
- knowledge reuse evidence selection.

Ownership:

- Platform Core Project Services.

Current usage:

- Classifies work as `RELATES_TO_CERTIFIED_CAPABILITY`, `ALREADY_SATISFIED`, `MODIFIES_EXISTING_CAPABILITY`, `EXTENDS_EXISTING_MILESTONE`, or `NEW_GOVERNED_WORK`.
- Records certified artifacts, related milestones, implementation history matches, reuse recommendation, duplicate-work avoidance, and evidence-selection authority.

Certification status:

- G14-08 certified Project Knowledge Reuse.
- G14-08A extracted Platform Core Project Services authority.

Limitations:

- Project-goal and workspace oriented.
- It does not implement provider runtime, policy evaluation, worker execution, replay certification, or PCCL lifecycle.

PCCL reuse decision:

- Reuse unchanged for deterministic functional reuse and existing capability selection evidence.
- PCCL must not create separate knowledge reuse logic.

### Platform Capability Certification Registry

Files:

- `aigol/runtime/platform_capability_certification_registry.py`
- `docs/governance/G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY.md`

Components:

- `platform_capability_certification_registry()`
- `list_platform_capability_certifications()`
- `lookup_platform_capability_certification(...)`
- `is_platform_capability_certified(...)`
- owner, milestone, evidence, and scope lookup helpers.

Ownership:

- Platform Core certification metadata.

Current usage:

- Indexes certified and verified Platform Core capability records.
- Records evidence paths, owner, implementation owner, certification milestone, scope, status, and authority-denial flags.

Certification status:

- G15-GOVERNANCE-01 certified registry capability.
- Current registry includes certified PCCL foundation, PCCL session runtime, context envelope, and policy envelope records.

Limitations:

- Metadata-only.
- It explicitly does not grant runtime authority, human-interface authority, provider invocation, worker invocation, replay mutation, or governance mutation.
- It indexes evidence but does not replace governance reports or replay evidence.

PCCL reuse decision:

- Reuse as the certification metadata source.
- PCCL must not treat certification lookup as authorization or execution approval.

### Platform Core Capability Lookup

File:

- `aigol/runtime/platform_core_capability_lookup.py`

Component:

- `lookup_readonly_worker_capability(...)`

Ownership:

- Platform Core read-only worker capability lookup for G8 preview surfaces.

Current usage:

- Maps supported read-only capability identifiers to worker metadata for replay inspection, validation summary, and canonical mapping lookup.

Certification status:

- Existing G8 helper. No G16 PCCL certification authority identified.

Limitations:

- Narrow read-only worker capability lookup.
- Not a general capability resolution system.

PCCL reuse decision:

- Reuse only if future PCCL surfaces need these specific read-only worker descriptions.
- Do not elevate it into PCCL capability resolution authority.

### Capability Audit Runtime

File:

- `aigol/runtime/capability_audit_runtime.py`

Components:

- `run_capability_audit(...)`
- `detect_capabilities(...)`
- `build_capability_matrix(...)`

Ownership:

- AiGOL capability audit tooling under Platform Core governance evidence.

Current usage:

- Scans governance, runtime, and test artifacts.
- Builds replay-visible capability matrix, audit document, roadmap, and summary artifacts.

Certification status:

- Existing deterministic audit runtime. It is evidence tooling, not a PCCL service owner.

Limitations:

- Repository-evidence scanner.
- It does not resolve live human intent, bind PCCL sessions, select resources, govern execution, or certify replay.

PCCL reuse decision:

- Reuse for broad capability inventory and maturity evidence.
- Do not use as a live PCCL runtime resolver.

### Capability Normalization Runtime

File:

- `aigol/runtime/capability_normalization_runtime.py`

Components:

- `normalize_capability_identity(...)`
- `normalize_capability_matrix(...)`
- `run_capability_normalization(...)`

Ownership:

- AiGOL capability audit normalization tooling.

Current usage:

- Normalizes raw capability keys into stable capability identifiers and collapses duplicate capability groups in audit matrices.

Certification status:

- Existing deterministic audit normalization runtime.

Limitations:

- Matrix normalization only.
- Does not perform semantic interpretation, knowledge reuse, or runtime routing.

PCCL reuse decision:

- Reuse as audit-supporting identity normalization where needed.
- Do not treat normalization as capability resolution.

### Capability Delta Runtime

File:

- `aigol/runtime/capability_delta_runtime.py`

Components:

- `run_capability_delta(...)`
- `compute_capability_delta(...)`

Ownership:

- AiGOL capability audit evidence tooling.

Current usage:

- Compares capability audit matrices and emits added, removed, status, maturity, and layer-score deltas.

Certification status:

- Existing deterministic delta runtime.

Limitations:

- Historical audit comparison only.
- It does not resolve which capability a PCCL session should use.

PCCL reuse decision:

- Reuse for longitudinal capability evidence.
- Do not make it a PCCL runtime dependency unless a future audit milestone requires it.

### Unified Resource Selection Runtime

File:

- `aigol/runtime/unified_resource_selection_runtime.py`

Components:

- `default_resource_registry()`
- `select_unified_resource(...)`

Ownership:

- Platform Core resource selection for provider, worker, operator tool, governance runtime, and domain runtime roles.

Current usage:

- Matches explicit `required_capability`, `requested_role_type`, domain, trust level, authority profile, provider necessity classification, and worker authorization requirements to an eligible resource.
- Records replay-visible selection artifacts.
- Explicitly does not invoke providers or workers.

Certification status:

- Existing deterministic resource-selection runtime and part of the G16-05 provider integration decision.

Limitations:

- Resource and role selection only.
- It requires explicit capability and role inputs.
- It does not infer human goals, evaluate policy, authorize execution, or run providers/workers.

PCCL reuse decision:

- Reuse for future provider or worker resource selection after PCCL consumes existing capability and policy references.
- PCCL must not create a parallel provider or worker selector.

### Domain And Worker Resolution Registry

File:

- `aigol/runtime/domain_and_worker_resolution_registry.py`

Components:

- `default_domain_worker_registry()`
- `resolve_domain_worker_milestone(...)`

Ownership:

- Platform Core domain and worker family resolution registry.

Current usage:

- Resolves explicit domain, worker family, and milestone type identifiers without semantic interpretation.
- Records deterministic replay steps.

Certification status:

- Existing deterministic domain and worker resolution registry.

Limitations:

- Explicit identifier resolution only.
- Not a semantic capability resolver.

PCCL reuse decision:

- Reuse for future PCCL references that already have explicit domain and worker identifiers.
- Do not use it to infer capability intent.

### Resolution Strategy Runtimes

Files:

- `aigol/runtime/governance_resolution_strategy.py`
- `aigol/runtime/replay_resolution_strategy.py`
- `aigol/runtime/constitutional_memory_resolution_strategy.py`
- `aigol/runtime/resolution_strategy_runtime.py`
- `aigol/runtime/ocs_semantic_resolution_runtime.py`

Ownership:

- Platform Core domain-specific resolution and strategy evidence.

Current usage:

- Provide bounded resolution behavior for governance, replay, constitutional memory, and OCS semantic surfaces.

Certification status:

- Existing runtime surfaces. G16-06 found them relevant as domain-specific resolution capabilities, not as a general PCCL capability resolver.

Limitations:

- Domain-specific.
- They do not own cross-platform capability discovery or PCCL lifecycle.

PCCL reuse decision:

- Reuse only when a future PCCL artifact needs references from the specific owner.
- Do not centralize their responsibilities inside PCCL.

### Provider Registry And Provider Capability Metadata

Files:

- `aigol/provider/provider_registry.py`
- `docs/governance/G16_05_PCCL_PROVIDER_INTEGRATION_AUDIT.md`

Ownership:

- Provider Platform.

Current usage:

- Provider metadata registration and lookup.
- Provider capability metadata participates in provider integration and resource selection.

Certification status:

- Provider Platform operational completion is certified by Generation 14 evidence.
- G16-05 certified the decision that PCCL must reuse existing provider capabilities instead of creating a new Provider Runtime.

Limitations:

- Provider-specific.
- Does not own Platform Core semantic resolution, knowledge reuse, governance, replay, or PCCL orchestration.

PCCL reuse decision:

- Reuse through Provider Platform and unified resource selection only.
- PCCL must not directly own provider capability metadata.

## Gap Analysis

Already reusable by PCCL:

- Human Intent to Capability Resolution through Platform Core Project Services.
- Development Intent Resolution through Platform Core Project Services.
- Knowledge Reuse and Contextual Task Mapping through Platform Core Project Services.
- Certification metadata through Platform Capability Certification Registry.
- Provider and worker role matching through Unified Resource Selection Runtime.
- Explicit domain and worker identifier resolution through Domain and Worker Resolution Registry.
- Capability audit, normalization, and delta evidence for governance inventory reports.

Reusable with a thin integration layer:

- PCCL session, context envelope, and policy envelope can carry references to existing capability discovery artifacts, knowledge reuse artifacts, certification records, resource-selection artifacts, domain-worker resolution artifacts, replay references, and governance references.
- The thin layer must be an integration binding only. It should normalize references, verify required fields are present, and preserve ownership metadata.

Genuinely missing deterministic capability:

- No standalone PCCL-specific capability resolution service is missing.
- The only missing future surface is a PCCL Capability Resolution Binding artifact that references existing Platform Core outputs for a PCCL session. This is not a new resolver and should not be implemented until a later integration milestone explicitly requires it.

## Reuse Recommendations

PCCL should reuse:

1. `discover_candidate_capabilities(...)` for deterministic human-goal candidate capability evidence.
2. `resolve_development_intent(...)` for existing Human Intent Resolution and development intent artifacts.
3. `project_knowledge_context_from_workspace(...)` for knowledge reuse classification and functional reuse evidence.
4. `list_platform_capability_certifications(...)` and `lookup_platform_capability_certification(...)` for certification metadata references.
5. `select_unified_resource(...)` for future provider or worker resource selection after capability and policy inputs are already explicit.
6. `resolve_domain_worker_milestone(...)` for explicit domain and worker milestone references.
7. Capability audit, normalization, and delta runtimes for governance inventory reports, not live PCCL orchestration.

PCCL should not:

- infer capability intent independently;
- classify knowledge reuse independently;
- create a new capability catalog;
- create a new provider runtime;
- select providers independently;
- invoke providers;
- authorize workers;
- evaluate governance;
- certify replay;
- use audit matrices as runtime authority.

## Integration Recommendations

Recommended future sequence:

1. Define a PCCL Capability Resolution Binding artifact that attaches existing capability discovery, knowledge reuse, certification registry, context envelope, policy envelope, and PCCL session references.
2. Keep the binding reference-only and replay-visible.
3. Require all capability identity and certification fields to cite existing Platform Core records.
4. Require provider or worker resource choices to cite Unified Resource Selection artifacts.
5. Require policy constraints to cite Canonical Policy Envelope references.
6. Require context inputs to cite Canonical Context Envelope references.
7. Fail closed when required references are missing or owner metadata conflicts.
8. Do not add provider invocation, prompt generation, proposal generation, policy evaluation, comparison, cognitive loop control, worker execution, replay certification, or governance execution to the binding.

## Architectural Health Assessment

Duplication risk:

- High if PCCL implements its own capability discovery, capability catalog, knowledge reuse classifier, provider selector, or certification lookup.
- Low if PCCL consumes existing Platform Core artifacts by reference.

Ownership violation risk:

- PCCL-owned capability resolution would violate Platform Core Project Services and Human Intent Resolution ownership.
- PCCL-owned provider capability selection would duplicate Provider Platform and Unified Resource Selection.
- PCCL-owned certification decisions would violate Certification Registry and Replay/Governance boundaries.

Replay risk:

- Creating a new resolver could fragment replay evidence.
- Reference-only integration preserves existing replay authority.

Future risk:

- Future PCCL milestones may be tempted to combine context, policy, capability, and provider selection into one cognitive orchestration runtime.
- That should be rejected unless each referenced artifact remains owner-bound and replay-visible.

Overall health:

- Existing Platform Core capability resolution and reuse surfaces are sufficient for PCCL consumption.
- The architecture is healthier if PCCL remains an orchestration consumer of existing deterministic artifacts rather than becoming a second semantic or capability-resolution owner.

## Certification Verdict

CERTIFIED

G16-06 certifies that PCCL can reuse existing Platform Core capability discovery, development intent resolution, knowledge reuse, certification metadata, resource selection, and domain-worker resolution capabilities.

No new PCCL Capability Resolution service is authorized by this audit.

Future implementation, if required, should be limited to a deterministic PCCL Capability Resolution Binding artifact that references existing Platform Core outputs without taking ownership of their behavior.

## Validation Summary

Validation performed:

- `git diff --check`

Result:

- Passed.
