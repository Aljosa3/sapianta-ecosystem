# G19-05 Canonical Platform Presentation Layer Audit

Status: audit complete.

Final verdict: `CANONICAL_PLATFORM_PRESENTATION_LAYER_REUSE_WITH_MINIMAL_COMPOSITION_BINDING`.

## Executive Summary

Generation 19 now has deterministic Platform Core query selection through the Unified Platform Query Router. The remaining presentation gap is not that Platform Core lacks user-facing presentation evidence. The gap is that the evidence is distributed across service-specific response artifacts and Human Interfaces still render those artifacts with local formatting helpers.

Platform Core already contains most of the reusable foundations for a Canonical Platform Presentation Layer:

- Human Conversation Experience artifacts expose `user_headline`, `user_explanation`, `recommended_next_user_action`, progress messages, clarification questions, approval summaries, and fail-closed explanations.
- Platform Query Router artifacts expose selected service, route status, candidate routes, classification evidence, missing route evidence, service response hashes, and route descriptors.
- Platform Knowledge artifacts expose answerable architectural knowledge, source evidence, certification metadata, recommended Platform service, knowledge reuse classification, and PCCL reference owners.
- Root Cause Trace artifacts expose observed result, runtime stage, governance decision, originating request, causal predecessors, missing evidence, contradictions, replay sources, and `root_cause_explanation`.
- Governed Development intent and conversation artifacts expose approval-gated summaries, clarification state, recommended next step, and human approval boundaries.
- Certification and governance registries expose ownership, certification status, evidence references, implementation owner, and authority flags.

The audit concludes that a Canonical Platform Presentation Layer can be implemented as a thin Platform Core-owned composition layer. It should not reinterpret service semantics, replace the Query Router, own runtime diagnostics, own Knowledge, or perform interface rendering. It should normalize existing service responses into one deterministic presentation artifact that Human Interfaces can render without understanding Platform Core internals.

## Presentation Architecture

The recommended architecture is:

```text
Human Interface
  -> submits platform query
Platform Query Router
  -> selects and invokes responsible Platform Core runtime
Canonical Platform Presentation Layer
  -> composes router response and selected service response
  -> emits canonical presentation artifact
Human Interface
  -> renders artifact fields without semantic branching
```

The presentation layer should sit after the Query Router and before Human Interface rendering. This preserves the service selection boundary established in G19-04 while removing service-specific rendering logic from Human Interfaces.

The presentation layer should be read-only and deterministic. It should accept an existing router response and produce a canonical presentation artifact.

## Reusable Component Inventory

| Existing capability | Current owner | Existing public surface | Presentation evidence already available | Reuse readiness |
| --- | --- | --- | --- | --- |
| Human Conversation Experience | `PLATFORM_CORE` / Project Services | `prepare_unified_human_interface_project_context(...)` and embedded `human_conversation_experience` | `user_headline`, `user_explanation`, `recommended_next_user_action`, clarification questions, approval summary, fail-closed response, progress messages | High |
| Reference UHI rendering | Human Interface adapter | `_render_project_context`, `_render_summary`, `_render_clarification`, `_render_non_development_response`, `_render_runtime_result`, `_render_session_result` in `aigol/cli/aicli.py` | Local textual projection of Platform Core fields | Medium as evidence of duplicated logic; not canonical authority |
| Platform Query Router | `PLATFORM_CORE_QUERY_ROUTING` | `route_platform_query(...)` | selected service, route status, query class, scores, missing evidence, classification evidence, descriptors, service response hash | High |
| Platform Knowledge Runtime | `PLATFORM_CORE_KNOWLEDGE` | `query_platform_knowledge(...)` | capability existence, certification status, owner, implementation owner, source evidence, recommended service, reuse classification, PCCL owners | High |
| Root Cause Trace Runtime | `PLATFORM_CORE_REPLAY` | `trace_platform_core_root_cause(...)` | observed result, producing component, source artifact, runtime stage, governance decision, originating request, causal predecessors, missing evidence, replay sources, explanation | High |
| Governed Development intent | `PLATFORM_CORE_RUNTIME` | `resolve_development_intent(...)` and Human Conversation Experience | summary admissibility, runtime binding admissibility, approval requirement, canonical prompt, clarification status | High |
| Certification Registry | `PLATFORM_CORE_CERTIFICATION` | `lookup_platform_capability_certification(...)`, `list_platform_capability_certifications(...)` | certification status, scope, milestone, evidence, owner, implementation owner | High |
| PCCL metadata | `PLATFORM_CORE_COGNITION_LAYER` | `BINDING_REFERENCE_OWNER_BY_TYPE` and related references | reference owners and architectural authority metadata | Medium-high |
| Replay evidence | `PLATFORM_CORE_REPLAY` | replay references and replay-backed artifacts | replay source paths, replay hash references, causal evidence | High when service response includes references |
| Governance evidence | Governance / Platform Core | governance decision artifacts and registry evidence paths | authorization status, governance decision reference, conformance/certification evidence | High through selected service artifacts |

