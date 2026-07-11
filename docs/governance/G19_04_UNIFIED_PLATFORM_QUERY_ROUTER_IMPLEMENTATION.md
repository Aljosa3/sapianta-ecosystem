# G19-04 Unified Platform Query Router Implementation

Status: implemented and certified.

Final verdict: `UNIFIED_PLATFORM_QUERY_ROUTER_IMPLEMENTED`.

## Executive Summary

G19-04 implements the first Unified Platform Query Router as a thin Platform Core-owned composition service.

The router is now the deterministic entry point for Platform Core platform questions. It classifies a submitted query, selects the responsible Platform Core service, invokes that service through a route adapter, and returns a unified router response artifact.

The implementation preserves the G19-03 audit conclusion:

`UNIFIED_PLATFORM_QUERY_ROUTER_REUSE_WITH_MINIMAL_COMPOSITION_BINDING`

No new semantic subsystem, registry, provider path, worker path, replay diagnostic implementation, or governed development replacement was introduced.

## Implemented Files

- `aigol/runtime/platform_query_router.py`
- `tests/test_g19_04_platform_query_router.py`
- `docs/governance/G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_IMPLEMENTATION.md`

The certification registry was extended with metadata for:

- `UNIFIED_PLATFORM_QUERY_ROUTER`

## Runtime Interface

The canonical runtime interface is:

- `route_platform_query(...)`
- `platform_query_route_descriptors()`
- `validate_platform_query_router_response(...)`

The router response artifact is:

- `PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1`

The runtime version is:

- `G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_V1`

## Supported Initial Routes

The router supports the required initial Platform Core services:

| Route | Service Owner | Implementation Owner | Responsibility |
| --- | --- | --- | --- |
| `PLATFORM_KNOWLEDGE_RUNTIME` | `PLATFORM_CORE_KNOWLEDGE` | `aigol.runtime.platform_knowledge_runtime` | Architectural knowledge, capability ownership, certification metadata, reuse advice |
| `DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME` | `PLATFORM_CORE_REPLAY` | `aigol.runtime.platform_core_root_cause_trace` | Replay-backed runtime result explanation |
| `GOVERNED_DEVELOPMENT_RUNTIME` | `PLATFORM_CORE_RUNTIME` | `aigol.runtime.platform_core_project_services` | Governed development intent handoff before human approval |

## Reuse Composition

The router composes existing Platform Core capabilities:

- Platform Knowledge Runtime via `query_platform_knowledge(...)`
- Deterministic Root Cause Trace Runtime via `trace_platform_core_root_cause(...)`
- Governed Development intent resolution via `resolve_development_intent(...)`
- Capability and certification evidence through Platform Knowledge and the certification registry
- Knowledge Reuse and project capability discovery through Platform Project Services

The router does not duplicate these services. It records which service answered and preserves the selected service response unchanged except for wrapping it in the unified router artifact.

## Route Descriptor Model

G19-04 introduces `PlatformServiceRouteDescriptor` as reusable routing metadata.

Each descriptor records:

- service identifier
- service owner
- implementation owner
- supported query classes
- required inputs
- response artifact type
- service version
- adapter name
- deterministic routing terms
- route descriptor hash

Descriptors are Platform Core metadata. They do not grant execution authority, modify governance, mutate replay, or invoke providers or workers.

Future Platform Core services can be registered by supplying a descriptor and adapter map to the router without changing Human Interface behavior.

## Deterministic Classification

The router uses deterministic scoring over existing evidence:

- Platform Knowledge scoring uses architectural, ownership, certification, service, and capability terms, then incorporates Platform Knowledge evidence about certified capability and project capability detection.
- Root Cause Trace scoring uses runtime causality terms and receives an explicit observed-result boost for fields such as `worker_execution_reached`, `provider_invocation_reached`, `replay_certification_reached`, and `runtime_status`.
- Governed Development scoring uses implementation/change terms and existing `resolve_development_intent(...)` evidence.
- Future descriptors use deterministic descriptor routing terms.

If the highest score is tied, the router fails closed to `ROUTE_CLARIFICATION_REQUIRED`.

If the selected service requires evidence that was not supplied, the router returns `REQUIRED_EVIDENCE_MISSING` and does not invoke the selected service.

## Route Adapter Layer

The adapter layer preserves service ownership:

- Platform Knowledge adapter calls or returns `query_platform_knowledge(...)` evidence.
- Root Cause Trace adapter calls `trace_platform_core_root_cause(...)`.
- Governed Development adapter returns the existing development intent resolution with a router handoff marker and `runtime_execution_invoked = False`.

The Governed Development route prepares a handoff only. It does not execute governed runtime, invoke providers, invoke workers, or bypass human approval.

## Unified Response Artifact

The router response includes:

- query and query hash
- selected service
- selected query class
- selected route descriptor
- candidate routes and scores
- route status
- missing required evidence, if any
- ambiguity flag
- classification evidence from Platform Knowledge and Project Services
- service response and service response hash
- all route descriptors
- boundary flags
- final artifact hash

The validator recomputes the final hash and fails closed on mutation or boundary flag drift.

## Boundary Preservation

The implementation explicitly records:

- `platform_core_authority = True`
- `human_interface_authority = False`
- `human_interface_selects_service = False`
- `composition_layer_only = True`
- `semantic_interpretation_owned = False`
- `platform_knowledge_replaced = False`
- `root_cause_trace_replaced = False`
- `governed_development_replaced = False`
- `runtime_diagnostics_performed_by_router = False`
- `governance_modified = False`
- `replay_modified = False`
- `provider_invoked = False`
- `worker_invoked = False`

These flags are part of the validated artifact contract.

## Certification Registry

The capability registry now exposes:

- capability: `UNIFIED_PLATFORM_QUERY_ROUTER`
- owner: `PLATFORM_CORE_QUERY_ROUTING`
- certification status: `CERTIFIED`
- scope: `IMPLEMENTATION`
- implementation owner: `aigol.runtime.platform_query_router`
- verification type: `DETERMINISTIC_PLATFORM_QUERY_ROUTING_COMPOSITION`

The registry entry is metadata only. It does not create runtime authority.

## Validation

Validation performed:

```bash
python -m py_compile aigol/runtime/platform_query_router.py aigol/runtime/platform_capability_certification_registry.py tests/test_g19_04_platform_query_router.py
python -m pytest tests/test_g19_04_platform_query_router.py tests/test_g19_02_platform_knowledge_runtime.py tests/test_g18_09_platform_core_root_cause_trace.py tests/test_g15_governance_01_platform_capability_certification_registry.py
git diff --check
```

Validation result:

- router py_compile passed
- focused router regression suite passed
- composed Platform Knowledge, Root Cause Trace, and certification registry regression suites passed
- diff whitespace check passed

## Implementation Boundaries

G19-04 does not implement:

- provider execution
- worker execution
- replay traversal logic inside the router
- root cause diagnostics inside the router
- a new knowledge registry
- a new certification registry
- a replacement for Governed Development
- a replacement for Platform Knowledge
- a replacement for Deterministic Root Cause Trace

## Final Recommendation

Use `route_platform_query(...)` as the canonical Platform Core entry point for Human Interfaces that need to submit platform questions without selecting a service themselves.

Human Interfaces should remain thin adapters. Platform Core now owns service selection through deterministic reusable routing descriptors and route adapters.

## Final Verdict

`UNIFIED_PLATFORM_QUERY_ROUTER_IMPLEMENTED`
