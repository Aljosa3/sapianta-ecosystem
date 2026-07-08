# G15-ARCH-01 - Platform Core Architecture Reflection

Status: ARCHITECTURE REVIEW COMPLETE

Date: 2026-07-08

Milestone: G15-ARCH-01

Scope: Generation 15 architecture reflection. This milestone does not modify production code, runtime behavior, routing behavior, replay semantics, governance semantics, Platform Core ownership, or Human Interface behavior.

## Knowledge Reuse Audit

This review reused existing Generation 15 reports, implementation modules, and regression evidence.

Reviewed governance evidence:

- `docs/governance/G15_01_REPLAY_OBSERVATION_LAYER_V1.md`
- `docs/governance/G15_HIR_02_REPLAY_BACKED_CLARIFICATION_CONTINUITY.md`
- `docs/governance/G15_HIR_07_CLARIFICATION_RESOLUTION_STATE_MANAGEMENT.md`
- `docs/governance/G15_HIR_08_DETERMINISTIC_CLARIFICATION_PLANNER.md`
- `docs/governance/G15_HIR_09_CLARIFICATION_PLANNER_EFFECTIVENESS_VERIFICATION.md`
- `docs/governance/G15_ROUTING_01_GOVERNED_DEVELOPMENT_RUNTIME_SELECTION_AUDIT.md`
- `docs/governance/G15_RUNTIME_06_GOVERNED_DEVELOPMENT_RUNTIME_CONTINUATION.md`
- `docs/governance/G15_REPLAY_01_REPLAY_CERTIFICATION_LINEAGE_AUDIT.md`
- `docs/governance/G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY.md`
- `docs/governance/G15_SEMANTICS_01_CANONICAL_SEMANTIC_ARTIFACT_TRANSITION_AUDIT.md`
- `docs/governance/G15_UX_03_REAL_GOVERNED_DEVELOPMENT_USER_JOURNEY_VALIDATION.md`

Reviewed implementation evidence:

- `aigol/runtime/platform_core_project_services.py`
- `aigol/runtime/replay_observation_layer.py`
- `aigol/runtime/replay_certification_runtime.py`
- `aigol/runtime/platform_capability_certification_registry.py`
- `aigol/runtime/human_interface_runtime_entry_service.py`
- `aigol/runtime/canonical_semantic_artifact_runtime.py`
- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/cli/aigol_cli.py`
- `aigol/cli/aicli.py`

No duplicate architecture, registry, replay layer, Human Intent Resolution path, runtime selector, runtime continuation path, or certification model was introduced.

## Architectural Reflection

Generation 15 matured the Platform Core architecture from a set of certified runtime stages into a replay-visible operational system for governed human development.

The strongest architectural pattern is now:

```text
Human Interface
-> Platform Core Project Services
-> Development Intent Resolution
-> Clarification Planning or Approval Summary
-> Canonical Runtime Entry
-> Runtime Selection and Continuation
-> Worker Lifecycle
-> Result Validation
-> Replay Observation
-> Replay Certification
-> Certification Registry
```

The mature capabilities are not Human Interface behavior. AiCLI remains the user-facing composer, renderer, approval collector, and delegation point. The semantic decisions, clarification state, runtime gating, replay lineage, certification status, and governance evidence remain Platform Core-owned.

Generation 15 also confirms that not every helper should become a separate top-level service. Some capabilities are now canonical Platform Core capabilities while still being correctly implemented inside an existing service boundary.

## Platform Core Capability Review

| Capability | Current owner | Current consumers | Architectural classification | Recommendation |
| --- | --- | --- | --- | --- |
| Clarification Planner | Platform Core Project Services / HIR | UHI project context, AiCLI renderer, tests, governance reports | Reusable component inside a canonical Platform Core capability | Keep inside HIR for now; expose through project context artifacts rather than a separate runtime service. |
| Clarification Resolution | Platform Core Project Services / HIR | UHI continuation, workspace replay, approval summary creation | Canonical Platform Core capability | Keep Platform Core-owned; treat slot bindings and answered question IDs as stable clarification state evidence. |
| Replay Observation | Platform Core Replay | Replay Certification, future replay analytics, governance evidence | Reusable Platform Core service | Keep as a shared replay service because it normalizes evidence across runtime domains. |
| Replay Certification | Platform Core Replay Certification Runtime | Runtime completion, certification registry, governance reports | Canonical Platform Core capability | Keep as a standalone runtime service with fail-closed prerequisites. |
| Certification Registry | Platform Core Governance Metadata | Human Interfaces may query; governance and runtime reviews reference | Canonical Platform Core capability | Keep as canonical metadata index over immutable reports; do not turn it into execution authority. |
| Runtime Selection | Platform Core Project Services, Runtime Entry, Conversational Runtime | UHI entry, conversational routing, governed runtime continuation | Reusable Platform Core service candidate | Current layered implementation is correct; a named runtime-selection artifact may improve Generation 16 auditability. |
| Runtime Continuation | Platform Core Runtime Orchestration | Approved UHI requests, governed development bridge, worker lifecycle | Canonical Platform Core capability | Keep as runtime orchestration, not AiCLI behavior. |
| Canonical Semantic Artifact | Platform Core Semantics / UBTR path | Conversational routing, semantic audits, future CSA-first consumers | Canonical semantic artifact authority | Continue migration toward CSA consumption where parity is proven; do not force all compatibility paths out prematurely. |
| Platform Capability Certification Registry | Platform Core governance metadata | Architecture reviews, runtime-readable certification lookup | Canonical Platform Core capability | Expand records as future capabilities are certified; preserve governance reports as source evidence. |

## Platform Service Candidates

The following capabilities have matured enough to be treated as shared Platform Core services:

- Replay Observation Layer: cross-runtime, read-only, deterministic, and already reused by Replay Certification.
- Replay Certification Runtime: canonical fail-closed certification of validated runtime results.
- Platform Capability Certification Registry: canonical runtime-readable certification metadata index.
- Canonical Human Interface Runtime Entry: canonical boundary between Human Interfaces and Platform Core runtime.
- Runtime Continuation: shared orchestration from approved governed request through worker lifecycle and replay certification.

The following capabilities should remain inside Human Intent Resolution / Platform Core Project Services:

- Clarification Planner.
- Clarification Resolution state.
- Development Intent Resolution.
- Human conversation experience artifact construction.
- Project guidance and knowledge reuse assembly.

These are reusable within Platform Core, but their current consumers depend on the same project context, workspace replay, and active clarification state. Extracting them prematurely would risk duplicating HIR ownership.

The following capability should remain in Governance:

- Certification Registry semantics as metadata over governance reports.

The following capability should remain in Runtime:

- Runtime continuation, worker lifecycle continuation, result validation handoff, and replay certification invocation.

The following capability should remain in Semantics / UBTR:

- Canonical Semantic Artifact creation and CSA-aware routing participation.

## Ownership Review

Stable ownership baseline for Generation 16:

| Domain | Permanent owner | Notes |
| --- | --- | --- |
| Semantic interpretation | Platform Core Project Services and Platform Core Semantics | CSA participates where deterministic evidence is sufficient. |
| Clarification planning | Platform Core Human Intent Resolution | AiCLI renders questions only. |
| Clarification resolution | Platform Core Human Intent Resolution | Question identifiers and answered slot evidence are Platform Core state. |
| Project context | Platform Core Project Services | Includes workspace replay, guidance, knowledge reuse, development intent, and conversation artifact. |
| Runtime entry | Canonical Human Interface Runtime Entry Service | Gates approved prompts into certified runtime. |
| Runtime selection | Platform Core layered routing | Deterministic today; candidate for a named selection artifact later. |
| Runtime continuation | Platform Core Runtime Orchestration | Continues approved governed requests into worker lifecycle and certification. |
| Replay observation | Platform Core Replay | Read-only normalized observation of replay evidence. |
| Replay certification | Platform Core Replay Certification Runtime | Certifies validated results only. |
| Certification metadata | Platform Core Governance Metadata | Reports remain immutable evidence. |
| Human Interface | AiCLI and future UHI surfaces | Capture, render, approve, delegate; no semantic authority. |

No responsibility should move into AiCLI. No provider-specific logic should move into Platform Core semantic services. No replay certification semantics should move into worker runtimes or Human Interfaces.

## Reuse Opportunities

Recommended Generation 16 reuse opportunities:

- Make runtime selection evidence easier to inspect by emitting a named `Runtime Selection` artifact from the existing layered decision path.
- Extend the Certification Registry with newly verified G15 capabilities such as clarification planner effectiveness and architecture reflection when they become certification records.
- Reuse Replay Observation as the standard input for future governance analytics and improvement-readiness reports.
- Reuse clarification planner evidence for UHI rendering improvements without changing ownership.
- Reuse CSA fields as routing input where parity is proven, while retaining compatibility routing as fail-closed diagnostic support until coverage is complete.
- Keep Platform Core Project Services as the aggregation point for human-facing development context.

These are reuse recommendations, not production changes.

## Naming Recommendations

Naming changes are not required for Generation 15 closure.

Optional Generation 16 naming refinements:

- Promote `deterministic_clarification_plan` in reports as `Platform Core Clarification Plan` while leaving implementation names stable.
- Introduce `Platform Core Runtime Selection Evidence` as an artifact name if a standalone runtime-selection evidence artifact is added.
- Keep `Certification Registry` named as metadata, not certification authority, to avoid implying that registry records replace governance reports.
- Keep `Replay Observation Layer` as the name for normalized evidence observation, not improvement analysis.

No immediate renaming is required because existing names are deterministic, descriptive, and already certified in governance evidence.

## Boundary Confirmation

This architecture review did not modify:

- production code;
- runtime behavior;
- routing behavior;
- replay behavior;
- governance semantics;
- approval behavior;
- Human Interface ownership;
- Provider Platform ownership;
- Worker Platform ownership.

Generation 14 ownership boundaries remain unchanged.

AiCLI remains a thin Human Interface.

Platform Core remains the canonical owner of semantic interpretation, clarification planning, governance, replay, runtime orchestration, runtime selection, and certification metadata.

Governance reports remain immutable certification evidence. The Certification Registry remains the operational index over that evidence.

## Validation Summary

Validation performed:

- `python -m py_compile aigol/runtime/platform_core_project_services.py aigol/runtime/replay_observation_layer.py aigol/runtime/replay_certification_runtime.py aigol/runtime/platform_capability_certification_registry.py aigol/runtime/human_interface_runtime_entry_service.py aigol/runtime/canonical_semantic_artifact_runtime.py aigol/runtime/conversational_cli_runtime.py aigol/cli/aigol_cli.py aigol/cli/aicli.py`
- `python -m pytest -q` passed: `5835 passed, 4 skipped in 140.00s`.
- `git diff --check` passed.

Tracked runtime evidence regenerated by full validation was restored so the milestone diff remains scoped to governance artifacts.

## Governance Report

G15-ARCH-01 confirms that Generation 15 produced several canonical Platform Core capabilities and several reusable Platform Core components.

Canonical Platform Core capabilities for Generation 16 baseline:

- Replay Observation Layer.
- Replay Certification Runtime.
- Platform Capability Certification Registry.
- Canonical Human Interface Runtime Entry.
- Runtime Continuation.
- Clarification Resolution state.
- Canonical Semantic Artifact authority.

Reusable Platform Core components that should remain inside their current owner boundary:

- Clarification Planner inside Human Intent Resolution / Platform Core Project Services.
- Development Intent Resolution inside Platform Core Project Services.
- Human conversation experience construction inside Platform Core Project Services.
- Runtime selection as layered evidence across Project Services, Runtime Entry, and Conversational Runtime.

Architecture verdict:

`GENERATION_15_PLATFORM_CORE_ARCHITECTURE_STABLE_FOR_GENERATION_16`

No production implementation is required by this review.
