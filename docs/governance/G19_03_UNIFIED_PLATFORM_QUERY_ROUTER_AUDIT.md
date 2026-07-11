# G19-03 Unified Platform Query Router Audit

Status: AUDIT COMPLETE

Date: 2026-07-11

Scope: Architectural audit for a Unified Platform Query Router as the single deterministic Platform Core entry point for natural-language platform queries. This audit does not implement a router, introduce a new semantic interpreter, invoke providers, invoke workers, mutate replay, mutate governance, or change Human Interface behavior.

## Executive Summary

Platform Core now contains multiple certified services that can answer different classes of deterministic platform questions:

- Platform Knowledge Runtime answers architectural knowledge questions.
- Deterministic Root Cause Trace answers runtime-causality questions.
- Governed Development Runtime handles approved implementation workflow.
- Replay Certification and Replay Observation answer replay-evidence and certification questions when supplied required replay artifacts.
- Replay-derived Improvement Analysis can classify replay-visible gaps and produce bounded improvement intent, but remains proposal-only and evidence-dependent.
- Project Services, Human Intent Resolution, Knowledge Reuse, PCCL, and the certification registry already provide deterministic classification, ownership, and service metadata.

Human Interfaces still need to know which Platform Core service to invoke. That is now the architectural gap.

The preferred architecture is a thin Unified Platform Query Router owned by Platform Core. The router should compose existing classification and registry capabilities instead of becoming a new semantic interpretation layer.

Final verdict: `UNIFIED_PLATFORM_QUERY_ROUTER_REUSE_WITH_MINIMAL_COMPOSITION_BINDING`.

## Unified Query Router Architecture

Recommended architecture:

```text
Human Interface
-> Unified Platform Query Router
-> deterministic query classification
-> selected certified Platform Core service
-> service response or required-evidence clarification
```

The router should own only:

- query intake normalization;
- deterministic service classification;
- service capability lookup;
- service input-readiness assessment;
- routing decision artifact;
- selected service invocation or fail-closed/clarification response.

The router should not own:

- semantic interpretation;
- capability discovery;
- Knowledge Reuse;
- certification;
- replay traversal;
- runtime diagnostics;
- governed development execution;
- provider selection;
- worker execution;
- governance authorization.

## Which Platform Core Services Are Already Queryable

| Service | Current public entry point | Queryability status | Router implication |
| --- | --- | --- | --- |
| Platform Knowledge Runtime | `query_platform_knowledge(...)` | Directly queryable from a platform question; supports explicit and free-form queries | Ready as first target service |
| Deterministic Root Cause Trace | `trace_platform_core_root_cause(...)` | Queryable when observed field, failure reason, replay reference, artifact reference, runtime result, or user-visible result is available | Router must require runtime/replay evidence before routing or ask for it |
| Governed Development Runtime | `run_human_interface_runtime_entry(...)` and `run_interactive_conversation(...)` through existing approval-bound path | Not a simple answer service; requires governed summary and human approval | Router may classify "implement/build/change" as governed development intent and hand off to existing Project Services/UHI approval path |
| Replay Certification Runtime | `certify_validated_replay(...)`, `reconstruct_replay_certification_replay(...)` | Queryable for certification/reconstruction when result-validation or replay-certification evidence exists | Router should not fabricate missing replay evidence; it should request references |
| Replay Observation Layer | `generate_replay_observation_layer(...)`, `observe_replay_directory(...)`, replay observation reconstruction | Queryable when replay directory/artifacts are supplied | Router can classify "summarize/observe replay" but must require replay input |
| Replay Gap Detection | `detect_replay_gaps(...)`, `reconstruct_replay_gap_detection_replay(...)` | Evidence-dependent; not a general platform question service | Future Improvement Analysis route, with replay evidence required |
| Replay to Improvement Intent | `create_improvement_intent_from_replay_gap(...)` | Evidence-dependent and proposal-only | Router may classify as future improvement route after gap detection evidence exists |
| PCCL Reference/Decision Runtime | PCCL context, policy, reference binding, decision records | Queryable by explicit lifecycle/reference operations, not natural-language platform Q&A by itself | Router can cite PCCL metadata but must not move routing ownership into PCCL |
| Certification Registry | `lookup_platform_capability_certification(...)`, list/owner/evidence helpers | Queryable for exact certification metadata | Already composed by Platform Knowledge; router should usually route certification metadata questions to Platform Knowledge |

## Routing Responsibility Map