## Existing Presentation Ownership

Platform Core already owns the semantic presentation metadata. Human Interfaces currently duplicate only the final textual formatting.

Evidence:

- `aigol/runtime/platform_core_project_services.py` creates `PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_ARTIFACT_V1` with `conversation_authority = PLATFORM_CORE`, `user_headline`, `user_explanation`, `recommended_next_user_action`, `approval_summary`, and `fail_closed_response`.
- `aigol/cli/aicli.py` renders those fields locally through `_render_project_context`, `_render_summary`, `_render_clarification`, and `_render_non_development_response`.
- `aigol/cli/aicli.py` also renders runtime result fields directly through `_render_runtime_result`.
- `aigol/runtime/platform_query_router.py` already wraps selected service responses but does not normalize their presentation.

This means Human Interfaces are thin in authority but not yet presentation-stateless. They still know which service-specific fields should become visible text.

## Presentation Artifact Model

The Canonical Platform Presentation Layer should emit one artifact, for example:

`CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1`

The mandatory fields should be:

| Field | Purpose | Source reuse |
| --- | --- | --- |
| `artifact_type` | Stable presentation artifact identity | New binding |
| `presentation_version` | Runtime version | New binding |
| `query` | Original user/platform query | Query Router |
| `query_hash` | Deterministic query hash | Query Router |
| `presentation_status` | Ready, missing evidence, clarification required, fail-closed | Router route status and service response status |
| `selected_service` | Service that answered | Query Router |
| `summary` | One-line human-readable result | Existing service response fields |
| `answer` | Canonical response body | Existing service response fields |
| `confidence` | Deterministic confidence label, not probabilistic hidden reasoning | Route status, certification status, replay-backed flags |
| `reasoning_path` | Ordered explanation path | Router classification evidence, Root Cause causal predecessors, Knowledge source evidence, Development progress messages |
| `evidence` | Evidence list with source type, reference, hash/status | Service source evidence, replay sources, certification evidence, governance evidence |
| `sources` | Human-readable source references | Certification evidence, replay references, selected route descriptor |
| `recommended_next_step` | Next action for user/Human Interface | Conversation `recommended_next_user_action`, route missing evidence, fail-closed response |
| `certification_status` | Certification state where applicable | Certification Registry and Platform Knowledge |
| `governance_status` | Governance/authorization state where available | Root Cause governance decision, runtime result, conversation approval state |
| `replay_status` | Replay-backed or missing replay evidence | Root Cause Trace, Router missing evidence, runtime result |
| `warnings` | Missing or contradictory evidence | Root Cause missing/contradictory evidence, Router missing inputs |
| `actions` | Renderable commands or semantic action hints | Existing next-step/approval/clarification metadata |
| `source_response_hash` | Service response hash | Query Router |
| `presentation_hash` | Hash of presentation artifact | New binding |

These fields should be stable across all Platform Core service responses.

## Service-Specific Presentation Mapping

### Platform Knowledge

Reusable fields:

- `capability_exists`
- `certified_capability_exists`
- `capability_owner`
- `implementation_owner`
- `certification_status`
- `certification_evidence`
- `source_evidence`
- `recommended_platform_service`
- `knowledge_reuse_classification`
- `reuse_recommended`
- `pccl_reference_owners`

