# G16-11 - PCCL Orchestration Decision Record

Status: CERTIFIED

Date: 2026-07-09

Milestone: G16-11

Scope: Deterministic PCCL Orchestration Decision Record. This milestone implements a reference-only decision artifact that records admissible PCCL proposal lifecycle transitions from existing owner-produced evidence. It does not implement an orchestration engine, provider invocation, provider selection, governance execution, replay execution, worker execution, proposal generation, prompt generation, cognitive loop control, runtime behavior, or AiCLI behavior.

## Objective

Implement the smallest deterministic capability identified by G16-10:

```text
PCCL Orchestration Decision Record
-> validated PCCL Session
-> validated Context Envelope
-> validated Policy Envelope
-> validated Reference Binding
-> validated Proposal Lifecycle
-> supporting owner-produced evidence references
-> admissible next PCCL lifecycle transitions
```

The Decision Record records which proposal lifecycle transitions are admissible. It never executes the transition.

## Knowledge Reuse Audit

G16-11 reused existing PCCL and Platform Core capabilities.

Reviewed governance evidence:

- `docs/governance/G16_01_PCCL_FOUNDATION.md`
- `docs/governance/G16_02_PCCL_SESSION_RUNTIME.md`
- `docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md`
- `docs/governance/G16_04_CANONICAL_POLICY_ENVELOPE.md`
- `docs/governance/G16_05_PCCL_PROVIDER_INTEGRATION_AUDIT.md`
- `docs/governance/G16_06_PCCL_CAPABILITY_RESOLUTION_AUDIT.md`
- `docs/governance/G16_07_PCCL_ARCHITECTURE_CONSOLIDATION_REVIEW.md`
- `docs/governance/G16_08_PCCL_REFERENCE_BINDING.md`
- `docs/governance/G16_09_PCCL_PROPOSAL_LIFECYCLE_FOUNDATION.md`
- `docs/governance/G16_10_PCCL_OPERATIONAL_READINESS_REVIEW.md`

Reviewed implementation surfaces:

- `aigol/runtime/platform_core_cognition_layer.py`
- `aigol/runtime/platform_capability_certification_registry.py`
- `aigol/runtime/platform_core_project_services.py`
- `aigol/runtime/provider_proposal_production_runtime.py`
- `aigol/runtime/provider_proposal_repair_and_retry_runtime.py`
- `aigol/provider/certified_provider_attachment.py`
- `aigol/provider/provider_proposal_envelope.py`
- `aigol/runtime/replay_certification_runtime.py`
- `aigol/runtime/human_interface_runtime_entry_service.py`

Reused capabilities:

- PCCL Session Runtime.
- Canonical Context Envelope.
- Canonical Policy Envelope.
- PCCL Reference Binding.
- PCCL Proposal Lifecycle.
- Platform Capability Certification Registry.
- deterministic hashing through `replay_hash`.
- fail-closed validation through `FailClosedRuntimeError`.
- existing Human Intent Resolution, Knowledge Reuse, Capability Discovery, Clarification, Provider Platform, Governance, Replay, Runtime, Certification, and Worker Resolution references.

No Platform Core service behavior was duplicated.

## Architecture Review

G16-10 determined that PCCL was not ready to begin governed cognition orchestration because it could track references and lifecycle state but could not yet record why a next PCCL lifecycle action was admissible.

G16-11 implements that missing record.

PCCL owns:

- decision record artifact identity;
- current proposal lifecycle state reference;
- admissible next proposal lifecycle transition list;
- selected next proposal lifecycle transition;
- supporting evidence references;
- deterministic fail-closed terminal reason;
- non-authority flags and artifact hash.

PCCL does not own:

- semantic interpretation;
- Human Intent Resolution;
- capability discovery;
- capability resolution;
- knowledge reuse classification;
- clarification;
- provider selection;
- provider invocation;
- provider proposal generation;
- governance execution;
- approval;
- runtime execution;
- replay execution;
- replay certification;
- worker execution;
- prompt generation;
- cognitive loop control.

No Generation 14 ownership boundary changed.

## Existing Capability Discovery

Existing PCCL artifacts already own the state required by a Decision Record:

| Artifact | Existing implementation | G16-11 reuse |
| --- | --- | --- |
| PCCL Session | `create_pccl_session(...)` | Required validated reference. |
| Context Envelope | `create_canonical_context_envelope(...)` | Required validated reference. |
| Policy Envelope | `create_canonical_policy_envelope(...)` | Required validated reference. |
| Reference Binding | `create_pccl_reference_binding(...)` | Required validated reference. |
| Proposal Lifecycle | `create_pccl_proposal_lifecycle(...)` and transition helpers | Required validated current lifecycle state. |
| Certification Registry | `platform_capability_certification_registry(...)` | G16-11 capability registration. |

Existing Platform Core behavioral services remain reusable by reference only:

- Human Intent Resolution.
- Development Intent Resolution.
- Capability Discovery.
- Knowledge Reuse.
- Clarification.
- Runtime.
- Governance.
- Replay.
- Certification Registry.
- Provider Platform.
- Worker Resolution.

The genuinely missing deterministic capability was not an engine. It was the record connecting validated current lifecycle state to admissible PCCL lifecycle transitions.

## Decision Record Specification

Implemented artifact:

- `PCCL_ORCHESTRATION_DECISION_RECORD_ARTIFACT_V1`

Implemented version:

- `G16_11_PCCL_ORCHESTRATION_DECISION_RECORD_V1`

Implemented operations:

- `create_pccl_orchestration_decision_record(...)`
- `validate_pccl_orchestration_decision_record(...)`
- `PlatformCoreCognitionLayer.create_orchestration_decision_record(...)`

Core fields:

- `decision_id`
- `created_at`
- `pccl_session_id`
- `pccl_session_hash`
- `context_envelope_id`
- `context_envelope_hash`
- `policy_envelope_id`
- `policy_envelope_hash`
- `reference_binding_id`
- `reference_binding_hash`
- `proposal_id`
- `proposal_lifecycle_hash`
- `current_lifecycle_state`
- `admissible_next_lifecycle_transitions`
- `selected_next_lifecycle_transition`
- `decision_rationale_reference`
- `fail_closed_reason`
- `supporting_evidence_references`
- `artifact_hash`

Supported supporting evidence reference types:

- `PCCL_SESSION`
- `CONTEXT_ENVELOPE`
- `POLICY_ENVELOPE`
- `REFERENCE_BINDING`
- `PROPOSAL_LIFECYCLE`
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

Validation invariants:

- PCCL Session must validate.
- Context Envelope must validate and belong to the PCCL Session.
- Policy Envelope must validate and belong to the PCCL Session and Context Envelope.
- Reference Binding must validate and belong to the PCCL Session, Context Envelope, and Policy Envelope.
- Proposal Lifecycle must validate and belong to the PCCL Session and Reference Binding.
- Admissible next lifecycle transitions are calculated from the existing proposal lifecycle transition table.
- Selected transition must be one of the admissible transitions.
- Terminal proposal lifecycle states record no selected transition and set `fail_closed_reason` to `TERMINAL_PROPOSAL_LIFECYCLE_STATE`.
- Supporting evidence references are normalized, sorted, deduplicated, and independently hashed.
- The artifact is independently hashed.

Non-execution invariants:

- transition execution is false;
- Platform Core service invocation is false;
- semantic interpretation is false;
- capability resolution is false;
- provider selection is false;
- provider invocation is false;
- proposal generation is false;
- governance execution is false;
- approval granting is false;
- runtime invocation is false;
- replay execution and mutation are false;
- worker invocation is false;
- cognitive loop start is false;
- prompt generation is false.

## Integration Summary

G16-11 integrates only with existing deterministic artifacts:

```text
PCCL Session
-> Context Envelope
-> Policy Envelope
-> Reference Binding
-> Proposal Lifecycle
-> Orchestration Decision Record
```

The Decision Record may reference Platform Core evidence created by existing owners. It does not dereference, execute, evaluate, select, invoke, authorize, certify, or mutate that evidence.

The selected transition is advisory for PCCL lifecycle progression only. It is not itself a transition operation.

## Architectural Health Assessment

Duplication assessment:

- No orchestration engine introduced.
- No provider runtime introduced.
- No provider selection introduced.
- No capability resolver introduced.
- No proposal generator introduced.
- No governance path introduced.
- No replay path introduced.
- No worker execution path introduced.
- No prompt builder introduced.
- No cognitive loop introduced.

Ownership assessment:

- PCCL owns the decision record shape only.
- Proposal Lifecycle owns state transitions.
- Provider Platform owns providers.
- Governance owns policy execution and approval semantics.
- Replay owns replay persistence, reconstruction, and certification.
- Runtime owns runtime entry and continuation.
- Worker Platform owns worker execution.

Risk assessment:

- Future milestones must not treat `selected_next_lifecycle_transition` as an executed transition.
- Future milestones must not treat admissibility as governance authorization.
- Future milestones must not derive provider selection, approval, or replay certification from this record.

Current health verdict:

```text
ARCHITECTURALLY_HEALTHY_REFERENCE_ONLY_DECISION_RECORD
```

## Validation Summary

Validation performed:

- `python -m py_compile aigol/runtime/platform_core_cognition_layer.py aigol/runtime/platform_capability_certification_registry.py tests/test_g16_11_pccl_orchestration_decision_record.py`
- `python -m pytest tests/test_g16_11_pccl_orchestration_decision_record.py tests/test_g16_09_pccl_proposal_lifecycle.py tests/test_g16_08_pccl_reference_binding.py tests/test_g16_04_canonical_policy_envelope.py tests/test_g16_03_canonical_context_envelope.py tests/test_g16_02_pccl_session_runtime.py tests/test_g15_governance_01_platform_capability_certification_registry.py -q`
- `git diff --check`

Observed result:

- Focused py_compile passed.
- Focused regression passed: `44 passed`.
- `git diff --check` passed.

## Boundary Confirmation

G16-11 did not modify AiCLI.

G16-11 did not implement an orchestration engine.

G16-11 did not execute a lifecycle transition.

G16-11 did not invoke Cognition Providers.

G16-11 did not select providers.

G16-11 did not generate proposals.

G16-11 did not execute governance.

G16-11 did not grant approval.

G16-11 did not execute replay.

G16-11 did not invoke workers.

G16-11 did not implement a cognitive loop.

G16-11 did not generate prompts.

G16-11 did not change Generation 14 ownership boundaries.

## Certification Verdict

CERTIFIED

G16-11 gives Platform Core a deterministic PCCL Orchestration Decision Record.

The artifact records current proposal lifecycle state, admissible next PCCL lifecycle transitions, and supporting evidence references without executing or duplicating any Platform Core behavior.