| Query class | Responsible service | Required evidence | Router behavior |
| --- | --- | --- | --- |
| "Does this capability exist?", "Who owns it?", "Where is it implemented?", "Is it certified?" | Platform Knowledge Runtime | Query text, optional capability id/workspace state | Route directly to Platform Knowledge |
| "Why did this runtime result occur?", "Why is `worker_execution_reached=false`?", "Explain this failure" | Deterministic Root Cause Trace | Observed field/failure/replay/runtime result/reference | Route when evidence exists; otherwise ask for runtime/replay evidence |
| "Implement/build/change/improve this capability" | Governed Development Runtime through Project Services and Human approval | Human request, Project Services context, approval summary | Route to existing governed development intake, not directly to execution |
| "Certify this replay/result" | Replay Certification Runtime | Result validation artifact and replay directory | Request evidence if missing; route only when supplied |
| "Show/reconstruct/observe replay" | Replay Observation / replay command surfaces | Replay directory or artifact references | Route to replay observation/reconstruction surfaces |
| "Detect gaps / propose improvement from replay" | Replay Gap Detection and Improvement Intent | Replay artifacts, thresholds/domain, later gap artifacts | Route to future Improvement Analysis only with replay evidence and proposal-only boundaries |
| "Which service should answer this?" | Platform Knowledge plus router classification evidence | Query text | Router can return classification without invoking target service |

## Reusable Platform Core Components

The router can reuse existing components:

- `query_platform_knowledge(...)` for architectural knowledge and service metadata.
- `trace_platform_core_root_cause(...)` for runtime-causality traces.
- `discover_candidate_capabilities(...)` for deterministic capability inference.
- `resolve_development_intent(...)` for governed development admissibility.
- `project_knowledge_context_from_workspace(...)` for reuse classification.
- `lookup_platform_capability_certification(...)` and registry listing for certified service metadata.
- `BINDING_REFERENCE_OWNER_BY_TYPE` and PCCL reference metadata for owner-bound service references.
- `is_conversation_native_development_intent(...)` and native-development routing evidence for development-intent classification where appropriate.
- `select_resolution_strategy(...)` as precedent for deterministic strategy selection, not as a replacement router.
- replay reconstruction/certification functions for evidence-dependent replay service routes.

These are enough to build the router as a composition layer.

## Existing Classification Capabilities

Existing UBTR/Human Intent/Project Services capabilities are reusable, but they should not be duplicated.

Current deterministic classification sources:

- G14-47 Human Intent to Capability Resolution derives candidate capabilities from ordinary language.
- Project Services `resolve_development_intent(...)` determines whether a request is governed development, clarification, summary-admissible, or runtime-admissible.
- Knowledge Reuse classifies whether a request relates to certified capabilities, existing workspace work, or new governed work.
- Platform Knowledge classifies architectural queries as certified capability, project capability knowledge, or unknown platform knowledge.
- Conversation native-development routing classifies native-development intent families such as domain, worker, provider, governance, and replay-derived improvement.
- Resolution Strategy Runtime records deterministic strategy choices such as replay, governance, constitutional memory, provider, or self-resolution.

Conclusion: the router should compose these existing classifiers, not create a second semantic layer.

## Routing Lifecycle

Recommended lifecycle:

1. Receive platform question.
2. Normalize query text and compute query hash.
3. Run read-only classification evidence:
   - Platform Knowledge query classification;
   - Project Services capability/development intent classification;
   - optional evidence-reference detection for replay/runtime artifacts.
4. Evaluate candidate service routes in deterministic precedence.
5. Check required evidence for the selected route.
6. If evidence is missing, return a required-evidence clarification, not a guessed answer.
7. If route is ready, invoke the selected Platform Core service.
8. Return a unified router response containing:
   - selected service;
   - rejected candidates;
   - classification evidence;
   - required evidence status;
   - service response hash/reference;
   - non-execution and authority flags.

## Deterministic Classification Model

Recommended route precedence:

1. Explicit service or capability identifier.
2. Runtime-causality keywords plus supplied runtime/replay evidence.
3. Architectural knowledge queries.
4. Replay/certification queries with supplied replay/certification evidence.
5. Replay-derived improvement queries with supplied replay/gap evidence.
6. Governed development implementation requests.
7. Unknown/clarification required.

Examples:

| Query signal | Likely route |
| --- | --- |
| "Does X exist?", "where is X implemented", "who owns X", "is X certified" | Platform Knowledge |
| "why did X fail", "why is field false", "explain runtime result" | Root Cause Trace if replay/runtime evidence exists |
| "certify this replay/result" | Replay Certification if validation artifact exists |
| "observe/summarize this replay" | Replay Observation if replay reference exists |
| "detect replay gap", "turn this gap into improvement" | Improvement Analysis route if replay/gap evidence exists |
| "implement/add/build/change/refine" | Governed Development Runtime through existing approval path |