Canonical presentation mapping:

- `summary`: whether the queried capability exists and whether it is certified.
- `answer`: owner, implementation owner, recommended reuse service, and reuse status.
- `evidence`: certification registry, project services, knowledge reuse, PCCL metadata.
- `recommended_next_step`: reuse the recommended Platform service or request a more specific capability identifier.

### Root Cause Trace

Reusable fields:

- `trace_status`
- `observed_result`
- `producing_component`
- `source_artifact`
- `source_projection`
- `runtime_stage`
- `governance_decision`
- `originating_request`
- `causal_predecessors`
- `missing_evidence`
- `contradictory_evidence`
- `root_cause_explanation`
- `replay_sources_inspected`
- `replay_backed`
- `fail_closed`

Canonical presentation mapping:

- `summary`: `root_cause_explanation`.
- `answer`: observed result plus producing component and runtime stage.
- `reasoning_path`: originating request -> governance decision -> runtime stage -> source artifact/projection -> causal predecessors.
- `evidence`: replay sources, source artifact, missing evidence, contradictory evidence.
- `recommended_next_step`: provide replay/runtime evidence when missing, or inspect the source artifact when trace is ready.

### Governed Development

Reusable fields:

- `summary_admissible`
- `runtime_binding_admissible`
- `clarification_required`
- `requires_human_approval`
- `canonical_runtime_prompt`
- Human Conversation Experience `approval_summary`
- Human Conversation Experience `fail_closed_response`
- Human Conversation Experience `clarification_questions`
- Human Conversation Experience `recommended_next_user_action`

Canonical presentation mapping:

- `summary`: governed implementation summary, clarification required, or fail-closed state.
- `answer`: approval summary or clarification/fail-closed explanation.
- `reasoning_path`: progress messages and Project Services decision fields.
- `evidence`: development intent hash, capability discovery, knowledge reuse classification.
- `recommended_next_step`: approve, clarify, cancel, or refine the request.

### Query Router

Reusable fields:

- `route_status`
- `selected_service`
- `selected_query_class`
- `candidate_routes`
- `required_evidence_missing`
- `ambiguity_detected`
- `classification_evidence`
- `selected_route_descriptor`
- `service_response_hash`

Canonical presentation mapping:

- `summary`: which service answered or why no service was invoked.
- `reasoning_path`: candidate route scores and selected route descriptor.
- `warnings`: missing required evidence or ambiguity.
- `sources`: selected route descriptor and service response hash.

## Ownership Map

| Presentation concern | Canonical owner |
| --- | --- |
| Query classification and selected service | Platform Query Router |
| Architectural knowledge answer | Platform Knowledge Runtime |
| Runtime causality answer | Deterministic Root Cause Trace Runtime |
| Governed development handoff answer | Platform Core Project Services / Governed Development Runtime |
| Certification status | Capability Certification Registry |
| Replay-backed evidence | Replay and Root Cause Trace |
| Governance evidence | Governance / selected runtime |
| Human-readable presentation artifact | Proposed Canonical Platform Presentation Layer |
| Terminal/browser/native rendering | Human Interface adapter |

Human Interfaces should own display mechanics only: ordering, terminal wrapping, UI widgets, and accessibility. They should not decide which service fields mean "answer", "evidence", or "next step".

## Existing Duplication in Human Interfaces

The Reference UHI currently contains local presentation logic:

- `_render_project_context(...)`
- `_render_summary(...)`
- `_render_clarification(...)`
- `_render_non_development_response(...)`
- `_render_runtime_result(...)`
- `_render_session_result(...)`

These functions are not governance violations, but they demonstrate duplicated presentation mapping. They know which Platform Core fields should be shown for different states.

The presentation layer would not remove terminal formatting. It would remove service-specific semantic selection from the Human Interface.

## Implementation Readiness

Readiness is high.

Required reusable inputs already exist:

- Query Router response artifact
- selected service response
- service response hash
- route status and missing evidence
- Platform Knowledge source evidence and certification metadata
- Root Cause Trace reasoning/evidence path
- Governed Development conversation and approval/clarification fields
- governance and replay boundary flags

The missing binding is small:

1. Define `CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1`.
2. Implement a read-only composer that accepts a router response.
3. Add deterministic extractors for known service response artifact types.
4. Validate mandatory fields and hash the presentation artifact.
5. Add fail-closed behavior for unsupported or malformed service responses.
6. Add tests covering Platform Knowledge, Root Cause Trace, Governed Development, missing evidence, and ambiguity.
7. Register the presentation layer in the certification registry after implementation evidence exists.

No new query router, knowledge registry, evidence registry, governance registry, or replay traversal is required.

## Certification Readiness

Certification readiness is high after implementation.

The certification criteria should verify:

- read-only operation
- no provider invocation
- no worker invocation
- no replay mutation
- no governance mutation
- no service replacement
- deterministic field extraction
- stable artifact hash validation
- identical mandatory field shape across supported service responses
- Human Interface rendering without service-specific semantic branching

Recommended certification scope:

- `IMPLEMENTATION`

Recommended capability identifier:

- `CANONICAL_PLATFORM_PRESENTATION_LAYER`

Recommended owner:

- `PLATFORM_CORE_PRESENTATION`

## Gaps

Only minimal reusable bindings are missing:

| Gap | Smallest required binding |
| --- | --- |
| No single canonical presentation artifact | Define `CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1` |
| No service-response-to-presentation mapping | Add deterministic extractor functions keyed by artifact type and selected service |
| No unified mandatory presentation fields | Validate a stable field contract |
| Human Interfaces still map service fields to text | Make Human Interfaces render canonical presentation fields |
| No presentation certification record | Add registry metadata after implementation report |

These gaps do not require a new presentation subsystem with independent semantics. They require a composition layer over existing Platform Core responses.

## Architectural Conclusions

1. Platform Core already owns most presentation metadata.

The key user-facing fields are already generated by Platform Core artifacts, especially Human Conversation Experience, Platform Knowledge, Root Cause Trace, and Query Router.

2. Human Interfaces currently duplicate presentation mapping.

The Reference UHI remains thin in authority, but it still contains local field selection and formatting rules for service-specific responses.

3. A canonical presentation layer should be service-agnostic to Human Interfaces.

Human Interfaces should render `summary`, `answer`, `evidence`, `reasoning_path`, `recommended_next_step`, and `warnings` without knowing whether the answer came from Knowledge, Root Cause Trace, or Governed Development.

4. Presentation should be deterministic, not generative.

The layer should compose and normalize existing fields. It should not invent new explanations, summarize with a provider, or perform hidden semantic inference.

5. The layer should follow the G19 reuse pattern.

Like Platform Knowledge and the Query Router, the presentation layer should be a thin Platform Core composition binding with explicit boundary flags and artifact validation.

## Recommended Minimal Implementation

Implement:

- `aigol/runtime/platform_presentation_layer.py`
- `present_platform_response(router_response: dict[str, Any]) -> dict[str, Any]`
- `validate_platform_presentation(response: dict[str, Any]) -> dict[str, Any]`
- deterministic extractors for:
  - `PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1`
  - `PLATFORM_CORE_ROOT_CAUSE_TRACE_ARTIFACT_V1`
  - `PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_ARTIFACT_V1`
  - missing-evidence router responses with no service response
  - clarification-required router responses

Do not implement:

- provider summarization
- service-specific Human Interface rendering
- replay traversal
- governance decisions
- query classification
- a new knowledge/certification/evidence registry

## Final Recommendation

Proceed with a Canonical Platform Presentation Layer as a minimal Platform Core composition binding.

The implementation should consume the Unified Platform Query Router response and emit one canonical presentation artifact for Human Interfaces. This will allow Human Interfaces to become nearly stateless renderers while preserving Platform Core ownership of semantics, evidence, and service responsibility.

## Final Verdict

`CANONICAL_PLATFORM_PRESENTATION_LAYER_REUSE_WITH_MINIMAL_COMPOSITION_BINDING`
