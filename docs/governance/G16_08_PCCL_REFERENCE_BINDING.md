# G16-08 - PCCL Reference Binding

Status: CERTIFIED

Date: 2026-07-09

Milestone: G16-08

Scope: Deterministic PCCL Reference Binding layer. This milestone implements reference-only binding from PCCL artifacts to existing Platform Core services. It does not implement Provider Runtime, Capability Resolution, Governance, Replay, Proposal Pipeline, Cognitive Loop, Prompt Generation, Worker Execution, provider invocation, runtime execution, AiCLI behavior, or any new service behavior.

## Objective

Implement the smallest missing deterministic capability identified by G16-07:

```text
PCCL-owned reference binding
-> validated PCCL Session
-> validated Canonical Context Envelope
-> validated Canonical Policy Envelope
-> owner-bound references to existing Platform Core services
```

The binding deterministically connects PCCL to existing certified services through references only. It does not execute, dereference, select, resolve, govern, invoke, certify, or mutate any referenced service.

## Knowledge Reuse Audit

G16-08 reused the completed Generation 16 architecture and existing Platform Core capabilities.

Reviewed governance evidence:

- `docs/governance/G16_01_PCCL_FOUNDATION.md`
- `docs/governance/G16_02_PCCL_SESSION_RUNTIME.md`
- `docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md`
- `docs/governance/G16_04_CANONICAL_POLICY_ENVELOPE.md`
- `docs/governance/G16_05_PCCL_PROVIDER_INTEGRATION_AUDIT.md`
- `docs/governance/G16_06_PCCL_CAPABILITY_RESOLUTION_AUDIT.md`
- `docs/governance/G16_07_PCCL_ARCHITECTURE_CONSOLIDATION_REVIEW.md`
- `docs/governance/G15_ARCH_02_CANONICAL_GOVERNED_DEVELOPMENT_WORKFLOW.md`
- `docs/governance/G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY.md`
- `docs/governance/G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1.md`

Reviewed implementation surfaces:

- `aigol/runtime/platform_core_cognition_layer.py`
- `aigol/runtime/platform_capability_certification_registry.py`
- `aigol/runtime/platform_core_project_services.py`
- `aigol/runtime/human_interface_runtime_entry_service.py`
- `aigol/runtime/canonical_semantic_artifact_runtime.py`
- `aigol/runtime/replay_certification_runtime.py`
- `aigol/runtime/unified_resource_selection_runtime.py`
- `aigol/runtime/domain_and_worker_resolution_registry.py`
- `aigol/provider/certified_provider_attachment.py`

Reused Platform Core capabilities:

- PCCL Foundation.
- PCCL Session Runtime.
- Canonical Context Envelope.
- Canonical Policy Envelope.
- Human Intent Resolution.
- Development Intent Resolution.
- Candidate Capability Discovery.
- Knowledge Reuse.
- Clarification.
- Runtime Entry and Runtime Continuation references.
- Governance references.
- Replay references.
- Certification Registry.
- Provider Platform references.
- Worker Resolution references.
- deterministic hashing through `replay_hash`.
- fail-closed validation through `FailClosedRuntimeError`.

No provider runtime, capability resolver, governance logic, replay logic, prompt generation, proposal pipeline, cognitive loop, or worker execution was introduced.

## Architecture Review

G16-07 certified that PCCL is required only as a Platform Core cognition reference-boundary and deterministic session/envelope owner.

The Reference Binding implements that conclusion.

PCCL owns:

- binding artifact identity;
- PCCL Session reference;
- Context Envelope reference;
- Policy Envelope reference;
- deterministic service reference entries;
- deterministic owner metadata;
- deterministic artifact hash;
- fail-closed binding validation.

PCCL does not own:

- Human Intent Resolution;
- capability discovery;
- capability resolution;
- Knowledge Reuse;
- clarification;
- governance;
- runtime execution;
- provider registry;
- provider selection;
- provider orchestration;
- provider invocation;
- worker resolution semantics;
- worker execution;
- replay;
- certification;
- prompt generation;
- proposal generation;
- cognitive loop control.

No Generation 14 ownership boundary changed.

## Existing Capability Discovery

Existing services already own the capabilities PCCL needs to reference:

| Capability | Existing owner | G16-08 decision |
| --- | --- | --- |
| Human Intent Resolution | Platform Core Project Services | Reference only. |
| Development Intent Resolution | Platform Core Project Services | Reference only. |
| Capability Discovery | Platform Core Project Services | Reference only. |
| Knowledge Reuse | Platform Core Project Services | Reference only. |
| Clarification | Platform Core HIR / Project Services | Reference only. |
| Canonical Semantic Artifact | Platform Core Semantics | Reference only. |
| Runtime | Platform Core Runtime | Reference only. |
| Governance | Platform Core Governance | Reference only. |
| Replay | Platform Core Replay | Reference only. |
| Certification Registry | Platform Core Certification metadata | Reference only. |
| Provider Platform | Provider Platform | Reference only. |
| Worker Resolution | Worker Platform / domain-worker registry | Reference only. |

The missing capability was not any of those services. The missing capability was a deterministic PCCL binding artifact that can carry references to them without duplicating them.

## Reference Binding Specification

Implemented artifact:

- `PCCL_REFERENCE_BINDING_ARTIFACT_V1`

Implemented version:

- `G16_08_PCCL_REFERENCE_BINDING_V1`

Implemented operations:

- `create_pccl_reference_binding(...)`
- `validate_pccl_reference_binding(...)`
- `PlatformCoreCognitionLayer.create_reference_binding(...)`

Supported binding reference types:

- `PCCL_SESSION`
- `CONTEXT_ENVELOPE`
- `POLICY_ENVELOPE`
- `HUMAN_INTENT_RESOLUTION`
- `DEVELOPMENT_INTENT_RESOLUTION`
- `CAPABILITY_DISCOVERY`
- `KNOWLEDGE_REUSE`
- `CLARIFICATION`
- `CANONICAL_SEMANTIC_ARTIFACT`
- `RUNTIME`
- `GOVERNANCE`
- `REPLAY`
- `CERTIFICATION_REGISTRY`
- `PROVIDER_PLATFORM`
- `WORKER_RESOLUTION`

Binding invariants:

- PCCL Session artifacts are validated before binding.
- Canonical Context Envelope artifacts are validated before binding.
- Canonical Policy Envelope artifacts are validated before binding.
- Context and Policy envelopes must belong to the same PCCL Session.
- Session, Context Envelope, and Policy Envelope references are always included.
- Caller-provided service references are normalized, sorted, and deduplicated.
- Each binding reference is independently hashed.
- The binding artifact is independently hashed.
- Referenced payloads are not embedded.
- Existing Platform Core services are not invoked.
- Provider runtime is not created.
- Capability resolver is not created.
- Capability resolution is not performed.
- Governance logic is not duplicated.
- Replay is not implemented or modified.
- Proposal pipeline is not implemented.
- Cognitive loop is not implemented.
- Prompt text is not generated.
- Providers and workers are not invoked.

## Implementation Summary

Updated:

- `aigol/runtime/platform_core_cognition_layer.py`
  - Added `PCCL_REFERENCE_BINDING_VERSION`.
  - Added `PCCL_REFERENCE_BINDING_ARTIFACT_V1`.
  - Added binding reference type and owner metadata.
  - Added `create_pccl_reference_binding(...)`.
  - Added `validate_pccl_reference_binding(...)`.
  - Added service method `PlatformCoreCognitionLayer.create_reference_binding(...)`.
  - Added fail-closed validation for binding artifacts and binding reference entries.

- `aigol/runtime/platform_capability_certification_registry.py`
  - Registered `PCCL_REFERENCE_BINDING` as a certified metadata-only Platform Core capability.

Added:

- `tests/test_g16_08_pccl_reference_binding.py`
- `docs/governance/G16_08_PCCL_REFERENCE_BINDING.md`

## Integration Summary

The binding integrates with existing Platform Core services through certified references only.

Integration flow:

```text
PCCL Session
-> Canonical Context Envelope
-> Canonical Policy Envelope
-> PCCL Reference Binding
-> existing Platform Core service references
```

The binding does not call:

- `resolve_development_intent(...)`;
- `project_knowledge_context_from_workspace(...)`;
- provider selection;
- provider attachment;
- governance;
- replay;
- worker resolution;
- worker execution.

The binding can carry references to those services only after their owner-produced artifacts or certification references are available.

## Architectural Health Assessment

Duplication assessment:

- No duplicate Human Intent Resolution path introduced.
- No duplicate Capability Resolution path introduced.
- No duplicate Knowledge Reuse classifier introduced.
- No duplicate Governance logic introduced.
- No duplicate Replay logic introduced.
- No duplicate Provider Runtime introduced.
- No duplicate Provider Selection introduced.
- No duplicate Worker Execution path introduced.
- No prompt builder introduced.
- No proposal pipeline introduced.
- No cognitive loop introduced.

Ownership assessment:

- PCCL owns binding structure only.
- Existing Platform Core services retain behavioral authority.
- Provider Platform remains owner of provider mechanics.
- Worker Platform remains owner of execution.
- Governance remains owner of authorization.
- Replay remains certification authority.
- Certification Registry remains metadata only.

Risk assessment:

- Future milestones must not treat binding references as authorization.
- Future milestones must not dereference and execute services inside PCCL.
- Future milestones must not use the binding to bypass owner-specific validation.

Current health verdict:

```text
ARCHITECTURALLY_HEALTHY_REFERENCE_ONLY_BINDING
```

## Validation Summary

Validation performed:

- `python -m py_compile aigol/runtime/platform_core_cognition_layer.py aigol/runtime/platform_capability_certification_registry.py tests/test_g16_08_pccl_reference_binding.py`
- `python -m pytest tests/test_g16_08_pccl_reference_binding.py tests/test_g16_04_canonical_policy_envelope.py tests/test_g16_03_canonical_context_envelope.py tests/test_g16_02_pccl_session_runtime.py -q`
- `git diff --check`

Observed result:

- Focused py_compile passed.
- Focused regression passed: `29 passed`.
- `git diff --check` passed.

## Boundary Confirmation

G16-08 did not modify AiCLI.

G16-08 did not create a Provider Runtime.

G16-08 did not create Capability Resolution.

G16-08 did not execute Governance.

G16-08 did not implement Replay.

G16-08 did not implement a Proposal Pipeline.

G16-08 did not implement a Cognitive Loop.

G16-08 did not generate prompts.

G16-08 did not invoke providers.

G16-08 did not invoke workers.

G16-08 did not change Generation 14 ownership boundaries.

## Certification Verdict

CERTIFIED

G16-08 gives PCCL a deterministic reference binding layer that connects PCCL to existing Platform Core services exclusively through certified references.

No new runtime behavior is introduced.