The router must preserve deterministic ambiguity handling. If two routes remain plausible with equal evidence, it should fail closed into a clarification rather than select arbitrarily.

## Service Registration Model

Future Platform Core services should become routable without Human Interface changes.

Recommended model:

- service identity remains indexed by the Platform Capability Certification Registry;
- each routable service exposes a minimal query contract:
  - `service_identifier`;
  - `service_owner`;
  - `implementation_owner`;
  - `query_classes`;
  - `required_inputs`;
  - `authority_flags`;
  - `response_artifact_type`;
  - `certification_evidence`;
- the router derives its service catalog from certification metadata plus small route adapters;
- Human Interfaces call only the router.

This does not require a duplicate capability registry. It requires a thin routability binding over certified services.

G19-02 proves this pattern: Platform Knowledge is already registered in the certification registry and exposes a single deterministic query interface.

## Implementation Readiness

Implementation readiness is high for a minimal router.

Already ready:

- Platform Knowledge route.
- Root Cause Trace route when replay/runtime evidence is supplied.
- Governed Development classification through Project Services.
- Certification Registry and ownership metadata.
- PCCL reference owner metadata.
- deterministic replay/certification functions for evidence-bound routes.

Still missing:

- a unified router response artifact;
- deterministic service route descriptors;
- required-evidence schema per route;
- conflict/ambiguity handling across candidate routes;
- a service invocation adapter layer that stays read-only until the selected service's own authority boundary applies;
- regression tests proving Human Interfaces are service-agnostic.

## Certification Readiness

Certification should prove:

- Human Interfaces submit one platform query and do not select services.
- Platform Knowledge questions route to Platform Knowledge.
- Root-cause questions route to Root Cause Trace only when replay/runtime evidence exists.
- Missing evidence produces deterministic required-evidence clarification.
- Governed development requests route to Project Services and approval flow, not direct execution.
- Replay/certification/improvement routes preserve evidence requirements and proposal-only boundaries.
- No new semantic interpretation layer is introduced.
- No provider, worker, replay mutation, governance mutation, certification ownership, or Root Cause Trace ownership moves into the router.
- Future service registration does not require Human Interface changes.

## Architectural Conclusion

A Unified Platform Query Router should be implemented as a Platform Core composition layer.

It should reuse:

- Platform Knowledge for architectural questions;
- Root Cause Trace for runtime-causality questions;
- Project Services and Human Intent Resolution for development-intent classification;
- certification registry metadata for service identity and ownership;
- PCCL reference metadata for owner-bound service references;
- replay/certification/improvement runtimes for evidence-bound routes.

It should not duplicate UBTR, Human Intent Resolution, Project Services, Knowledge Reuse, or service-specific runtime logic.

Human Interfaces can become service-agnostic if they call this router as the single Platform Core platform-question entry point and render the returned router/service response.

## Final Recommendation

Proceed to a future implementation milestone for a minimal Unified Platform Query Router.

The first implementation should support:

- Platform Knowledge route;
- Root Cause Trace route with required replay/runtime evidence;
- Governed Development route through Project Services classification;
- fail-closed required-evidence responses for replay/certification/improvement routes;
- metadata-driven future service routability.

## Final Verdict

`UNIFIED_PLATFORM_QUERY_ROUTER_REUSE_WITH_MINIMAL_COMPOSITION_BINDING`

The conclusion is supported by deterministic implementation and governance evidence:

- `aigol/runtime/platform_knowledge_runtime.py` already exposes a unified architectural query response.
- `aigol/runtime/platform_core_root_cause_trace.py` already exposes deterministic runtime-causality trace.
- `aigol/runtime/platform_core_project_services.py` already exposes Human Intent Resolution, development intent resolution, Knowledge Reuse, and Project Services context.
- `aigol/runtime/platform_capability_certification_registry.py` already indexes certified service identity, ownership, implementation owner, and evidence.
- `aigol/runtime/platform_core_cognition_layer.py` already provides PCCL owner-bound reference metadata.
- `aigol/runtime/conversation_native_development_intent_routing.py`, `aigol/runtime/intent_routing_attachment.py`, and `aigol/runtime/resolution_strategy_runtime.py` prove deterministic routing and strategy-selection precedents, while also showing why a universal router must remain a thin composition layer instead of another semantic owner.
